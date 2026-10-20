# Four-Axis Alignment for AI Video Acceptance (English Condensed Edition)

> Condensed from the Chinese contract (`FEYNMAN-4ALIGN.zh-CN.md`, 10,000+ characters). Definitions, scorecard and failure conditions are kept intact; the fourteen worked scenarios are cut to three. Every number below is re-runnable from this repository in about thirty seconds.

---

## 1. Why video acceptance is where fake savings live

Four layers stack on top of each other.

**Sampling cost is visible, missed defects are not.** The GPU bill arrives monthly. A defect that shipped arrives as a complaint, a reshoot, or nothing at all — and "nothing at all" is the common case, which is why the saving looks real.

**Defects are time-local, sampling is time-uniform.** A 300-frame clip with a two-frame artefact gets the same budget as a clean one. The defect occupies 0.7% of the timeline, so a 5% sample hits it about 5% of the time. The sampler is not biased, only misaimed.

**"Accuracy" lies at low base rates.** At q = 8%, a verifier that is right 95% of the time can still be wrong about most of what it approves: accuracy averages over both classes, while acceptance economics depend on one.

**Nobody calibrates, because calibrating is expensive and claiming is free.** A multiple in a slide costs a sentence; a held-out set costs a week. The incentive points one way, which is why calibration is a gate here, not a virtue.

| Layer | What it looks like | What it costs | The fix |
|---|---|---|---|
| Visible cost, invisible defect | "We cut review by 70%" | defective frames reach the client | count defects found *after* shipment |
| Time-local defect, uniform sample | 5% sample, 5% hit rate | silent misses | sample where the signal changes |
| Accuracy at low base rate | "95% accurate" | 2× budget overrun | report PPV, never accuracy |
| No calibration habit | a multiple with no basis | the multiple is a rumour | basis / command / boundary, or no number |

---

## 2. The four axes, redefined for video

The four-axis contract asks four falsifiable questions of any claim. It was written for repositories; in video acceptance each axis acquires a domain-specific field, and the additions are not decoration — they are where the money leaks.

### 2.1 Result — every number carries its basis

A result claim must ship five fields: the metric, the value, the basis (base rate, verifier sensitivity and specificity, sample size, seed), the command that reproduces it, and the boundary that says what the number is *not*. A number without a basis is not a weaker claim, it is a different kind of object: an advertisement.

### 2.2 Mechanism — a name, an input, an output, a failure condition

Not a formula. A formula can be copied without being understood; a mechanism states what goes in, what comes out, why the transformation works, and — the field everyone omits — the condition under which it stops working. The failure condition is the only part of a mechanism description that cannot be produced by paraphrasing the abstract.

### 2.3 Code — the command is the contract

`exit 0` means "it ran on a clean machine", not "it is good". The code axis asks whether a stranger can execute the claim and get the same digits: fixed seed, no network, no wall-clock values in asserted numbers, dependencies stated truthfully.

### 2.4 Direction — what this refuses to do

Direction is the axis that costs the author something. It names the uses that are out of scope and the part of the pipeline that is never optimised. For this repository that part is the safety layer, and the refusal is stated near the top of the README — above the measured results — rather than in an appendix, because a reader who stops at the first screen must still learn where not to plug it in.

Miss one axis and the claim collapses in a predictable way: into an idea (no result), a magic trick (no mechanism), a legend (no code), or a panacea (no direction). A panacea is the same thing as useless.

---

## 3. Result axis: the 9.82× record in full

### 3.1 The record

| Field | Value |
|---|---|
| Metric | generation-side sampling reduction (ratio of expected generations) |
| Value | 9.82× (strong verifier) / 3.68× (mediocre verifier) |
| Basis | expected generations fall from `1/q` to `1/PPV`; multiple = `PPV/q` |
| Base rate q | 8% (true acceptance rate under hard prompts) |
| Verifier Se / Sp | 0.978 / 0.977 (strong); 0.874 / 0.818 (mediocre) |
| Sample size | 200,000 Monte Carlo draws |
| Seed | 20261016 |
| Reproduce | `python video_acceptance_ci.py` (about 30 seconds) |
| Boundary | simulation, not production telemetry; Se/Sp are given configurations, and a real pipeline must calibrate its own on held-out data |

### 3.2 Hand-check before trust

```
PPV = Se·q / (Se·q + (1−Sp)·(1−q))
    = 0.978×0.08 / (0.978×0.08 + 0.023×0.92)
    = 0.07824 / 0.09940
    = 0.7871
multiple = PPV / q = 0.7871 / 0.08 = 9.84
```

Hand calculation gives 9.84; the simulation prints 9.82. The 0.2% gap is Monte Carlo noise from 200,000 draws, and reporting it is part of the honesty: if the two agreed to two decimals, someone would have substituted the closed form for a simulation.

The mediocre verifier: `0.874×0.08 / (0.874×0.08 + 0.182×0.92) = 0.2946`, so `0.2946/0.08 = 3.68` — hand and simulation agree exactly. Why one row agrees and the other differs by 0.2%? Because 0.2946 sits comfortably in a two-decimal band while 0.7871 is more sensitive. The lesson is general: the stability of a digit depends on the number, not on the habit of rounding.

