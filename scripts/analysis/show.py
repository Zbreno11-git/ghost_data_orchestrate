import csv, json, sys
D=sys.argv[1]; ids=sys.argv[2].split(',')
reqs={r['case_id']:r for r in csv.DictReader(open(D+'/sample_deletion_requests.csv'))}
for r in csv.DictReader(open(D+'/sample_output.csv')):
    if r['case_id'] in ids:
        q=reqs[r['case_id']]
        print('##',r['case_id'],r['deletion_status'],q['email'],q['reported_status'],'req',q['requested_at'],'audit',q['audit_at'])
        print('   text:',q['request_text'][:160])
        for s in json.loads(r['steps_json']):
            print('   ',s['step_no'],s['phase'][:5],s['system_id'],s['resource_id'],s['operation'],s['state'],s['evidence_id'])
