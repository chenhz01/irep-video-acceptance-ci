# IREP-AVC — AI Video Acceptance: Cutting the Luck Tax

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![Python 3.10+ · stdlib only](https://img.shields.io/badge/python-3.10%2B%20%C2%B7%20stdlib%20only-3776AB.svg)](#reproduce) [![Measured 9.82x](https://img.shields.io/badge/measured-9.82%C3%97-brightgreen.svg)](#measured-results) [![Safety layer never trades away](https://img.shields.io/badge/safety%20layer-never%20trades%20away-critical.svg)](#the-discipline-non-negotiable)

> **An AI-generated video — would you put it straight into an ad campaign?**

Status: prototype v1.0.0 · License: MIT · Dependencies: Python standard library only · Every number below is re-runnable.

**Three ways in — pick one, thirty seconds each**

- **Here to cut a bill** → the number first: 9.82× fewer generations, 200,000-draw Monte Carlo, seed 20261016, re-runnable in about 30 seconds.
- **Here to integrate** → `python video_acceptance_ci.py`; then adopt the one rule: no sampling-reduction claim ships without held-out calibration.
- **Here to doubt it** → an uncalibrated verifier over-promised by +112%; read the arithmetic and the honest boundaries before trusting any multiple.


---

## Feynman guide — read this first (60 seconds)

**What is this?**
A prototype that attacks "luck-based sampling" in AI-video acceptance on two fronts: the **generation draw** (blindly generating K candidates and picking one — the GPU bill) and the **review frame-check** (uniformly sampling N frames and hoping to catch the defect — the eyes/compute bill). It replaces both with searches constrained by invariants calibrated on held-out data.

**Why should you care?**
Because if you accept AI video by luck, you cannot know whether you are losing money. This prototype's sharpest finding is a warning: an uncalibrated verifier that "feels 95% accurate" over-promised its own sampling reduction by **+112%**. Calibration is not about bigger claims — it is about being falsifiable.

**What should you do?**
Run `python video_acceptance_ci.py` (fixed seed, ~30 seconds). Then apply its one rule to your own pipeline: **no sampling-reduction claim ships without held-out calibration.**

<!-- FGA4:axes -->
**Four-axis alignment — the number is checked, not asserted**

A lone "9.82×" is meaningless: change the base rate and it moves. So every claim here is pinned on four axes, and the structure is enforced by a runnable checker.

| Axis | What it pins down | How it is checked here | Where the evidence lives |
|---|---|---|---|
| **Result** | the multiple is always shipped with `q`, verifier `Se/Sp`, seed and draw count | §3 of the long-form doc gives a hand calculation you can do on paper | `video_acceptance_ci.py`, exit 0 |
| **Mechanism** | why *specificity* decides everything at a low base rate | PPV formula + a table showing Sp → multiple | §4.2 |
| **Code** | one command, stdlib only, fixed seed 20261016, deterministic | run it and compare two lines | `## Reproduce` |
| **Direction** | the safety layer never trades away; G8 is out of scope | three hard bindings, stated before the results | `## Safety binding` |

Full contract — 10,000+ Chinese characters, fourteen scenarios, six analogies, sourced references, and four failure modes: [`docs/FEYNMAN-4ALIGN.zh-CN.md`](docs/FEYNMAN-4ALIGN.zh-CN.md).

English condensed edition (about 2,200 words) — the same four axes for the video domain, the same number ledger (9.84 hand / 9.82 simulation / 3.68 mediocre / +112% overstated), the same failure conditions, and the safety bindings placed before the numbers: [`docs/FEYNMAN-4ALIGN.en.md`](docs/FEYNMAN-4ALIGN.en.md). If the two editions ever disagree on a number, the Chinese edition is authoritative.

```bash
python feynman_align_check.py --repo .   # vendored copy of the parent repo's checker; fails closed
```

---

## The two luck taxes

```
T1  generation draw — per prompt, blindly generate K candidates, keep 1. Burns the GPU bill.
T2  review sampling — uniformly check N frames, hoping to hit the defect. Burns eyes and compute.
```

IREP's treatment: T1 uses a **held-out calibrated verifier**, turning the blind draw's true acceptance rate `q` into `PPV` (accepted ⇒ actually good). Expected generations drop from `1/q` to `1/PPV`. The reduction multiple is `PPV/q`. T2 uses **frame-to-frame invariants (change-point detection)**: a cheap 1-D signal scans the whole timeline almost for free; expensive re-checks zoom only near change points.

<a id="measured-results"></a>
## Measured results (200,000-draw Monte Carlo, seed = 20261016, re-runnable)

**T1 — generation draw** (hard prompt, base acceptance rate q = 8%):

| Verifier | held-out Se / Sp | measured reduction | naive guess ("95% accurate") | verdict |
|---|---|---|---|---|
| Strong verifier | 0.978 / 0.977 | **9.82×** | 7.79× | conservative −21% (missed upside) |
| Mediocre verifier | 0.874 / 0.818 | **3.68×** | 7.79× | **dangerous +112% overconfidence** |

The mediocre row is the whole point: without held-out calibration you do not merely miss the upside — you book a saving you never had.

**T2 — review frame-check** (300-frame video, 2% defect duration, 95% catch confidence):

| Strategy | frames to check | |
|---|---|---|
| Uniform sampling | 149 | |
| IREP adaptive (15-frame sparse baseline + 16-frame zoom × 2 change points) | 47 | **3.2×** |

**The judgment rule:** at a low base rate, PPV is decided almost entirely by **specificity Sp** — and Sp can only be established by held-out calibration. That is why the calibration step is not optional decoration; it is the load-bearing wall.

## The discipline (non-negotiable)

> **No held-out calibration ⇒ no reduction claim.** An uncalibrated reduction is luck wearing the costume of determinism.

## Safety binding — G8 (read before using this in production)

Video synthesis is dual-use. This repository's scope is **acceptance and provenance, never synthesis guidance**:

1. The L1 safety layer (deepfake / IP / prohibited-content checks) **never participates in sampling reduction** — safety frames are always fully checked.
2. The held-out calibration set **must include adversarial safety samples**; a verifier calibrated only on benign samples is a liability, not an asset.
3. Any use touching weapons, malware, unauthorized surveillance, or other dual-use lethal domains is out of scope, full stop (this is the parent protocol's G8 gate: <https://github.com/chenhz01/irep>).

## Honest boundaries

- Every number here comes from a **Monte Carlo simulation with a fixed seed (20261016)**, re-runnable via `python video_acceptance_ci.py`. They demonstrate the mechanism; they are **not production measurements**.
- The verifier's Se/Sp are *given* configurations in the simulation. In a real pipeline they must be calibrated on your own held-out set — that is the discipline the prototype exists to teach.
- This is a prototype: no framework dependencies, no I/O beyond stdout, exit code 0 on success.

## Reproduce

```bash
python video_acceptance_ci.py     # stdlib only, ~30 seconds, seed 20261016
```

## The repo next door — and why we don't trade stars

<!-- FGA4:sister -->
This repo is the money side. The protocol side lives one click away, and neither works as an argument alone.

| | **`chenhz01/irep-video-acceptance-ci`** (you are here) | **`chenhz01/irep`** |
|---|---|---|
| The question it answers | "How much does luck cost me per finished video?" | "May I stand on this system — and is my build a second generation?" |
| Unit of value | a multiple (9.82× generation, 3.2× frame-check) | a verdict (one word, four scales) |
| 30-second payoff | a measured number you can hand-check | four contrast verdicts from one command |
| Best if you are | paying GPU bills or reviewers' hours | shipping something derived from someone else's system |
| Star it when | you want the number that survives a budget meeting | you want the gate that runs before the build |

**Read them in this order:** if you do not yet believe the method is honest, go to the parent repo — its first proof is the ruler measuring itself. If you already believe it and want the economics, stay here. A star on both is a vote for "measure before you claim"; a star on one is a vote for the half you needed.

**What we will NOT do:** star-for-star exchanges, bought placements, follow-back schemes, or asking for a star before you have run the command. Star counts are the only unfakeable feedback signal; trading them away would be trading away the instrument.

## Trending pledge — a guarantee we can actually keep

<!-- FGA4:trending -->
"Guaranteed to trend" cannot be promised by anyone: ranking belongs to a platform algorithm. Promising what you do not control is marketing; promising what you do control is a contract. Here is the falsifiable version.

| # | Commitment | Measurable test | If we break it |
|---|---|---|---|
| 1 | The 9.82× / 3.68× / 3.2× can be recomputed from the command | run it twice, same numbers (seed 20261016) | numbers corrected or removed within 7 days |
| 2 | The hand calculation in the long-form doc matches the simulation | do the arithmetic on paper (§3.2) | errata published, credited to you |
| 3 | Issues get a first response within 48 h | issue timestamp vs first reply | we say so publicly if we miss it |
| 4 | No adoption claim we cannot evidence | we publish no usage numbers we cannot source | claim retracted |
| 5 | Unstar any time, no argument | your star is not a contract | — (that is the point) |

**What "trending" honestly means here:** no chart position, no star target, no algorithm boost — we do not control those, and a repo promising them is telling you something about how it treats evidence. We promise the causes: a first screen worth reading, a number that survives a hand-check, and a maintainer who answers.

**The falsification test, stated up front:** run `python video_acceptance_ci.py` on a clean Python 3.10+. If it fails, or the printed multiple disagrees with the hand calculation, this pledge is void — the repo is wrong, not your environment.

## Lineage

Prototype of the video-acceptance direction of the IREP protocol — parent repository: [`chenhz01/irep`](https://github.com/chenhz01/irep). Same license (MIT), same collaboration terms.

Contact: `hcac4735@agent.qq.com` (primary; 50 messages/day cap) · `shanlun2029@outlook.com` (overseas alternative). Response target: 48 hours.