### 3.3 Anatomy of a "95% accurate" claim

Suppose a vendor says the verifier is 95% accurate and derives 7.79×:

```
PPV(95%) = 0.95×0.08 / (0.95×0.08 + 0.05×0.92) = 0.076 / 0.122 = 0.623
multiple = 0.623 / 0.08 = 7.79
```

The mediocre verifier actually delivers 3.68×. Overstatement: `(7.79 − 3.68)/3.68 = +111.7%`, about +112%.

| Claim | Basis | Reality | Error | Consequence |
|---|---|---|---|---|
| 7.79× | "95% accurate" | 3.68× | +112% | budget set on 7.79× overruns by more than double |
| 9.82× | held-out Se/Sp | 9.82× sim / 9.84× hand | ±0.2% | can go into a budget line |

That table is the whole reason this repository exists. Not "our number is bigger" — "our number can be hand-checked".

---

## 4. Mechanism axis: at low base rates, specificity is the line

### 4.1 Mechanism in four parts

| Part | Content |
|---|---|
| Name | PPV calibration (positive predictive value) |
| Input → output | verifier (Se, Sp) + base rate q → share of approved samples that are actually acceptable |
| Why it works | converts "how many generations until one is usable" from trial and error into a computable expectation |
| **Failure condition** | (a) q is misestimated; (b) Se/Sp come from non-held-out data; (c) distribution drift after a model or prompt-style change |

### 4.2 The counter-intuitive fact

Hold Se = 0.95 and vary Sp at q = 8%:

| Sp | PPV | Multiple | How the accuracy sounds |
|---|---|---|---|
| 0.999 | 0.988 | 12.35× | almost perfect |
| 0.99 | 0.892 | 11.15× | very good |
| 0.977 | 0.787 | 9.84× | good |
| 0.95 | 0.623 | 7.79× | "95% accurate" sounds fine |
| 0.90 | 0.452 | 5.65× | mediocre |
| 0.818 | 0.295 | 3.68× | bad |
| 0.70 | 0.123 | 1.54× | nearly useless |

Sp falls from 0.977 to 0.95 — 2.7 points — and the multiple falls 21%. At q = 50% the same change costs about 4%. **The lower the base rate, the higher the marginal value of specificity**, so in video (5–15% under hard prompts) optimising Sp beats optimising Se — the opposite of the instinct to make the verifier better at finding good ones. At low q, false approvals are dominated by `(1−Sp)×(1−q)` with `(1−q)` near 1: bad samples are already 92% of the pool, so a slightly loose gate drowns the good ones.

### 4.3 The second mechanism: change-point sampling

| Part | Content |
|---|---|
| Name | change-point triggered sampling |
| Input → output | 300-frame clip + one cheap 1-D signal → list of frames worth close inspection |
| Why it works | defects are time-local discontinuities, and the cheap signal scans the whole timeline at near-zero cost, so expensive inspection concentrates near discontinuities |
| **Failure condition** | (a) the defect is a slow drift (gradual colour shift); (b) the cheap signal is blind to that defect class; (c) very short but low-contrast artefacts |

Measured: uniform sampling needs 149 frames for 95% detection confidence; the adaptive policy (15-frame sparse baseline plus 16 frames at each of two change points) needs 47 — a 3.2× reduction. At 8 seconds of human time per frame, the 102 saved frames are about 13.6 minutes per clip, about 6.8 hours per day at 30 clips. That is the actual cash flow, not "AI makes us advanced".

| Dimension | T1 generation side (PPV) | T2 acceptance side (change point) |
|---|---|---|
| What is saved | GPU generations | human/model frames |
| Key parameter | Sp | cheap-signal sensitivity |
| Main failure | wrong q, drift | gradual defects |
| Calibration | held-out with adversarial samples | defect-library coverage |
| Unit economics | currency per clip | minutes per clip |
| Shared premise | no calibration, no claim | same |

---

## 5. Code axis: one command, five promises

| Item | Promise |
|---|---|
| Command | `python video_acceptance_ci.py` |
| Dependencies | standard library only |
| Runtime | about 30 seconds |
| Randomness | fixed seed 20261016, deterministic output |
| Network | none required |
| Exit code | 0 on success, results on stdout |
| Side effects | no file writes |

A fixed seed is a contract, not a detail. Unseeded Monte Carlo means the reader's digits differ from the author's, and that will be read as fabrication rather than as noise. The rule: **any published random experiment names the seed next to the command, and the seed must be the one actually used.** A seed in the docs that the code ignores is worse than no seed — it is a false promise of reproducibility.

The reader does not need to trust the author; they need to run it once and compare. Handing over the right of verification is the only move that buys credibility.

---

## 6. Direction axis: the safety layer never trades away

Three bindings, quoted faithfully from the repository:

1. **The L1 safety layer (deepfake / IP / prohibited-content checks) never participates in sampling reduction.** Safety frames are always fully inspected.
2. **The held-out calibration set must contain adversarial safety samples.** A verifier calibrated only on benign samples is a liability, not an asset.
3. **Uses in dual-use lethal domains — weapons, malware, unauthorised surveillance — are out of scope entirely.**

