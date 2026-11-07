"""Same legacy memory input shapes; deterministic no-SQL public evidence seam.

Does not install into live runtime. Bind a new snapshot through its original host
tool dispatcher and one authoritative original charge callback.
"""
import copy
import json
from evidence_foundation import encoded, exact

def tool_specs():
    return [
        {'name': 'memory_query', 'description': 'Read bounded public episode observations and explicitly fallible claims. SQL unsupported in this foundation.',
         'inputSchema': {'type': 'object', 'properties': {'query': {'type': 'string'}, 'sql': {'type': 'string'},
                          'params': {'type': 'array', 'items': {'type': ['string', 'number', 'boolean', 'null']}}},
                         'required': ['query', 'sql', 'params'], 'additionalProperties': False}},
        {'name': 'memory_write', 'description': 'Record a fallible claim citing original public observation IDs; never verifies truth or task completion.',
         'inputSchema': {'type': 'object', 'properties': {'text': {'type': 'string'}, 'entity': {'type': 'string'},
                         'attribute': {'type': 'string'}, 'value': {'type': 'string'},
                         'evidence_ids': {'type': 'array', 'items': {'type': 'string'}, 'maxItems': 8},
                         'supersedes': {'type': 'array', 'items': {'type': 'string'}, 'maxItems': 8}},
                         'required': ['text', 'entity', 'attribute', 'value', 'evidence_ids', 'supersedes'], 'additionalProperties': False}}
    ]

class MemoryToolFacade:
    def __init__(self, bridge, *, tool_schema_ref, enabled=True):
        reference = {x['name']: x['inputSchema'] for x in tool_schema_ref}
        expected = {x['name']: x['inputSchema'] for x in tool_specs()}
        if reference != expected:
            raise ValueError('Original memory input schema mismatch; no silent tool migration')
        self.bridge, self.ledger, self.enabled = bridge, bridge.ledger, enabled
        self.reads = self.writes = self.output_bytes = 0

    def begin_decision(self):
        # Host calls once at ORIGINAL policy decision boundary, never during a retry.
        self.reads = self.writes = self.output_bytes = 0

    def _deliver(self, result):
        payload = encoded(result)
        if len(payload) > 2048 or self.output_bytes+len(payload) > 4096:
            raise RuntimeError('OriginalContextReadoutBoundExceeded')
        self.output_bytes += len(payload)
        return [{'type': 'inputText', 'text': payload.decode('utf-8')}]

    def call(self, name, args):
        if name not in ('memory_query', 'memory_write'): raise ValueError('Unknown memory tool')
        # Even failed schema/SQL requests consume the same original tool budget.
        self.bridge._charge(name)
        if name == 'memory_query':
            exact(args, ('query', 'sql', 'params'))
            if not isinstance(args['query'], str) or not isinstance(args['sql'], str) or not isinstance(args['params'], list):
                raise ValueError('Original query input types required')
            self.reads += 1
            if self.reads > 4: raise RuntimeError('OriginalContextReadCallBoundExceeded')
            if args['sql'].strip() or args['params']:
                raise ValueError('SQL_UNSUPPORTED: no SQL execution, filesystem or expression fallback')
            if len(args['query'].encode('utf-8')) > 2048: raise ValueError('Query too large')
            if not self.enabled:
                return self._deliver({'status': 'external_memory_disabled_for_native_baseline', 'records': []})
            words = args['query'].casefold().split()
            ids = [e['id'] for e in reversed(self.ledger.events) if e['kind'] in ('observation', 'claim')
                   and (not words or any(w in encoded(e).decode('utf-8').casefold() for w in words))][:64]
            rows = self.ledger.read(ids)
            result = {'rows': rows, 'truncated': False, 'claims_are_not_verified_facts': True}
            room = min(2048, 4096-self.output_bytes)
            while rows and len(encoded(result)) > room:
                rows.pop(); result['truncated'] = True
            return self._deliver(result)
        exact(args, ('text','entity','attribute','value','evidence_ids','supersedes'))
        self.writes += 1
        if self.writes > 1: raise RuntimeError('OriginalContextWriteCallBoundExceeded')
        for field in ('text','entity','attribute','value'):
            if not isinstance(args[field], str) or len(args[field].encode('utf-8')) > 2048: raise ValueError('Original belief field bound/type')
        for field in ('evidence_ids', 'supersedes'):
            refs = args[field]
            if not isinstance(refs,list) or len(refs)>8 or any(not isinstance(x,str) for x in refs) or len(refs)!=len(set(refs)):
                raise ValueError('Original reference list bound/type')
        if not self.enabled: return self._deliver({'status':'external_memory_disabled_for_native_baseline','accepted':False})
        if not args['evidence_ids']: raise ValueError('Original public observation evidence required')
        lookup = {e['id']:e for e in self.ledger.events}
        if any(x not in lookup or lookup[x]['kind']!='observation' for x in args['evidence_ids']):
            raise ValueError('Evidence must cite original public observations, never claims as facts')
        if any(x not in lookup or lookup[x]['kind']!='claim' or lookup[x]['body']['scope']!='current_state' for x in args['supersedes']):
            raise ValueError('Only fallible current-state claims can be superseded')
        event = self.ledger.claim({'entity': args['entity'], 'predicate':args['attribute'],
                                  'value': {'text':args['text'],'value':args['value']}, 'evidence_ids':copy.deepcopy(args['evidence_ids']),
                                  'scope':'current_state', 'confidence':None})
        for previous in args['supersedes']:
            self.ledger.invalidate(previous, 'superseded_by_'+event, copy.deepcopy(args['evidence_ids']))
        return self._deliver({'accepted':True,'event_id':event,'semantic_truth_verified':False})
