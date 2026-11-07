import copy
import json
from pathlib import Path
import tempfile
import unittest
from evidence_foundation import EvidenceLedger, aggregate, prepare_binding, validate_six, validate_panel, BOUND_COMPONENTS
from paired_ci import paired_ci
from build_profiles import build
from public_bridge import PublicBridge
from bind_deployed_readonly import bind
from memory_tool_facade import MemoryToolFacade

class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)/'events.jsonl'
        self.ledger = EvidenceLedger(self.path, 'episodeA', ['frame1', 'frame2'])
    def tearDown(self): self.tmp.cleanup()
    def observation(self, frame='frame1'):
        return self.ledger.observe({'source': 'original_rgb', 'asset_ids': [frame], 'text': '', 'tool_call_id': 'view1'})
    def test_chain_tamper_rejected(self):
        self.observation()
        EvidenceLedger(self.path, 'episodeA', ['frame1'])
        self.path.write_text(self.path.read_text().replace('frame1', 'frame2'))
        with self.assertRaises(ValueError): EvidenceLedger(self.path, 'episodeA')
    def test_unknown_expired_and_historical_fact_not_rewritten(self):
        obs = self.observation()
        claim = self.ledger.claim({'entity': 'boxA', 'predicate': 'contains', 'value': 'part1', 'evidence_ids': [obs], 'scope': 'current_state', 'confidence': .7})
        obs2 = self.observation('frame2')
        self.ledger.invalidate(claim, 'binding_may_have_changed', [obs2])
        self.assertEqual(self.ledger.read([claim])[0]['status'], 'expired')
        self.assertEqual(self.ledger.read([claim], 1)[0]['status'], 'recorded_not_verified')
        self.assertEqual(self.ledger.read(['e99999999'])[0]['status'], 'unknown')
        self.assertEqual(self.ledger.events[1]['body']['value'], 'part1')
    def test_future_unregistered_or_privileged_ingress_rejected(self):
        for source in ('native_score', 'gt_pose', 'oracle'):
            with self.assertRaises(ValueError):
                self.ledger.observe({'source': source, 'asset_ids': [], 'text': '', 'tool_call_id': None})
        with self.assertRaises(ValueError): self.observation('../../secret')
        with self.assertRaises(ValueError):
            self.ledger.claim({'entity': 'x', 'predicate': 'y', 'value': 'z', 'evidence_ids': ['e00000000'], 'scope': 'current_state', 'confidence': .5})
    def test_policy_cannot_inject_time_or_extra_info(self):
        with self.assertRaises(ValueError):
            self.ledger.observe({'source': 'original_rgb', 'asset_ids': [], 'text': '', 'tool_call_id': None, 'native_state': {}})
    def test_historical_event_cannot_expire(self):
        o = self.observation()
        c = self.ledger.claim({'entity': 'x', 'predicate': 'was_seen', 'value': True, 'evidence_ids': [o], 'scope': 'historical_event', 'confidence': .5})
        with self.assertRaises(ValueError): self.ledger.invalidate(c, 'stale', [o])

class ConfigurationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): build()
    def profiles(self, name='RoboMemArena'):
        return json.loads((Path(__file__).parent/'configs'/f'{name}-six-arms.json').read_text(encoding='utf-8'))
    def test_five_routes_six_arm_equal_controls(self):
        for name in ('LADDER', 'RoboMME', 'RoboMemArena', 'LIBERO-PRO', 'RoboCasa'):
            self.assertTrue(validate_six(self.profiles(name))['noncontext_equal'])
        self.assertNotEqual(self.profiles('LADDER')[0]['common']['action_contract'], self.profiles()[0]['common']['action_contract'])
    def test_changed_budget_or_action_rejected(self):
        for key, value in [('decision_cap', 151), ('action_contract', 'DROID8'), ('native_steps', 999999)]:
            p = self.profiles(); p[5]['common'][key] = value
            with self.assertRaises(ValueError): validate_six(p)
    def test_context_cannot_override_model_or_tool(self):
        p = self.profiles(); p[0]['context']['model'] = 'different'
        with self.assertRaises(ValueError): validate_six(p)
    def test_unresolved_binding_cannot_activate(self):
        with self.assertRaises(ValueError): prepare_binding(self.profiles()[0], {'benchmark': 'RoboMemArena', 'hashes': {}})
    def test_core_has_identical_memory_and_five_routes(self):
        for benchmark in ('LADDER','RoboMME','RoboMemArena','LIBERO-PRO','RoboCasa'):
            p = json.loads((Path(__file__).parent/'configs'/f'{benchmark}-CORE2x2.json').read_text())
            self.assertTrue(validate_panel(p, 'core2x2')['noncontext_equal'])
            p[3]['context']['representation'] = 'more-memory'
            with self.assertRaises(ValueError): validate_panel(p, 'core2x2')
    def test_cross_route_receipt_rejected(self):
        p = self.profiles()[0]
        hashes = {key: 'a'*64 for key in BOUND_COMPONENTS}
        p['common']['required_bound_hashes'] = hashes
        with self.assertRaises(ValueError): prepare_binding(p, {'benchmark': 'RoboMME', 'hashes': hashes})
        result = prepare_binding(p, {'benchmark': 'RoboMemArena', 'hashes': hashes})
        self.assertFalse(result['execution_enabled'])