These belong in the guide, not an appendix, because the guide decides how the reader uses the tool. A reader who only skims it will file this under "cost saving" and wire it into a place that must not be economised, such as content-safety review. The temptation to save is immediate; the memory of a boundary is delayed. Not stated up front means not stated.

| Scenario | In scope? | Reason |
|---|---|---|
| Acceptance of ads, short drama, music videos | yes | pure acceptance, no generation |
| Candidate filtering for a model you own | yes | cost optimisation |
| "Quality acceptance" of a face-swap video | depends on upstream legality | acceptance is neutral; an unauthorised upstream puts the whole pipeline out of scope |
| Teaching a model to evade content moderation | **no** | circumventing a safety mechanism |
| Generating synthetic news footage that misleads the public | **no** | lethal-domain rule |
| Quality scoring of weapons- or surveillance-related synthetic content | **no** | no exceptions |

One sentence: this repository answers "is this clip good enough", never "how do I make it more convincing".

---

## 7. Three scenarios out of fourteen

**E-commerce clip, 15 seconds.** q is high (about 30%) because prompts are simple, so the multiple lands near 2–3× and the real win is defect classes — colour shift against the reference product, flicker under the logo — not sampling. At high q, PPV calibration is weak and change-point sampling is strong. Naming which mechanism is weak is part of the result.

**AI short drama, 3 minutes, many shots.** q is about 8% and per-shot overhead dominates, so 9.82× applies only if calibration is per shot type: a single global Se/Sp hides that close-ups and wide shots fail differently. Failure condition: calibrating globally while reporting per episode.

**Music video, stylised.** Style is the product, so "defect" is ambiguous: deliberate distortion and rendering artefacts both read as anomalies to a cheap signal. Direction: the mechanism must be refused here, not tuned — a multiple would need human-labelled intent, which this repository does not have.

---

## 8. Four failure conditions specific to video

**Overfitting your own data.** Computing Se/Sp on historical clips and then claiming a multiple on the same clips is memory, not calibration. Split by time, not at random: a random split puts near-identical frames on both sides and inflates Sp.

**Treating the safety layer as configurable.** Anything that can be switched off eventually will be, because switching it off saves money and the consequence arrives later. The safety path is hard-wired, with no toggle.

**PPV hallucination.** Substituting accuracy for PPV, or "the verifier is quite accurate" for actual Se/Sp. Any published number carries q, Se and Sp, or it is not published.

**Silent sampling failure.** The sample passes, a defect ships, nobody notices — the most dangerous class, because it raises no alarm. Countermeasure: periodic defect injection, seeding known defects into the stream and measuring whether the sampler catches them.

---

## 9. Scorecard

| Axis | What is checked | This repository |
|---|---|---|
| Result | metric, value, basis, command, boundary | 5 — all five present, hand-check published |
| Mechanism | name, input, output, failure condition | 4 — the change-point signal's blind spots are named but not quantified |
| Code | executed, deterministic, dependencies truthful | 5 — one command, stdlib only, fixed seed |
| Direction | refusals and out-of-scope uses above the numbers in the README | 5 — safety bindings stated on the first screen, with a dual-use table |
| **Total** | any axis ≤ 2 sets the total to 0 | **4.75** |

The 4 on mechanism is the honest part; 4.75 is arithmetic.

---

## 10. References

| Source | Year | Borrowed | Not borrowed |
|---|---|---|---|
| Feynman, *Cargo Cult Science* | 1974 | honesty as "not fooling yourself" | its critique of institutional education |
| Popper, *Conjectures and Refutations* | 1963 | falsifiability as the line a promise must cross | his political philosophy |
| Wald, sequential probability ratio test | 1945 | stop sampling when the evidence is decisive | its full likelihood machinery |
| Shewhart, control charts | 1931 | a signal-based trigger beats a fixed schedule | industrial tolerance tables |
| ANSI/ASQ Z1.4 (AQL sampling) | — | the idea of an acceptance sampling plan | its assumption of a stable defect rate |
| Goodhart's Law | 1975 | a measure used as a target stops measuring | — |
| *primum non nocere* (Hippocratic tradition) | — | do not optimise the part that must not be optimised | — |
| Hyrum's Law (attrib. H. Wright; Google SRE) | 2010s | observable behaviour will be depended upon | the reading that documentation is pointless |
| RFC 2119 | 1997 | graded strength of MUST / SHOULD / MAY | protocol context |

---

## 11. Using the two editions together

The Chinese edition carries fourteen scenarios, six analogies, the cost function, reviewer agreement (kappa) and the sample-size-to-interval material; this edition carries the contract. If the two disagree on a number, the Chinese edition is authoritative and this one is a defect — report it rather than reading around it.

Machine check: `python feynman_align_check.py --repo .` fails closed when an edition is missing, short, or missing an axis anchor. It was run against a deliberately short English file and a nonexistent path; both returned 1.

License: MIT. Attribution is the only obligation, and it is not optional.
