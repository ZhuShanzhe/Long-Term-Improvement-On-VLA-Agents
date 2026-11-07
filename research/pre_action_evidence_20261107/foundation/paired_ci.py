"""Offline paired native-success difference; bootstrap tasks, never event rows.

One benchmark per invocation. Estimand: equally weighted task means of paired
episodes. UNKNOWN sensitivity bounds include all predeclared paired identities;
complete-pair CI is conditional on valid pairs and must not hide low coverage.
"""
import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

def quantile(xs, q):
    xs = sorted(xs)
    k = (len(xs)-1)*q; lo = int(k); hi = min(lo+1, len(xs)-1)
    return xs[lo] + (xs[hi]-xs[lo])*(k-lo)

def paired_ci(rows, reference, target, seed=20261107, resamples=10000):
    if reference == target or resamples < 100: raise ValueError('Need distinct arms and >=100 resamples')
    table = {}
    benchmarks = set()
    for row in rows:
        if row['arm'] not in (reference, target): continue
        if row.get('integration_only', False): raise ValueError('Integration fixtures are not independent full cases')
        benchmark = row['benchmark']; benchmarks.add(benchmark)
        # Whole tasks are resampling units; episodes/seeds remain paired within task.
        key = (benchmark, str(row['task_id']), str(row['seed']), str(row['episode_id']))
        arm_key = key + (row['arm'],)
        if arm_key in table: raise ValueError('Duplicate task/seed/episode/arm: select one attempt without score cherry-picking')
        value = row.get('native')
        table[arm_key] = int(value) if row.get('valid') is True and type(value) is bool else None
    if len(benchmarks) != 1: raise ValueError('Analyze independent benchmarks separately')
    keys = sorted({k[:-1] for k in table})
    grouped, lower, upper = defaultdict(list), defaultdict(list), defaultdict(list)
    complete = 0
    for key in keys:
        a, b = table.get(key+(reference,)), table.get(key+(target,))
        task = key[:2]
        lower[task].append((b if b is not None else 0) - (a if a is not None else 1))
        upper[task].append((b if b is not None else 1) - (a if a is not None else 0))
        if a is not None and b is not None:
            grouped[task].append(b-a); complete += 1
    mean = lambda xs: sum(xs)/len(xs)
    task_means = [mean(grouped[t]) for t in sorted(grouped)]
    observed = mean(task_means) if task_means else None
    # A single task cannot support between-task generalization; refuse a false narrow CI.
    ci = None
    if len(task_means) >= 2:
        rng = random.Random(seed)
        samples = [mean([rng.choice(task_means) for _ in task_means]) for _ in range(resamples)]
        ci = [quantile(samples, .025), quantile(samples, .975)]
    return {'benchmark': next(iter(benchmarks)), 'reference': reference, 'target': target,
            'estimand': 'task-macro mean of within-task paired episode native-success differences (target-reference)',
            'pair_count': len(keys), 'complete_pair_count': complete, 'complete_pair_coverage': complete/len(keys) if keys else None,
            'task_clusters_total': len(lower), 'task_clusters_with_complete_pairs': len(task_means),
            'complete_pair_difference': observed, 'task_cluster_bootstrap_CI95': ci,
            'unknown_sensitivity_interval_all_pairs_task_macro': [mean([mean(v) for v in lower.values()]), mean([mean(v) for v in upper.values()])] if lower else None,
            'bootstrap_seed': seed, 'bootstrap_resamples': resamples, 'events_are_not_independent_samples': True,
            'caution': 'CI conditional on complete pairs. Report UNKNOWN coverage/bounds; no CI with <2 valid task clusters. Small cluster counts remain exploratory.'}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('jsonl', type=Path); p.add_argument('--reference', required=True); p.add_argument('--target', required=True)
    p.add_argument('--seed', type=int, default=20261107); p.add_argument('--resamples', type=int, default=10000)
    a = p.parse_args()
    rows = [json.loads(x) for x in a.jsonl.read_text(encoding='utf-8').splitlines() if x.strip()]
    print(json.dumps(paired_ci(rows,a.reference,a.target,a.seed,a.resamples),indent=2))

if __name__ == '__main__': main()
