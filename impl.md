# Vireo Audio — Task 1 (Set E): Project Explanation + Master Prompt

---

## PART 1 — WHAT THIS PROJECT IS (plain-English explanation)

### The situation
Vireo Audio is a Bengaluru consumer-audio and wearables brand (earbuds, headphones, smart speakers, watches) selling on its own site, Amazon and Flipkart. Its support desk has **44 agents** across **Bengaluru and Indore**, on **3 shifts**, handling **chat, email, voice callbacks and social**. Volume is roughly **650 tickets/week**.

You are playing a **vendor being evaluated**. The client, **Priya Raman (Head of CX)**, wrote:

> "I want to know where to add headcount. Can you auto-categorise the tickets and give me a monthly breakdown chart by category and by team? Our tags are probably rubbish but they're a start. Whichever team has the most volume gets the next two hires. Sameer has the exports."

### What is really being tested
This is not "build a classifier." It is a test of judgment:

1. **Can you turn a vague email into a measurable business goal** (a number + rupees) that you find yourself in the data?
2. **Can you prove your tool works** (sample size, error rate, failure types)?
3. **Will you push back** where the client's ask is flawed? ("Most volume = most hires" is a shaky rule — volume is not the same as workload, cost, or avoidable work. Check handle time, reopens, escalations, repeat contacts, and the cost figures in `support-policy.pdf`.)
4. **Can you scope honestly?** The brief says ~5 hours, "going over is not rewarded", and that not finishing everything is expected. What you *leave out and why* is scored.
5. **Are you honest about AI use, cost, and flaws?** Two form questions ("did you push back" and "what is wrong with your work") *can only raise your score*.

### The files you were given
| File | What it is | How you will likely use it |
|---|---|---|
| `tickets.csv` | 18 months of tickets (Jan 2025–Jun 2026) with 2 free-text fields: customer's opening message + agent's closing note | Core dataset; categorise from text, compare to existing tags |
| `agents.csv` | Roster, one row per assignment | Map tickets → agent → team/site/shift. "One row per assignment" means agents can move teams, so join by date, not just agent id |
| `orders.csv`, `customers.csv`, `products.csv` | Reference data | Enrich tickets (product, region, order value, repeat customers, return/refund exposure) |
| `support-policy.pdf` | Operating policy **including what things cost** | Source of the rupee figures for your business-goal number (refund costs, SLA penalties, cost per contact, etc.) |
| `email-thread.txt` | Prior Vireo ↔ vendor conversation | Hidden requirements/context. **Read it first and carefully.** |
| `README.txt` | Column definitions | Data dictionary — read before touching the CSVs |

### What you must deliver (6 things)
1. **A working AI-assisted tool** — any stack/model; must start from your README on a clean machine. "A small thing that runs beats a large thing that does not."
2. **A business goal stated as a number** — e.g. "Cut X from 22% to 15%, worth about Rs Y a quarter." You find X and Y in the data.
3. **Evidence it works** — how you know the output is correct and how often it's wrong.
4. **A one-page memo to Priya** — non-technical, ≤ 11 minutes reading.
5. **A screen recording ≤ 3 min** — prompts used, what changed between versions, what you threw away. No slides.
6. **`submission-form.md` completed** (the form questions are listed in Part 4 below).

### Rules of the game
- 48-hour window, ~5 hours of effort. **Respect the cap.**
- No one to ask. Where unclear: **Decide → write down what you decided → explain why.**
- AI tools are fine; honestly report what you used, what it cost, what you discarded.
- Bring your own API keys; no credits provided.

### Likely traps / things to investigate (verify in the data — don't assume)
- **Tags are "probably rubbish"**: measure how bad. Compare existing tag vs. your text-derived category (a confusion matrix is a great artifact).
- **"Most volume gets the hires"**: volume ≠ workload. Check handle/resolution time, reopen rate, escalations, repeat contacts, channel mix, shift coverage, per-agent load.
- **Team attribution**: tickets may be routed to one team but handled by another; roster changes over time (agents.csv has multiple assignments per agent).
- **Duplicates / spam / merged tickets / test tickets / missing values / timezone issues** in the exports.
- **Mixed-language or messy text** (Hinglish, typos, very short messages) in the free-text fields.
- **Avoidable contacts**: categories that exist because of a product defect, bad documentation, delivery delay, or a policy gap — fixing the root cause may save more than hiring.
- **Policy PDF costs** — use these for your Rs figure; state assumptions.
- **Seasonality / launches / spikes** (sales events like Big Billion Days / Great Indian Festival) may distort "monthly" trends.
- **Closing note vs. opening message may disagree** — the true issue is often only in the agent's closing note.

