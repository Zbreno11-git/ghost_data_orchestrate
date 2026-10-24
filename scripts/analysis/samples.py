import csv, json, sys, collections
D=sys.argv[1]
rows=list(csv.DictReader(open(D+'/sample_output.csv')))
reqs={r['case_id']:r for r in csv.DictReader(open(D+'/sample_deletion_requests.csv'))}
tgt=list(csv.DictReader(open(D+'/deletion_requests.csv')))
print('target ids', tgt[0]['case_id'], '...', sorted(r['case_id'] for r in tgt)[:3], sorted(r['case_id'] for r in tgt)[-3:])
print('overlap sample/target ids', len(set(reqs)&{r['case_id'] for r in tgt}))
print('overlap emails', len({r['email'] for r in reqs.values()}&{r['email'] for r in tgt}))
print('status', collections.Counter(r['deletion_status'] for r in rows))
print('reported vs actual', collections.Counter((reqs[r['case_id']]['reported_status'], r['deletion_status']) for r in rows))
ops=collections.Counter(); sysres=collections.Counter(); ev=collections.Counter()
for r in rows:
    st=json.loads(r['steps_json'])
    for s in st:
        ops[(s['phase'],s['operation'])]+=1; sysres[s['system_id']]+=1
        ev[s['evidence_id'].split('_')[0] if s['evidence_id'] else '""']+=1
print(ops); print(sysres); print(ev)
print('target reported_status', collections.Counter(r['reported_status'] for r in tgt))
