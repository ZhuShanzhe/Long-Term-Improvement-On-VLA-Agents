"""CPU-only pre-action evidence infrastructure. No robot, network or model access.

Policy inputs must already have been projected from original public tool returns.
Hash integrity establishes provenance, never truth or physical task completion.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Protocol

SCHEMA = 'pre-action-evidence-foundation-v1'
BOUND_COMPONENTS = frozenset(('checkpoint', 'norm', 'physical_tool_schema', 'native_scorer', 'native_adapter', 'planner_prefix', 'execution_protocol'))
PUBLIC_SOURCES = {'original_rgb', 'original_proprio', 'original_tool_return', 'ordinary_error', 'task_instruction'}
ARMS = ('B0_native', 'B1_retrieval', 'B2_fixed_precheck', 'B3_predict_only', 'B4_joint_preserve', 'B5_joint_learned')
MAIN_ARMS = ('B0_native', 'B1_summary', 'B2_retrieval', 'B3_fixed_precheck', 'Ours_S', 'Ours_SH')
CORE_ARMS = ('S0H0', 'S1H0', 'S0H1', 'S1H1')
CONTEXT_FIELDS = {'representation', 'access', 'pre_action_skill', 'availability_predictor', 'selector', 'offline_fit_artifact'}
ZERO = '0' * 64

def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')

def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()

def exact(obj, keys):
    if not isinstance(obj, dict) or set(obj) != set(keys):
        raise ValueError('Unexpected fields; project explicitly, never pass env.info wholesale')

def identity(value):
    if not isinstance(value, str) or not value or len(value) > 256:
        raise ValueError('Invalid bounded identity')
    return value

class EvidenceLedger:
    """Append-only single-host-writer ledger; never accepts caller-selected time/id.

    Public ingress takes exact fields. Adapter ownership remains essential: this
    library cannot determine whether arbitrary text contains an oracle or secret.
    Registered asset refs are opaque identifiers, never paths opened by this API.
    """
    def __init__(self, path, episode, public_asset_ids=()):
        self.path = Path(path)
        self.episode = identity(episode)
        self.assets = frozenset(public_asset_ids)
        self.events = self.load(self.path, self.episode)

    @staticmethod
    def load(path, episode):
        rows = []
        if not Path(path).exists():
            return rows
        prev = ZERO
        for line in Path(path).read_text(encoding='utf-8').splitlines():
            row = json.loads(line)
            exact(row, ('seq', 'id', 'episode', 'kind', 'body', 'previous_hash', 'hash'))
            if row['seq'] != len(rows) or row['id'] != f'e{len(rows):08d}' or row['episode'] != episode or row['previous_hash'] != prev:
                raise ValueError('Ledger order/episode/hash chain mismatch')
            signature = row.pop('hash')
            if digest(row) != signature:
                raise ValueError('Ledger tampering detected')
            row['hash'] = signature
            rows.append(row)
            prev = signature
        return rows

    def _append(self, kind, body):
        row = {'seq': len(self.events), 'id': f'e{len(self.events):08d}', 'episode': self.episode,
               'kind': kind, 'body': body, 'previous_hash': self.events[-1]['hash'] if self.events else ZERO}
        row['hash'] = digest(row)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('a', encoding='utf-8', newline='\n') as out:
            out.write(encoded(row).decode('utf-8') + '\n')
        self.events.append(row)
        return row['id']

    def _refs(self, ids, required=False):
        if not isinstance(ids, list) or len(ids) != len(set(ids)) or (required and not ids):
            raise ValueError('Invalid evidence reference list')
        known = {row['id'] for row in self.events if row['kind'] in ('observation', 'claim')}
        if any(ref not in known for ref in ids):
            raise ValueError('Future, missing or non-evidence reference')

    def observe(self, payload):
        exact(payload, ('source', 'asset_ids', 'text', 'tool_call_id'))
        if payload['source'] not in PUBLIC_SOURCES:
            raise ValueError('Not an original public source')
        if not isinstance(payload['asset_ids'], list) or any(x not in self.assets for x in payload['asset_ids']):
            raise ValueError('Unregistered asset; file and network reads forbidden')
        if not isinstance(payload['text'], str) or len(payload['text'].encode('utf-8')) > 4096:
            raise ValueError('Public text bound exceeded')
        if payload['tool_call_id'] is not None:
            identity(payload['tool_call_id'])
        return self._append('observation', copy.deepcopy(payload))

    def claim(self, payload):
        exact(payload, ('entity', 'predicate', 'value', 'evidence_ids', 'scope', 'confidence'))
        identity(payload['entity']); identity(payload['predicate'])
        if payload['scope'] not in ('historical_event', 'current_state'):
            raise ValueError('Separate historical events from current state')
        self._refs(payload['evidence_ids'], required=True)
        c = payload['confidence']
        if c is not None and (type(c) not in (int, float) or not math.isfinite(c) or not 0 <= c <= 1):
            raise ValueError('Invalid confidence')
        # Always a model belief. Citing an observation never promotes belief to fact.
        return self._append('claim', copy.deepcopy(payload))

    def invalidate(self, claim_id, reason, evidence_ids):
        target = next((r for r in self.events if r['id'] == claim_id and r['kind'] == 'claim'), None)
        if target is None or target['body']['scope'] != 'current_state':
            raise ValueError('Only current-state claims can expire; retain history')
        self._refs(evidence_ids, required=True)
        return self._append('invalidation', {'claim_id': claim_id, 'reason': identity(reason), 'evidence_ids': evidence_ids})

    def read(self, ids, at_seq=None):
        """Read only a past prefix; unknown is explicit, expired history retained."""
        limit = len(self.events) - 1 if at_seq is None else at_seq
        if type(limit) is not int or limit < -1 or limit >= len(self.events):
            raise ValueError('Invalid cutoff or future access')
        prefix = self.events[:limit + 1]
        invalid = {r['body']['claim_id'] for r in prefix if r['kind'] == 'invalidation'}
        by_id = {r['id']: r for r in prefix}
        return [{'id': i, 'status': 'unknown'} if i not in by_id else
                {'id': i, 'status': 'expired' if i in invalid else 'recorded_not_verified', 'record': copy.deepcopy(by_id[i])}
                for i in ids]

class AvailabilityPredictor(Protocol):
    def predict(self, public_prefix: list, candidate_action: dict, future_requirement: dict) -> dict:
        """Return availability by retrieval/reobserve/physical_recovery and cost/unknown.
        Research extension only; never receives future events, native state or score.
        """
        ...

class PreservationSelector(Protocol):
    def select(self, public_prefix: list, candidate_options: list, predictions: list) -> dict:
        """Research extension: choose observe/save/retrieve/act/reorder within original tools."""
        ...

def common_fingerprint(profile):
    exact(profile, ('schema', 'benchmark', 'arm', 'common', 'context', 'execution_enabled'))
    if profile['schema'] != SCHEMA or profile['arm'] not in set(ARMS + MAIN_ARMS + CORE_ARMS):
        raise ValueError('Unsupported schema or arm')
    if set(profile['context']) - CONTEXT_FIELDS:
        raise ValueError('Context override outside permitted surface')
    relay = profile['common']['relay']
    if relay != {'per_key_seconds': 600, 'slots': 7, 'attempts_per_slot': 1, 'sdk_retries': 0, 'case_wall_seconds': None,
                 'failed_partial_tools': 'discard', 'physical_replay': False}:
        raise ValueError('Credential/case policy drift')
    return digest({'benchmark': profile['benchmark'], 'common': profile['common']})

def validate_six(profiles):
    if {p['arm'] for p in profiles} != set(ARMS) or len(profiles) != 6:
        raise ValueError('Need each arm exactly once')
    hashes = {common_fingerprint(p) for p in profiles}
    if len(hashes) != 1:
        raise ValueError('Non-context controls differ within benchmark')
    return {'noncontext_equal': True, 'fingerprint': next(iter(hashes)), 'execution_enabled': False}

def validate_panel(profiles, family):
    expected = {'main': MAIN_ARMS, 'core2x2': CORE_ARMS, 'staged-methods': ARMS}[family]
    if {p['arm'] for p in profiles} != set(expected) or len(profiles) != len(expected):
        raise ValueError('Missing, duplicate or wrong comparison family')
    hashes = {common_fingerprint(p) for p in profiles}
    if len(hashes) != 1: raise ValueError('Non-context controls differ within benchmark')
    if family == 'core2x2':
        bases = {(p['context']['representation'], p['context']['access'], p['context']['offline_fit_artifact']) for p in profiles}
        if len(bases) != 1: raise ValueError('CORE2x2 must share the same provenance memory/access/training artifact')
    return {'family': family, 'noncontext_equal': True, 'fingerprint': next(iter(hashes)), 'execution_enabled': False}

def prepare_binding(profile, deployed_receipt):
    """Check immutable deployed route binding. Does not start a process or API call."""
    common_fingerprint(profile)
    expected = profile['common']['required_bound_hashes']
    if set(expected) != BOUND_COMPONENTS or any(not isinstance(v, str) or len(v) != 64 or set(v) - set('0123456789abcdef') for v in expected.values()):
        raise ValueError('Unresolved hashes: bind from actual deployment before any activation')
    if deployed_receipt['benchmark'] != profile['benchmark'] or deployed_receipt['hashes'] != expected:
        raise ValueError('Wrong benchmark or changed deployed controls')
    return {'prepared_only': True, 'benchmark': profile['benchmark'], 'arm': profile['arm'], 'fingerprint': common_fingerprint(profile),
            'execution_enabled': False, 'native_launch_request': copy.deepcopy(profile['common']['launcher'])}

def aggregate(rows):
    """Offline counters, strict native denominator, no model or scorer invocation.
    causal labels are optional evaluator-only annotations, never inferred from self-report.
    All rows must describe independent final cases; no repeated turn usage summation.
    """
    ids = [r['case_id'] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate case identity; choose final attempt explicitly')
    result = {'cases': len(rows), 'native_true': 0, 'native_false': 0, 'unknown': 0, 'integration_only': 0,
              'decisions': 0, 'physical_steps': 0, 'preservation_actions': 0, 'final_reported_usage': {},
              'eligible': 0, 'preserved_before_loss': 0, 'future_decisions': 0, 'correct_future_decisions': 0,
              'stale_uses': 0, 'recoveries': 0, 'recovery_steps': 0}
    result.update({'preservation_labeled': 0, 'preservation_unknown': 0,
                   'future_decision_labeled': 0, 'future_decision_unknown': 0,
                   'stale_use_labeled': 0, 'stale_use_unknown': 0})
    result['resource_missing_cases'] = {k: 0 for k in ('decisions', 'physical_steps', 'preservation_actions', 'final_reported_usage')}
    for row in rows:
        if row.get('integration_only', False):
            result['integration_only'] += 1
            continue
        val = row.get('native')
        if row.get('valid') is True and type(val) is bool:
            result['native_true' if val else 'native_false'] += 1
        else:
            result['unknown'] += 1
        for k in ('decisions', 'physical_steps', 'preservation_actions'):
            if k not in row: result['resource_missing_cases'][k] += 1
            v = row.get(k, 0)
            if type(v) is not int or v < 0:
                raise ValueError('Invalid resource counter')
            result[k] += v
        if 'final_reported_usage' not in row: result['resource_missing_cases']['final_reported_usage'] += 1
        for k, v in row.get('final_reported_usage', {}).items():
            if type(v) is not int or v < 0:
                raise ValueError('Invalid final cumulative usage')
            result['final_reported_usage'][k] = result['final_reported_usage'].get(k, 0) + v
        for event in row.get('offline_labels', []):
            if event['kind'] == 'eligible_loss':
                result['eligible'] += 1
                label = event.get('preserved_before_loss')
                if type(label) is bool:
                    result['preservation_labeled'] += 1
                    result['preserved_before_loss'] += int(label)
                else:
                    result['preservation_unknown'] += 1
            elif event['kind'] == 'future_decision':
                result['future_decisions'] += 1
                label = event.get('correct')
                if type(label) is bool:
                    result['future_decision_labeled'] += 1
                    result['correct_future_decisions'] += int(label)
                else:
                    result['future_decision_unknown'] += 1
                stale = event.get('stale_evidence_used')
                if type(stale) is bool:
                    result['stale_use_labeled'] += 1
                    result['stale_uses'] += int(stale)
                else:
                    result['stale_use_unknown'] += 1
            elif event['kind'] == 'recovery':
                steps = event['steps']
                if type(steps) is not int or steps < 0: raise ValueError('Invalid recovery steps')
                result['recoveries'] += 1; result['recovery_steps'] += steps
            else:
                raise ValueError('Unknown offline label')
    valid = result['native_true'] + result['native_false']
    result['valid_native_rate'] = result['native_true'] / valid if valid else None
    result['valid_coverage'] = valid / (len(rows)-result['integration_only']) if len(rows)>result['integration_only'] else None
    result['pre_loss_preservation_rate'] = result['preserved_before_loss'] / result['preservation_labeled'] if result['preservation_labeled'] else None
    result['future_decision_accuracy'] = result['correct_future_decisions'] / result['future_decision_labeled'] if result['future_decision_labeled'] else None
    result['stale_evidence_use_rate'] = result['stale_uses'] / result['stale_use_labeled'] if result['stale_use_labeled'] else None
    result['preservation_label_coverage'] = result['preservation_labeled'] / result['eligible'] if result['eligible'] else None
    result['future_decision_label_coverage'] = result['future_decision_labeled'] / result['future_decisions'] if result['future_decisions'] else None
    result['stale_use_label_coverage'] = result['stale_use_labeled'] / result['future_decisions'] if result['future_decisions'] else None
    result['reported_usage_is_bill'] = False
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    x = sub.add_parser('validate-six'); x.add_argument('profiles', type=Path)
    x = sub.add_parser('validate-panel'); x.add_argument('profiles', type=Path); x.add_argument('--family', choices=('main','core2x2','staged-methods'), required=True)
    x = sub.add_parser('aggregate'); x.add_argument('cases_jsonl', type=Path)
    x = sub.add_parser('prepare-binding'); x.add_argument('profile', type=Path); x.add_argument('receipt', type=Path)
    args = p.parse_args()
    if args.command == 'validate-six':
        out = validate_six(json.loads(args.profiles.read_text(encoding='utf-8')))
    elif args.command == 'validate-panel':
        out = validate_panel(json.loads(args.profiles.read_text(encoding='utf-8')), args.family)
    elif args.command == 'prepare-binding':
        out = prepare_binding(json.loads(args.profile.read_text(encoding='utf-8')), json.loads(args.receipt.read_text(encoding='utf-8')))
    else:
        out = aggregate([json.loads(x) for x in args.cases_jsonl.read_text(encoding='utf-8').splitlines() if x.strip()])
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
