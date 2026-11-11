"""Public tool-boundary tests, without private task constructors."""
import unittest
import numpy as np
from task_port import PackToolPort

class PortTests(unittest.TestCase):
    def make(self):
        class Env:
            terminal=False;_frames={};query={'item':'dispatch','field':'outside_label'}
            def step(self,a):self.actions=getattr(self,'actions',0)+1;return {'terminated':False},False
            def observation(self):return {'RGB':'current'}
            def submit_verification(self,*args):self.terminal=True;return {'submitted':True,'terminated':True}
        e=Env();return PackToolPort(e,lambda _:np.zeros((5,7))),e
    def test_no_action_replay(self):
        p,e=self.make();p.dispatch('a','act',{'instruction':'public goal'})
        with self.assertRaisesRegex(RuntimeError,'DoNotReplay'):p.dispatch('a','act',{'instruction':'public goal'})
        self.assertEqual(e.actions,1)
    def test_no_hidden_score_tool(self):
        p,_=self.make();self.assertEqual(p.dispatch('a','check_success',{})['error'],'UnknownPublicTaskTool')
    def test_original_decision_budget(self):
        p,_=self.make();p.used=600
        with self.assertRaisesRegex(RuntimeError,'BudgetExceeded'):p.dispatch('a','view',{})
    def test_submission_response_has_no_oracle(self):
        p,_=self.make();r=p.dispatch('a','submit_verification',{'value':'unknown','container':None,'evidence_ids':[]})
        self.assertEqual(set(r),{'submitted','terminated'})
    def test_error_attempt_charges_budget(self):
        p,_=self.make();self.assertTrue(p.dispatch('a','act',{'GT_target':'private'})['rejected']);self.assertEqual(p.used,1)
    def test_bad_reference_does_not_close_episode(self):
        p,e=self.make();r=p.dispatch('a','submit_verification',{'value':['A'],'container':'c0','evidence_ids':['future']})
        self.assertTrue(r['rejected']);self.assertFalse(e.terminal)
    def test_ordinary_error_can_recover(self):
        p,e=self.make();p.dispatch('bad','act',{});self.assertNotIn('rejected',p.dispatch('good','act',{'instruction':'public goal'}));self.assertEqual(e.actions,1)

if __name__=='__main__':unittest.main()
