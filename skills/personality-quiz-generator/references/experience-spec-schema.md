# Interactive experience specification

Use `experience.json` to describe how a validated `quiz.json` becomes a conversation, result-based game, or webpage. Keep scores and result targets in the quiz core.

## Required contract

```json
{
  "experience_schema_version": "1.0",
  "id": "office-animals-web",
  "quiz_ref": "./quiz.json",
  "delivery": "web",
  "mechanic": "linear-cards",
  "flow": ["intro", "questions", "calculating", "result"],
  "screens": {
    "intro": {
      "eyebrow": "4 分钟趣味测试",
      "start_label": "进入办公室动物园",
      "disclaimer": "结果仅供娱乐与自我观察。"
    },
    "questions": {
      "show_progress": true,
      "allow_back": true
    },
    "calculating": {
      "duration_ms": 900,
      "messages": ["正在观察你的工位生态……"]
    },
    "result": {
      "show_secondary": true,
      "show_dimensions": true,
      "actions": ["share", "restart"]
    }
  },
  "theme": {
    "tone": "playful",
    "visual_direction": "editorial office badge",
    "background_color": "#F4F0E8",
    "text_color": "#1D1D1F",
    "accent_color": "#FF6B35"
  },
  "interaction": {
    "transition": "slide",
    "shuffle_questions": false,
    "shuffle_options": false,
    "auto_advance": true
  },
  "share": {
    "title_template": "我的结果是：{result_name}",
    "text_template": "{share_line}",
    "prompt": "你觉得我像吗？"
  },
  "data": {
    "answer_persistence": "none",
    "analytics": false
  },
  "accessibility": {
    "keyboard_navigation": true,
    "reduced_motion": true,
    "minimum_contrast": "WCAG-AA"
  }
}
```

## Field rules

- `delivery`: Use `conversation`, `game`, or `web`.
- `mechanic`: Use a stable kebab-case value documented in the gameplay guide.
- `flow`: Include `intro`, `questions`, and `result`; add `calculating` only when the reveal benefits from a brief transition.
- `quiz_ref`: Resolve relative to `experience.json`.
- `screens`: Keep participant-facing UI copy and behavior here. Do not duplicate questions, scores, or results.
- `interaction`: Shuffling may change presentation order only. It must preserve question and option IDs.
- `share`: Use placeholders from result fields. Never invent rarity or compatibility claims.
- `data.answer_persistence`: Default to `none`; use `session` or `server` only when requested and disclosed.
- `data.analytics`: Default to `false`. If enabled, describe collected events and avoid answer text or sensitive data unless explicitly required.
- `accessibility`: Keep keyboard navigation and reduced-motion support enabled for web artifacts.

## Optional game fields

For `delivery: game`, add:

```json
{
  "game_rules": {
    "framing": "Survive one chaotic office day",
    "resource_name": "energy",
    "starting_resource": 5,
    "branching": "presentation-only",
    "timer_seconds": null
  }
}
```

Game resources, branches, and timers may alter copy, scene order, or feedback. They must not override result scoring unless their actions are represented as stable scored option IDs in `quiz.json`.

## Validation

Run:

```bash
python3 scripts/validate_experience.py experience.json quiz.json
```

Fix missing states, invalid references, unsupported persistence, and accessibility errors before delivery.
