from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ai_adoption_audit_v2.shared.json_utils import print_json
from ai_adoption_audit_v2.skills_contracts import (
    DevexSummaryOutput,
    ErrorOutput,
    MetricsSummaryOutput,
)
from ai_adoption_audit_v2.use_cases.skills.devex import generate_metrics_summary


def _load_metrics_summary(source: Path) -> MetricsSummaryOutput:
    if source.is_dir():
        summary_path = source / "metrics_summary.json"
        if summary_path.is_file():
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
            return MetricsSummaryOutput(**payload)
        metrics_path = source / "metrics.json"
        if metrics_path.is_file():
            return generate_metrics_summary.summarize_metrics(metrics_path)
        raise FileNotFoundError(
            f"Missing metrics.json or metrics_summary.json in {source}"
        )

    payload = json.loads(source.read_text(encoding="utf-8"))
    if "summary" in payload and "score" in payload:
        return MetricsSummaryOutput(**payload)
    if "metrics" in payload:
        return generate_metrics_summary.summarize_metrics(source)
    raise ValueError("Invalid metrics summary payload")


def generate_summary(source: Path) -> DevexSummaryOutput:
    summary_output = _load_metrics_summary(source)
    metrics_count = summary_output.summary.get("metrics_count", 0)
    scored_metrics = summary_output.summary.get("scored_metrics", 0)
    metadata = summary_output.summary.get("metadata", {})
    highlights = [
        f"Metrics analyzed: {metrics_count}",
        f"Metrics scored: {scored_metrics}",
    ]
    if metadata.get("proxy_used"):
        highlights.append("PR cycle time derived from commit-interval proxy.")
    return DevexSummaryOutput(
        overall_score=summary_output.score,
        highlights=highlights,
        metrics_summary=summary_output.summary,
        metrics=summary_output.summary.get("metrics"),
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("metrics_source")
    parser.add_argument("output_path", nargs="?")
    parser.add_argument("--period-days", type=int)
    parser.add_argument("--repository")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
    except SystemExit:
        print_json(
            ErrorOutput(
                error=(
                    "Usage: generate_devex_summary.py <metrics_source> [output_path] "
                    "[--period-days <days>] [--repository <name>]"
                ),
                code=2,
            )
        )
        return 2

    metrics_source = Path(args.metrics_source)
    if not metrics_source.exists():
        print_json(
            ErrorOutput(error=f"Metrics source not found: {metrics_source}", code=2)
        )
        return 2

    try:
        result = generate_summary(metrics_source)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print_json(ErrorOutput(error=str(exc), code=2))
        return 2

    if args.repository:
        result.highlights.append(f"Repository: {args.repository}")
    if args.period_days:
        result.highlights.append(f"Period: {args.period_days} days")

    if args.output_path:
        output_path = Path(args.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(result.model_dump(), indent=2), encoding="utf-8"
        )

    print_json(result)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