---

## PART 2 — MASTER PROMPT (copy everything inside the box below into your AI coding assistant)

> Tip: Paste this into Claude Code / Cursor / ChatGPT with the project folder containing all 8 files + `submission-form.md`. If the assistant can't read files, paste the relevant file contents too.

````text
ROLE
You are a senior data/AI engineer and analytics consultant helping me complete a time-boxed vendor evaluation task. I am the vendor; the client is Vireo Audio. Be pragmatic, honest, and scope-aware. A small thing that runs beats a large thing that does not.

HARD CONSTRAINTS
- Total effort budget: ~5 hours. Do not over-build. Plan the work in phases and tell me what you are deliberately cutting.
- Any stack, any models. Prefer Python + pandas + a small CLI/Streamlit app. Must start from a README on a clean machine (pinned requirements, one command to run, sample output committed).
- The tool must work even with NO API key (e.g. a rules/TF-IDF/embedding fallback) so reviewers can run it; LLM calls should be optional and cached.
- Keep API cost low and track it (tokens in/out, $ and Rs per run).
- Do not fabricate numbers. Every figure in the memo/form must be reproducible from the data and a script I can re-run.
- Where the brief is unclear: DECIDE, WRITE DOWN what was decided, and WHY. Keep a running DECISIONS.md.

CONTEXT
Vireo Audio is a Bengaluru consumer-audio and wearables brand (earbuds, headphones, smart speakers, watches) selling via its own site, Amazon and Flipkart. Its support desk has 44 agents across Bengaluru and Indore on three shifts, across chat, email, voice callbacks and social. Volume ≈ 650 tickets/week.

The client email from Priya Raman, Head of Customer Experience:
"I want to know where to add headcount. Can you auto-categorise the tickets and give me a monthly breakdown chart by category and by team? Our tags are probably rubbish but they're a start. Whichever team has the most volume gets the next two hires. Sameer has the exports."

FILES PROVIDED (in the project folder)
- tickets.csv — 18 months of tickets (Jan 2025–Jun 2026) incl. two free-text fields: the customer's opening message and the agent's closing note
- agents.csv — roster, one row per assignment (agents may change team/site/shift over time)
- orders.csv, customers.csv, products.csv — reference data
- support-policy.pdf — Vireo's support operating policy, INCLUDING what things cost
- email-thread.txt — prior conversation between Vireo and us (hidden context; read carefully)
- README.txt — column definitions

DELIVERABLES
1. Working AI-assisted tool (runs from README on a clean machine)
2. A business goal stated as a number with a rupee value (e.g. "Cut X from A% to B%, worth ~Rs Y per quarter"), derived from the data and the policy PDF costs
3. Evidence the tool works: sample size, method, error rate, kinds of cases it gets wrong
4. A one-page, non-technical memo to Priya (≤ 11 minutes reading; ideally ~1 page)
5. Notes for a ≤ 3-minute screen recording: prompts used, what changed between versions, what was thrown away
6. Completed submission-form.md

STEP-BY-STEP WORKPLAN (follow in order; stop and summarise after each phase)

PHASE 0 — Read everything first (≈20 min)
- Read README.txt, email-thread.txt, and support-policy.pdf fully. Extract: (a) any requirements or constraints in the email thread that go beyond Priya's email, (b) every cost figure/SLA/penalty/target in the policy, (c) category or team definitions the client already uses.
- Inspect every CSV: shape, dtypes, nulls, duplicates, date ranges, value counts for tags/teams/channels/shifts. Report data-quality issues (duplicates, test/spam tickets, merged tickets, timezone problems, inconsistent labels, missing closing notes, language mix, PII).
- Output: a short "What I learned" summary and a list of open ambiguities with the decision you propose for each.

