"""Actual scorer boundary tests, without a simulator or model."""
import unittest
from pack_env import PackPhysicalEnv

class ScoreBoundaries(unittest.TestCase):
    def make(self,required=True,container=False,intact=True):
        e=PackPhysicalEnv.__new__(PackPhysicalEnv)
        e.terminal=False;e.success=None;e.reason=None;e._score_cache=None;e.steps=350;e.act_chunks=70;e.stage=5
        e._frames={'obs-1':{}};e.private={'required':required};e.expected_bindings={'i0':'c0','i1':'c0'};e.objects={'i0':{},'i1':{}}
        e.truth={'items':{'i0':{'mark':'red','lot':'A'},'i1':{'mark':'red','lot':'B'}}}
        e.inside=lambda i,c:bool(intact and c=='c0');e.measured_binding=lambda i:'c0' if intact else None
        e.query=({'container':'c0','field':'mark'} if container else {'item':'i0','field':'mark'}) if required else {'item':'dispatch','field':'outside_label'}
        return e
    def submit(self,e,value,container='c0',refs=None):
        e.submit_verification(value,container,['obs-1'] if refs is None else refs);return e.scorer_result()
    def test_correct_item_and_measured_binding(self):self.assertIs(self.submit(self.make(),'red')['success'],True)
    def test_correct_value_wrong_container_rejected(self):self.assertIs(self.submit(self.make(),'red','c1')['success'],False)
    def test_work_must_remain_intact(self):self.assertIs(self.submit(self.make(intact=False),'red')['success'],False)
    def test_contents_retain_duplicate_values(self):self.assertIs(self.submit(self.make(container=True),['red','red'])['success'],True)
    def test_missing_duplicate_is_wrong(self):self.assertIs(self.submit(self.make(container=True),['red'])['success'],False)
    def test_extra_value_is_wrong(self):self.assertIs(self.submit(self.make(container=True),['red','red','blue'])['success'],False)
    def test_unknown_is_valid_but_not_success(self):
        r=self.submit(self.make(),None,None);self.assertIs(r['valid'],True);self.assertIs(r['success'],False)
    def test_unseen_reference_cannot_terminate(self):
        e=self.make()
        with self.assertRaisesRegex(ValueError,'PublicReferenceBoundary'):self.submit(e,'red',refs=['future'])
        self.assertFalse(e.terminal)
    def test_control_outside_label_with_real_work(self):self.assertIs(self.submit(self.make(False),'lane_public',None)['success'],True)
    def test_control_still_requires_real_work(self):self.assertIs(self.submit(self.make(False,intact=False),'lane_public',None)['success'],False)
    def test_submission_without_workorder_rejected(self):
        e=self.make();e.query=None
        with self.assertRaisesRegex(ValueError,'NotYetArrived'):self.submit(e,'red')
        self.assertFalse(e.terminal)
    def test_final_score_immutable(self):
        e=self.make();first=self.submit(e,'blue')
        with self.assertRaisesRegex(RuntimeError,'AlreadyTerminal'):self.submit(e,'red')
        self.assertEqual(first,e.scorer_result())

if __name__=='__main__':unittest.main()
