import copy
import json
import unittest
from pathlib import Path
from metrics import summarize

class MetricsTests(unittest.TestCase):
    def setUp(self):
        self.rows=[json.loads(x) for x in Path(__file__).with_name('fixture.jsonl').read_text().splitlines()]
    def test_valid_false_is_unknown_and_no_cross_arm_pool(self):
        r=summarize(self.rows)['arms']
        self.assertEqual(r['text']['native_unknown_count'],1)
        self.assertIsNone(r['text']['native_success_rate'])
        self.assertEqual(r['contract']['native_success_rate'],1)
    def test_independent_evidence_and_cost_calibration(self):
        r=summarize(self.rows)['arms']
        self.assertEqual(r['text']['mechanism']['ESC']['value'],0)
        self.assertEqual(r['contract']['mechanism']['ESC']['value'],1)
        self.assertEqual(r['text']['mechanism']['LMER']['value'],1)
        self.assertAlmostEqual(r['text']['availability']['historical_retrieval']['brier'],.64)
        self.assertEqual(r['text']['availability']['historical_retrieval']['cost_mae'],2)
        self.assertEqual(r['contract']['mechanism']['overpreservation']['value'],1)
    def test_unknown_labels_never_become_false(self):
        r=summarize(self.rows)['arms']['contract']
        self.assertIsNone(r['mechanism']['LMER']['value'])
        self.assertEqual(r['mechanism']['LMER']['annotation_coverage'],0)
        self.assertIsNone(r['availability']['physical_recovery']['brier'])
        self.assertIsNone(r['availability']['physical_recovery']['cost_mae'])
    def test_partial_evidence_unknown_and_known_failure(self):
        rows=copy.deepcopy(self.rows);e=rows[1]['labels']['necessary_evidence'][0]
        e['retained']=None
        self.assertIsNone(summarize(rows)['arms']['text']['mechanism']['ESC']['value'])
        e['observed']=False
        self.assertEqual(summarize(rows)['arms']['text']['mechanism']['ESC']['value'],0)
    def test_reject_duplicate_and_cross_benchmark(self):
        with self.assertRaises(ValueError):summarize(self.rows+[self.rows[0]])
        row=copy.deepcopy(self.rows[0]);row['benchmark']='OTHER'
        with self.assertRaises(ValueError):summarize(self.rows+[row])
    def test_self_report_not_truth_and_invalid_probability_rejected(self):
        rows=copy.deepcopy(self.rows);rows[1]['label_source']='model_self_report'
        self.assertIsNone(summarize(rows)['arms']['text']['mechanism']['ESC']['value'])
        rows[1]['prediction']['historical_retrieval']['p_available']=1.1
        with self.assertRaises(ValueError):summarize(rows)
    def test_nonboolean_label_and_empty_required_evidence_rejected(self):
        rows=copy.deepcopy(self.rows);rows[1]['labels']['commitment_required']=1
        with self.assertRaises(ValueError):summarize(rows)
        rows=copy.deepcopy(self.rows);rows[1]['labels']['necessary_evidence']=[]
        with self.assertRaises(ValueError):summarize(rows)

if __name__=='__main__':unittest.main()
