"""Offline independent annotations only; no simulator, model, scorer or network.

JSONL schema is documented in annotation_guide.md. One benchmark per call;
results separated by arm. Event rows are descriptive, not independent CI units.
"""
import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

ROUTES = ('current_view', 'historical_retrieval', 'reobserve', 'physical_recovery')
REASONS = ('none', 'not_observed', 'not_retained', 'stale_binding', 'unknown')

def mean(xs):
    return sum(xs)/len(xs) if xs else None

def boolean(value, name):
    if value is not None and type(value) is not bool:
        raise ValueError(name + ' must be boolean or null')
    return value

def number(value, name, probability=False):
    if value is None:
        return None
    if type(value) not in (float, int) or not math.isfinite(value) or value < 0 or (probability and value > 1):
        raise ValueError(name + ' must be finite nonnegative number, or probability in [0,1]')
    return value

def ratio(eligible, known, numerator):
    return {'value': numerator/known if known else None, 'numerator': numerator,
            'labeled_denominator': known, 'eligible_count': eligible,
            'annotation_coverage': known/eligible if eligible else None}

def calibration(points, bins):
    if not points:
        return {'brier': None, 'ece': None, 'labeled_pairs': 0, 'bins': []}
    table = []
    for i in range(bins):
        group = [(p,y) for p,y in points if min(int(p*bins), bins-1) == i]
        if group:
            table.append({'index': i, 'count': len(group),
                          'mean_probability': mean([p for p,y in group]),
                          'frequency': mean([int(y) for p,y in group])})
    return {'brier': mean([(p-int(y))**2 for p,y in points]),
            'ece': sum(x['count']*abs(x['mean_probability']-x['frequency']) for x in table)/len(points),
            'labeled_pairs': len(points), 'bins': table}

