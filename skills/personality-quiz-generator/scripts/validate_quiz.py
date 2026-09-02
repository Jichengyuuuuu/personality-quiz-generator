#!/usr/bin/env python3
"""Validate a personality-quiz JSON specification using only the standard library."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


EXPECTED_TIE_BREAK = [
    "distance",
    "close_dimensions",
    "priority",
    "result_id",
]
ALLOWED_PRESETS = {"quick", "standard", "deep", "custom"}
SUPPORTED_SCHEMA_VERSIONS = {"1.0", "1.1"}
ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")
COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")
DURATION_LIMITS = {
    "quick": {"questions": (6, 8), "results": (4, 6)},
    "standard": {"questions": (10, 14), "results": (6, 10)},
    "deep": {"questions": (18, 24), "results": (8, 16)},
}
BEAM_WIDTH = 1500
FINALISTS_PER_RESULT = 100


class ValidationReport:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def require_text(data: dict[str, Any], key: str, where: str, report: ValidationReport) -> None:
    if not isinstance(data.get(key), str) or not data[key].strip():
        report.error(f"{where}.{key} must be a nonempty string")


def duplicate_values(values: list[Any]) -> set[Any]:
    seen: set[Any] = set()
    duplicates: set[Any] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def validate_structure(data: Any, report: ValidationReport) -> tuple[list[str], dict[str, float]]:
    if not isinstance(data, dict):
        report.error("top level must be a JSON object")
        return [], {}

    schema_version = data.get("schema_version")
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        report.error(f"schema_version must be one of {sorted(SUPPORTED_SCHEMA_VERSIONS)}")
    require_text(data, "title", "quiz", report)
    require_text(data, "promise", "quiz", report)
    if schema_version == "1.1":
        for field in ("id", "locale", "audience"):
            require_text(data, field, "quiz", report)
        if isinstance(data.get("id"), str) and not ID_PATTERN.fullmatch(data["id"]):
            report.error("quiz.id must use lowercase ASCII kebab-case")

    duration = data.get("duration")
    if not isinstance(duration, dict):
        report.error("duration must be an object")
    else:
        if duration.get("preset") not in ALLOWED_PRESETS:
            report.error("duration.preset must be quick, standard, deep, or custom")
        if not is_number(duration.get("minutes")) or duration["minutes"] <= 0:
            report.error("duration.minutes must be a positive number")

    dimensions = data.get("dimensions")
    if not isinstance(dimensions, list):
        report.error("dimensions must be an array")
        return [], {}
    if not 2 <= len(dimensions) <= 8:
        report.error("dimensions must contain 2–8 entries")
    elif not 4 <= len(dimensions) <= 6:
        report.warn("4–6 dimensions are recommended for most personality quizzes")

    dimension_ids: list[str] = []
    weights: dict[str, float] = {}
    for index, dimension in enumerate(dimensions):
        where = f"dimensions[{index}]"
        if not isinstance(dimension, dict):
            report.error(f"{where} must be an object")
            continue
        for field in ("id", "name", "low_label", "high_label"):
            require_text(dimension, field, where, report)
        dim_id = dimension.get("id")
        if isinstance(dim_id, str) and dim_id:
            dimension_ids.append(dim_id)
        weight = dimension.get("weight", 1)
        if not is_number(weight) or weight <= 0:
            report.error(f"{where}.weight must be a positive number")
        elif isinstance(dim_id, str) and dim_id:
            weights[dim_id] = float(weight)

    for duplicate in sorted(duplicate_values(dimension_ids)):
        report.error(f"duplicate dimension id: {duplicate}")

    preset = duration.get("preset") if isinstance(duration, dict) else None
    validate_questions(data.get("questions"), dimension_ids, preset, report)
    validate_results(data.get("results"), dimension_ids, weights, schema_version, report)
    validate_duration_fit(preset, data.get("questions"), data.get("results"), report)

    scoring = data.get("scoring")
    if schema_version == "1.1":
        if not isinstance(scoring, dict):
            report.error("scoring must be an object for schema 1.1")
        else:
            if scoring.get("method") != "weighted_rms":
                report.error('scoring.method must be "weighted_rms"')
            for field in ("close_dimension_threshold", "secondary_result_threshold"):
                value = scoring.get(field)
                if not is_number(value) or not 0 <= value <= 100:
                    report.error(f"scoring.{field} must be between 0 and 100")

    if data.get("tie_break") != EXPECTED_TIE_BREAK:
        report.error(f"tie_break must equal {EXPECTED_TIE_BREAK}")

    return dimension_ids, weights


def validate_questions(questions: Any, dimension_ids: list[str], preset: Any, report: ValidationReport) -> None:
    if not isinstance(questions, list) or not questions:
        report.error("questions must be a nonempty array")
        return

    question_ids: list[str] = []
    coverage = {dim_id: 0 for dim_id in dimension_ids}
    ranges = {dim_id: [] for dim_id in dimension_ids}
    known_dimensions = set(dimension_ids)

    for q_index, question in enumerate(questions):
        where = f"questions[{q_index}]"
        if not isinstance(question, dict):
            report.error(f"{where} must be an object")
            continue
        require_text(question, "id", where, report)
        require_text(question, "text", where, report)
        question_id = question.get("id")
        if isinstance(question_id, str) and question_id:
            question_ids.append(question_id)
            if not ID_PATTERN.fullmatch(question_id):
                report.error(f"{where}.id must use lowercase ASCII kebab-case")

        options = question.get("options")
        if not isinstance(options, list) or not 2 <= len(options) <= 6:
            report.error(f"{where}.options must contain 2–6 entries")
            continue

        option_ids: list[str] = []
        values_by_dimension = {dim_id: [] for dim_id in dimension_ids}
        for o_index, option in enumerate(options):
            option_where = f"{where}.options[{o_index}]"
            if not isinstance(option, dict):
                report.error(f"{option_where} must be an object")
                continue
            require_text(option, "id", option_where, report)
            require_text(option, "text", option_where, report)
            option_id = option.get("id")
            if isinstance(option_id, str) and option_id:
                option_ids.append(option_id)
                if not ID_PATTERN.fullmatch(option_id):
                    report.error(f"{option_where}.id must use lowercase ASCII kebab-case")
            scores = option.get("scores")
            if not isinstance(scores, dict):
                report.error(f"{option_where}.scores must be an object")
                continue
            for score_dimension, value in scores.items():
                if score_dimension not in known_dimensions:
                    report.error(f"{option_where}.scores uses unknown dimension {score_dimension}")
                if not is_number(value):
                    report.error(f"{option_where}.scores.{score_dimension} must be numeric")
                elif abs(value) > 2:
                    report.warn(f"{option_where}.scores.{score_dimension} exceeds the usual -2 to 2 range: {value}")
            for dim_id in dimension_ids:
                value = scores.get(dim_id, 0)
                values_by_dimension[dim_id].append(float(value) if is_number(value) else 0.0)

        for duplicate in sorted(duplicate_values(option_ids)):
            report.error(f"{where} has duplicate option id: {duplicate}")
        for dim_id, values in values_by_dimension.items():
            question_range = max(values) - min(values) if values else 0
            ranges[dim_id].append(question_range)
            if question_range > 0:
                coverage[dim_id] += 1

    for duplicate in sorted(duplicate_values(question_ids)):
        report.error(f"duplicate question id: {duplicate}")
    for dim_id, count in coverage.items():
        if count == 0:
            report.error(f"dimension {dim_id} never varies across answer options")
        elif count < 2:
            report.warn(f"dimension {dim_id} varies in only {count} question; use repeated measurement")
        elif preset in {"standard", "deep"} and count < 3:
            report.warn(f"dimension {dim_id} varies in only {count} questions; use at least 3 for {preset}")
        total_range = sum(ranges[dim_id])
        if total_range > 0:
            largest_share = max(ranges[dim_id]) / total_range
            if largest_share > 0.4:
                report.warn(f"one question contributes {largest_share:.0%} of dimension {dim_id}'s theoretical range")


def validate_results(
    results: Any,
    dimension_ids: list[str],
    weights: dict[str, float],
    schema_version: Any,
    report: ValidationReport,
) -> None:
    if not isinstance(results, list) or len(results) < 2:
        report.error("results must contain at least two entries")
        return
    if len(results) > 24:
        report.warn("more than 24 results may be difficult to distinguish and validate")

    result_ids: list[str] = []
    priorities: list[int] = []
    vectors: dict[tuple[float, ...], str] = {}
    result_vectors: list[tuple[str, tuple[float, ...]]] = []
    dimension_set = set(dimension_ids)

    for index, result in enumerate(results):
        where = f"results[{index}]"
        if not isinstance(result, dict):
            report.error(f"{where} must be an object")
            continue
        required_text = ["id", "name", "hook"]
        if schema_version == "1.1":
            required_text.extend(
                ["code", "description", "behavior", "evidence_template", "share_line", "conversation_prompt"]
            )
        for field in required_text:
            require_text(result, field, where, report)
        result_id = result.get("id")
        if isinstance(result_id, str) and result_id:
            result_ids.append(result_id)
            if not ID_PATTERN.fullmatch(result_id):
                report.error(f"{where}.id must use lowercase ASCII kebab-case")

        if schema_version == "1.1":
            for field in ("strengths", "tradeoffs"):
                value = result.get(field)
                if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
                    report.error(f"{where}.{field} must be a nonempty array of strings")
            visual = result.get("visual")
            if not isinstance(visual, dict):
                report.error(f"{where}.visual must be an object")
            else:
                require_text(visual, "symbol", f"{where}.visual", report)
                color = visual.get("accent_color")
                if not isinstance(color, str) or not COLOR_PATTERN.fullmatch(color):
                    report.error(f"{where}.visual.accent_color must be a six-digit hex color")

        priority = result.get("priority")
        if not isinstance(priority, int) or isinstance(priority, bool):
            report.error(f"{where}.priority must be an integer")
        else:
            priorities.append(priority)

        target = result.get("target")
        if not isinstance(target, dict):
            report.error(f"{where}.target must be an object")
            continue
        missing = dimension_set - set(target)
        extra = set(target) - dimension_set
        if missing:
            report.error(f"{where}.target is missing dimensions: {sorted(missing)}")
        if extra:
            report.error(f"{where}.target has unknown dimensions: {sorted(extra)}")
        vector: list[float] = []
        valid_vector = True
        for dim_id in dimension_ids:
            value = target.get(dim_id)
            if not is_number(value) or not 0 <= value <= 100:
                report.error(f"{where}.target.{dim_id} must be between 0 and 100")
                valid_vector = False
            else:
                vector.append(float(value))
        if valid_vector:
            vector_key = tuple(vector)
            if vector_key in vectors:
                report.warn(f"results {vectors[vector_key]} and {result_id} have identical target vectors")
            elif isinstance(result_id, str):
                vectors[vector_key] = result_id
                result_vectors.append((result_id, vector_key))

    for duplicate in sorted(duplicate_values(result_ids)):
        report.error(f"duplicate result id: {duplicate}")
    for duplicate in sorted(duplicate_values(priorities)):
        report.error(f"duplicate result priority: {duplicate}")

    weight_values = [weights.get(dim_id, 1.0) for dim_id in dimension_ids]
    weight_sum = sum(weight_values)
    if weight_sum <= 0:
        return
    for index, (left_id, left) in enumerate(result_vectors):
        for right_id, right in result_vectors[index + 1 :]:
            distance = math.sqrt(
                sum(weight * (left_value - right_value) ** 2 for weight, left_value, right_value in zip(weight_values, left, right))
                / weight_sum
            )
            if distance < 15:
                report.warn(f"results {left_id} and {right_id} have close target vectors (distance {distance:.1f})")


def validate_duration_fit(preset: Any, questions: Any, results: Any, report: ValidationReport) -> None:
    if preset not in DURATION_LIMITS:
        return
    limits = DURATION_LIMITS[preset]
    if isinstance(questions, list):
        low, high = limits["questions"]
        if not low <= len(questions) <= high:
            report.warn(f"{preset} duration recommends {low}–{high} questions; found {len(questions)}")
    if isinstance(results, list):
        low, high = limits["results"]
        if not low <= len(results) <= high:
            report.warn(f"{preset} duration recommends {low}–{high} results; found {len(results)}")


def extract_model(data: dict[str, Any], dimension_ids: list[str]) -> tuple[list[list[tuple[float, ...]]], list[dict[str, Any]]]:
    questions: list[list[tuple[float, ...]]] = []
    for question in data["questions"]:
        options: list[tuple[float, ...]] = []
        for option in question["options"]:
            options.append(tuple(float(option["scores"].get(dim_id, 0)) for dim_id in dimension_ids))
        questions.append(options)
    return questions, data["results"]


def theoretical_ranges(questions: list[list[tuple[float, ...]]]) -> tuple[tuple[float, ...], tuple[float, ...]]:
    dimension_count = len(questions[0][0])
    minimums = [0.0] * dimension_count
    maximums = [0.0] * dimension_count
    for options in questions:
        for index in range(dimension_count):
            values = [option[index] for option in options]
            minimums[index] += min(values)
            maximums[index] += max(values)
    return tuple(minimums), tuple(maximums)


def normalize(raw: tuple[float, ...], minimums: tuple[float, ...], maximums: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(
        100.0 * (value - low) / (high - low)
        for value, low, high in zip(raw, minimums, maximums)
    )


def result_key(scores: tuple[float, ...], result: dict[str, Any], dimension_ids: list[str], weights: dict[str, float]) -> tuple[Any, ...]:
    target = tuple(float(result["target"][dim_id]) for dim_id in dimension_ids)
    weight_values = tuple(weights[dim_id] for dim_id in dimension_ids)
    weighted_sum = sum(weight * (score - expected) ** 2 for score, expected, weight in zip(scores, target, weight_values))
    distance = math.sqrt(weighted_sum / sum(weight_values))
    close_dimensions = sum(abs(score - expected) <= 15 for score, expected in zip(scores, target))
    return (round(distance, 12), -close_dimensions, result["priority"], result["id"])


def classify(scores: tuple[float, ...], results: list[dict[str, Any]], dimension_ids: list[str], weights: dict[str, float]) -> str:
    return min(results, key=lambda result: result_key(scores, result, dimension_ids, weights))["id"]


def lower_bound_to_target(
    raw: tuple[float, ...],
    remaining_min: tuple[float, ...],
    remaining_max: tuple[float, ...],
    ideal_raw: tuple[float, ...],
) -> float:
    total = 0.0
    for value, low_delta, high_delta, ideal in zip(raw, remaining_min, remaining_max, ideal_raw):
        low = value + low_delta
        high = value + high_delta
        if ideal < low:
            total += (low - ideal) ** 2
        elif ideal > high:
            total += (ideal - high) ** 2
    return total


def candidate_states_for_result(
    questions: list[list[tuple[float, ...]]],
    target: tuple[float, ...],
    minimums: tuple[float, ...],
    maximums: tuple[float, ...],
) -> list[tuple[float, ...]]:
    dimension_count = len(target)
    ideal_raw = tuple(low + score * (high - low) / 100.0 for score, low, high in zip(target, minimums, maximums))

    suffix_min = [[0.0] * dimension_count for _ in range(len(questions) + 1)]
    suffix_max = [[0.0] * dimension_count for _ in range(len(questions) + 1)]
    for q_index in range(len(questions) - 1, -1, -1):
        for d_index in range(dimension_count):
            values = [option[d_index] for option in questions[q_index]]
            suffix_min[q_index][d_index] = suffix_min[q_index + 1][d_index] + min(values)
            suffix_max[q_index][d_index] = suffix_max[q_index + 1][d_index] + max(values)

    states: set[tuple[float, ...]] = {tuple(0.0 for _ in range(dimension_count))}
    for q_index, options in enumerate(questions):
        expanded = {
            tuple(current + delta for current, delta in zip(state, option))
            for state in states
            for option in options
        }
        if len(expanded) > BEAM_WIDTH:
            remaining_min = tuple(suffix_min[q_index + 1])
            remaining_max = tuple(suffix_max[q_index + 1])
            ordered = sorted(
                expanded,
                key=lambda state: (lower_bound_to_target(state, remaining_min, remaining_max, ideal_raw), state),
            )
            states = set(ordered[:BEAM_WIDTH])
        else:
            states = expanded

    return sorted(
        states,
        key=lambda state: (
            sum((value - ideal) ** 2 for value, ideal in zip(state, ideal_raw)),
            state,
        ),
    )[:FINALISTS_PER_RESULT]


def validate_reachability(data: dict[str, Any], dimension_ids: list[str], weights: dict[str, float], report: ValidationReport) -> None:
    questions, results = extract_model(data, dimension_ids)
    minimums, maximums = theoretical_ranges(questions)
    for index, (low, high) in enumerate(zip(minimums, maximums)):
        if high == low:
            report.error(f"dimension {dimension_ids[index]} has a zero theoretical range")
    if report.errors:
        return

    for result in results:
        target = tuple(float(result["target"][dim_id]) for dim_id in dimension_ids)
        candidates = candidate_states_for_result(questions, target, minimums, maximums)
        reachable = any(
            classify(normalize(candidate, minimums, maximums), results, dimension_ids, weights) == result["id"]
            for candidate in candidates
        )
        if not reachable:
            report.warn(
                f"result {result['id']} was not reached by deterministic beam search; review its target vector and neighboring results"
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a personality quiz JSON specification")
    parser.add_argument("spec", type=Path, help="Path to the quiz JSON file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = ValidationReport()
    try:
        data = json.loads(args.spec.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: file not found: {args.spec}", file=sys.stderr)
        return 2
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: unable to read valid JSON: {exc}", file=sys.stderr)
        return 2

    dimension_ids, weights = validate_structure(data, report)
    if not report.errors and dimension_ids:
        validate_reachability(data, dimension_ids, weights, report)

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
