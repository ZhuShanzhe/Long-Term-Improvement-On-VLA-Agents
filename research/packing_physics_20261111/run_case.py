"""Dedicated PACK-EVID entry: no API by default, explicit fixed-policy prefix.

The generic action port is available to the shared Codex tool host. This CLI
does not silently launch a paid model or resume another benchmark namespace.
"""
import argparse,fcntl,hashlib,importlib.util,json,pathlib,subprocess,sys,traceback
import numpy as np
import pack_env
from pack_env import PackPhysicalEnv,E,R
from task_port import PackToolPort
ROOT=pathlib.Path(__file__).resolve().parent
D=E/'Pre-action-evidence-preservation-study-20261107-v1/EVID-shared-execution-feedback-candidate-20261110-v1/runtime'
class Instruction:
    def __init__(self):self.text='put the cream cheese into container 0';self.index=0
    def decide(self,*args):self.index+=1;return {'name':'act','arguments':{'instruction':self.text},'call_id':'public-fixed-'+str(self.index)}
    def dispatched(self,ident):pass
    def close(self):pass
def main():
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--run-name',required=True);p.add_argument('--diagnostic-chunks',type=int,default=3);p.add_argument('--instruction',default='put the cream cheese into container 0');a=p.parse_args()
    if not 1<=a.diagnostic_chunks<=3:raise ValueError('FiniteZeroAPIPrefixOnly')
    if '/' in a.run_name or '\\' in a.run_name or a.run_name.startswith('.'):raise ValueError('LocalNewRunNameRequired')
    path=ROOT/'release-physical/private/cases'/f'{a.case}.json'
    if not path.exists():raise ValueError('CaseNotMaterialized')
    cfg=json.loads(path.read_text());run=ROOT/'runs'/a.run_name;run.mkdir(parents=True,exist_ok=False)
    lock=(E/'Server-autonomous-benchmark-dispatch-20261102-v1/dispatch.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
    env=agent=None;result={'upper_API_calls':0,'valid':False,'success':None}
    try:
        env=PackPhysicalEnv(cfg['case']['carrier'],run/'backend');state=np.load(cfg['state_file'],allow_pickle=False)['state'];env.reset(cfg['public'],cfg['private'],state)
        sys.path[:0]=[str(D),str(R)];sys.modules['physical_env']=pack_env
        s=importlib.util.spec_from_file_location('same_pack_frozen_adapter',D/'episode_adapter.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
        profile=R/'compatibility-closedloop-20261107-v1/runs/RMA-native-full600-quota-restored-v11/profile.json'
        agent=m.CodexFrozenPi05(str(profile),run/'execution',None,False);fixed=Instruction();agent.upper=fixed
        def infer(text):fixed.text=text;return agent.propose(env)
        port=PackToolPort(env,infer,run/'public-tool-delivery.jsonl')
        for i in range(a.diagnostic_chunks):port.dispatch('prefix-'+str(i),'act',{'instruction':a.instruction})
        result.update(control_steps=env.steps,actual_frozen_inferences=agent.index,scope='finite interface diagnostic, not a native task score')
    except BaseException as exc:traceback.print_exc();result.update(error_class=type(exc).__name__)
    finally:
        if agent:agent.close()
        if env:env.close()
        (run/'result.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result))
if __name__=='__main__':main()