def summarize(rows, bins=10):
    if type(bins) is not int or bins < 1:
        raise ValueError('bins must be positive integer')
    seen, groups, benchmarks = set(), defaultdict(list), set()
    for row in rows:
        for key in ('benchmark','task_id','seed','episode_id','arm','kind'):
            if key not in row or row[key] is None:
                raise ValueError('Missing identity field: '+key)
        if row['kind'] not in ('episode','event'):
            raise ValueError('kind must be episode or event')
        if row['kind']=='event' and not isinstance(row.get('event_id'),str):
            raise ValueError('event_id must be string')
        identity = tuple(str(row[k]) for k in ('benchmark','task_id','seed','episode_id','arm','kind')) + ((row['event_id'],) if row['kind']=='event' else ())
        if identity in seen:
            raise ValueError('Duplicate episode/event identity; no cherry-picking attempts')
        seen.add(identity); benchmarks.add(row['benchmark']); groups[row['arm']].append(row)
    if len(benchmarks)!=1:
        raise ValueError('Exactly one benchmark per invocation; never pool independent profiles')
    result = {'schema':'evidence-metrics-v1','benchmark':next(iter(benchmarks)),
              'ci_tool':'../foundation/paired_ci.py',
              'event_rows_are_not_independent_samples':True,'arms':{}}
    for arm, items in sorted(groups.items()):
        eps=[r for r in items if r['kind']=='episode']; ev=[r for r in items if r['kind']=='event']
        valid=[r for r in eps if r.get('valid') is True and type(r.get('native')) is bool]
        true=sum(r['native'] for r in valid)
        counters={k:[0,0,0] for k in ('ESC','LMER','stale_binding_use','overpreservation')}
        reason_counts={k:0 for k in REASONS}
        preds={route:[] for route in ROUTES}; costs={route:[] for route in ROUTES}
        eligible_preds={route:0 for route in ROUTES}; eligible_costs={route:0 for route in ROUTES}
        independently_labeled=0
        for r in ev:
            # Unknown/unreviewed/model-self-reported annotations never become truth.
            independent=r.get('label_source') in ('blinded_public_prefix','isolated_evaluator')
            independently_labeled += independent
            labels=r.get('labels',{}) if independent else {}
            for name in ('commitment_required','critical_decision','requires_binding','stale_evidence_used','preservation_needed','preservation_action'):
                boolean(labels.get(name), name)
            if labels.get('commitment_required') is True:
                c=counters['ESC'];c[0]+=1
                evidence=labels.get('necessary_evidence')
                if not isinstance(evidence,list) or not evidence:
                    raise ValueError('Required commitment needs nonempty necessary_evidence list')
                ids=[x.get('id') for x in evidence]
                if any(not isinstance(x,str) for x in ids) or len(set(ids))!=len(ids):
                    raise ValueError('Evidence IDs must be distinct strings')
                vals=[]
                for e in evidence:
                    vals.extend(boolean(e.get(k),k) for k in ('observed','retained','binding_current'))
                # One known failure establishes insufficiency, even if others unknown.
                sufficient=False if False in vals else (True if all(v is True for v in vals) else None)
                if sufficient is not None:c[1]+=1;c[2]+=sufficient
            if labels.get('critical_decision') is True:
                c=counters['LMER'];c[0]+=1;reason=labels.get('missing_reason')
                if reason is not None and reason not in REASONS:raise ValueError('Unknown missing_reason')
                if reason in REASONS:reason_counts[reason]+=1
                if reason not in (None,'unknown'):c[1]+=1;c[2]+=(reason!='none')
            if labels.get('requires_binding') is True:
                c=counters['stale_binding_use'];c[0]+=1;v=labels.get('stale_evidence_used')
                if v is not None:c[1]+=1;c[2]+=v
            if labels.get('preservation_needed') is False:
                c=counters['overpreservation'];c[0]+=1;v=labels.get('preservation_action')
                if v is not None:c[1]+=1;c[2]+=v
            prediction=r.get('prediction',{})
            if any(route not in ROUTES for route in prediction):raise ValueError('Unknown availability route')
            route_labels=labels.get('routes',{})
            for route,p in prediction.items():
                prob=number(p.get('p_available'),'p_available',True)
                pcost=number(p.get('predicted_cost'),'predicted_cost')
                truth=route_labels.get(route,{})
                available=boolean(truth.get('available'),'available')
                acost=number(truth.get('actual_cost'),'actual_cost')
                if prob is not None:
                    eligible_preds[route]+=1
                    if available is not None:preds[route].append((prob,available))
                if pcost is not None:
                    eligible_costs[route]+=1
                    if acost is not None:costs[route].append(abs(pcost-acost))
        a={'episodes':len(eps),'valid_native_count':len(valid),'native_true_count':true,
           'native_false_count':len(valid)-true,'native_unknown_count':len(eps)-len(valid),
           'native_success_rate':true/len(valid) if valid else None,
           'native_coverage':len(valid)/len(eps) if eps else None,
           'native_missing_sensitivity_interval':[true/len(eps),(true+len(eps)-len(valid))/len(eps)] if eps else None,
           'event_count':len(ev),'independent_label_source_count':independently_labeled,
           'independent_annotation_coverage':independently_labeled/len(ev) if ev else None,
           'mechanism':{k:ratio(*v) for k,v in counters.items()},
           'LMER_reason_counts':reason_counts,'availability':{}}
        for route in ROUTES:
            d=calibration(preds[route],bins);n=eligible_preds[route];m=eligible_costs[route]
            d.update({'prediction_count':n,'annotation_coverage':len(preds[route])/n if n else None,
                      'cost_mae':mean(costs[route]),'cost_labeled_pairs':len(costs[route]),
                      'cost_prediction_count':m,'cost_annotation_coverage':len(costs[route])/m if m else None})
            a['availability'][route]=d
        result['arms'][arm]=a
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('jsonl',type=Path);p.add_argument('--bins',type=int,default=10);p.add_argument('--output',type=Path)
    args=p.parse_args(); rows=[json.loads(line) for line in args.jsonl.read_text(encoding='utf-8').splitlines() if line.strip()]
    text=json.dumps(summarize(rows,args.bins),ensure_ascii=False,indent=2,allow_nan=False)
    if args.output:args.output.write_text(text+'\n',encoding='utf-8')
    else:print(text)

if __name__=='__main__':main()
