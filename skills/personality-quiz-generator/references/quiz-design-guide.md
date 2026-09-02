# Personality quiz design guide

Use this guide to turn a broad theme into a quiz that is enjoyable, credible, and easy to share.

## 1. Choose the right product promise

Build the quiz around one user-facing question. Good promises are specific enough to constrain the result:

- Which role do you naturally take when a team faces uncertainty?
- Which fictional world would reward the way you make decisions?
- What kind of creative collaborator are you?
- Which career environment brings out your best work?

Avoid promises that imply complete personality coverage or diagnosis. Narrow promises make shorter quizzes more believable.

If the source is a document, webpage, or dataset, extract its native concepts before inventing new ones. Preserve supplied role names and factual boundaries. Use source content as evidence, not decoration.

## 2. Translate duration into scope

| Preset | Time | Questions | Core dimensions | Results | Best use |
| --- | ---: | ---: | ---: | ---: | --- |
| Quick | ~2 min | 6–8 | 3–4 | 4–6 | Social campaign, event, lightweight match |
| Standard | ~4 min | 10–14 | 4–5 | 6–10 | Default consumer personality quiz |
| Deep | ~7 min | 18–24 | 5–6 | 8–16 | Rich report, repeated measurement |

Treat these as design budgets, not scientific thresholds. Reduce reading load when questions contain long scenarios. Increase repeated measurement before increasing the number of result types.

## 3. Build useful dimensions

Write dimensions as tensions between two legitimate strategies. A dimension should:

- matter to the test promise;
- describe a repeatable preference or behavior;
- be observable in more than one context;
- avoid moral hierarchy;
- produce meaningful differences between results.

Good examples:

- initiate ↔ observe;
- improvise ↔ plan;
- preserve harmony ↔ challenge directly;
- follow evidence ↔ explore possibility;
- act independently ↔ coordinate closely.

Weak examples:

- good ↔ bad;
- intelligent ↔ unintelligent;
- successful ↔ unsuccessful;
- normal ↔ abnormal.

Do not reuse a famous framework merely because it is familiar. Select dimensions from the supplied theme unless the user explicitly requests MBTI, Big Five, DISC, Enneagram, or another framework.

## 4. Create results before questions

For each result, define:

1. **Role in the system**: what makes it different from neighboring results.
2. **Target vector**: desired 0–100 value on every dimension.
3. **Identity hook**: a sentence users might willingly share.
4. **Strength and cost**: the same tendency expressed as an advantage and a trade-off.
5. **Behavioral evidence**: what this result would likely choose in relevant situations.

Avoid result pairs that differ only in wording. Check the distance between target vectors and revise near-duplicates.

Keep all results socially claimable. Distinction should come from different strategies, not from assigning some users flattering identities and others humiliating ones.

## 5. Write engaging items

### Prefer behavior over identity

Weak:

> I am an imaginative person.

Better:

> A project brief leaves half the details open. What do you do first?

### Give every option a real benefit

Design choices as trade-offs:

- move quickly with incomplete information;
- gather evidence before committing;
- align people before choosing;
- prototype several possibilities.

Avoid one heroic option surrounded by obviously careless options.

### Limit what each item measures

Let a question mainly affect one dimension and optionally a second. If every option changes every dimension, the relationship between answers and results becomes hard to explain.

### Cross-check without repetition

Measure a dimension through different settings—for example, a new group, a conflict, and a deadline. Do not paraphrase the same question three times.

### Control response bias

- Match option length and specificity.
- Balance social desirability.
- Mix high- and low-pole wording.
- Avoid absolutes such as “always” and “never” unless the situation requires them.
- Do not make the result identity obvious from the option wording.
- Use a neutral option only when neutrality is meaningful, not as an escape from every trade-off.

### Create pacing

Open with an easy, vivid choice. Put more diagnostic trade-offs in the middle. End with a memorable identity-relevant situation. For thematic quizzes, connect questions through a light journey without making earlier choices lock later answers.

## 6. Select a response format

Use scenario multiple choice by default for playful, themed quizzes. Use three or four options so each choice can represent a distinct strategy.

Use a Likert scale when measuring agreement with many short behavioral statements. Include both directions and keep the scale consistent.

Use forced choice when two statements can be matched closely for desirability. Do not claim forced choice removes all response bias.

Do not use open-ended responses for the scored core. Open-ended prompts may appear after the result for reflection, but they must not silently change the computed type.

## 7. Engineer shareable results

Treat the result as an identity artifact with four layers:

1. **Recognition**: a memorable name, code, or archetype.
2. **Evidence**: why the answers produced this result.
3. **Tension**: a strength paired with its cost.
4. **Conversation**: a prompt that gives other people something to respond to.

A good share card usually contains:

- result name and short code;
- one visual identity;
- one sentence with a recognizable tension;
- two short traits or dimension highlights;
- a prompt such as “Do you see this in me?”;
- a path for others to take the same quiz.

Keep the card readable at social-feed size. Put the detailed explanation on the result page, not the card.

Do not use unsupported rarity claims, deterministic compatibility claims, or negative labels that users would hide rather than share.

## 8. Write specific result copy

Prefer conditional, behavioral language:

> When a group is stuck, you tend to create a workable direction before everyone agrees. This gives the team momentum, but it can make quieter objections arrive late.

Avoid universal statements:

> You value relationships but sometimes need time alone.

Tie the explanation to high or low dimension scores and, when possible, recognizable answer patterns. Do not list only compliments; credible recognition comes from a useful tension.

## 9. Validate the design

### Structural checks

- Give every question and option a stable ID.
- Use only declared dimension IDs in score mappings.
- Ensure every dimension has a nonzero theoretical range.
- Ensure every result has a complete target vector.
- Specify deterministic tie-breaks.

### Experience checks

- Ask whether a user can predict a desired result too easily.
- Ask whether any option is embarrassing or obviously correct.
- Confirm that all results are attractive enough to share.
- Confirm that result explanations differ in substance.
- Confirm that the selected duration matches actual reading time.

### Data checks after launch

When response data exists, examine:

- completion and abandonment by question;
- option selection imbalance;
- result distribution;
- internal consistency by dimension;
- short-interval retest stability;
- result acceptance and disagreement reasons;
- group-level bias and translation effects.

Treat unusual distributions as a reason to investigate, not permission to randomize or secretly rebalance individual results.

## 10. Separate creator and participant views

Creator-facing output may include scoring vectors, target profiles, formulas, and validation warnings.

Participant-facing output should include only the questions, options, progress, result explanation, and share experience. Hide scoring keys unless transparency is part of the product concept.
