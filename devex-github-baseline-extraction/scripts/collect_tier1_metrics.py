from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import median
from typing import Any

# Add ~/.claude/lib to path for local dependencies
sys.path.insert(0, str(Path.home() / ".claude" / "lib"))

from ai_adoption_audit_v2.shared.git_utils import is_git_repo, run_git
from ai_adoption_audit_v2.shared.json_utils import print_json
from ai_adoption_audit_v2.skills_contracts import (
    ErrorOutput,
    Tier1MetricsCollectionOutput,
)


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    return float(median(values))


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return float(sum(values) / len(values))


def _p90(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = int(math.ceil(0.9 * len(ordered)) - 1)
    return float(ordered[max(0, min(index, len(ordered) - 1))])


def _metric_entry(
    metric_id: str,
    name: str,
    value: float | int | None,
    unit: str | None,
    *,
    description: str | None = None,
    reason: str | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "id": metric_id,
        "name": name,
        "value": value,
        "unit": unit,
        "available": value is not None,
    }
    if description:
        entry["description"] = description
    if reason:
        entry["reason"] = reason
    if details:
        entry["details"] = details
    return entry


def _git_lines(repo_path: Path, args: list[str]) -> list[str]:
    code, stdout, _ = run_git(args, repo_path)
    if code != 0:
        return []
    return [line.strip() for line in stdout.splitlines() if line.strip()]


def _gh_enabled() -> bool:
    return os.getenv("AUDIT_DEVEX_ENABLE_GITHUB_API") == "1"


def _run_gh(args: list[str]) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            ["gh", *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return 1, "", "gh not available"
    return completed.returncode, completed.stdout, completed.stderr


def _parse_github_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _parse_github_repo(remote: str) -> str | None:
    remote = remote.strip()
    if not remote:
        return None
    if remote.startswith("git@github.com:"):
        slug = remote.split(":", 1)[1]
    elif "github.com/" in remote:
        slug = remote.split("github.com/", 1)[1]
    else:
        return None
    slug = slug.strip().rstrip("/")
    if slug.endswith(".git"):
        slug = slug[:-4]
    parts = slug.split("/")
    if len(parts) < 2:
        return None
    return f"{parts[0]}/{parts[1]}"


def _resolve_github_repo(repository: str, repo_path: Path | None) -> str | None:
    if repository and not Path(repository).exists() and "/" in repository:
        return repository
    if repo_path and is_git_repo(repo_path):
        code, stdout, _ = run_git(["config", "--get", "remote.origin.url"], repo_path)
        if code == 0:
            slug = _parse_github_repo(stdout.strip())
            if slug:
                return slug
    return None


def _is_bot_author(author: str | None) -> bool:
    if not author:
        return False
    lowered = author.lower()
    return any(
        marker in lowered
        for marker in ("bot", "dependabot", "renovate", "github-actions")
    )


def _get_commit_time(repo_path: Path, commit: str) -> int | None:
    lines = _git_lines(repo_path, ["show", "-s", "--format=%ct", commit])
    if not lines:
        return None
    try:
        return int(lines[0])
    except ValueError:
        return None


def _merge_base(repo_path: Path, parent1: str, parent2: str) -> str | None:
    lines = _git_lines(repo_path, ["merge-base", parent1, parent2])
    return lines[0] if lines else None


def _count_commits(repo_path: Path, range_spec: str) -> int | None:
    lines = _git_lines(repo_path, ["rev-list", "--count", range_spec])
    if not lines:
        return None
    try:
        return int(lines[0])
    except ValueError:
        return None


def _estimate_review_iterations(commits_in_branch: int | None) -> float | None:
    if commits_in_branch is None or commits_in_branch <= 0:
        return None
    if commits_in_branch <= 1:
        return 1.0
    if commits_in_branch <= 3:
        return 1.3
    if commits_in_branch <= 6:
        return 1.7
    if commits_in_branch <= 10:
        return 2.2
    return 2.8


def _collect_git_metrics(
    repo_path: Path, since_date: str, period_days: int
) -> tuple[dict[str, Any], dict[str, Any]]:
    metrics: dict[str, Any] = {
        "pr_cycle_time_hours": None,
        "review_time_hours": None,
        "review_iterations": None,
        "commit_count": 0,
        "m7_revert_rate": None,
        "m8_hotfix_frequency": None,
        "m9_commit_distribution": None,
    }
    metadata = {"source": "git", "proxy_used": False, "since_date": since_date}

    commit_times = [
        int(value)
        for value in _git_lines(
            repo_path, ["log", f"--since={since_date}", "--pretty=%ct"]
        )
        if value.isdigit()
    ]
    metrics["commit_count"] = len(commit_times)

    merge_commits = _git_lines(
        repo_path, ["log", f"--since={since_date}", "--merges", "--pretty=%H"]
    )
    pr_cycle_times: list[float] = []
    review_times: list[float] = []
    review_iterations: list[float] = []

    for merge_commit in merge_commits:
        parents = _git_lines(
            repo_path, ["rev-list", "--parents", "-n", "1", merge_commit]
        )
        if not parents:
            continue
        parts = parents[0].split()
        if len(parts) < 3:
            continue
        parent1, parent2 = parts[1], parts[2]
        merge_time = _get_commit_time(repo_path, merge_commit)
        branch_head_time = _get_commit_time(repo_path, parent2)
        if merge_time and branch_head_time:
            review_times.append((merge_time - branch_head_time) / 3600.0)

        base = _merge_base(repo_path, parent1, parent2)
        base_time = _get_commit_time(repo_path, base) if base else None
        if merge_time and base_time:
            pr_cycle_times.append((merge_time - base_time) / 3600.0)

        if base:
            commits_in_branch = _count_commits(repo_path, f"{base}..{parent2}")
            iteration_estimate = _estimate_review_iterations(commits_in_branch)
            if iteration_estimate is not None:
                review_iterations.append(iteration_estimate)

    if pr_cycle_times:
        metrics["pr_cycle_time_hours"] = _median(pr_cycle_times)
    if review_times:
        metrics["review_time_hours"] = _median(review_times)
    if review_iterations:
        metrics["review_iterations"] = _median(review_iterations)

    if not merge_commits and len(commit_times) > 1:
        commit_times_sorted = sorted(commit_times)
        intervals = [
            (second - first) / 3600.0
            for first, second in zip(commit_times_sorted, commit_times_sorted[1:])
            if second > first
        ]
        proxy_cycle_time = _median(intervals)
        if proxy_cycle_time is not None:
            metrics["pr_cycle_time_hours"] = proxy_cycle_time
            metadata["proxy_used"] = True
            metadata["proxy_note"] = "PR cycle time derived from commit interval proxy."

    total_non_merge_commits = len(
        _git_lines(
            repo_path, ["log", f"--since={since_date}", "--no-merges", "--pretty=%H"]
        )
    )
    revert_patterns = [
        "revert",
        "rollback",
        "roll back",
        "undo",
        "backing out",
    ]
    hotfix_patterns = [
        "hotfix",
        "hot-fix",
        "critical fix",
        "emergency",
        "urgent",
        "prod fix",
        "production fix",
        "[p0]",
        "[p1]",
        "[sev0]",
        "[sev1]",
    ]
    revert_commits: set[str] = set()
    for pattern in revert_patterns:
        revert_commits.update(
            _git_lines(
                repo_path,
                [
                    "log",
                    f"--since={since_date}",
                    "--no-merges",
                    f"--grep={pattern}",
                    "-i",
                    "--pretty=%H",
                ],
            )
        )
    hotfix_commits: set[str] = set()
    for pattern in hotfix_patterns:
        hotfix_commits.update(
            _git_lines(
                repo_path,
                [
                    "log",
                    f"--since={since_date}",
                    "--no-merges",
                    f"--grep={pattern}",
                    "-i",
                    "--pretty=%H",
                ],
            )
        )

    if total_non_merge_commits > 0:
        metrics["m7_revert_rate"] = len(revert_commits) / total_non_merge_commits

    weeks = period_days / 7 if period_days > 0 else 0
    if weeks > 0:
        metrics["m8_hotfix_frequency"] = len(hotfix_commits) / weeks

    author_lines = _git_lines(
        repo_path, ["log", f"--since={since_date}", "--no-merges", "--pretty=%an"]
    )
    author_counts = Counter(author_lines)
    if author_counts:
        counts = list(author_counts.values())
        total = sum(counts)
        if total > 0:
            sorted_counts = sorted(counts)
            gini_n = len(sorted_counts)
            cumulative = sum(
                (idx + 1) * count for idx, count in enumerate(sorted_counts)
            )
            gini = (2 * cumulative) / (gini_n * total) - (gini_n + 1) / gini_n
            metrics["m9_commit_distribution"] = gini

    return metrics, metadata


def _collect_pr_metrics(
    repository: str, since_date: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    metrics: dict[str, Any] = {
        "m1_cycle_time": _metric_entry(
            "m1_cycle_time",
            "PR Cycle Time",
            None,
            "hours",
            reason="pr_data_unavailable",
        ),
        "m2_pr_size": _metric_entry(
            "m2_pr_size", "PR Size", None, "lines", reason="pr_data_unavailable"
        ),
        "m3_time_to_first_review": _metric_entry(
            "m3_time_to_first_review",
            "Time to First Review",
            None,
            "hours",
            reason="pr_data_unavailable",
        ),
        "m4_review_comments": _metric_entry(
            "m4_review_comments",
            "Review Comments per PR",
            None,
            "count",
            reason="pr_data_unavailable",
        ),
        "m5_commits_per_pr": _metric_entry(
            "m5_commits_per_pr",
            "Commits per PR",
            None,
            "count",
            reason="pr_data_unavailable",
        ),
        "m6_rejection_rate": _metric_entry(
            "m6_rejection_rate",
            "PR Rejection Rate",
            None,
            "percent",
            reason="pr_data_unavailable",
        ),
        "m10_review_iterations": _metric_entry(
            "m10_review_iterations",
            "Review Iterations",
            None,
            "count",
            reason="pr_data_unavailable",
        ),
    }
    metadata: dict[str, Any] = {
        "source": "github_api",
        "since_date": since_date,
        "pr_count": 0,
        "merged_prs": 0,
        "rejected_prs": 0,
    }
    if not _gh_enabled():
        metadata["source"] = "disabled"
        metadata["note"] = "GitHub API extraction disabled."
        return metrics, metadata

    limit = int(os.getenv("AUDIT_DEVEX_GITHUB_LIMIT", "1000"))
    cmd = [
        "pr",
        "list",
        "-R",
        repository,
        "--state",
        "all",
        "--search",
        f"created:>={since_date}",
        "--limit",
        str(limit),
        "--json",
        ",".join(
            [
                "number",
                "createdAt",
                "mergedAt",
                "closedAt",
                "additions",
                "deletions",
                "changedFiles",
                "commits",
                "comments",
                "reviews",
                "isDraft",
                "author",
            ]
        ),
    ]
    code, stdout, stderr = _run_gh(cmd)
    if code != 0:
        metadata["source"] = "error"
        metadata["note"] = stderr.strip() or "gh pr list failed"
        return metrics, metadata
    try:
        pr_payload = json.loads(stdout)
    except json.JSONDecodeError:
        metadata["source"] = "error"
        metadata["note"] = "Unable to parse GitHub PR JSON."
        return metrics, metadata

    prs: list[dict[str, Any]] = []
    for pr in pr_payload if isinstance(pr_payload, list) else []:
        if pr.get("isDraft"):
            continue
        author_login = None
        author = pr.get("author")
        if isinstance(author, dict):
            author_login = author.get("login")
        if _is_bot_author(author_login):
            continue
        prs.append(pr)

    metadata["pr_count"] = len(prs)
    merged_prs = [pr for pr in prs if pr.get("mergedAt")]
    rejected_prs = [pr for pr in prs if pr.get("closedAt") and not pr.get("mergedAt")]
    metadata["merged_prs"] = len(merged_prs)
    metadata["rejected_prs"] = len(rejected_prs)

    if not merged_prs:
        return metrics, metadata

    cycle_times: list[float] = []
    additions: list[float] = []
    deletions: list[float] = []
    files_changed: list[float] = []
    total_changes: list[float] = []
    review_times: list[float] = []
    review_comments: list[float] = []
    commits_per_pr: list[float] = []
    review_iterations: list[float] = []

    for pr in merged_prs:
        created_at = _parse_github_datetime(pr.get("createdAt"))
        merged_at = _parse_github_datetime(pr.get("mergedAt"))
        if created_at and merged_at:
            cycle_times.append((merged_at - created_at).total_seconds() / 3600.0)

        pr_additions = pr.get("additions")
        pr_deletions = pr.get("deletions")
        pr_files = pr.get("changedFiles")
        if isinstance(pr_additions, (int, float)):
            additions.append(float(pr_additions))
        if isinstance(pr_deletions, (int, float)):
            deletions.append(float(pr_deletions))
        if isinstance(pr_files, (int, float)):
            files_changed.append(float(pr_files))
        if isinstance(pr_additions, (int, float)) and isinstance(
            pr_deletions, (int, float)
        ):
            total_changes.append(float(pr_additions + pr_deletions))

        pr_commits = pr.get("commits")
        if isinstance(pr_commits, (int, float)):
            commits_per_pr.append(float(pr_commits))

        pr_comments = pr.get("comments")
        if isinstance(pr_comments, (int, float)):
            review_comments.append(float(pr_comments))

        pr_reviews = pr.get("reviews")
        if isinstance(pr_reviews, list) and created_at:
            review_times_for_pr: list[float] = []
            changes_requested = 0
            for review in pr_reviews:
                if not isinstance(review, dict):
                    continue
                submitted = _parse_github_datetime(review.get("submittedAt"))
                if submitted:
                    review_times_for_pr.append(
                        (submitted - created_at).total_seconds() / 3600.0
                    )
                if review.get("state") == "CHANGES_REQUESTED":
                    changes_requested += 1
            if review_times_for_pr:
                review_times.append(min(review_times_for_pr))
            review_iterations.append(float(changes_requested))

    metrics["m1_cycle_time"] = _metric_entry(
        "m1_cycle_time",
        "PR Cycle Time",
        _median(cycle_times),
        "hours",
        description="Median hours from PR creation to merge.",
        details={"p90_hours": _p90(cycle_times), "mean_hours": _mean(cycle_times)},
    )

    metrics["m2_pr_size"] = _metric_entry(
        "m2_pr_size",
        "PR Size",
        _median(total_changes),
        "lines",
        description="Median total lines changed per PR (additions + deletions).",
        details={
            "median_additions": _median(additions),
            "median_deletions": _median(deletions),
            "median_files_changed": _median(files_changed),
        },
    )

    metrics["m3_time_to_first_review"] = _metric_entry(
        "m3_time_to_first_review",
        "Time to First Review",
        _median(review_times),
        "hours",
        description="Median hours from PR creation to first review submission.",
        details={"p90_hours": _p90(review_times), "mean_hours": _mean(review_times)},
    )

    metrics["m4_review_comments"] = _metric_entry(
        "m4_review_comments",
        "Review Comments per PR",
        _median(review_comments),
        "count",
        description="Median PR comment count (proxy for review depth).",
    )

    metrics["m5_commits_per_pr"] = _metric_entry(
        "m5_commits_per_pr",
        "Commits per PR",
        _median(commits_per_pr),
        "count",
        description="Median commits per PR.",
    )

    total_prs = len(merged_prs) + len(rejected_prs)
    rejection_rate = (len(rejected_prs) / total_prs) if total_prs else None
    metrics["m6_rejection_rate"] = _metric_entry(
        "m6_rejection_rate",
        "PR Rejection Rate",
        rejection_rate,
        "percent",
        description="Closed PRs without merge divided by total closed PRs.",
    )

    metrics["m10_review_iterations"] = _metric_entry(
        "m10_review_iterations",
        "Review Iterations",
        _median(review_iterations),
        "count",
        description="Median count of CHANGES_REQUESTED reviews per PR.",
        details={
            "prs_with_iterations_pct": (
                (sum(1 for value in review_iterations if value > 0) / len(merged_prs))
                if merged_prs
                else None
            )
        },
    )

    return metrics, metadata


def _resolve_repo_path(repository: str, git_clone_path: str | None) -> Path | None:
    if git_clone_path:
        candidate = Path(git_clone_path)
        return candidate if candidate.exists() else None
    candidate = Path(repository)
    if candidate.exists():
        return candidate
    return None


def _resolve_since_date(since_date: str | None, period_days: int) -> str:
    if since_date:
        return since_date
    cutoff = datetime.now(timezone.utc) - timedelta(days=period_days)
    return cutoff.date().isoformat()


def collect_metrics(
    repository: str,
    output_dir: Path,
    since_date: str | None = None,
    git_clone_path: str | None = None,
    period_days: int | None = None,
) -> Tier1MetricsCollectionOutput:
    period_days = period_days or int(os.getenv("AUDIT_DEVEX_PERIOD_DAYS", "180"))
    since_date = _resolve_since_date(since_date, period_days)

    repo_path = _resolve_repo_path(repository, git_clone_path)
    metrics: dict[str, Any] = {}
    metadata: dict[str, Any] = {"since_date": since_date, "period_days": period_days}

    git_metrics: dict[str, Any] = {}
    git_metadata: dict[str, Any] = {}
    if repo_path and is_git_repo(repo_path):
        git_metrics, git_metadata = _collect_git_metrics(
            repo_path, since_date, period_days
        )
    else:
        git_metadata = {
            "source": "unavailable",
            "proxy_used": False,
            "note": "Repository not available or missing git history.",
        }

    github_repo = _resolve_github_repo(repository, repo_path)
    pr_metrics: dict[str, Any] = {}
    pr_metadata: dict[str, Any] = {}
    if github_repo:
        pr_metrics, pr_metadata = _collect_pr_metrics(github_repo, since_date)
    else:
        pr_metadata = {"source": "unavailable", "note": "GitHub repo not resolved."}

    metadata["git"] = git_metadata
    metadata["pr_metrics"] = pr_metadata
    if github_repo:
        metadata["github_repo"] = github_repo

    metrics.update(pr_metrics)

    pr_cycle_time = None
    pr_cycle_entry = pr_metrics.get("m1_cycle_time")
    if isinstance(pr_cycle_entry, dict):
        pr_cycle_time = pr_cycle_entry.get("value")

    if pr_cycle_time is None:
        pr_cycle_time = git_metrics.get("pr_cycle_time_hours")
        metadata["proxy_used"] = bool(
            git_metrics.get("pr_cycle_time_hours") is not None
        )
        metadata.setdefault(
            "proxy_note",
            git_metadata.get("proxy_note") if git_metadata.get("proxy_used") else None,
        )
    else:
        metadata["proxy_used"] = False

    metrics["pr_cycle_time_hours"] = _metric_entry(
        "pr_cycle_time_hours",
        "PR Cycle Time",
        pr_cycle_time,
        "hours",
        reason="git_proxy" if metadata.get("proxy_used") else None,
    )

    m10_entry = pr_metrics.get("m10_review_iterations")
    using_m10 = isinstance(m10_entry, dict) and m10_entry.get("available") is True
    review_iterations_value = (
        m10_entry.get("value") if using_m10 else git_metrics.get("review_iterations")
    )

    metrics["review_iterations"] = _metric_entry(
        "review_iterations",
        "Review Iterations",
        review_iterations_value,
        "count",
        reason="git_proxy" if not using_m10 else None,
    )

    metrics["review_time_hours"] = _metric_entry(
        "review_time_hours",
        "Review Time",
        git_metrics.get("review_time_hours"),
        "hours",
        reason=(
            "git_proxy" if git_metrics.get("review_time_hours") is not None else None
        ),
    )

    metrics["commit_count"] = _metric_entry(
        "commit_count",
        "Commit Count",
        git_metrics.get("commit_count"),
        "count",
    )

    metrics["m7_revert_rate"] = _metric_entry(
        "m7_revert_rate",
        "Revert Rate",
        git_metrics.get("m7_revert_rate"),
        "percent",
        description="Share of commits that are reverts (git log).",
    )
    metrics["m8_hotfix_frequency"] = _metric_entry(
        "m8_hotfix_frequency",
        "Hotfix Frequency",
        git_metrics.get("m8_hotfix_frequency"),
        "per_week",
        description="Hotfix commits per week (git log).",
    )
    metrics["m9_commit_distribution"] = _metric_entry(
        "m9_commit_distribution",
        "Commit Distribution",
        git_metrics.get("m9_commit_distribution"),
        "gini",
        description="Gini coefficient of commit distribution by author.",
    )

    repo_name = Path(repository).name if Path(repository).exists() else repository
    repo_name = repo_name.split("/")[-1]
    tier1_dir = output_dir / repo_name / "tier1"
    tier1_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "repository": repository,
        "period_days": period_days,
        "since_date": since_date,
        "metrics": metrics,
        "metadata": metadata,
    }

    output_file = tier1_dir / "metrics.json"
    output_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return Tier1MetricsCollectionOutput(
        output_file=str(output_file),
        metrics_collected=len(metrics),
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("repository")
    parser.add_argument("output_dir")
    parser.add_argument("since_date", nargs="?")
    parser.add_argument("git_clone_path", nargs="?")
    parser.add_argument("--period-days", type=int)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
    except SystemExit:
        print_json(
            ErrorOutput(
                error=(
                    "Usage: collect_tier1_metrics.py <org/repo> <output_dir> "
                    "[since_date] [git_clone_path] [--period-days <days>]"
                ),
                code=2,
            )
        )
        return 2

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    result = collect_metrics(
        args.repository,
        output_dir,
        since_date=args.since_date,
        git_clone_path=args.git_clone_path,
        period_days=args.period_days,
    )
    print_json(result)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
