"""Non-strategic public-tool boundary; executors are injected, never imported here."""
from evidence_foundation import EvidenceLedger, encoded

class PublicBridge:
    def __init__(self, ledger: EvidenceLedger, original_executor, public_projector, cap=None, *, original_charge=None, fixture_mode=False):
        self.ledger, self.executor, self.projector = ledger, original_executor, public_projector
        self.cap, self.used = cap, 0
        self.fixture_mode = fixture_mode
        # Ledger construction already verified its complete hash chain. A proposal
        # is a durable dispatch intent, including attempts that raised before return.
        # Restart must never turn an uncertain physical result into permission to replay.
        self.dispatched = {e['body']['call_id'] for e in ledger.events if e['kind'] == 'proposal'}
        if original_charge is None and not fixture_mode:
            raise ValueError('Production requires the original shared budget charge callback')
        if original_charge is None and (type(cap) is not int or cap < 1):
            raise ValueError('Fixture local counter requires an explicit positive cap')
        self.original_charge = original_charge

    def _charge(self, tool):
        if self.original_charge is not None:
            # One authoritative original counter, not an additional memory budget.
            # This callback must raise when the ORIGINAL shared ledger is exhausted.
            self.original_charge(tool)
        elif self.used >= self.cap: raise RuntimeError('OriginalDecisionCapReached')
        self.used += 1

    def observe_original(self, returned):
        # Same projection used for original current observation and evidence ingress.
        # Adapter must whitelist public fields; no env.info forwarding.
        return self.ledger.observe(self.projector(returned))

    def memory_query(self, evidence_ids, at_seq=None):
        self._charge('memory_query')
        rows = self.ledger.read(evidence_ids, at_seq)
        while rows and len(encoded({'rows': rows, 'truncated': True})) > 2048:
            rows.pop()
        return {'rows': rows, 'truncated': len(rows) != len(evidence_ids)}

    def execute_original_proposal(self, call_id, original_arguments, *, original_tool_name=None):
        if call_id in self.dispatched: raise RuntimeError('PhysicalReplayForbidden')
        if original_tool_name is None:
            if not self.fixture_mode: raise ValueError('Production requires original host tool name')
            original_tool_name = 'act'
        if not isinstance(original_tool_name, str) or not original_tool_name or len(original_tool_name)>128:
            raise ValueError('Invalid original host tool name')
        self._charge(original_tool_name)
        # Only an original host-accepted complete proposal enters this method.
        # No generation, parsing shortcuts, repair/retry, interrupt or rescoring here.
        self.ledger._append('proposal', {'call_id': call_id, 'original_tool_name': original_tool_name, 'original_arguments': original_arguments})
        self.dispatched.add(call_id)  # mark before call; exceptions never replay
        returned = self.executor(original_arguments)
        evidence_id = self.observe_original(returned)
        self.ledger._append('action_return', {'call_id': call_id, 'public_evidence_id': evidence_id})
        return returned
