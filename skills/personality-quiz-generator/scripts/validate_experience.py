#!/usr/bin/env python3
"""Validate an interactive quiz experience config and its quiz reference."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")
COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")
ALLOWED_DELIVERIES = {"conversation", "game", "web"}
ALLOWED_PERSISTENCE = {"none", "session", "server"}
REQUIRED_FLOW = {"intro", "questions", "result"}
ALLOWED_ACTIONS = {"share", "restart"}
ALLOWED_SHARE_FIELDS = {"result_name", "share_line", "quiz_title", "result_hook"}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"file not found: {path}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"unable to read valid JSON from {path}: {exc}") from exc


def require_text(data: dict[str, Any], key: str, where: str, report: Report) -> None:
    if not isinstance(data.get(key), str) or not data[key].strip():
        report.error(f"{where}.{key} must be a nonempty string")


def validate(experience: Any, quiz: Any, report: Report) -> None:
    if not isinstance(experience, dict):
        report.error("experience must be a JSON object")
        return
    if not isinstance(quiz, dict):
        report.error("quiz must be a JSON object")
        return

    if experience.get("experience_schema_version") != "1.0":
        report.error('experience_schema_version must be "1.0"')
    for field in ("id", "quiz_ref", "delivery", "mechanic"):
        require_text(experience, field, "experience", report)
    if isinstance(experience.get("id"), str) and not ID_PATTERN.fullmatch(experience["id"]):
        report.error("experience.id must use lowercase ASCII kebab-case")
    if experience.get("delivery") not in ALLOWED_DELIVERIES:
        report.error(f"experience.delivery must be one of {sorted(ALLOWED_DELIVERIES)}")
    if isinstance(experience.get("mechanic"), str) and not ID_PATTERN.fullmatch(experience["mechanic"]):
        report.error("experience.mechanic must use lowercase ASCII kebab-case")

    flow = experience.get("flow")
    if not isinstance(flow, list) or not all(isinstance(item, str) for item in flow):
        report.error("experience.flow must be an array of strings")
        flow = []
    else:
        missing_flow = REQUIRED_FLOW - set(flow)
        if missing_flow:
            report.error(f"experience.flow is missing states: {sorted(missing_flow)}")
        if flow and flow[0] != "intro":
            report.warn("experience.flow should begin with intro")
        if flow and flow[-1] != "result":
            report.warn("experience.flow should end with result")
        if len(flow) != len(set(flow)):
            report.error("experience.flow must not contain duplicate states")

    screens = experience.get("screens")
    if not isinstance(screens, dict):
        report.error("experience.screens must be an object")
        screens = {}
    for state in flow:
        if state not in screens:
            report.error(f"experience.screens is missing flow state {state}")

    intro = screens.get("intro", {})
    if isinstance(intro, dict):
        require_text(intro, "start_label", "experience.screens.intro", report)
        require_text(intro, "disclaimer", "experience.screens.intro", report)
    questions = screens.get("questions", {})
    if isinstance(questions, dict):
        for field in ("show_progress", "allow_back"):
            if not isinstance(questions.get(field), bool):
                report.error(f"experience.screens.questions.{field} must be boolean")
    result_screen = screens.get("result", {})
    if isinstance(result_screen, dict):
        actions = result_screen.get("actions")
        if not isinstance(actions, list) or not all(action in ALLOWED_ACTIONS for action in actions):
            report.error(f"experience.screens.result.actions must use {sorted(ALLOWED_ACTIONS)}")
        elif "restart" not in actions:
            report.warn("result actions should include restart")

    theme = experience.get("theme")
    if not isinstance(theme, dict):
        report.error("experience.theme must be an object")
    else:
        for field in ("tone", "visual_direction"):
            require_text(theme, field, "experience.theme", report)
        for field in ("background_color", "text_color", "accent_color"):
            value = theme.get(field)
            if not isinstance(value, str) or not COLOR_PATTERN.fullmatch(value):
                report.error(f"experience.theme.{field} must be a six-digit hex color")

    interaction = experience.get("interaction")
    if not isinstance(interaction, dict):
        report.error("experience.interaction must be an object")
    else:
        require_text(interaction, "transition", "experience.interaction", report)
        for field in ("shuffle_questions", "shuffle_options", "auto_advance"):
            if not isinstance(interaction.get(field), bool):
                report.error(f"experience.interaction.{field} must be boolean")

    data = experience.get("data")
    if not isinstance(data, dict):
        report.error("experience.data must be an object")
    else:
        if data.get("answer_persistence") not in ALLOWED_PERSISTENCE:
            report.error(f"experience.data.answer_persistence must be one of {sorted(ALLOWED_PERSISTENCE)}")
        if not isinstance(data.get("analytics"), bool):
            report.error("experience.data.analytics must be boolean")
        if (data.get("answer_persistence") == "server" or data.get("analytics") is True) and not isinstance(data.get("disclosure"), str):
            report.error("experience.data.disclosure is required for server persistence or analytics")

    accessibility = experience.get("accessibility")
    if not isinstance(accessibility, dict):
        report.error("experience.accessibility must be an object")
    elif experience.get("delivery") == "web":
        for field in ("keyboard_navigation", "reduced_motion"):
            if accessibility.get(field) is not True:
                report.error(f"web experiences must set accessibility.{field} to true")
        if accessibility.get("minimum_contrast") != "WCAG-AA":
            report.error('web experiences must set accessibility.minimum_contrast to "WCAG-AA"')

    share = experience.get("share", {})
    if isinstance(share, dict):
        for field in ("title_template", "text_template"):
            value = share.get(field)
            if not isinstance(value, str) or not value.strip():
                report.error(f"experience.share.{field} must be a nonempty string")
                continue
            placeholders = set(re.findall(r"\{([a-z_]+)\}", value))
            unknown = placeholders - ALLOWED_SHARE_FIELDS
            if unknown:
                report.error(f"experience.share.{field} has unknown placeholders: {sorted(unknown)}")

    if experience.get("delivery") == "game" and not isinstance(experience.get("game_rules"), dict):
        report.error("game delivery requires experience.game_rules")

    if not isinstance(quiz.get("id"), str) or not quiz["id"]:
        report.error("quiz.id must be present for an interactive experience")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate experience.json against quiz.json")
    parser.add_argument("experience", type=Path, help="Path to experience.json")
    parser.add_argument("quiz", type=Path, help="Path to quiz.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = Report()
    try:
        validate(load_json(args.experience), load_json(args.quiz), report)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for warning in report.warnings:
        print(f"WARNING: {warning}")
    for error in report.errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if report.errors:
        print(f"FAIL: {len(report.errors)} error(s), {len(report.warnings)} warning(s)", file=sys.stderr)
        return 1
    print(f"PASS: 0 errors, {len(report.warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
