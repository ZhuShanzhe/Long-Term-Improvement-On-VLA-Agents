"""Pure offline paired-case planning. No execution option, process, API or secrets."""
import argparse
import json
import random
import re
from pathlib import Path
from evidence_foundation import common_fingerprint, digest, validate_panel

ROOT = Path(__file__).resolve().parent

def identities(benchmark, spec, panel):
    if benchmark == 'RoboMME':
        if panel not in ('development', 'heldout_same_task', 'heldout_mechanism'):
            raise ValueError('Unknown RoboMME panel')
        part = spec[panel]
        for task in part['tasks']:
            for episode in part['episodes']:
                # Native builder resolves its own seed from dataset metadata. Do
                # not invent a reset seed from episode index or prior examples.
                yield {'task_id': task, 'seed': None, 'episode_id': episode,
                       'dataset': part['dataset'], 'seed_binding': 'original builder metadata; unresolved offline',
                       'launcher_arguments': {'task': task, 'split': part['dataset'], 'episode': episode}}
    elif benchmark == 'RoboMemArena':
        pairs = {'development': ('development_tasks','development_seeds'),
                 'heldout_same_task': ('development_tasks','same_task_heldout_seeds'),
                 'heldout_task': ('heldout_tasks','unseen_task_seeds')}
        if panel not in pairs: raise ValueError('Unknown RoboMemArena panel')
        tasks, seeds = pairs[panel]
        for task in spec[tasks]:
            match = re.fullmatch(r'(\d+)_[A-Za-z0-9_]+', task)
            if not match: raise ValueError('RMA task needs original numeric-prefix identity')
            for seed in spec[seeds]:
                yield {'task_id':task,'native_task_id':int(match[1]),'seed':seed,'episode_id':'native_reset_by_seed',
                       'launcher_arguments':{'task_id':int(match[1]),'seed':seed}}
    elif benchmark == 'LADDER':
        pairs = {'development':('development_tasks','development_seeds'),
                 'heldout_same_task':('development_tasks','same_task_heldout_seeds'),
                 'heldout_composition':('heldout_composition_tasks','heldout_composition_seeds')}
        if panel not in pairs: raise ValueError('Unknown LADDER panel')
        tasks,seeds=pairs[panel]
        for task in spec[tasks]:
            for seed in spec[seeds]:
                yield {'task_id':task,'seed':seed,'episode_id':'native_reset_by_seed',
                       'launcher_arguments':{'task':task,'seed':seed}}
    elif benchmark in ('LIBERO-PRO','RoboCasa'):
        raise ValueError('Semantic/version/catalog binding pending: no formal paired plan for '+benchmark)
    else:
        raise ValueError('Unsupported independent benchmark')

def prepare(task_panel, profiles, benchmark, panel, family, plan_id, random_seed=20261107):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', plan_id): raise ValueError('Invalid unique plan ID')
    if family not in ('main','core2x2'): raise ValueError('Choose main or core2x2; staged methods are not the main table')
    validation=validate_panel(profiles,family)
    if any(p['benchmark']!=benchmark for p in profiles): raise ValueError('Profile benchmark mismatch')
    spec=task_panel['panels'][benchmark]
    rng=random.Random(random_seed)
    cases=[]
    arms={p['arm']:p for p in profiles}
    for block_no, identity in enumerate(identities(benchmark,spec,panel)):
        block_id=digest({'benchmark':benchmark, 'identity':identity})[:20]
        order=list(arms); rng.shuffle(order)
        for position,arm in enumerate(order):
            run_id='pae-'+digest({'plan_id':plan_id,'block_id':block_id,'arm':arm})[:24]
            cases.append({'run_id':run_id,'case_id':run_id,'block_id':block_id,'block_index':block_no,
                          'within_block_order':position,'benchmark':benchmark,'panel':panel,'arm':arm,
                          **identity,'noncontext_fingerprint':common_fingerprint(arms[arm]),
                          'method_context_fingerprint':digest(arms[arm]['context']),
                          'seen_status':'REQUIRES_REVIEW_AGAINST_HISTORICAL_IDENTITIES_NOT_AUTOMATICALLY_UNSEEN',
                          'catalog_validation_status':'PROPOSED_IDS_REQUIRE_PINNED_NATIVE_CATALOG_BINDING_BEFORE_LAUNCH',
                          'execution_enabled':False,'valid':False,'native':None})
    return {'schema':'offline-paired-case-plan-v1','plan_id':plan_id,'benchmark':benchmark,'panel':panel,
            'family':family,'random_seed':random_seed,'within_block_order':'fixed-seed shuffled arms; whole blocks remain paired',
            'execution_enabled':False,'not_a_launch_manifest':True,'noncontext_validation':validation,
            'task_panel_fingerprint':digest(task_panel),'profile_panel_fingerprint':digest(profiles),
            'split_status':'Proposed study split; dataset val/test uses native metadata where supplied; not a claim of unseen tasks',
            'budget_policy':'No changes to supplied profiles, original native budgets or per-key600/no-case-wall policy',
            'unknown_materialization':'All preregistered arms have a row even if neither arm later runs; replace result fields by actual outcomes without dropping missing rows',
            'block_count':len({c['block_id'] for c in cases}),'case_count':len(cases),'cases':cases}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--benchmark',required=True,choices=('RoboMME','RoboMemArena','LADDER','LIBERO-PRO','RoboCasa'))
    p.add_argument('--panel',required=True)
    p.add_argument('--family',choices=('main','core2x2'),default='core2x2')
    p.add_argument('--plan-id',required=True)
    p.add_argument('--random-seed',type=int,default=20261107)
    p.add_argument('--task-panel',type=Path,default=ROOT.parent/'design/task_panel.proposed.json')
    p.add_argument('--profiles',type=Path)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    profiles=a.profiles or ROOT/'configs'/f'{a.benchmark}-{("MAIN_COMPARISONS" if a.family=="main" else "CORE2x2")}.json'
    result=prepare(json.loads(a.task_panel.read_text(encoding='utf-8')),json.loads(profiles.read_text(encoding='utf-8')),
                   a.benchmark,a.panel,a.family,a.plan_id,a.random_seed)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x',encoding='utf-8') as out: out.write(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))

if __name__=='__main__': main()
