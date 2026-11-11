"""Readiness contract for future real native scenes; fail closed today.

No fallback to the protocol environment. No success synthesized from a tool
ACK, matching object IDs, or a Python scripted trace. No environment step here.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Qualification:
    recipe_id: str
    source_lock: str
    reset_render_verified: bool
    cue_readable_before_commit: bool
    cue_access_after_commit_verified: bool
    original_image_retrieval_verified: bool
    physical_binding_observed: bool
    common_executor_completed: bool
    final_custom_scorer_once_verified: bool
    exact_budget_bound: bool

def require_native(q):
    if not q.source_lock:raise RuntimeError('NativeSourceLockMissing')
    missing=[name for name,value in vars(q).items() if isinstance(value,bool) and not value]
    if missing:raise RuntimeError('PhysicalQualificationPending:'+','.join(missing))
    return True

def proposed_action(kind,affected_items):
    """Proposal only. Host still owns the original physical act/view tools."""
    if kind not in ('pack','transfer','nest','close','handover'):raise ValueError('OperationOutsideDomain')
    return {'kind':kind,'affected_items':list(affected_items),'execute':False}

def classify_terminal(record):
    valid=record.get('valid') is True and type(record.get('success')) is bool
    return {'valid':valid,'success':record['success'] if valid else None,
            'label':('TRUE' if record['success'] else 'FALSE') if valid else 'UNKNOWN'}
