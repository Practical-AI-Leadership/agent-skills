#!/usr/bin/env python3
"""
Generate customer-friendly metrics summary from DevEx extraction output.

Usage:
    python3 generate_metrics_summary.py <baseline.json> [output.json]

Transforms raw DevEx extraction data into a report-ready summary with:
- North Star metrics (M1, M3, M10) - metrics we expect to improve
- Guardrail metrics (M7, M8, G1, G2) - metrics that must not regress
- Status classification based on industry thresholds
"""

import json
import sys
from datetime import datetime
from typing import Any


def load_baseline(filepath: str) -> dict:
    """Load baseline JSON from file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def classify_metric(metric_id: str, value: float, thresholds: dict) -> str:
    """Classify metric status based on thresholds."""
    t = thresholds.get(metric_id, {})

    # Handle inverted thresholds (higher is better, like success rates)
    if 'healthy_above' in t:
        if value >= t.get('healthy_above', 0):
            return 'Healthy'
        if value >= t.get('needs_work_above', 0):
            return 'Needs Work'
        return 'Critical'

    # Standard thresholds (lower is better)
    if 'critical_above' in t and value > t['critical_above']:
        return 'Critical'
    if 'needs_work_above' in t and value > t['needs_work_above']:
        return 'Needs Work'
    if 'healthy_below' in t and value < t['healthy_below']:
        return 'Healthy'
    return 'Adequate'


# Industry benchmarks with source citations
# Sources:
#   - Code Climate Velocity: PR flow metrics (M1, M3, M10)
#   - DORA Accelerate State of DevOps 2022: Stability metrics (M7)
#   - CircleCI 2025 State of Software Delivery: CI metrics (G1, G2)
INDUSTRY_BENCHMARKS = {
    'M1': {
        'elite': 2.4,        # <58h (~2.4 days)
        'median': 3.5,       # ~83h (~3.5 days)
        'unit': 'days',
        'source': 'Code Climate Velocity',
        'url': 'https://docs.velocity.codeclimate.com',
        'note': 'Median 83h; fastest quarter <58h; slowest quarter >124h',
    },
    'M3': {
        'elite': 10.0,       # <10h
        'median': 15.0,      # ~15h
        'unit': 'hours',
        'source': 'Code Climate Velocity',
        'url': 'https://docs.velocity.codeclimate.com',
        'note': 'Median 15h; fastest quarter <10h; slowest quarter >23h',
    },
    'M10': {
        'elite': 1.5,        # ~1-2 cycles (avoid >1.5)
        'median': 1.2,       # ~1.2 cycles
        'unit': 'cycles',
        'source': 'Code Climate Velocity',
        'url': 'https://docs.velocity.codeclimate.com',
        'note': 'Median 1.2; guidance on >1.5 and <1.0',
    },
    'M7': {
        'elite': 15.0,       # 0-15%
        'median': 23.0,      # 16-30% (midpoint)
        'unit': '%',
        'source': 'DORA Accelerate State of DevOps 2022',
        'url': 'https://dora.dev',
        'note': 'Change failure rate ranges: 0-15% (elite), 16-30% (high), 46-60% (low)',
    },
    'M8': {
        'elite': None,       # N/A - no consistent cross-industry benchmark
        'median': None,
        'unit': '/week',
        'source': None,
        'url': None,
        'note': 'No consistent cross-industry benchmark with a single per-week number',
    },
    'G1': {
        'elite': 2.5,        # <2.5 min (top performers)
        'median': 2.72,      # p50 2m43s
        'average': 11.03,    # avg 11m02s
        'unit': 'minutes',
        'source': 'CircleCI 2025 State of Software Delivery',
        'url': 'https://circleci.com/resources/2025-state-of-software-delivery/',
        'note': 'p50 2m43s; p75 8m7s; avg 11m2s; top performers under ~2.5 min',
    },
    'G2': {
        'elite': 90.0,       # ~90% (top-performing teams)
        'median': 82.15,     # 82.15% average
        'unit': '%',
        'source': 'CircleCI 2025 State of Software Delivery',
        'url': 'https://circleci.com/resources/2025-state-of-software-delivery/',
        'note': 'Average main-branch workflow success rate 82.15%; top-performing teams closer to 90%',
    },
}

# Legacy alias for backward compatibility
INDUSTRY_MEDIANS = {k: {'value': v.get('median'), 'unit': v['unit'], 'source': v.get('source'), 'url': v.get('url')} for k, v in INDUSTRY_BENCHMARKS.items()}

# Thresholds for metric classification
# Based on industry benchmarks: elite = healthy, median = adequate, worse = needs work/critical
THRESHOLDS = {
    'M1': {'critical_above': 5.2, 'needs_work_above': 3.5, 'healthy_below': 2.4},  # Elite <58h (2.4d), Median ~83h (3.5d)
    'M3': {'critical_above': 23.0, 'needs_work_above': 15.0, 'healthy_below': 10.0},  # Elite <10h, Median ~15h
    'M10': {'critical_above': 2.0, 'needs_work_above': 1.5, 'healthy_below': 1.2},  # Elite <1.5, Median ~1.2
    'M7': {'critical_above': 30.0, 'needs_work_above': 15.0, 'healthy_below': 15.0},  # Elite 0-15%, Average 16-30%
    'M8': {},  # N/A - no consistent cross-industry benchmark
    'G1': {'critical_above': 11.0, 'needs_work_above': 2.72, 'healthy_below': 2.5},  # Elite <2.5m, Median 2m43s, Avg 11m
    'G2': {'healthy_above': 90.0, 'needs_work_above': 82.0, 'critical_below': 75.0},  # Elite ~90%, Average 82.15%
}


def safe_get(data: dict, *keys, default=None) -> Any:
    """Safely navigate nested dictionary."""
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key, default)
        else:
            return default
    return result if result is not None else default


def generate_summary(baseline: dict) -> dict:
    """Generate customer-friendly summary from baseline data."""
    summary = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'extraction_window': safe_get(baseline, 'metadata', 'window', default='90 days'),
        'north_star_metrics': {},
        'guardrail_metrics': {},
        'interpretation': '',
        'recommendations': [],
        'benchmark_sources': {
            'pr_flow': {
                'name': 'Code Climate Velocity',
                'url': 'https://docs.velocity.codeclimate.com',
                'metrics': ['M1', 'M3', 'M10'],
                'notes': 'Cycle Time, Time to First Review, Review Cycles benchmarks',
            },
            'stability': {
                'name': 'DORA Accelerate State of DevOps 2022',
                'url': 'https://dora.dev',
                'metrics': ['M7'],
                'notes': 'Change failure rate ranges (0-15%, 16-30%, 46-60%) including hotfix/rollback/patch',
            },
            'ci': {
                'name': 'CircleCI 2025 State of Software Delivery',
                'url': 'https://circleci.com/resources/2025-state-of-software-delivery/',
                'metrics': ['G1', 'G2'],
                'notes': 'Workflow duration (p50 2m43s, avg 11m02s) and success rate (avg 82.15%, elite ~90%)',
            },
        },
    }

    # Extract North Star metrics (M1, M3, M10)

    # M1: PR Cycle Time
    m1_value = safe_get(baseline, 'M1', 'median') or safe_get(baseline, 'pr_metrics', 'm1_cycle_time', 'median_hours')
    if m1_value is not None:
        # Convert hours to days if needed
        if m1_value > 24:
            m1_value = m1_value / 24
        benchmark = INDUSTRY_BENCHMARKS['M1']
        summary['north_star_metrics']['pr_cycle_time'] = {
            'id': 'M1',
            'name': 'PR Cycle Time',
            'value': round(m1_value, 1),
            'unit': 'days',
            'elite_threshold': benchmark['elite'],
            'industry_median': benchmark['median'],
            'industry_source': benchmark['source'],
            'industry_url': benchmark['url'],
            'status': classify_metric('M1', m1_value, THRESHOLDS),
            'p90': safe_get(baseline, 'M1', 'p90') or safe_get(baseline, 'pr_metrics', 'm1_cycle_time', 'p90_hours')
        }

    # M3: Time to First Review
    m3_value = safe_get(baseline, 'M3', 'median') or safe_get(baseline, 'pr_metrics', 'm3_time_to_first_review', 'median_hours')
    if m3_value is not None:
        benchmark = INDUSTRY_BENCHMARKS['M3']
        summary['north_star_metrics']['time_to_first_review'] = {
            'id': 'M3',
            'name': 'Time to First Review',
            'value': round(m3_value, 1),
            'unit': 'hours',
            'elite_threshold': benchmark['elite'],
            'industry_median': benchmark['median'],
            'industry_source': benchmark['source'],
            'industry_url': benchmark['url'],
            'status': classify_metric('M3', m3_value, THRESHOLDS),
            'p90': safe_get(baseline, 'M3', 'p90')
        }

    # M10: Review Iterations
    m10_value = (
        safe_get(baseline, 'M10', 'median') or
        safe_get(baseline, 'pr_metrics', 'm10_review_iterations', 'median') or
        safe_get(baseline, 'm10_review_iterations', 'median')
    )
    if m10_value is not None:
        benchmark = INDUSTRY_BENCHMARKS['M10']
        summary['north_star_metrics']['review_iterations'] = {
            'id': 'M10',
            'name': 'Review Iterations',
            'value': round(m10_value, 1),
            'unit': 'cycles',
            'elite_threshold': benchmark['elite'],
            'industry_median': benchmark['median'],
            'industry_source': benchmark['source'],
            'industry_url': benchmark['url'],
            'status': classify_metric('M10', m10_value, THRESHOLDS),
            'note': 'Counted as CHANGES_REQUESTED reviews per PR'
        }

    # Extract Guardrail metrics (M7, M8, G1, G2)

    # M7: Revert Rate (proxy for DORA Change Failure Rate)
    m7_value = safe_get(baseline, 'M7') or safe_get(baseline, 'stability_metrics', 'm7_revert_rate')
    if m7_value is not None:
        # Convert to percentage if needed
        if m7_value < 1:
            m7_value = m7_value * 100
        benchmark = INDUSTRY_BENCHMARKS['M7']
        summary['guardrail_metrics']['revert_rate'] = {
            'id': 'M7',
            'name': 'Revert Rate',
            'value': round(m7_value, 1),
            'unit': '%',
            'elite_threshold': benchmark['elite'],
            'industry_median': benchmark['median'],
            'industry_source': benchmark['source'],
            'industry_url': benchmark['url'],
            'status': classify_metric('M7', m7_value, THRESHOLDS),
            'note': 'Proxy for DORA Change Failure Rate (includes rollback/hotfix/patch)'
        }

    # M8: Hotfix Frequency - no industry benchmark available
    m8_value = (
        safe_get(baseline, 'M8') or
        safe_get(baseline, 'stability_metrics', 'm8_hotfix_per_week') or
        safe_get(baseline, 'm8_hotfix_per_week')
    )
    # Fallback to count if per-week not available
    if m8_value is None:
        m8_value = safe_get(baseline, 'stability_metrics', 'm8_hotfix_count')
    if m8_value is not None:
        summary['guardrail_metrics']['hotfix_frequency'] = {
            'id': 'M8',
            'name': 'Hotfix Frequency',
            'value': round(m8_value, 1),
            'unit': '/week',
            'elite_threshold': None,
            'industry_median': None,
            'industry_source': None,
            'status': 'N/A',
            'note': 'No consistent cross-industry benchmark available'
        }

    # G1: Build Duration
    g1_value = safe_get(baseline, 'G1', 'p90') or safe_get(baseline, 'ci_metrics', 'build_duration_p90')
    if g1_value is not None:
        benchmark = INDUSTRY_BENCHMARKS['G1']
        summary['guardrail_metrics']['build_duration_p90'] = {
            'id': 'G1',
            'name': 'Build Duration (p90)',
            'value': round(g1_value, 1),
            'unit': 'minutes',
            'elite_threshold': benchmark['elite'],
            'industry_median': benchmark['median'],
            'industry_average': benchmark.get('average'),
            'industry_source': benchmark['source'],
            'industry_url': benchmark['url'],
            'status': classify_metric('G1', g1_value, THRESHOLDS),
            'note': 'p50 2m43s; p75 8m7s; avg 11m02s'
        }

    # G2: CI Success Rate
    g2_value = safe_get(baseline, 'G2') or safe_get(baseline, 'ci_metrics', 'success_rate') or safe_get(baseline, 'm15_build_success_rate', 'success_rate_pct')
    if g2_value is not None:
        benchmark = INDUSTRY_BENCHMARKS['G2']
        summary['guardrail_metrics']['ci_success_rate'] = {
            'id': 'G2',
            'name': 'CI Success Rate',
            'value': round(g2_value, 1),
            'unit': '%',
            'elite_threshold': benchmark['elite'],
            'industry_median': benchmark['median'],
            'industry_source': benchmark['source'],
            'industry_url': benchmark['url'],
            'status': classify_metric('G2', g2_value, THRESHOLDS)
        }

    # Generate interpretation
    summary['interpretation'] = generate_interpretation(summary)

    # Generate recommendations
    summary['recommendations'] = generate_recommendations(summary)

    return summary


def generate_interpretation(summary: dict) -> str:
    """Generate human-readable interpretation of metrics."""
    north_star = summary['north_star_metrics']
    guardrails = summary['guardrail_metrics']

    critical_count = sum(1 for m in north_star.values() if m.get('status') == 'Critical')
    critical_count += sum(1 for m in guardrails.values() if m.get('status') == 'Critical')

    needs_work_count = sum(1 for m in north_star.values() if m.get('status') == 'Needs Work')

    if critical_count > 0:
        return f"Found {critical_count} critical metric(s) requiring immediate attention. Review the specific metrics below for improvement priorities."
    elif needs_work_count > 0:
        return f"Delivery stability is solid. The bottleneck is in the review cycle - {needs_work_count} metric(s) need improvement. This is where AI coding tools may be creating friction."
    else:
        return "Metrics are within healthy ranges. Focus on maintaining current practices and monitoring for regression."


def generate_recommendations(summary: dict) -> list:
    """Generate actionable recommendations based on metrics."""
    recs = []

    north_star = summary['north_star_metrics']

    # Check Time to First Review
    ttfr = north_star.get('time_to_first_review', {})
    if ttfr.get('status') in ('Critical', 'Needs Work'):
        recs.append({
            'metric': 'M3',
            'priority': 'High' if ttfr.get('status') == 'Critical' else 'Medium',
            'recommendation': 'Reduce time to first review by establishing reviewer SLAs and improving PR descriptions with AI context.'
        })

    # Check Review Iterations
    iterations = north_star.get('review_iterations', {})
    if iterations.get('status') in ('Critical', 'Needs Work'):
        recs.append({
            'metric': 'M10',
            'priority': 'High' if iterations.get('status') == 'Critical' else 'Medium',
            'recommendation': 'Reduce review cycles by adding AGENTS.md for AI context and implementing pre-commit quality gates.'
        })

    # Check PR Cycle Time
    cycle_time = north_star.get('pr_cycle_time', {})
    if cycle_time.get('status') in ('Critical', 'Needs Work'):
        recs.append({
            'metric': 'M1',
            'priority': 'Medium',
            'recommendation': 'Address PR cycle time through smaller PRs, clearer PR templates, and reduced review friction.'
        })

    return recs


def main():
    if len(sys.argv) < 2:
        print('Usage: generate_metrics_summary.py <baseline.json> [output.json]')
        print()
        print('Arguments:')
        print('  baseline.json  - Path to DevEx baseline extraction output')
        print('  output.json    - Optional output path (defaults to stdout)')
        sys.exit(1)

    baseline_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        baseline = load_baseline(baseline_path)
    except FileNotFoundError:
        print(f'Error: Baseline file not found: {baseline_path}', file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f'Error: Invalid JSON in baseline file: {e}', file=sys.stderr)
        sys.exit(1)

    summary = generate_summary(baseline)
    output = json.dumps(summary, indent=2)

    if output_path:
        with open(output_path, 'w') as f:
            f.write(output)
        print(f'Summary written to: {output_path}')
    else:
        print(output)


if __name__ == '__main__':
    main()
