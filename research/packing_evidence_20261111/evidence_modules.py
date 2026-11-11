"""Research prototypes. Inputs are public events, never evaluator task truth.

The ledger is append-only; assertions can be superseded. A successful lower
tool ACK is not a semantic confirmation and cannot update object membership.
"""
from dataclasses import dataclass, asdict
import hashlib, json

def encoded(x):return json.dumps(x,ensure_ascii=False,separators=(',',':')).encode('utf-8')

@dataclass(frozen=True)
class Fact:
    entity: str
    field: str
    value: str
    sources: tuple
    status: str='observed_fallible'

class EvidenceLedger:
    def __init__(self):self.events=[];self.facts={};self.membership={}
    def add(self,fact,public_ids):
        if not fact.sources or len(set(fact.sources))>8:raise ValueError('ReferenceBudget')
        if not set(fact.sources)<=set(public_ids):raise ValueError('UnknownPublicReference')
        if fact.status not in ('observed_fallible','unknown'):raise ValueError('UnverifiedTruthPromotion')
        self.events.append({'kind':'observation','fact':asdict(fact)})
        self.facts[(fact.entity,fact.field)]=fact
    def transition(self,item,target,refs,confirmed=False):
        event={'kind':'transfer','item':item,'target':target,'sources':list(refs),'confirmed':bool(confirmed)}
        self.events.append(event)
        # A partial or ambiguous observation makes current membership unknown.
        self.membership[item]=target if confirmed and refs else None
    def get(self,item,field):return self.facts.get((item,field))

def precommit(public_action,required_fields,ledger,history_available,reinspection):
    """Small domain contract; it does not predict arbitrary robot physics."""
    if public_action['kind'] not in ('pack','close','handover','transfer','nest'):return {'decision':'continue','obligations':[]}
    obligations=[]
    for item in public_action.get('affected_items',[]):
        for field in required_fields:
            fact=ledger.get(item,field)
            if fact and fact.status=='observed_fallible':
                route='retain'
            elif history_available.get((item,field),False):route='retrieve'
            elif reinspection is True:route='inspect_or_explicitly_defer'
            else:route='inspect_before_commit'
            obligations.append({'entity':item,'field':field,'route':route,
                'post_action_reinspection':reinspection if reinspection in (True,False) else 'unknown'})
    return {'decision':'evidence_action' if any(x['route']!='retain' for x in obligations) else 'continue',
            'obligations':obligations}

def render_workset(facts,required_pairs,max_bytes=2048,max_refs=8,hard_coverage=True):
    """Render compact semantics separately from reversible full source chains.

    Every underlying source counts against max_refs; a pointer never launders
    excess refs. Coverage shortfalls are explicit rather than silently skipped.
    """
    facts=list(facts); wanted=list(dict.fromkeys(required_pairs)); by={(f.entity,f.field):f for f in facts}
    ordered=[by[p] for p in wanted if p in by] if hard_coverage else list(reversed(facts))
    if hard_coverage:ordered += [f for f in facts if (f.entity,f.field) not in wanted]
    card=[];refs=[];covered=[]
    for f in ordered:
        newrefs=list(dict.fromkeys(refs+list(f.sources)))
        candidate={'facts':card+[{'entity':f.entity,'field':f.field,'value':f.value,'status':f.status,'sources':list(f.sources)}],
                   'sources':newrefs}
        if len(newrefs)>max_refs or len(encoded(candidate))>max_bytes:continue
        card=candidate['facts'];refs=newrefs
        if f.status!='unknown':covered.append((f.entity,f.field))
    missing=[list(p) for p in wanted if p not in covered]
    obj={'facts':card,'sources':refs,'missing':missing}
    # Metadata is part of the active budget too. Never emit an oversized card.
    while len(encoded(obj))>max_bytes and obj['facts']:
        obj['facts'].pop();obj['sources']=list(dict.fromkeys(r for f in obj['facts'] for r in f['sources']))
        present={(f['entity'],f['field']) for f in obj['facts'] if f['status']!='unknown'}
        obj['missing']=[list(p) for p in wanted if p not in present]
    if len(encoded(obj))>max_bytes:raise ValueError('InsufficientBudgetForCoverageMetadata')
    return obj

def delivery_manifest(card,turn_id,request_id):
    return {'turn_id':turn_id,'request_id':request_id,
        'card_sha256':hashlib.sha256(encoded(card)).hexdigest(),
        'covered_pairs':[[f['entity'],f['field']] for f in card['facts'] if f['status']!='unknown'],
        'references':card['sources'],'bytes':len(encoded(card)),
        'meaning':'delivered bytes, not model semantic understanding or physical truth'}

def verify_delivery(manifest,actual_card,turn_id,request_id):
    return manifest==delivery_manifest(actual_card,turn_id,request_id)

class ContextHook:
    """Framework-neutral host hook; deliberately has no environment/secret API."""
    def __init__(self,config):self.config=config;self.ledger=EvidenceLedger();self.public_ids=set()
    def on_observation(self,event):
        self.public_ids.add(event['id'])
        for f in event.get('facts',[]):self.ledger.add(Fact(f['entity'],f['field'],f['value'],(event['id'],)),self.public_ids)
    def before_commit(self,action,required_fields,history,reinspection):
        if not self.config.get('gate',False):return {'decision':'continue','obligations':[]}
        return precommit(action,required_fields,self.ledger,history,reinspection)
    def for_request(self,required,turn_id,request_id):
        facts=list(self.ledger.facts.values())
        if self.config.get('strict_revision',False):
            facts=[f for f in facts if not (f.field=='container' and f.entity in self.ledger.membership and self.ledger.membership[f.entity] is None)]
        card=render_workset(facts,required,hard_coverage=self.config.get('coverage',False))
        return card,delivery_manifest(card,turn_id,request_id)
    def on_transfer(self,event):
        refs=event.get('evidence_ids',[])
        if not set(refs)<=self.public_ids:raise ValueError('UnknownPublicReference')
        self.ledger.transition(event['item'],event['target'],refs,event.get('semantic_confirmation',False))
