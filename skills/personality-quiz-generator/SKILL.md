---
name: personality-quiz-generator
description: Generate personality quizzes, role-matching tests, entertainment divination quizzes, intuition or projection tests, result-based interactive games, and playable quiz webpages from a topic, prompt, document, webpage, dataset, character library, or other context. Use when users ask to 生成性格测试、人格测试、趣味测试、趣味占卜、占卜测试、心理投射测试、直觉选择测试、角色匹配测试、答题小游戏、测试类 H5/网页, or need questions, symbolic readings, result archetypes, deterministic scoring, quiz JSON, result cards, or a runnable interactive experience. Keep the scope to experiences whose choices produce a personality, role, character, symbolic reflection, or type result; do not use for generic games, clinical assessment, or factual supernatural prediction.
---

# Personality Quiz Generator

Turn limited context into a reusable quiz core, then deliver it as questions, a playable conversation, an implementation package, a result-based game, or a runnable webpage. Keep scoring deterministic and results enjoyable to claim. Frame divination-style themes as entertainment and reflection rather than factual prediction.

## Load only the needed resources

Always read [references/quiz-design-guide.md](references/quiz-design-guide.md).

Read [references/entertainment-divination-guide.md](references/entertainment-divination-guide.md) for 趣味占卜, fortune-themed, oracle-style, intuition-choice, or psychological-projection quizzes.

Read [references/quiz-spec-schema.md](references/quiz-spec-schema.md) when producing JSON, files, code, a game, a webpage, or scoring validation.

Read [references/experience-spec-schema.md](references/experience-spec-schema.md) for games and interactive webpages.

Read [references/gameplay-patterns.md](references/gameplay-patterns.md) only for a game or playful interaction.

Read [references/web-experience-guide.md](references/web-experience-guide.md) only for a webpage or app. Reuse [assets/web-template](assets/web-template) when a portable web artifact is appropriate.

Resolve every relative path from this `SKILL.md` directory.

## Collect the minimum input

Require two inputs:

1. **Test theme**: Accept a word, prompt, pasted text, document, webpage, dataset, role library, or other supplied context.
2. **Expected duration**: If missing, offer these mutually exclusive choices instead of requesting a free-form number:
   - **Quick — about 2 minutes**: 6–8 questions; 4–6 results.
   - **Standard — about 4 minutes (recommended)**: 10–14 questions; 6–10 results.
   - **Deep — about 7 minutes**: 18–24 questions; 8–16 results.

Honor an exact duration and do not ask again. Infer audience, tone, result granularity, visual direction, and delivery target from the request. Ask another question only when ambiguity would materially change the artifact or create unsafe claims.

## Route to the requested delivery target

Infer one target without asking when the user's wording is clear:

- **Design**: Deliver positioning, dimensions, results, questions, scoring, result copy, sharing, and quality notes. Use this default when the user only asks to generate a test.
- **Play now**: Administer one participant-facing question at a time, record stable option IDs, and reveal the computed result only after completion.
- **Implementation package**: Create a validated `quiz.json` and, when relevant, an `experience.json`.
- **Interactive game**: Select a fitting mechanic, keep every scored action mapped to a stable quiz option ID, and create the requested playable artifact when the user asks to build rather than only design it.
- **Interactive webpage**: Create a runnable responsive experience, not only a concept or code excerpt. Use an available site/app builder when explicitly requested; otherwise adapt the bundled portable template.

Do not expand into a generic game or website builder. If choices do not produce a personality, role, character, symbolic reflection, or type result, use a more appropriate skill.

## Build the reusable quiz core

### 1. Understand the theme

Read supplied context with the relevant read-only tool. Extract the participant's reason for taking the quiz, intended social setting, source-defined entities and constraints, emotional tone, and claims that must not be invented. Keep source facts, assumptions, and creative proposals distinct. If linked content is inaccessible, request the relevant text. For a divination-style theme, identify the reflective lens—current energy, opportunity, relationship pattern, inner need, or next-step reminder—without promising that the result predicts external events.

### 2. Write one concrete promise

State what the participant will discover in one sentence. Avoid promises to explain a whole personality.

### 3. Design results before questions

