"""Benchmark-owned common tool boundary; same for all six evidence arms.

No scoring query/oracle tool exists. submit_verification is a declared task
response that terminates the custom task, not a request for hidden feedback.
Context read/write/image quotas remain owned by the existing shared archive.
"""
import json,pathlib
TOOLS=[
 {'name':'act','description':'Execute the original frozen pi0.5 instruction as one 5x7 OSC action chunk.',
  'inputSchema':{'type':'object','properties':{'instruction':{'type':'string'}},'required':['instruction'],'additionalProperties':False}},
 {'name':'view','description':'Return the current original RGB and proprio without a physics step.',
  'inputSchema':{'type':'object','properties':{},'additionalProperties':False}},
 {'name':'submit_verification','description':'Respond once to the arrived public packing work order. Ends the task; does not return expected answers or private score.',
  'inputSchema':{'type':'object','properties':{'value':{'anyOf':[{'type':'string','maxLength':64},{'type':'array','items':{'type':'string','maxLength':64},'maxItems':3},{'type':'null'}]},'container':{'enum':['c0','c1',None]},
   'evidence_ids':{'type':'array','items':{'type':'string'},'maxItems':8}},'required':['value','container','evidence_ids'],'additionalProperties':False}},
]
class PackToolPort:
    def __init__(self,env,infer_instruction,journal=None,max_decisions=600):
        if max_decisions!=600:raise ValueError('OriginalCommonDecisionCapRequired')
        self.env=env;self.infer=infer_instruction;self.max_decisions=max_decisions;self.used=0;self.seen=set()
        self.journal=pathlib.Path(journal) if journal else None
        if self.journal:
            if self.journal.exists():raise RuntimeError('NewNamespaceRequiredNoPhysicalReplay')
            self.journal.parent.mkdir(parents=True,exist_ok=True)
    def _record(self,obj):
        if self.journal:
            with self.journal.open('a',encoding='utf-8') as f:f.write(json.dumps(obj)+'\n');f.flush()
            self.journal.chmod(0o600)
    def dispatch(self,call_id,name,args):
        if not isinstance(call_id,str) or not call_id:raise ValueError('CallIDRequired')
        if call_id in self.seen:raise RuntimeError('DoNotReplayPhysicalAction')
        if self.used>=self.max_decisions:raise RuntimeError('PolicyDecisionBudgetExceeded')
        if self.env.terminal:raise RuntimeError('EpisodeAlreadyTerminal')
        self.seen.add(call_id);self.used+=1;self._record({'call_id':call_id,'tool':name,'status':'DISPATCHED','decision':self.used})
        rejection=None
        if not isinstance(args,dict):rejection='Tool arguments must be an object'
        elif name=='act' and (set(args)!={'instruction'} or not isinstance(args.get('instruction'),str)):rejection='OriginalInstructionRequired'
        elif name=='view' and args:rejection='ViewHasNoPrivateArguments'
        elif name=='submit_verification':
            value=args.get('value');refs=args.get('evidence_ids')
            if set(args)!={'value','container','evidence_ids'}:rejection='InvalidPublicVerificationFields'
            elif args['container'] not in ('c0','c1',None):rejection='UnknownPublicContainer'
            elif not (value is None or isinstance(value,str) and len(value)<=64 or isinstance(value,list) and len(value)<=3 and all(isinstance(v,str) and len(v)<=64 for v in value)):rejection='BoundedPublicValuesRequired'
            elif not isinstance(refs,list) or not all(isinstance(r,str) for r in refs) or len(set(refs))>8:rejection='PublicReferenceBoundary'
            elif not set(refs)<=set(self.env._frames):rejection='PublicReferenceBoundary'
            elif self.env.query is None:rejection='PublicWorkorderNotYetArrived'
        elif name not in ('act','view'):rejection='UnknownPublicTaskTool'
        if rejection:
            self._record({'call_id':call_id,'tool':name,'status':'REJECTED','decision':self.used,'error':rejection})
            return {'rejected':True,'error':rejection,'budget_charged':True}
        if name=='act':
            observation,done=self.env.step(self.infer(args['instruction']))
            result=observation
        elif name=='view':
            result=self.env.observation()
        elif name=='submit_verification':
            result=self.env.submit_verification(args['value'],args['container'],args['evidence_ids'])
        else:raise ValueError('UnknownPublicTaskTool')
        self._record({'call_id':call_id,'tool':name,'status':'RETURNED','decision':self.used,'terminated':self.env.terminal})
        return result
