# Result-based gameplay patterns

Choose the lightest mechanic that strengthens the theme. Every scored action must resolve to a stable option ID in `quiz.json`.

| Mechanic | Use when | Interaction | Main risk |
| --- | --- | --- | --- |
| `linear-cards` | Default quizzes and mobile pages | Pick one option per scene | Can feel generic without strong scenes |
| `swipe-cards` | Fast, visual, binary or ternary choices | Swipe or tap a card | Oversimplifies nuanced dimensions |
| `scenario-journey` | The theme supports a day, trip, mission, or story | Move through connected scenes | Branches can accidentally bias reachability |
| `resource-draft` | Choices involve priorities or trade-offs | Spend limited tokens across options | Resource rules can dominate personality evidence |
| `rapid-rounds` | Social campaigns and event screens | Answer short timed rounds | Timers reduce accessibility and reflection |

## Selection rules

- Use `linear-cards` unless another mechanic adds meaning.
- Use `scenario-journey` for themes such as office survival, fantasy roles, travel partners, or crisis behavior.
- Use `resource-draft` only when scarcity is part of the promise.
- Make swipe and keyboard controls equivalent.
- Make timers optional and never penalize users who enable reduced motion or accessibility modes.

## Narrative rules

- Open with an easy, vivid situation.
- Increase tension through the middle without implying one morally correct route.
- End with an identity-relevant choice that feels memorable but does not override the full score.
- Let earlier choices change flavor text or scene order only when all result types remain reachable.
- Never disguise random result assignment as story logic.

## Feedback rules

Prefer lightweight reactions such as changing scene copy, an avatar expression, or a resource indicator. Do not reveal dimension labels, score changes, or the likely result during play unless transparency is the explicit concept.

Keep failure playful and reversible. A personality experience should not punish a participant for choosing an honest answer.

## Delivery checklist

- Define the mechanic and why it fits the promise.
- Map every action to `question_id` and `option_id`.
- Keep the quiz core valid without the game shell.
- Test at least three different paths and one back-navigation path.
- Confirm restart clears all prior answers and resources.
- Confirm narrative branches never replace deterministic classification.
