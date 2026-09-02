# Quiz core specification

Use this contract for the reusable scored content behind documents, conversations, games, and webpages. Keep interface behavior in `experience.json`, not here.

## Contents

- Top-level contract
- Dimensions and questions
- Results and scoring
- Answer and result payloads
- Validation rules

## Top-level contract

Create UTF-8 JSON with these required fields:

```json
{
  "schema_version": "1.1",
  "id": "office-animals",
  "title": "你是哪种办公室动物？",
  "promise": "发现团队忙起来时你会自然承担的角色。",
  "locale": "zh-CN",
  "audience": "职场用户与同事社交场景",
  "duration": { "preset": "standard", "minutes": 4 },
  "dimensions": [],
  "questions": [],
  "results": [],
  "scoring": {
    "method": "weighted_rms",
    "close_dimension_threshold": 15,
    "secondary_result_threshold": 5
  },
  "tie_break": ["distance", "close_dimensions", "priority", "result_id"]
}
```

Use short, stable, lowercase ASCII IDs matching `^[a-z][a-z0-9-]*$`. Keep participant-facing copy in the requested language.

Duration presets:

| Preset | Minutes | Questions | Results |
| --- | ---: | ---: | ---: |
| `quick` | about 2 | 6–8 | 4–6 |
| `standard` | about 4 | 10–14 | 6–10 |
| `deep` | about 7 | 18–24 | 8–16 |
| `custom` | supplied | proportional | appropriate to evidence |

## Dimensions and questions

Declare 4–6 dimensions by default:

```json
{
  "id": "initiative",
  "name": "行动起点",
  "low_label": "先观察",
  "high_label": "先发起",
  "weight": 1
}
```

Give each question and option a stable ID. Map an option only to dimensions it affects; omitted dimensions contribute zero.

```json
{
  "id": "q1",
  "text": "一个新项目只给了模糊方向，你先做什么？",
  "options": [
    {
      "id": "a",
      "text": "先做出一个粗略版本",
      "scores": { "initiative": 2, "planning": -2 }
    }
  ]
}
```

Use 3–4 plausible options for playful quizzes. Normally keep contributions between -2 and 2. Make every core dimension vary across at least two questions and preferably three or more in Standard and Deep modes.

## Results and scoring

Every result requires:

```json
{
  "id": "pathfinder",
  "name": "安静探路者",
  "code": "PATH",
  "priority": 1,
  "hook": "你总是在别人发现问题前找到入口。",
  "description": "你倾向于先观察局面，再给出可靠路径。",
  "strengths": ["识别弱信号", "独立形成判断"],
  "tradeoffs": ["可能太晚公开担忧"],
  "behavior": "局面混乱时，你通常先收集线索并缩小问题。",
  "evidence_template": "你的观察倾向为 {initiative}，更接近先确认再行动。",
  "share_line": "我会先找到路，再宣布出发。",
  "conversation_prompt": "你觉得我平时也是这样吗？",
  "target": { "initiative": 20, "planning": 80 },
  "visual": {
    "symbol": "猫头鹰与便签",
    "accent_color": "#6757D9"
  }
}
```

Include every declared dimension exactly once in each target, with values from 0 to 100. Give results unique integer priorities and meaningfully separated vectors.

For every dimension `d`:

```text
raw_d = sum(selected option contribution for d)
min_d = sum(minimum option contribution for d in every question)
max_d = sum(maximum option contribution for d in every question)
score_d = 100 * (raw_d - min_d) / (max_d - min_d)
```

Reject a dimension when `max_d == min_d`.

For every result `r`:

```text
distance_r = sqrt(sum(weight_d * (score_d - target_r,d)^2) / sum(weight_d))
match_r = floor(max(0, 100 - distance_r) + 0.5)
```

Sort results by distance, dimensions within `close_dimension_threshold`, priority, and result ID. Show the runner-up only when its integer match is within `secondary_result_threshold` of the primary match.

## Answer and result payloads

Accept either a direct answer map or an object containing `answers`:

```json
{
  "answers": {
    "q1": "a",
    "q2": "c"
  }
}
```

The scoring runtime returns:

```json
{
  "quiz_id": "office-animals",
  "scores": { "initiative": 40, "planning": 80 },
  "primary": { "id": "pathfinder", "name": "安静探路者", "match": 91 },
  "secondary": null,
  "ranking": [],
  "evidence": []
}
```

Do not persist answers by default. Presentation order may be shuffled only when stable IDs and mappings remain unchanged.

## Validation rules

Run `scripts/validate_quiz.py` before delivery. Treat errors as blockers and review warnings for duration mismatch, weak repeated measurement, dominant questions, near-duplicate result vectors, and unreachable results.

Run `scripts/score_quiz.py` on at least three answer fixtures: all first options, all last options, and one mixed path. Repeated runs must return byte-equivalent JSON when the same runtime and formatting are used.
