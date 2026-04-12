#!/usr/bin/env python3
"""
parse_tier1_metrics.py
Aggregates raw JSONL output from collect_tier1_metrics.sh into summary statistics.

Usage: python parse_tier1_metrics.py <tier1_dir> <output_dir>

Input files expected (in tier1_dir):
  - prs.jsonl - PR metrics from collect_tier1_metrics.sh
  - stability.json - Stability metrics from collect_tier1_metrics.sh

Output (in output_dir):
  - {repo}_tier1_summary.json - Aggregated statistics
  - {repo}_tier1_summary.csv - CSV format for spreadsheet analysis

Directory structure:
  output/{repo_name}/tier1/       <- tier1_dir input
  output/{repo_name}/             <- output_dir for summary files
"""

import json
import csv
import sys
import statistics
from pathlib import Path
from datetime import datetime
from typing import Any


def load_jsonl(filepath: Path) -> list[dict]:
    """Load a JSONL file into a list of dicts."""
    records = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def calculate_percentile(values: list[float], percentile: int) -> float | None:
    """Calculate the nth percentile of a list of values."""
    if not values:
        return None
    sorted_values = sorted(values)
    index = (len(sorted_values) - 1) * percentile / 100
    lower = int(index)
    upper = lower + 1
    if upper >= len(sorted_values):
        return sorted_values[-1]
    weight = index - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def aggregate_pr_metrics(prs: list[dict]) -> dict:
    """Aggregate PR-level metrics into summary statistics."""
    merged_prs = [p for p in prs if p.get("status") == "merged"]
    rejected_prs = [p for p in prs if p.get("status") == "rejected"]

    # Separate bot and human PRs
    human_merged = [p for p in merged_prs if not p.get("is_bot", False)]
    bot_merged = [p for p in merged_prs if p.get("is_bot", False)]

    # M1: Cycle time
    cycle_times = [
        p["metrics"]["m1_cycle_time_hours"]
        for p in human_merged
        if p["metrics"].get("m1_cycle_time_hours") not in (None, "null")
    ]

    # M2: PR Size
    additions = [p["metrics"]["m2_additions"] for p in human_merged if "m2_additions" in p["metrics"]]
    deletions = [p["metrics"]["m2_deletions"] for p in human_merged if "m2_deletions" in p["metrics"]]
    changed_files = [p["metrics"]["m2_changed_files"] for p in human_merged if "m2_changed_files" in p["metrics"]]

    # M3: Time to first review
    review_times = []
    prs_without_review = 0
    for p in human_merged:
        val = p["metrics"].get("m3_time_to_first_review_hours")
        if val == "no_review":
            prs_without_review += 1
        elif val not in (None, "null"):
            try:
                review_times.append(float(val))
            except (ValueError, TypeError):
                pass

    # M4: Review comments
    review_comments = [p["metrics"]["m4_review_comments"] for p in human_merged if "m4_review_comments" in p["metrics"]]

    # M5: Commits per PR
    commits = [p["metrics"]["m5_commits"] for p in human_merged if "m5_commits" in p["metrics"]]

    # M10: Review iterations (CHANGES_REQUESTED count per PR)
    review_iterations = [
        p["metrics"]["m10_review_iterations"]
        for p in human_merged
        if "m10_review_iterations" in p["metrics"]
    ]

    # M6: Rejection rate
    total_human_prs = len([p for p in prs if not p.get("is_bot", False)])
    human_rejected = len([p for p in rejected_prs if not p.get("is_bot", False)])
    rejection_rate = human_rejected / total_human_prs if total_human_prs > 0 else 0

    return {
        "total_prs": len(prs),
        "merged_prs": len(merged_prs),
        "rejected_prs": len(rejected_prs),
        "bot_prs": len(bot_merged),
        "human_prs": len(human_merged),
        "m1_cycle_time": {
            "median_hours": round(statistics.median(cycle_times), 2) if cycle_times else None,
            "mean_hours": round(statistics.mean(cycle_times), 2) if cycle_times else None,
            "p90_hours": round(calculate_percentile(cycle_times, 90), 2) if cycle_times else None,
            "min_hours": round(min(cycle_times), 2) if cycle_times else None,
            "max_hours": round(max(cycle_times), 2) if cycle_times else None,
        },
        "m2_pr_size": {
            "median_additions": round(statistics.median(additions), 0) if additions else None,
            "median_deletions": round(statistics.median(deletions), 0) if deletions else None,
            "median_changed_files": round(statistics.median(changed_files), 0) if changed_files else None,
            "p90_additions": round(calculate_percentile(additions, 90), 0) if additions else None,
            "total_additions": sum(additions) if additions else 0,
            "total_deletions": sum(deletions) if deletions else 0,
        },
        "m3_time_to_first_review": {
            "median_hours": round(statistics.median(review_times), 2) if review_times else None,
            "mean_hours": round(statistics.mean(review_times), 2) if review_times else None,
            "p90_hours": round(calculate_percentile(review_times, 90), 2) if review_times else None,
            "prs_without_review": prs_without_review,
            "prs_without_review_pct": round(prs_without_review / len(human_merged) * 100, 1) if human_merged else 0,
        },
        "m4_review_comments": {
            "median": round(statistics.median(review_comments), 1) if review_comments else None,
            "mean": round(statistics.mean(review_comments), 1) if review_comments else None,
            "total": sum(review_comments) if review_comments else 0,
        },
        "m5_commits_per_pr": {
            "median": round(statistics.median(commits), 1) if commits else None,
            "mean": round(statistics.mean(commits), 1) if commits else None,
            "max": max(commits) if commits else None,
        },
        "m6_rejection_rate": {
            "rate": round(rejection_rate, 4),
            "rate_pct": round(rejection_rate * 100, 2),
            "rejected_count": human_rejected,
        },
        "m10_review_iterations": {
            "median": round(statistics.median(review_iterations), 1) if review_iterations else None,
            "mean": round(statistics.mean(review_iterations), 1) if review_iterations else None,
            "max": max(review_iterations) if review_iterations else None,
            "prs_with_iterations": len([r for r in review_iterations if r > 0]),
            "prs_with_iterations_pct": round(
                len([r for r in review_iterations if r > 0]) / len(review_iterations) * 100, 1
            ) if review_iterations else 0,
        },
    }


