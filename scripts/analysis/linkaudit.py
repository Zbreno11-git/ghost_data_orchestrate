import csv, json, re, sys, os, collections
D=sys.argv[1]
ids=list(csv.DictReader(open(D+'/user_identities.csv')))
aud=list(csv.DictReader(open(D+'/user_audit_log.csv')))
by_email={r['email'].lower():r['user_id'] for r in ids}
for a in aud:
    if a['field_name']=='email': by_email.setdefault(a['old_value'].lower(),a['user_id'])
def subj(uid):
    s={uid}
    for r in ids:
        if r['user_id']==uid: s|={r['email'].lower(),r['phone'],r['email_hash'],r['name']}
    for a in aud:
        if a['user_id']==uid: s|={a['old_value'].lower() if '@' in a['old_value'] else a['old_value'], a['new_value'].lower() if '@' in a['new_value'] else a['new_value']}
    return {x for x in s if x}
# units: list of (source_id, text)
units=[]
man={r['file_id']:r for r in csv.DictReader(open(D+'/evidence_files.csv'))}
for fid,m in man.items():
    p=os.path.join(D,m['file_path'])
    if p.endswith('.json'):
        def walk(o):
            if isinstance(o,dict):
                if 'resource_id' in o: units.append((fid,json.dumps(o).lower()))
                for v in o.values(): walk(v)
            elif isinstance(o,list):
                for v in o: walk(v)
        walk(json.load(open(p)))
    elif p.endswith(('.log','.sql','.txt')):
        lines=open(p,encoding='utf-8',errors='replace').read().splitlines()
        # group log lines by trace_id
        groups=collections.defaultdict(list)
        for i,l in enumerate(lines):
            m2=re.search(r'trace_id=(\S+)',l)
            groups[m2.group(1) if m2 else (p,i)].append(l)
        for g in groups.values(): units.append((fid,' '.join(g).lower()))
for r in csv.DictReader(open(D+'/system_activity.csv')):
    units.append((r['activity_id'],' '.join(r.values()).lower()))
reqs={r['case_id']:r for r in csv.DictReader(open(D+'/sample_deletion_requests.csv'))}
tot=0; linked=0; unl=[]
for r in csv.DictReader(open(D+'/sample_output.csv')):
    q=reqs[r['case_id']]; uid=by_email.get(q['email'].lower())
    S_=subj(uid) if uid else set()
    S_l={x.lower() for x in S_}
    for res in sorted({s['resource_id'] for s in json.loads(r['steps_json'])}):
        tot+=1
        pat=re.compile(r'\b'+re.escape(res.lower())+r'\b')
        hit=[u[0] for u in units if pat.search(u[1]) and any(x in u[1] for x in S_l if len(x)>3)]
        if hit: linked+=1
        else: unl.append((r['case_id'],uid,res))
print('sample resources',tot,'with explicit co-occurring subject link',linked)
for x in unl: print('  UNLINKED',x)
