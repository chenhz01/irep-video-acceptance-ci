# -*- coding: utf-8 -*-
"""
IREP-AVC: AI 视频验收 CI 减抽卡原型
费曼导读（60 秒）：
    这是什么——一台减抽卡机：把 AI 视频的「盲抽」变成「受不变量约束的搜索」——生成端期望数 1/q → 1/PPV，验收端只在突变处加密抽帧。
    为什么和你有关——视频烧的是 GPU 账单和眼睛；本原型实测减抽卡 9.82×，且安全层永不参与减抽卡。
    你该怎么办——python video_acceptance_ci.py，看校准后的 PPV 与减抽卡倍数是怎么算出来的。
=====================================
核心命题: 抽卡 = 未受教育的搜索; IREP = 把它变成受「不变量」约束的搜索。
两路抽卡:
  T1 生成抽卡  — 每 prompt 盲生成 K 个候选挑 1。烧的是 GPU 账单。
  T2 验收抽帧  — 均匀抽 N 帧人工/重模型验。烧的是眼睛/算力。
IREP 处置:
  T1 用 held-out 标定的 verifier, 把盲抽的「真接受率 q」提升为「PPV(被认可即真好)」,
     期望生成数 1/q -> 1/PPV。减抽卡倍数 = PPV / q。
  T2 用帧间不变量 change-point, 把均匀抽帧变自适应: 只在突变处 zoom, 平时只留稀疏基线。
关键纪律: 减抽卡倍数由 held-out 校准的「特异性 Sp」决定; 没校准的减抽卡 = 把运气伪装成确定性。
"""
import random, math

random.seed(20261016)

# ---------------------------------------------------------------------------
# T1 生成抽卡: 盲抽 vs IREP 标定 verifier
# ---------------------------------------------------------------------------
def expect_blind(q):
    """盲抽卡: 期望多少个生成才能拿到 1 个真可接受 (q = 原始可接受率)"""
    return 1.0 / q

def ppv(q, se, sp):
    """阳性预测值 P(真可接受 | verifier 说可接受)"""
    num = q * se
    den = q * se + (1 - q) * (1 - sp)
    return num / den

def expect_irep(q, se, sp):
    return 1.0 / ppv(q, se, sp)

def reduction(q, se, sp):
    return expect_blind(q) / expect_irep(q, se, sp)

def heldout_calibrate(q, mu_g, mu_b, sigma, thr, n=200000):
    """蒙特卡洛: 在 held-out 标定集上真算 Se / Sp, 而非拍脑袋"""
    se_hit = sp_hit = g = b = 0
    for _ in range(n):
        if random.random() < q:           # 真可接受
            g += 1
            if random.gauss(mu_g, sigma) > thr: se_hit += 1
        else:                              # 真不可接受
            b += 1
            if random.gauss(mu_b, sigma) <= thr: sp_hit += 1
    return se_hit / g, sp_hit / b

def demo_t1():
    q = 0.08                              # 难 prompt: 仅 8% 原始生成可接受
    # 两个 verifier 配置: 一个真强, 一个中庸 —— 看「没标定」会往哪边偏
    scenarios = [
        ("强 verifier",   0.85, 0.25, 0.15, 0.55),
        ("中庸 verifier", 0.80, 0.35, 0.22, 0.55),
    ]
    naive_se = naive_sp = 0.95            # 拍胸脯「我的 verifier 95% 准」
    naive_red = reduction(q, naive_se, naive_sp)
    blind = expect_blind(q)
    print("=== T1 生成抽卡 (减 GPU 账单) ===")
    print(f"原始可接受率 q                 = {q:.2%}  | 盲抽期望生成 1/q = {blind:.2f}")
    print(f"朴素声称倍数(未标定, 猜 95%)  = {naive_red:.2f}x")
    rows = []
    for name, mu_g, mu_b, sigma, thr in scenarios:
        se, sp = heldout_calibrate(q, mu_g, mu_b, sigma, thr)
        real_red = reduction(q, se, sp)
        drift = (naive_red - real_red) / real_red
        tag = "保守(漏报潜力)" if drift < 0 else "危险(过度自信)"
        print(f"  [{name}] held-out Se/Sp={se:.3f}/{sp:.3f} "
              f"实标={real_red:.2f}x  朴素差 {drift:+.0%} -> {tag}")
        rows.append(dict(name=name, se=se, sp=sp, real_red=real_red, drift=drift))
    print("  判据: 没 held-out 你连自己亏没亏都不知道; 标定的价值是「可证伪」, 不是吹更大。")
    return dict(q=q, blind=blind, naive_red=naive_red, rows=rows)

# ---------------------------------------------------------------------------
# T2 验收抽帧: 均匀 vs IREP 自适应 change-point
# ---------------------------------------------------------------------------
def uniform_needed(D, w, P):
    """均匀抽帧, 想以概率 P 命中占比 w/D 的缺陷, 需抽多少帧"""
    return math.ceil(math.log(1 - P) / math.log(1 - w / D))

def demo_t2():
    D, w, P = 300, 6, 0.95          # 300 帧视频, 2% 时长的缺陷, 要 95% 抓住
    m_uniform = uniform_needed(D, w, P)
    baseline = math.ceil(0.05 * D)  # IREP 稀疏安全基线 5%
    r = 8                            # 突变处 zoom 半径 (>= w/2)
    n_cp = 2                         # 缺陷进出产生 2 个 change point
    m_irep = baseline + n_cp * (2 * r)
    red = m_uniform / m_irep
    print("\n=== T2 验收抽帧 (减人工/重模型眼睛) ===")
    print(f"视频时长 D / 缺陷占比 w / 置信 P = {D}f / {w}f({w/D:.0%}) / {P:.0%}")
    print(f"均匀抽帧需检                    = {m_uniform} 帧")
    print(f"IREP 自适应需检 (基线{baseline}+zoom{2*r}*{n_cp}) = {m_irep} 帧")
    print(f"减抽帧倍数                      = {red:.1f}x")
    print("机理: 帧间不变量 diff 是「廉价 1D 信号」(几乎免费全扫),")
    print("      贵的「重检/人眼」只在 change point 附近 zoom。")
    return dict(D=D, w=w, m_uniform=m_uniform, m_irep=m_irep, red=red)

# ---------------------------------------------------------------------------
# 主报告
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("#" * 64)
    print("# IREP-AVC 减抽卡原型实跑")
    print("#" * 64)
    t1 = demo_t1()
    t2 = demo_t2()
    print("\n=== 一句话结论 ===")
    print("抽卡是未受教育的搜索; IREP 把它变成受不变量约束的搜索。")
    for r in t1["rows"]:
        print(f"  生成抽卡[{r['name']}] 实标减 {r['real_red']:.1f}x")
    print(f"  验收抽帧 实标减 {t2['red']:.1f}x")
    print("两路都吃。但减抽卡倍数必须由 held-out 校准, 否则只是把运气当确定性。")
