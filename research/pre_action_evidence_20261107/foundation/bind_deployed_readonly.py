"""Server-side read-only binding of existing G8 receipts; output new directory only.

No private configs, models, keys, modules, native evaluator or subprocesses loaded.
Component map explicitly selects already-recorded digests; no guessed checkpoint hash.
"""
import argparse
import copy
import json
from pathlib import Path
from evidence_foundation import BOUND_COMPONENTS, SCHEMA, digest, prepare_binding, validate_panel, ARMS, MAIN_ARMS, CORE_ARMS

def read_json(path): return json.loads(Path(path).read_text(encoding='utf-8'))

def bind(common_bound, route_profile, component_map, six_profiles, output_dir):
    bound, deployed, mapping, profiles = map(read_json, (common_bound, route_profile, component_map, six_profiles))
    expected = profiles[0]['benchmark']
    if deployed['benchmark'] != expected: raise ValueError('Independent route mismatch')
    # Current launch profile is authoritative; refuse old wholecase/shared600 metadata.
    if deployed.get('case_seconds', 'MISSING') is not None or deployed.get('credential_attempt_seconds') != 600:
        raise ValueError('Not a current no-case-wall/per-key600 deployed route')
    if deployed.get('model') != profiles[0]['common']['model']:
        raise ValueError('Model profile changed')
    if set(mapping) != BOUND_COMPONENTS: raise ValueError('Explicit seven-component map required')
    hashes = {}
    for name, selector in mapping.items():
        # JSON-key path only, no filesystem path loading or eval.
        if not isinstance(selector, list) or not selector: raise ValueError('Invalid receipt JSON path')
        value = bound
        for key in selector: value = value[key]
        if not isinstance(value, str) or len(value) != 64 or set(value) - set('0123456789abcdef'):
            raise ValueError('Receipt does not contain actual SHA256 for '+name)
        hashes[name] = value
    prepared = []
    for profile in profiles:
        profile['common']['required_bound_hashes'] = copy.deepcopy(hashes)
        prepared.append(prepare_binding(profile, {'benchmark': expected, 'hashes': hashes}))
    names = {p['arm'] for p in profiles}
    family = next((name for name, arms in (('staged-methods', ARMS), ('main', MAIN_ARMS), ('core2x2', CORE_ARMS)) if names == set(arms)), None)
    if family is None: raise ValueError('Unknown comparison family')
    validation = validate_panel(profiles, family)
    out = Path(output_dir)
    # Never allow overwrite of G8 or an existing snapshot/live namespace.
    out.mkdir(parents=True, exist_ok=False)
    receipt = {'schema': SCHEMA, 'benchmark': expected, 'prepared_only': True, 'execution_enabled': False,
               'deployed_profile_fingerprint': digest(deployed), 'bound_receipt_fingerprint': digest(bound),
               'component_hashes': hashes, 'validation': validation}
    (out/'frozen_receipt.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    (out/'six-profiles-bound.json').write_text(json.dumps(profiles, indent=2)+'\n', encoding='utf-8')
    (out/'prepared-launch-requests.json').write_text(json.dumps(prepared, indent=2)+'\n', encoding='utf-8')
    return receipt

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('common-bound', 'route-profile', 'component-map', 'six-profiles', 'output-dir'):
        p.add_argument('--'+name, required=True)
    a = p.parse_args()
    print(json.dumps(bind(a.common_bound,a.route_profile,a.component_map,a.six_profiles,a.output_dir),indent=2))

if __name__ == '__main__': main()
