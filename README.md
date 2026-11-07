# Prospective Evidence Preservation for Long-Horizon Robot Agents

This repository's current research direction is **preserving the ability to make evidence-grounded future decisions before physical actions change what can be observed, retrieved, or recovered**.

The execution stack uses Codex for reasoning, tools, versioned evidence and offline improvement, with benchmark-specific frozen π0.5 policies for motor execution. The research variable is the context-related skill/harness: prospective evidence requirements, action-conditioned availability and binding predictions, and preservation choices. The framework itself is not claimed as the scientific contribution.

## Start here

- [Revised research report, Chinese](research/pre_action_evidence_20261107/REPORT.md)
- [Exact benchmark tasks, splits, metrics and comparisons](research/pre_action_evidence_20261107/design/benchmark_protocol.md)
- [Methods, primary references and novelty boundaries](research/pre_action_evidence_20261107/design/methods_and_related_work.md)
- [Codex implementation blueprints](research/pre_action_evidence_20261107/design/implementation_blueprints.md)
- [Public execution/evidence foundation](research/pre_action_evidence_20261107/foundation/README.md)
- [Actual delivery status and remaining research](research/pre_action_evidence_20261107/DELIVERY_STATUS.md)

RoboMME and RoboMemArena are the primary mechanism-development routes; LADDER tests long-horizon continuity and unnecessary-check overhead. LIBERO-PRO and RoboCasa provide separate transfer checks. Proposed EVID-Preserve scenarios are an independent diagnostic extension, not official native benchmark scores.

## Reproducibility boundary

Within each benchmark, all comparison groups freeze the upper model/effort, Codex protocol/compaction, π0.5 checkpoint and normalization, observations, action semantics/chunk, initial state, decision/control-step budgets and native scoring. Each benchmark retains its own adapter and launcher. Only context-related research modules vary.

The public foundation includes provenance/temporal evidence logs, bounded memory-tool compatibility, shared-budget injection, immutable profile templates and offline metrics. It has CPU tests; the proposed predictors, selectors and evidence skills are research extension points, not completed native experiments. No private keys, datasets, weights, raw observations or HTTP payloads belong in Git.

```bash
python -B -m unittest discover -s research/pre_action_evidence_20261107/foundation -p test_foundation.py
```

## Historical work

The previous active-verification research description is preserved in [the historical README](docs/archive/README-before-evidence-20261107.md). Existing baseline source, results and reproductions remain available as historical infrastructure and references. A new direction does not justify erasing unsuccessful or invalid runs, changing an active evaluation, or mixing different policy profiles into one controlled score.

Large artifacts and execution logs remain on the server data volume under `/root/autodl-tmp`; the new research preparation package is separate from the currently running compatibility tests.