def load_stability_metrics(filepath: Path) -> dict:
    """Load stability metrics from JSON file."""
    if not filepath.exists():
        return {"skipped": True, "reason": "file_not_found"}

    with open(filepath, "r") as f:
        return json.load(f)


def generate_summary(pr_metrics: dict, stability_metrics: dict, repo: str) -> dict:
    """Generate combined summary report."""
    return {
        "repository": repo,
        "generated_at": datetime.now().isoformat(),
        "pr_metrics": pr_metrics,
        "stability_metrics": stability_metrics,
    }


def write_csv_summary(summary: dict, output_path: Path) -> None:
    """Write summary as flat CSV for spreadsheet analysis."""
    flat_data = {
        "repository": summary["repository"],
        "generated_at": summary["generated_at"],
        # PR counts
        "total_prs": summary["pr_metrics"]["total_prs"],
        "merged_prs": summary["pr_metrics"]["merged_prs"],
        "rejected_prs": summary["pr_metrics"]["rejected_prs"],
        "bot_prs": summary["pr_metrics"]["bot_prs"],
        "human_prs": summary["pr_metrics"]["human_prs"],
        # M1: Cycle time
        "m1_cycle_time_median_hours": summary["pr_metrics"]["m1_cycle_time"]["median_hours"],
        "m1_cycle_time_p90_hours": summary["pr_metrics"]["m1_cycle_time"]["p90_hours"],
        # M2: PR Size
        "m2_median_additions": summary["pr_metrics"]["m2_pr_size"]["median_additions"],
        "m2_median_deletions": summary["pr_metrics"]["m2_pr_size"]["median_deletions"],
        "m2_total_additions": summary["pr_metrics"]["m2_pr_size"]["total_additions"],
        "m2_total_deletions": summary["pr_metrics"]["m2_pr_size"]["total_deletions"],
        # M3: Time to first review
        "m3_time_to_first_review_median_hours": summary["pr_metrics"]["m3_time_to_first_review"]["median_hours"],
        "m3_prs_without_review_pct": summary["pr_metrics"]["m3_time_to_first_review"]["prs_without_review_pct"],
        # M4: Review comments
        "m4_review_comments_median": summary["pr_metrics"]["m4_review_comments"]["median"],
        "m4_review_comments_total": summary["pr_metrics"]["m4_review_comments"]["total"],
        # M5: Commits per PR
        "m5_commits_per_pr_median": summary["pr_metrics"]["m5_commits_per_pr"]["median"],
        # M6: Rejection rate
        "m6_rejection_rate_pct": summary["pr_metrics"]["m6_rejection_rate"]["rate_pct"],
        # M10: Review iterations
        "m10_review_iterations_median": summary["pr_metrics"].get("m10_review_iterations", {}).get("median"),
        "m10_prs_with_iterations_pct": summary["pr_metrics"].get("m10_review_iterations", {}).get("prs_with_iterations_pct"),
    }

    # Add stability metrics if available
    stability = summary.get("stability_metrics", {})
    if not stability.get("skipped"):
        flat_data.update({
            "m7_revert_count": stability.get("m7_revert_count"),
            "m7_revert_rate": stability.get("m7_revert_rate"),
            "m8_hotfix_count": stability.get("m8_hotfix_count"),
            "m8_hotfix_per_week": stability.get("m8_hotfix_per_week"),
            "m9_total_commits": stability.get("m9_total_commits"),
        })

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=flat_data.keys())
        writer.writeheader()
        writer.writerow(flat_data)


