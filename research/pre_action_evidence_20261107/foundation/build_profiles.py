"""Create reviewable five-route/six-arm templates; never launch or load keys."""
import copy
import json
from pathlib import Path
from evidence_foundation import SCHEMA, ARMS, MAIN_ARMS, CORE_ARMS, validate_six, validate_panel

def build():
    root = Path(__file__).resolve().parent / 'configs'
    root.mkdir(exist_ok=True)
    routes = {
        'LADDER': ('gpt-6-astra', 150, 'launch_ladder_study.py', 'official pi05_droid_jointpos',
                   'absolute joint7 + original binary gripper; original 8D/15Hz', 'original DROID chunk', 'original task SPECS horizon'),
        'RoboMME': ('gpt-6-astra', 150, 'launch_robomme_study.py', 'frozen pi05_droid_jointpos transfer',
                    'Panda absolute joint7 + documented gripper encoding; native builder Hz', 'original 15x8', 'original 10000 + wrapper 2'),
        'RoboMemArena': ('gpt-6-astra', 150, 'launch_robomemarena_study.py', 'rlinf-pi05-libero-130',
                         'relative EE OSC7/native gripper, 20Hz', 'original 5x7; no padding', '2500 + original postgoal200; original strict pour monitor30'),
        'LIBERO-PRO': ('gpt-6.1-sol', 100, 'launch_libero_pro_study.py', 'original PRO independent frozen checkpoint',
                       'original PRO native action/observation', 'original PRO chunk', 'original 10000'),
        'RoboCasa': ('gpt-6.1-sol', 100, 'launch_robocasa_study.py', 'original RoboCasa independent frozen checkpoint',
                     'original RC native action/observation', 'original RC chunk', 'original task catalog evaluator limits'),
    }
    context = [
        ('native16k', 'native-only', 'disabled', 'disabled', 'disabled', None),
        ('provenance', 'bounded-retrieval', 'disabled', 'disabled', 'disabled', None),
        ('provenance', 'bounded-retrieval', 'fixed-check-skill', 'disabled', 'fixed-precheck', None),
        ('provenance', 'bounded-retrieval', 'requirement-skill', 'extension-not-implemented', 'disabled', None),
        ('provenance', 'bounded-retrieval', 'requirement-skill', 'extension-not-implemented', 'joint-extension-not-implemented', None),
        ('provenance', 'bounded-retrieval', 'requirement-skill', 'extension-not-implemented', 'joint-extension-not-implemented', 'TRAIN_SPLIT_ONLY_NOT_FITTED'),
    ]
    receipts = {}
    for name, (model, cap, launcher, checkpoint, action, chunk, steps) in routes.items():
        common = {
            'model': model, 'reasoning_effort': 'high', 'codex_cli': '0.149.1', 'native_compaction_tokens': 16000,
            'frozen_checkpoint_profile': checkpoint, 'action_contract': action, 'action_chunk': chunk,
            'observations': 'original public RGB/proprio in original ordering; no GT/info wholesale',
            'native_scoring': 'original evaluator only; missing=UNKNOWN; no extra goalcheck', 'native_steps': steps,
            'decision_cap': cap, 'memory_tools_count_inside_cap': True, 'generation_budget': 'original resolved CLI metadata; no increase',
            'context_tool_schema': 'identical across arms; no physical capability',
            'storage_cap_bytes': 16777216, 'storage_cap_status': 'PREREGISTRATION_CANDIDATE_NOT_APPROVED_FOR_LONG_RGB',
            'storage_scope': 'candidate evidence metadata/reference bytes only; original RGB retention unchanged; preflight sizing required',
            'historical_read_bytes_per_decision': 4096,
            'same_current_observation': True, 'new_motion_skills': False, 'online_code_edits': False,
            'relay': {'per_key_seconds': 600, 'slots': 7, 'attempts_per_slot': 1, 'sdk_retries': 0,
                      'case_wall_seconds': None, 'failed_partial_tools': 'discard', 'physical_replay': False},
            'required_bound_hashes': {key: None for key in ('checkpoint', 'norm', 'physical_tool_schema', 'native_scorer', 'native_adapter', 'planner_prefix', 'execution_protocol')},
            'launcher': {'module': launcher, 'binding_source': 'Long-context-continuity-study-20261107-v1/runtime-g8',
                         'default': 'prepare-only', 'new_unique_namespace': True, 'live_activation': False},
        }
        profiles = []
        for arm, values in zip(ARMS, context):
            profiles.append({'schema': SCHEMA, 'benchmark': name, 'arm': arm, 'common': copy.deepcopy(common),
                             'context': dict(zip(('representation', 'access', 'pre_action_skill', 'availability_predictor', 'selector', 'offline_fit_artifact'), values)),
                             'execution_enabled': False})
        (root / f'{name}-six-arms.json').write_text(json.dumps(profiles, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
        main_values = [context[0], ('summary', 'bounded-summary', 'disabled', 'disabled', 'disabled', None),
                       context[1], context[2], ('provenance', 'bounded-retrieval', 'requirement-skill', 'disabled', 'skill-guided-only-not-implemented', None), context[4]]
        core_values = [('provenance', 'bounded-retrieval', 'requirement-skill' if s else 'disabled',
                        'extension-not-implemented' if h else 'disabled',
                        'joint-extension-not-implemented' if h else ('skill-guided-only-not-implemented' if s else 'disabled'), None)
                       for s,h in ((0,0),(1,0),(0,1),(1,1))]
        def panel(names, values):
            return [{'schema': SCHEMA, 'benchmark': name, 'arm': arm, 'common': copy.deepcopy(common),
                     'context': dict(zip(('representation', 'access', 'pre_action_skill', 'availability_predictor', 'selector', 'offline_fit_artifact'), value)),
                     'execution_enabled': False} for arm,value in zip(names,values)]
        main, core = panel(MAIN_ARMS, main_values), panel(CORE_ARMS, core_values)
        for suffix, group in (('MAIN_COMPARISONS', main), ('CORE2x2', core)):
            (root / f'{name}-{suffix}.json').write_text(json.dumps(group, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
        receipts[name] = {'staged-methods': validate_six(profiles), 'main': validate_panel(main, 'main'), 'core2x2': validate_panel(core, 'core2x2')}
    (root / 'CPU-noncontext-equality.json').write_text(json.dumps(receipts, indent=2)+'\n', encoding='utf-8')
    mapping = {'schema': 'comparison-family-mapping-v1', 'execution_enabled': False,
               'main_table': dict(zip(MAIN_ARMS, ['native16k', 'summary', 'provenance-retrieval', 'fixed-precheck', 'skill-only', 'skill+harness'])),
               'causal_core': {'S0H0': 'same-memory/no-S/no-H', 'S1H0': 'same-memory/S-only', 'S0H1': 'same-memory/H-only', 'S1H1': 'same-memory/S+H'},
               'staged_methods_not_main_table': list(ARMS),
               'not_equivalent': 'B0/B1/B2 numbers in staged-methods are NOT main-table numbers; no automatic historical result remapping',
               'selection': 'Use exactly one declared family per analysis. MAIN measures package comparisons; CORE isolates S/H holding memory constant.'}
    (root / 'COMPARISON_FAMILY_MAPPING.json').write_text(json.dumps(mapping, indent=2)+'\n', encoding='utf-8')
    return receipts

if __name__ == '__main__':
    print(json.dumps(build(), indent=2))
