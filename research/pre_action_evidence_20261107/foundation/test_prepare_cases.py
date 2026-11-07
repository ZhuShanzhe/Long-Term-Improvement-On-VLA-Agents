import copy
import json
from pathlib import Path
import unittest
from prepare_cases import prepare

ROOT=Path(__file__).resolve().parent

class OfflinePlanTests(unittest.TestCase):
    def setUp(self):
        self.panel=json.loads((ROOT.parent/'design/task_panel.proposed.json').read_text(encoding='utf-8'))
    def profiles(self,benchmark,family='CORE2x2'):
        return json.loads((ROOT/'configs'/f'{benchmark}-{family}.json').read_text(encoding='utf-8'))
    def test_robomme_actual_schema_count_and_seed_not_invented(self):
        profiles=self.profiles('RoboMME'); before=copy.deepcopy(profiles)
        result=prepare(self.panel,profiles,'RoboMME','development','core2x2','fixture-plan')
        self.assertEqual(result['block_count'],60)
        self.assertEqual(result['case_count'],240)
        self.assertTrue(all(c['seed'] is None and c['dataset']=='val' for c in result['cases']))
        self.assertEqual(profiles,before)
        self.assertEqual(result,prepare(self.panel,profiles,'RoboMME','development','core2x2','fixture-plan'))
    def test_rma_and_ladder_identity_and_main_family(self):
        rma=prepare(self.panel,self.profiles('RoboMemArena'),'RoboMemArena','development','core2x2','rma-plan')
        self.assertEqual(rma['block_count'],25)
        self.assertEqual(rma['cases'][0]['launcher_arguments'],{'task_id':4,'seed':0})
        ladder=prepare(self.panel,self.profiles('LADDER','MAIN_COMPARISONS'),'LADDER','development','main','ladder-plan')
        self.assertEqual(ladder['case_count'],8*2*6)
        for offset in range(0,len(ladder['cases']),6):
            block=ladder['cases'][offset:offset+6]
            self.assertEqual(len({x['block_id'] for x in block}),1)
            self.assertEqual(len({x['noncontext_fingerprint'] for x in block}),1)
        self.assertEqual(len({c['run_id'] for c in ladder['cases']}),len(ladder['cases']))
        self.assertTrue(all(c['native'] is None and not c['execution_enabled'] and 'REQUIRES_REVIEW' in c['seen_status'] for c in ladder['cases']))
    def test_pending_routes_and_wrong_profiles_rejected(self):
        for route in ('LIBERO-PRO','RoboCasa'):
            with self.assertRaisesRegex(ValueError,'binding pending'):
                prepare(self.panel,self.profiles(route),route,'development','core2x2','pending-plan')
        with self.assertRaises(ValueError): prepare(self.panel,self.profiles('LADDER'),'RoboMME','development','core2x2','wrong-route')
    def test_plan_namespace_makes_independent_run_ids(self):
        a=prepare(self.panel,self.profiles('RoboMemArena'),'RoboMemArena','heldout_same_task','core2x2','plan-a')
        b=prepare(self.panel,self.profiles('RoboMemArena'),'RoboMemArena','heldout_same_task','core2x2','plan-b')
        self.assertTrue({c['run_id'] for c in a['cases']}.isdisjoint({c['run_id'] for c in b['cases']}))
        self.assertEqual([c['arm'] for c in a['cases']],[c['arm'] for c in b['cases']])

if __name__=='__main__': unittest.main(verbosity=2)