- Use 4–6 continuous dimensions with understandable, equally respectable poles.
- Define every result as a distinct target vector on all dimensions.
- Keep results reachable, non-hierarchical, memorable, and worth sharing.
- Treat types as a presentation layer over continuous scores, not absolute categories.

### 4. Write behavior-based choices

- Prefer concrete situations and observable choices over self-labels.
- Give each question 3–4 plausible options with similar length and desirability.
- Let each question mainly affect one or two dimensions.
- Measure every dimension in different contexts at least twice; target three or more times for Standard and Deep.
- Avoid obvious heroic, intelligent, kind, or embarrassing answers.
- Use a light narrative rhythm when the theme supports it.

### 5. Make scoring deterministic

Assign fixed numeric contributions to stable option IDs. Derive each dimension's theoretical range from the actual options, normalize it to 0–100, and match the participant vector to result target vectors with weighted root-mean-square distance. Apply tie-breaks in this order:

1. lower distance;
2. more dimensions within the configured close-dimension threshold;
3. lower result priority;
4. lexical result ID.

Never add random assignment, secret balancing, or an unrelated override question. The same spec and answers must always produce the same scores and result.

### 6. Write evidence-backed result content

Give every result a name, hook, description, strengths, trade-offs, relevant behavior, answer-linked evidence, share line, conversation prompt, complete target vector, and consistent visual identity. Show a secondary tendency only when it falls within the configured threshold. Do not invent rarity percentages.

## Create the requested artifact

### Design

Deliver the creator-facing quiz in this order:

1. positioning and assumptions;
2. dimensions;
3. result map;
4. participant-facing questions;
5. hidden scoring specification;
6. result copy;
7. sharing package;
8. quality report.

### Play now

Show only title, promise, progress, questions, options, and final results. Do not expose score mappings during play. Preserve selected option IDs, calculate with the bundled scoring rules, and explain the result through measured dimensions or recognizable answer patterns.

### Implementation package

Create `quiz.json` using schema version `1.1`. Run:

```bash
python3 scripts/validate_quiz.py /path/to/quiz.json
python3 scripts/score_quiz.py /path/to/quiz.json /path/to/answers.json
```

Fix errors before delivery. Include `experience.json` and validate it when the output has screens, mechanics, navigation, or sharing behavior:

```bash
python3 scripts/validate_experience.py /path/to/experience.json /path/to/quiz.json
```

### Interactive game

Choose one mechanic from the gameplay guide. Keep branching, animation, inventory, timers, and narrative consequences in `experience.json`; keep all scored choices and result targets in `quiz.json`. Narrative branches may change presentation but must not secretly override the computed result.

### Interactive webpage

Create a working artifact with intro, question, progress, transition, result, share, restart, loading, and error states. Keep hidden mappings out of visible UI. Default to local-only answers with analytics disabled unless the user explicitly requests collection and disclosure.

When adapting the bundled template:

1. copy `assets/web-template/` into the output project;
2. replace its sample `quiz.json` and `experience.json`;
3. preserve or deliberately reimplement `scoring.js` behavior;
4. run the validators and score the same fixture with Python and JavaScript when both runtimes are used;
5. serve the project over HTTP, complete multiple answer paths, test restart/share, and inspect mobile and keyboard behavior;
6. return the runnable artifact path or preview URL plus validation results.

## Validate before delivery

Confirm that:

- question count fits the selected duration;
- every dimension varies repeatedly across different contexts;
- every result has a distinct target vector and a reachable winning region;
- no single ordinary question dominates a dimension;
- result claims trace to scores or answer patterns;
- participant UI never reveals hidden mappings accidentally;
- game actions map to stable option IDs;
- repeated scoring produces identical output;
- webpages work on narrow screens and with keyboard navigation;
- result cards make sense without the full report.

Treat validator warnings as review prompts, not permission to ignore weak design.

## Respect the boundary

Use generated quizzes for entertainment, reflection, education, or product engagement. Treat fortune- and divination-themed output as symbolic entertainment: use possibility language, disclose that it is not factual prediction, and never introduce curses, threats, guaranteed outcomes, or certainty about health, pregnancy, death, money, legal matters, or major life decisions. Do not claim clinical validity, diagnose conditions, or recommend an unvalidated quiz for hiring, medical, legal, financial, or other high-stakes decisions. Do not collect personal answers or analytics without explicit user intent and visible disclosure.
