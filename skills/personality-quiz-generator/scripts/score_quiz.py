#!/usr/bin/env python3
"""Score a personality quiz deterministically from a quiz spec and answer map."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"file not found: {path}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"unable to read valid JSON from {path}: {exc}") from exc


def half_up(value: float) -> int:
    return math.floor(value + 0.5)


def extract_answers(data: Any) -> dict[str, str]:
    if not isinstance(data, dict):
        raise ValueError("answers must be a JSON object")
    answers = data.get("answers", data)
    if not isinstance(answers, dict):
        raise ValueError("answers.answers must be an object")
    if not all(isinstance(question_id, str) and isinstance(option_id, str) for question_id, option_id in answers.items()):
        raise ValueError("answer keys and values must be strings")
    return answers


def theoretical_ranges(spec: dict[str, Any], dimension_ids: list[str]) -> tuple[dict[str, float], dict[str, float]]:
    minimums = {dimension_id: 0.0 for dimension_id in dimension_ids}
    maximums = {dimension_id: 0.0 for dimension_id in dimension_ids}
    for question in spec["questions"]:
        for dimension_id in dimension_ids:
            values = [float(option.get("scores", {}).get(dimension_id, 0)) for option in question["options"]]
            minimums[dimension_id] += min(values)
            maximums[dimension_id] += max(values)
    return minimums, maximums


def score(spec: dict[str, Any], answers: dict[str, str]) -> dict[str, Any]:
    dimensions = spec.get("dimensions")
    questions = spec.get("questions")
    results = spec.get("results")
    if not isinstance(dimensions, list) or not dimensions:
        raise ValueError("quiz spec has no dimensions")
    if not isinstance(questions, list) or not questions:
        raise ValueError("quiz spec has no questions")
    if not isinstance(results, list) or not results:
        raise ValueError("quiz spec has no results")

    dimension_ids = [dimension["id"] for dimension in dimensions]
    weights = {dimension["id"]: float(dimension.get("weight", 1)) for dimension in dimensions}
    question_ids = [question["id"] for question in questions]
    missing = [question_id for question_id in question_ids if question_id not in answers]
    extras = sorted(set(answers) - set(question_ids))
    if missing:
        raise ValueError(f"missing answers for questions: {missing}")
    if extras:
        raise ValueError(f"answers contain unknown questions: {extras}")

    raw = {dimension_id: 0.0 for dimension_id in dimension_ids}
    for question in questions:
        selected_id = answers[question["id"]]
        selected = next((option for option in question["options"] if option["id"] == selected_id), None)
        if selected is None:
            raise ValueError(f"question {question['id']} has no option {selected_id}")
        for dimension_id, contribution in selected.get("scores", {}).items():
            if dimension_id in raw:
                raw[dimension_id] += float(contribution)

    minimums, maximums = theoretical_ranges(spec, dimension_ids)
    normalized: dict[str, float] = {}
    for dimension_id in dimension_ids:
        low = minimums[dimension_id]
        high = maximums[dimension_id]
        if high == low:
            raise ValueError(f"dimension {dimension_id} has a zero theoretical range")
        normalized[dimension_id] = 100.0 * (raw[dimension_id] - low) / (high - low)

    scoring = spec.get("scoring", {})
    close_threshold = float(scoring.get("close_dimension_threshold", 15))
    secondary_threshold = int(scoring.get("secondary_result_threshold", 5))
    weight_sum = sum(weights.values())

    ranking: list[dict[str, Any]] = []
    for result in results:
        weighted_sum = sum(
            weights[dimension_id] * (normalized[dimension_id] - float(result["target"][dimension_id])) ** 2
            for dimension_id in dimension_ids
        )
        distance = math.sqrt(weighted_sum / weight_sum)
        close_dimensions = sum(
            abs(normalized[dimension_id] - float(result["target"][dimension_id])) <= close_threshold
            for dimension_id in dimension_ids
        )
        ranking.append(
            {
                "id": result["id"],
                "name": result["name"],
                "match": half_up(max(0.0, 100.0 - distance)),
                "distance": distance,
                "close_dimensions": close_dimensions,
                "priority": result["priority"],
            }
        )

    ranking.sort(key=lambda item: (round(item["distance"], 12), -item["close_dimensions"], item["priority"], item["id"]))
    public_ranking = [
        {"id": item["id"], "name": item["name"], "match": item["match"]}
        for item in ranking
    ]
    primary = public_ranking[0]
    secondary = None
    if len(public_ranking) > 1 and primary["match"] - public_ranking[1]["match"] <= secondary_threshold:
        secondary = public_ranking[1]

    rounded_scores = {dimension_id: half_up(normalized[dimension_id] * 100) / 100 for dimension_id in dimension_ids}
    evidence = []
    for dimension in dimensions:
        dimension_id = dimension["id"]
        dimension_score = rounded_scores[dimension_id]
        evidence.append(
            {
                "dimension_id": dimension_id,
                "name": dimension["name"],
                "score": dimension_score,
                "lean": dimension["high_label"] if dimension_score >= 50 else dimension["low_label"],
            }
        )

    return {
        "quiz_id": spec.get("id", "quiz"),
        "scores": rounded_scores,
        "primary": primary,
        "secondary": secondary,
        "ranking": public_ranking,
        "evidence": evidence,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score a personality quiz from a quiz spec and answers JSON")
    parser.add_argument("spec", type=Path, help="Path to quiz.json")
    parser.add_argument("answers", type=Path, help="Path to answers.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        spec = load_json(args.spec)
        answer_map = extract_answers(load_json(args.answers))
        result = score(spec, answer_map)
    except (KeyError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
