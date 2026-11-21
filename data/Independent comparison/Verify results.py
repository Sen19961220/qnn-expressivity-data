"""Check the deposited independent comparison (Python 3.10+).

Run with --raw to inspect all 153,600 endpoint records and --bootstrap to
recalculate the archived confidence interval (requires NumPy).
"""
from pathlib import Path
import argparse
import csv
import gzip
import hashlib
import json
from collections import Counter

ROOT = Path(__file__).resolve().parent

def load_csv(name):
    path=ROOT/name
    opener=gzip.open if name.endswith('.gz') else open
    with opener(path,'rt',encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f))

def run(check_raw=False, check_bootstrap=False):
    metadata=json.loads((ROOT/'Experiment metadata.json').read_text())
    calibration=load_csv('Calibration targets.csv')
    confirmation=load_csv('Confirmation targets.csv')
    cal_targets={int(r['target_index']) for r in calibration}
    conf_targets={int(r['target_index']) for r in confirmation}
    assert len(cal_targets)==1024 and len(conf_targets)==4096
    assert not cal_targets.intersection(conf_targets)
    for table in [calibration,confirmation]:
        for row in table:
            target=int(row['target_index'])
            assert row['canonical_bits']==format(target,'016b')
            assert int(row['complement_target_index'])==65535-target
            assert int(row['pair_representative'])==min(target,65535-target)

    paired=load_csv('Paired target results.csv.gz')
    bykey={(int(r['target_index']),int(r['pair_seed_id'])):
           {'map1':int(r['map1_exact']),'signsin2':int(r['signsin2_exact'])} for r in paired}
    assert len(bykey)==len(paired)==40960
    seeds=metadata['stages']['confirmation']['seeds']
    assert set(bykey)=={(t,s) for t in conf_targets for s in seeds}
    for row in paired:
        assert int(row['difference'])==int(row['map1_exact'])-int(row['signsin2_exact'])
    counts={branch:sum(row[branch] for row in bykey.values()) for branch in ['map1','signsin2']}
    assert counts=={'map1':26353,'signsin2':19481}
    gap=(counts['map1']-counts['signsin2'])/40960
    assert gap==metadata['recorded_results']['paired_difference_fraction']
    for row in load_csv('Seed results.csv'):
        seed=int(row['pair_seed_id'])
        q=sum(bykey[(t,seed)]['map1'] for t in conf_targets)/4096
        c=sum(bykey[(t,seed)]['signsin2'] for t in conf_targets)/4096
        assert q==float(row['map1_rate']) and c==float(row['signsin2_rate'])
        assert q-c==float(row['paired_difference_fraction'])

    calibration_scores={(r['branch_id'],int(r['k'])):r for r in load_csv('Calibration scores.csv')}
    assert len(calibration_scores)==14
    for branch in ['map1','signsin2']:
        scores=[r for (b,k),r in calibration_scores.items() if b==branch]
        chosen=max(scores,key=lambda r:json.loads(r['selection_key']))
        assert chosen['epsilon_hex']==metadata['selected_candidates'][branch]['epsilon_hex']
        assert int(chosen['k'])==0

    raw_count=0
    if check_raw:
        cal_counts=Counter(); cal_coverage=set(); conf_coverage=set()
        for stage in ['Calibration','Confirmation']:
            for name,branch in [('QNN','map1'),('CNN','signsin2')]:
                with gzip.open(ROOT/f'{stage} {name} runs.jsonl.gz','rt',encoding='utf-8') as f:
                    for line in f:
                        row=json.loads(line); raw_count+=1
                        assert row['branch_id']==branch and row['stage']==stage.lower()
                        target=row['target_index']; seed=row['pair_seed_id']
                        bits=format(target,'016b')
                        errors=sum(a!=b for a,b in zip(bits,row['best_canonical_prediction']))
                        final_errors=sum(a!=b for a,b in zip(bits,row['final_canonical_prediction']))
                        assert errors==row['best_errors']
                        assert row['best_loss']==errors/16 and row['final_loss']==final_errors/16
                        assert row['exact_fit']==(errors==0)
                        assert row['attempted_steps']==row['accepted_steps']+row['rejected_steps']
                        assert row['attempted_steps']==row['candidate_evaluations']
                        assert row['objective_evaluations']==row['attempted_steps']+1
                        if stage=='Confirmation':
                            key=(branch,target,seed)
                            assert key not in conf_coverage
                            conf_coverage.add(key)
                            assert bykey[(target,seed)][branch]==int(row['exact_fit'])
                            assert row['epsilon_hex']==metadata['selected_candidates'][branch]['epsilon_hex']
                        else:
                            key=(branch,row['k'],target,seed)
                            assert key not in cal_coverage
                            cal_coverage.add(key)
                            assert target in cal_targets
                            cal_counts[(branch,row['k'],seed)]+=int(row['exact_fit'])
        assert len(cal_coverage)==71680 and len(conf_coverage)==81920
        assert raw_count==153600
        for key,score in calibration_scores.items():
            branch,k=key
            actual=[cal_counts[(branch,k,s)] for s in metadata['stages']['calibration']['seeds']]
            assert actual==json.loads(score['seed_counts'])
            assert sum(actual)==int(score['total_success'])

    interval=None
    if check_bootstrap:
        import numpy as np
        reps=sorted({min(t,65535-t) for t in conf_targets})
        matrix=np.array([[
            sum(bykey[(t,s)]['map1']-bykey[(t,s)]['signsin2']
                for t in (rep,65535-rep))/2 for s in seeds] for rep in reps])
        boot=metadata['bootstrap']; repeats=boot['replicates']
        rng=np.random.default_rng(boot['rng_seed'])
        draws=np.empty(repeats)
        # Batch size and the seed/pair draw order reproduce the archived RNG stream.
        n,s=matrix.shape
        for start in range(0,repeats,500):
            stop=min(start+500,repeats); b=stop-start
            si=rng.integers(0,s,size=(b,s))
            pi=rng.integers(0,n,size=(b,n))
            means=matrix[:,si].mean(axis=2).T
            draws[start:stop]=np.take_along_axis(means,pi,axis=1).mean(axis=1)
        interval=[float(np.quantile(draws,.025)),float(np.quantile(draws,.975))]
        assert interval==metadata['recorded_results']['paired_difference_95ci_fraction']

    result={'result':'PASS','QNN exact fits':counts['map1'],
            'CNN exact fits':counts['signsin2'],'paired targets and seeds':40960,
            'mean difference fraction':gap,'raw records checked':raw_count,
            'bootstrap interval fraction':interval}
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--raw',action='store_true')
    parser.add_argument('--bootstrap',action='store_true')
    args=parser.parse_args()
    run(args.raw,args.bootstrap)