class MetricsTests(unittest.TestCase):
    def test_invalid_false_unknown_and_integration_excluded(self):
        rows = [{'case_id': 'a', 'valid': True, 'native': True, 'final_reported_usage': {'input': 10}},
                {'case_id': 'b', 'valid': False, 'native': False},
                {'case_id': 'c', 'valid': True, 'native': False},
                {'case_id': 'd', 'valid': True, 'native': True, 'integration_only': True}]
        r = aggregate(rows)
        self.assertEqual((r['native_true'], r['native_false'], r['unknown'], r['integration_only']), (1,1,1,1))
        self.assertEqual(r['valid_native_rate'], .5)
        self.assertEqual(r['valid_coverage'], 2/3)
        self.assertEqual(r['final_reported_usage']['input'], 10)
    def test_duplicate_cases_and_nonboolean_native(self):
        with self.assertRaises(ValueError): aggregate([{'case_id': 'a'}, {'case_id': 'a'}])
        self.assertEqual(aggregate([{'case_id': 'a', 'valid': True, 'native': 1}])['unknown'], 1)
    def test_event_denominators(self):
        r = aggregate([{'case_id': 'a', 'offline_labels': [
            {'kind': 'eligible_loss', 'preserved_before_loss': True}, {'kind': 'eligible_loss', 'preserved_before_loss': False},
            {'kind': 'future_decision', 'correct': False, 'stale_evidence_used': True}, {'kind': 'recovery', 'steps': 7}]}])
        self.assertEqual(r['pre_loss_preservation_rate'], .5)
        self.assertEqual(r['future_decision_accuracy'], 0)
        self.assertEqual(r['recovery_steps'], 7)

