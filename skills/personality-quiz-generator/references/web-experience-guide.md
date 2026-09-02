# Interactive quiz webpage guide

Build a runnable mobile-first artifact from a validated quiz core. Use the bundled `assets/web-template/` for a portable zero-dependency page unless the user requests another framework or platform.

## Build flow

1. Copy the template into the requested output directory.
2. Replace `quiz.json` with the generated schema `1.1` core.
3. Replace `experience.json` with the selected UI and interaction configuration.
4. Preserve `question_id` and `option_id` through all DOM events.
5. Preserve the deterministic algorithm in `scoring.js` or prove parity with it.
6. Serve the directory over HTTP because the page loads JSON with `fetch`.
7. Complete multiple answer paths and inspect the result, restart, back, and share flows.

## Required states

- Intro: title, concrete promise, expected duration, start action, entertainment disclaimer.
- Loading: visible status while configuration loads.
- Question: progress, one situation, balanced choices, back navigation when allowed.
- Calculating: optional brief transition without fake scientific claims.
- Result: name, hook, explanation, evidence, strengths, trade-offs, dimensions when enabled, share, restart.
- Error: readable recovery instructions when files or scoring fail.

## Interaction requirements

- Keep tap targets at least 44 by 44 CSS pixels.
- Support keyboard focus, Enter/Space selection, and visible focus states.
- Respect `prefers-reduced-motion`.
- Avoid requiring hover, drag, sound, or color alone.
- Keep progress accurate after back navigation.
- Clear answers, result state, and temporary resources on restart.

## Data and sharing

- Keep answers in memory only by default.
- Do not add analytics, cookies, storage, or remote submission unless requested.
- When collection is requested, disclose what is collected and why before the test starts.
- Prefer the Web Share API with clipboard fallback.
- Share the result identity and line, not raw answer history.
- Add Open Graph assets only when the page will be hosted and the user requests social previews.

## Visual direction

Infer one coherent visual metaphor from the theme. Use a single result-card system with shared composition, typography, and information hierarchy. Vary symbols and accent colors by result without making any result look rare or superior.

## QA before handoff

- Validate `quiz.json` and `experience.json`.
- Score identical fixtures with every runtime included in the artifact.
- Test first-option, last-option, and mixed paths.
- Test narrow mobile and desktop widths.
- Test keyboard-only completion and reduced motion.
- Confirm hidden score mappings are absent from rendered participant copy.
- Return the project path or preview URL and disclose any untested hosting behavior.