def main():
    if len(sys.argv) < 3:
        print("Usage: python parse_tier1_metrics.py <tier1_dir> <output_dir>")
        print("")
        print("Arguments:")
        print("  tier1_dir   Directory containing tier1 data (prs.jsonl, stability.json)")
        print("  output_dir  Directory for output summary files")
        print("")
        print("Example:")
        print("  python parse_tier1_metrics.py output/ai/tier1 output/ai")
        sys.exit(1)

    tier1_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    if not tier1_dir.exists():
        print(f"Error: Tier 1 directory does not exist: {tier1_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Look for prs.jsonl in tier1 directory
    pr_file = tier1_dir / "prs.jsonl"
    if not pr_file.exists():
        print(f"Error: prs.jsonl not found in {tier1_dir}")
        sys.exit(1)

    # Extract repo name from parent directory (e.g., output/ai/tier1 -> ai)
    repo_name = tier1_dir.parent.name

    print(f"Processing: {repo_name}")

    # Load PR data
    prs = load_jsonl(pr_file)
    if not prs:
        print(f"  Warning: No PR data in {pr_file}")
        sys.exit(1)

    repo = prs[0].get("repository", repo_name)

    # Aggregate PR metrics
    pr_metrics = aggregate_pr_metrics(prs)

    # Load stability metrics
    stability_file = tier1_dir / "stability.json"
    stability_metrics = load_stability_metrics(stability_file)

    # Generate summary
    summary = generate_summary(pr_metrics, stability_metrics, repo)

    # Write outputs
    summary_json = output_dir / f"{repo_name}_tier1_summary.json"
    summary_csv = output_dir / f"{repo_name}_tier1_summary.csv"

    with open(summary_json, "w") as f:
        json.dump(summary, f, indent=2)

    write_csv_summary(summary, summary_csv)

    print(f"  Summary: {summary_json}")
    print(f"  CSV: {summary_csv}")

    # Print key metrics
    print(f"  --- Key Metrics ---")
    print(f"  Total PRs: {pr_metrics['total_prs']} (Human: {pr_metrics['human_prs']}, Bot: {pr_metrics['bot_prs']})")
    print(f"  M1 Cycle Time (median): {pr_metrics['m1_cycle_time']['median_hours']} hours")
    print(f"  M3 Time to First Review (median): {pr_metrics['m3_time_to_first_review']['median_hours']} hours")
    print(f"  M6 Rejection Rate: {pr_metrics['m6_rejection_rate']['rate_pct']}%")
    if not stability_metrics.get("skipped"):
        print(f"  M7 Revert Rate: {stability_metrics.get('m7_revert_rate', 'N/A')}")
        print(f"  M8 Hotfix Count: {stability_metrics.get('m8_hotfix_count', 'N/A')}")
    print("")

    print("Done!")


if __name__ == "__main__":
    main()