class BridgeAndBindingTests(unittest.TestCase):
    def test_original_fixture_closed_loop_and_no_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls = []
            ledger = EvidenceLedger(Path(tmp)/'ledger.jsonl', 'fixture', ['before', 'after'])
            def project(obs):
                return {'source': 'original_rgb', 'asset_ids': [obs['public_frame_id']], 'text': '', 'tool_call_id': obs['call_id']}
            def executor(arguments):
                calls.append(arguments)
                return {'public_frame_id': 'after', 'call_id': 'original-act1', 'private_native_state': 'NOT_PROJECTED'}
            bridge = PublicBridge(ledger, executor, project, 2, fixture_mode=True)
            evidence = bridge.observe_original({'public_frame_id': 'before', 'call_id': 'original-view1'})
            self.assertEqual(bridge.memory_query([evidence])['rows'][0]['status'], 'recorded_not_verified')
            bridge.execute_original_proposal('original-act1', {'instruction': 'original fixture only'})
            self.assertEqual([x['kind'] for x in ledger.events], ['observation', 'proposal', 'observation', 'action_return'])
            self.assertNotIn('private_native_state', ledger.path.read_text())
            with self.assertRaises(RuntimeError): bridge.execute_original_proposal('original-act1', {})
            self.assertEqual(len(calls), 1)
            with self.assertRaises(RuntimeError): bridge.memory_query([evidence])
    def test_readonly_existing_receipt_bind_new_namespace(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = [root/x for x in ('common.json','route.json','map.json','profiles.json')]
            objects = [{'source_hash_lock': {key: 'c'*64 for key in BOUND_COMPONENTS}},
                       {'benchmark': 'LADDER', 'case_seconds': None, 'credential_attempt_seconds': 600, 'model': 'gpt-6-astra'},
                       {key: ['source_hash_lock', key] for key in BOUND_COMPONENTS},
                       ConfigurationTests().profiles('LADDER')]
            for path, obj in zip(paths, objects): path.write_text(json.dumps(obj))
            before = [p.read_bytes() for p in paths]
            receipt = bind(*paths, root/'NEW_SNAPSHOT')
            self.assertFalse(receipt['execution_enabled'])
            self.assertEqual(before, [p.read_bytes() for p in paths])
            with self.assertRaises(FileExistsError): bind(*paths, root/'NEW_SNAPSHOT')

class PairedCITests(unittest.TestCase):
    def row(self, task, arm, value, valid=True, episode=0):
        return {'benchmark':'LADDER','task_id':task,'seed':0,'episode_id':episode,'arm':arm,'valid':valid,'native':value}
    def test_task_macro_not_event_or_episode_pseudoreplication(self):
        rows=[]
        for i in range(10): rows += [self.row('taskA','a',False,episode=i),self.row('taskA','b',True,episode=i)]
        rows += [self.row('taskB','a',True),self.row('taskB','b',False)]
        result=paired_ci(rows,'a','b',resamples=1000)
        self.assertEqual(result['complete_pair_difference'],0)
        self.assertEqual(result['task_clusters_total'],2)
        self.assertEqual(result,paired_ci(rows,'a','b',resamples=1000))
    def test_unknown_bounds_and_single_task_no_ci(self):
        result=paired_ci([self.row('taskA','a',True),self.row('taskA','b',False,valid=False)],'a','b',resamples=100)
        self.assertEqual(result['unknown_sensitivity_interval_all_pairs_task_macro'],[-1,0])
        self.assertIsNone(result['task_cluster_bootstrap_CI95'])
        self.assertEqual(result['complete_pair_coverage'],0)
    def test_duplicate_or_crossbenchmark_rejected(self):
        row=self.row('taskA','a',True)
        with self.assertRaises(ValueError): paired_ci([row,row],'a','b',resamples=100)
        other=self.row('taskB','b',True);other['benchmark']='RoboCasa'
        with self.assertRaises(ValueError): paired_ci([row,other],'a','b',resamples=100)

class OriginalMemorySeamTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = EvidenceLedger(Path(self.tmp.name)/'events.jsonl','old-schema-fixture',['rgb1'])
        self.charges=[]
        def original_charge(tool):
            if len(self.charges)>=5: raise RuntimeError('OriginalSharedLedgerExhausted')
            self.charges.append(tool)
        self.bridge=PublicBridge(self.ledger,lambda x:{'frame':'rgb1','call':'act1'},
                                 lambda x:{'source':'original_rgb','asset_ids':[x['frame']],'text':'box inspected','tool_call_id':x['call']},original_charge=original_charge)
        schema=json.loads((Path(__file__).parent/'original_memory_schema_reference.json').read_text())
        self.facade=MemoryToolFacade(self.bridge,tool_schema_ref=schema)
        self.obs=self.bridge.observe_original({'frame':'rgb1','call':'view1'})
    def tearDown(self): self.tmp.cleanup()
    def write(self, refs):
        return {'text':'fallible identification','entity':'box','attribute':'contains','value':'partA','evidence_ids':refs,'supersedes':[]}
    def test_old_schema_public_evidence_claim_query_original_charge(self):
        response=self.facade.call('memory_write',self.write([self.obs]))
        claim=json.loads(response[0]['text'])['event_id']
        result=self.facade.call('memory_query',{'query':'box','sql':'','params':[]})
        self.assertTrue(json.loads(result[0]['text'])['claims_are_not_verified_facts'])
        self.bridge.execute_original_proposal('act1',{'instruction':'unchanged'})
        self.assertEqual(self.charges,['memory_write','memory_query','act'])
        self.assertIsNone(self.ledger.events[1]['body']['confidence'])
        self.facade.begin_decision()
        with self.assertRaises(ValueError): self.facade.call('memory_write',self.write([claim]))
    def test_production_cannot_create_free_local_budget(self):
        with self.assertRaises(ValueError): PublicBridge(self.ledger,lambda x:x,lambda x:x,100)
        self.assertIsNone(self.bridge.cap)
    def test_original_shared_budget_stops_dispatch_after_memory_calls(self):
        for _ in range(5): self.bridge.memory_query([self.obs])
        with self.assertRaises(RuntimeError): self.bridge.execute_original_proposal('blocked-act',{})
        self.assertNotIn('blocked-act',self.bridge.dispatched)
        self.assertEqual(len(self.ledger.events),1)
    def test_sql_is_rejected_and_charged_not_executed(self):
        with self.assertRaises(ValueError): self.facade.call('memory_query',{'query':'','sql':'SELECT * FROM files','params':[]})
        self.assertEqual(self.charges,['memory_query'])
        self.assertEqual(len(self.ledger.events),1)
    def test_unknown_schema_and_superseding_observation_rejected(self):
        with self.assertRaises(ValueError): MemoryToolFacade(self.bridge,tool_schema_ref=[])
        values=self.write([self.obs]);values['supersedes']=[self.obs]
        with self.assertRaises(ValueError): self.facade.call('memory_write',values)
        self.assertEqual(len(self.ledger.events),1)

if __name__ == '__main__': unittest.main(verbosity=2)