PHASE 1 — Data model & team attribution (≈30 min)
- Join tickets → agents (by agent id AND ticket date vs. assignment dates, since agents have multiple assignments) → team/site/shift. Join orders/customers/products for enrichment (product line, order value, customer repeat-contact, region).
- Decide and document what "team" means (agent's team at ticket creation? resolving agent? routed queue?). Show how many tickets are ambiguous/unmatched.

PHASE 2 — Baseline: how bad are the existing tags? (≈20 min)
- Profile existing tags: distribution, obvious misuse (e.g. huge "Other/General" bucket), inconsistent labels, tags contradicted by the free text.
- Produce a first monthly breakdown by existing tag and by team so there's a baseline to compare against.

PHASE 3 — Auto-categorisation (≈90 min)
- Propose a category taxonomy (aim for 8–14 mutually exclusive categories, plus "Other/Unclear") grounded in a sample of the text and the client's existing tags. Explain the taxonomy and where it differs from the tags.
- Build the classifier as a layered pipeline: (1) cheap deterministic/keyword/regex rules for obvious cases, (2) embeddings/TF-IDF + a simple model or nearest-centroid as a no-API fallback, (3) optional LLM call (cached, batched, JSON-schema output, temperature 0) only for low-confidence tickets. Use BOTH the opening message and the agent's closing note, and say which one wins on conflict.
- Return for each ticket: category, confidence, short rationale, and which layer decided.
- Handle messy text (typos, Hinglish/mixed-language, very short messages).
- Track and print cost (tokens, $, Rs) per run.

PHASE 4 — Evaluation (≈60 min) — THIS IS SCORED
- Draw a stratified random sample (≥150–200 tickets, covering all categories, channels and months). Hand-label them (I will label; you prepare a labelling sheet that hides the model prediction to avoid bias). If I cannot label them all, use a clearly-disclosed alternative (e.g. LLM-as-judge with spot-check) and state its limitations.
- Report: overall accuracy, per-category precision/recall/F1, confusion matrix, confidence calibration (is low confidence actually less accurate?), and error rate with a confidence interval. Compare against the existing tags as a baseline.
- Characterise the failure modes with concrete examples (e.g. refund vs. return, defect vs. user error, multi-issue tickets).
- Report honestly how often it is wrong and what that means for the headcount decision.

PHASE 5 — Answer the real business question (≈60 min)
- Produce the requested monthly breakdown charts: tickets by category and by team (clean, labelled, readable; stacked bars or small multiples; both as PNG and inside the app).
- Then test Priya's rule ("most volume gets the next two hires") against better measures: per-agent load by team and shift, handle/resolution time, reopen/repeat-contact rate, escalation rate, backlog/SLA breach, channel mix, seasonality, and trend (growing vs. flat). State whether the rule holds. If it does not, say what the data recommends instead and why. Be explicit about what the data can and cannot show.
- Find the BUSINESS GOAL NUMBER: identify an avoidable or costly pattern (e.g. a category driven by a product defect or shipping delay, repeat contacts, refunds/escalations with policy-defined costs). Quantify current rate, a realistic target, and the rupee value per quarter using ONLY costs from support-policy.pdf and data. Show the arithmetic and assumptions. Format: "Cut X from A% to B%, worth about Rs Y a quarter."

PHASE 6 — Packaging (≈40 min)
- README: prerequisites, install, one-command run, expected output, how to run with and without an API key, how to reproduce the eval, folder structure.
- Provide sample outputs committed to the repo so a reviewer can see results without running anything.
- Write memo.md (one page, non-technical, no jargon: recommendation, the number, the money, the headcount answer, confidence/limits, what I'd do next). Lead with the answer.
- Write DECISIONS.md (every ambiguity → decision → reason), LIMITATIONS.md (honest list of bugs/shortcuts/known issues), and COST.md (cost of one run + a month at ~650 tickets/week).
- Draft answers for every question in submission-form.md.
- Draft a 3-minute screen-recording script: prompts used, v1 → v2 → v3 changes, what was thrown away.

COST ARITHMETIC (show it explicitly)
- Monthly volume ≈ 650 tickets/week × 52 / 12 ≈ 2,817 tickets/month.
- Cost per ticket = (avg input tokens × input price + avg output tokens × output price), adjusted by the share of tickets that actually reach the LLM layer. Show the formula, the assumptions, the model price used, the one-run cost on the 18-month dataset, and the monthly cost at Vireo's volume. If no paid calls were used, say so explicitly.

QUALITY BAR / THINGS TO WATCH
- Do not hide uncertainty. Report error rates and where the tool fails.
- Challenge the client's framing where the data warrants it, and say when and why.
- Anything built/found that nobody asked for (e.g. a data-quality finding, a defect hotspot, an agent-mobility problem in the roster) goes in the "unasked-for" section.
- Everything in the memo must be traceable to a script/notebook in the repo.
- Flag any place where you (the AI) are guessing instead of computing.

OUTPUT FORMAT EACH PHASE
1. What I did (3–5 lines)
2. Key findings (numbers)
3. Decisions made + why
4. What I am deliberately NOT doing + why
5. Risks / things that might be wrong
6. Next phase

START NOW with Phase 0. Do not skip ahead. Ask me only if you literally cannot proceed; otherwise decide and document.
````

---

## PART 3 — REPO STRUCTURE TO AIM FOR

```text
vireo-support-triage/
├── README.md                 # run from clean machine, with and without API key
├── requirements.txt          # pinned
├── DECISIONS.md              # ambiguity -> decision -> why
├── LIMITATIONS.md            # honest list of what is wrong
├── COST.md                   # one-run cost + monthly cost arithmetic
├── memo.md                   # one-page memo to Priya
├── submission-form.md        # completed
├── data/                     # (or instructions to place the CSVs)
├── src/
│   ├── load_and_clean.py
│   ├── attribute_teams.py
│   ├── classify.py           # rules -> embeddings/TF-IDF -> optional LLM
│   ├── evaluate.py
│   ├── analysis.py           # headcount test + business-goal number
│   └── charts.py
├── app.py                    # optional small Streamlit/CLI front end
├── eval/
│   ├── labelling_sheet.csv
│   ├── labels_done.csv
│   └── eval_report.md
└── outputs/
    ├── tickets_categorised.csv
    └── charts/*.png
```

---

## PART 4 — SUBMISSION FORM: WHAT EACH QUESTION WANTS

| Form question | What a strong answer contains |
|---|---|
| What did you build, and what business outcome does it move? State the number and the money. | 2–3 sentences on the tool + one line: "Cut X from A% to B%, worth ~Rs Y/quarter," with a pointer to the script that computes it |
| What does one run cost, and what would a month cost (~650 tickets/week)? Show arithmetic. | Formula, token counts, price, one-run cost, ~2,817 tickets/month cost. Say "no paid calls" if true |
| How do you know it works? | Sample size, how labelled, accuracy + CI, per-category weak spots, failure examples, comparison to existing tags |
| Did you change, narrow, or push back on the client's ask? *(can only raise score)* | E.g. "Tested the 'most volume gets hires' rule against workload/handle-time; here is what changed and when" |
| What is wrong with what you are handing us? *(can only raise score)* | Specific bugs, shortcuts, known-off numbers, untested assumptions |
| What did you deliberately leave out, and why? | 3–5 items with reasons tied to the 5-hour cap and impact |
| Anything you built/found that nobody asked for? | Data-quality issues, defect hotspots, roster problems |
| What did you use AI for? Link recording. | Tools/models, where they helped, where they wasted time, what was discarded + Drive link |
| Public Google Drive link | Recording, memo, charts, outputs |
| Someone picks this up Monday and you're unreachable — the three things they need to know | 1) how to run it, 2) the key decisions/assumptions, 3) the biggest known weakness / next step |
| Honest hours spent | One number, ≤ ~5 |
| GitHub repo link | Public repo URL |

---

## PART 5 — MEMO TEMPLATE (one page, for Priya)

```text
To: Priya Raman   From: <you>   Re: Where to add headcount at the support desk

THE ANSWER (2–3 sentences)
<Which team(s) to add to, and whether the "most volume" rule holds. Lead with the answer.>

THE NUMBER
<Cut X from A% to B% — worth about Rs Y a quarter.>

WHAT WE FOUND
- <3 bullets, plain language, each with a number>

WHERE I DISAGREED WITH THE BRIEF (and why)
- <e.g. Volume alone is not workload; here is what the data says instead>

HOW SURE WE ARE
- Checked <N> tickets by hand; the tool was right <X>% of the time. It struggles with <case>. Existing tags were right only <Y>% of the time.

WHAT I'D DO NEXT
1. <action>  2. <action>  3. <action>

WHAT I LEFT OUT (and why)
- <items>
```

---

## PART 6 — 3-MINUTE SCREEN-RECORDING SCRIPT

| Time | Show | Say |
|---|---|---|
| 0:00–0:20 | Repo + one-line description | What the tool does and the headline number |
| 0:20–1:00 | Prompt v1 → v2 → v3 | What each prompt was, what was wrong with the earlier ones, what changed |
| 1:00–1:40 | Eval report / confusion matrix | Sample size, error rate, worst failure mode |
| 1:40–2:20 | Charts + headcount finding | Where I pushed back on "most volume" and why |
| 2:20–3:00 | Thrown-away work + limitations | What I discarded (approaches, prompts, features) and what's still wrong |

---

## PART 7 — TIME BUDGET (~5 hours, hard cap)

| Block | Time |
|---|---|
| Read pack (email thread, policy, README) + data profiling | 0:50 |
| Team attribution + baseline | 0:30 |
| Categorisation tool | 1:30 |
| Evaluation (labelling + metrics) | 0:50 |
| Headcount test + business-goal number + charts | 0:50 |
| README, memo, form, recording | 0:50 |
| **Total** | **~5:20 → trim categorisation/eval polish to stay ≤ 5:00** |

**Cut-first list (if time runs short):** polished UI, multi-model comparison, fine-tuning, per-agent performance analysis, forecasting. **Never cut:** README that runs, error-rate evidence, the business-goal number, honest limitations.