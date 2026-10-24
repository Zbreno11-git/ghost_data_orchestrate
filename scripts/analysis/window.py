import csv, json, sys
D=sys.argv[1]
act=list(csv.DictReader(open(D+'/system_activity.csv')))
reqs={r['case_id']:r for r in csv.DictReader(open(D+'/sample_deletion_requests.csv'))}
for r in csv.DictReader(open(D+'/sample_output.csv')):
    q=reqs[r['case_id']]
    exp={s['resource_id'] for s in json.loads(r['steps_json'])}
    acc=[s['resource_id'] for s in json.loads(r['steps_json']) if s['system_id']=='account_service'][0]
    w=[a for a in act if a['source_system']=='deletion_worker' and q['requested_at']<=a['event_time']<=q['reported_at']]
    wacc=[a['resource_id'] for a in w if a['target_system']=='account_service']
    # any activity for expected account at all
    anyacc=[(a['event_time'],a['reported_result']) for a in act if a['resource_id']==acc]
    print(r['case_id'], 'req..rep', q['requested_at'][5:16], q['reported_at'][5:16], '| worker acts in window', len(w), 'acct cands', len(wacc), 'expected acct in cands', acc in wacc, '| acct activity', anyacc[:3])
