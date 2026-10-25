"""Offline evidence viewer: one self-contained HTML file from a run (S7 C7.2). No CDN, no fetch, no backend, no key,
no model call.

What it shows comes from `ghostaudit.explain.case_view`, the representation `main.py explain` prints, so the viewer
and the CLI cannot disagree. Provenance is attached only when `provenance.verify_run` confirms it (sha256 and run
fingerprint); otherwise each observation says why it is not attached.

Canonical vs execution metadata (what must match byte for byte):
- The HTML holds only canonical content: the run's configuration, fingerprints, artifact sha256s and counts from
  `summary.json` (fields that are equal between a live run and its replay), and every case view. It holds no local
  path, no run-directory name and no wall-clock time. Two builds from runs with the same `output.csv`,
  `decisions.jsonl`, `provenance.jsonl` and fingerprints are byte-identical; the release check compares exactly
  that.
- `<out>.meta.json` (beside the HTML, never inside it) records the execution metadata: the run directory, the
  generation time, and the HTML's sha256.

Untrusted evidence text is embedded as JSON inside `<script type="application/json">` with `<`, `>`, `&`, U+2028
and U+2029 written as `\\uXXXX`, and the page renders every string with text nodes only (no `innerHTML`).

Usage: python code/main.py viewer --run runs/<run> --out viewer.html
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

CANONICAL_SUMMARY = ("split", "engine", "model", "ownership", "agent_scope", "asserted_mechanisms", "time_policy",
                     "rows", "status", "support", "status_by_support", "fingerprints", "artifacts")


def script_safe_json(obj) -> str:
    s = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for ch, esc in (("&", "\\u0026"), ("<", "\\u003c"), (">", "\\u003e"), (" ", "\\u2028"), (" ", "\\u2029")):
        s = s.replace(ch, esc)
    return s


def _compact(view: dict, prov: dict) -> dict:
    """Replace each full provenance record by its obs_id (stored once in `prov`), to keep the page small."""
    def walk(x):
        if isinstance(x, dict):
            if "obs_id" in x and "source_kind" in x:
                prov[x["obs_id"]] = x
                return {"ref": x["obs_id"]}
            return {k: walk(v) for k, v in x.items()}
        if isinstance(x, list):
            return [walk(v) for v in x]
        return x
    return walk(view)


def build_data(run: Path) -> dict:
    from ghostaudit.explain import case_view, load_provenance
    summary = json.loads((run / "summary.json").read_text()) if (run / "summary.json").exists() else {}
    prov_state = load_provenance(run)
    prov: dict = {}
    cases = []
    for line in open(run / "decisions.jsonl", encoding="utf-8"):
        d = json.loads(line)
        cases.append(_compact(case_view(run, d["case_id"], prov_state, decision=d), prov))
    cases.sort(key=lambda c: c["case_id"])
    meta = {k: summary.get(k) for k in CANONICAL_SUMMARY if k in summary}
    meta["provenance"] = {"status": prov_state[0], "message": prov_state[2]}
    meta["heuristic_rows"] = sum(1 for c in cases if c["heuristic"])
    content = {"run": meta, "cases": cases, "prov": dict(sorted(prov.items()))}
    content["content_sha256"] = hashlib.sha256(script_safe_json({k: content[k] for k in ("run", "cases", "prov")})
                                               .encode()).hexdigest()
    return content


def render(data: dict) -> str:
    return PAGE.replace("/*DATA*/", script_safe_json(data))


def build(run: Path, out: Path) -> dict:
    html = render(build_data(run))
    out.write_text(html, encoding="utf-8")
    meta = {"run_dir": str(run), "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "html_sha256": hashlib.sha256(html.encode("utf-8")).hexdigest(), "bytes": len(html.encode("utf-8"))}
    Path(str(out) + ".meta.json").write_text(json.dumps(meta, indent=1) + "\n")
    return meta


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'none'; connect-src 'none'">
<title>Ghost Data evidence viewer</title>
<style>
:root{--bg:#ffffff;--panel:#f5f6f8;--ink:#16181d;--muted:#4a5160;--line:#d5d9e0;--accent:#1f4fbf;
--ok:#0f6b3a;--okbg:#e3f3ea;--bad:#9b1c1c;--badbg:#fbe9e9;--warn:#7a4b00;--warnbg:#fdf1d8;--na:#3d4452;--nabg:#eceef2}
@media (prefers-color-scheme: dark){:root{--bg:#121417;--panel:#1b1e23;--ink:#e8eaee;--muted:#b3b9c4;--line:#343a44;
--accent:#8fb0ff;--ok:#8fe0b0;--okbg:#173524;--bad:#ffb0b0;--badbg:#3d1d1d;--warn:#ffd48a;--warnbg:#3a2c12;--na:#d0d4dc;--nabg:#2a2e35}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{padding:14px 16px;border-bottom:1px solid var(--line)}
h1{font-size:18px;margin:0 0 4px}
h2{font-size:16px;margin:18px 0 6px}
h3{font-size:14px;margin:12px 0 4px}
.muted{color:var(--muted)}
.wrap{display:grid;grid-template-columns:320px 1fr;min-height:calc(100vh - 90px)}
aside{border-right:1px solid var(--line);padding:12px 16px;background:var(--panel)}
main{padding:12px 20px;min-width:0}
input,select{font:inherit;color:var(--ink);background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:6px 8px;width:100%;margin:4px 0}
label{font-size:13px;color:var(--muted)}
#list{list-style:none;margin:8px 0 0;padding:0;max-height:calc(100vh - 300px);overflow:auto}
#list li button{all:unset;display:flex;gap:6px;align-items:center;flex-wrap:wrap;width:100%;padding:6px 4px;border-bottom:1px solid var(--line);cursor:pointer}
#list li button:focus-visible,#list li button[aria-current=true]{outline:2px solid var(--accent);outline-offset:-2px}
.badge{display:inline-block;font-size:12px;font-weight:600;padding:1px 7px;border-radius:10px;border:1px solid currentColor}
.s-COMPLETE{color:var(--ok);background:var(--okbg)}.s-INCOMPLETE{color:var(--bad);background:var(--badbg)}
.s-NOT_APPLICABLE{color:var(--na);background:var(--nabg)}
.p-resolved{color:var(--ok);background:var(--okbg)}.p-weak,.p-unresolved{color:var(--warn);background:var(--warnbg)}
.heur{color:var(--warn);background:var(--warnbg);border:2px solid var(--warn);padding:8px 10px;border-radius:6px;font-weight:600;margin:8px 0}
.note{border-left:3px solid var(--accent);padding:4px 10px;margin:8px 0;background:var(--panel)}
table{border-collapse:collapse;width:100%;font-size:13px;margin:4px 0;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:4px 6px;text-align:left;vertical-align:top}
th{background:var(--panel)}
code,.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12.5px;word-break:break-all}
details{border:1px solid var(--line);border-radius:6px;padding:6px 10px;margin:6px 0}
summary{cursor:pointer;font-weight:600}
pre{white-space:pre-wrap;word-break:break-word;background:var(--panel);padding:6px;border-radius:4px;font-size:12px;margin:4px 0}
@media (max-width:760px){.wrap{grid-template-columns:1fr}aside{border-right:0;border-bottom:1px solid var(--line)}#list{max-height:260px}main{padding:12px 16px}}
</style>
</head>
<body>
<header><h1>Ghost Data Still Exists — evidence viewer</h1><div id="runinfo" class="muted"></div></header>
<div class="wrap">
<aside>
<label for="q">Search case, email, resource or evidence id</label><input id="q" type="search" autocomplete="off">
<label for="fs">Status</label><select id="fs"><option value="">all</option><option>COMPLETE</option><option>INCOMPLETE</option><option>NOT_APPLICABLE</option></select>
<label for="fp">Support</label><select id="fp"><option value="">all</option><option>resolved</option><option>weak</option><option>unresolved</option></select>
<label><input id="fh" type="checkbox" style="width:auto"> heuristic predictions only</label>
<div id="count" class="muted"></div>
<ul id="list"></ul>
</aside>
<main id="detail"><p class="muted">Choose a case.</p></main>
</div>
<script type="application/json" id="data">/*DATA*/</script>
<script>
"use strict";
const D = JSON.parse(document.getElementById("data").textContent);
function h(tag, attrs, ...kids){const e=document.createElement(tag);
  for(const [k,v] of Object.entries(attrs||{})){if(v!==undefined&&v!==null) e.setAttribute(k,v);}
  for(const k of kids.flat()){if(k===null||k===undefined||k===false) continue; e.append(k instanceof Node?k:document.createTextNode(String(k)));}
  return e;}
const MISSING="not recorded in the trace";
const STATUS_TEXT={COMPLETE:"COMPLETE",INCOMPLETE:"INCOMPLETE",NOT_APPLICABLE:"NOT APPLICABLE"};
const SUPPORT_TEXT={resolved:"support: resolved",weak:"support: weak",unresolved:"support: unresolved"};
function sbadge(s){return h("span",{class:"badge s-"+s},STATUS_TEXT[s]||s);}
function pbadge(p){return h("span",{class:"badge p-"+p},SUPPORT_TEXT[p]||("support: "+p));}
function prov(o){ if(!o) return h("span",{class:"muted"},MISSING);
  const r=o.ref?D.prov[o.ref]:o; if(!r) return h("span",{},"⚠ provenance missing for "+o.ref);
  if(r.unavailable) return h("span",{},h("code",{},r.obs_id)," — ⚠ provenance not attached: "+r.unavailable);
  const d=h("details",{},h("summary",{},h("code",{},r.obs_id)," · "+r.source_kind+" "+r.kind+" · captured "+r.captured_at+" · observed "+(r.observed_at||"none stated")));
  d.append(h("div",{},"File: ",h("code",{},r.file||r.source_id),"  · locator ",h("code",{},r.locator||"—"),"  · system "+(r.system_id||"?")+(r.topology?" / "+r.topology:"")+" · time basis "+r.time_basis+(r.snapshot_dated?" (snapshot envelope: observed = its own capture time)":"")));
  d.append(h("div",{class:"muted"},"Excerpt (untrusted evidence text, shown as text):"),h("pre",{},JSON.stringify(r.excerpt,null,1)));
  if(r.wrapper_excerpt&&Object.keys(r.wrapper_excerpt).length) d.append(h("div",{class:"muted"},"Lookup wrapper (not record content):"),h("pre",{},JSON.stringify(r.wrapper_excerpt,null,1)));
  return d;}
function hay(c){const p=c.person||{};return [c.case_id,(c.request||{}).request_email,p.user_id,...(p.identifiers||[]).map(i=>i.value),
  ...c.resources.map(r=>r.resource_id),...c.steps.map(s=>s.evidence_id)].filter(Boolean).join(" ").toLowerCase();}
const HAY=new Map(D.cases.map(c=>[c.case_id,hay(c)]));
function certainty(c){
  if(c.status==="NOT_APPLICABLE") return "The request does not authorize deletion, so no deletion is checked.";
  if(c.support==="resolved") return c.status==="COMPLETE"?"Every relevant copy is shown compliant by the cited evidence.":"The findings are tied to the person by explicit evidence.";
  if(c.status==="COMPLETE") return "Predicted complete, not proven: part of the evidence chain is missing or uncertain (see the limits below).";
  return "Best-effort answer: some links or states are uncertain (see the limits below).";}
function show(c){
  const m=document.getElementById("detail"); m.replaceChildren();
  m.append(h("h2",{},c.case_id+" ",sbadge(c.status)," ",pbadge(c.support)));
  m.append(h("div",{class:"note"},certainty(c)," Status and support are separate: status is the answer written to output.csv; support is how well the evidence establishes it (the CSV cannot carry it)."));
  if(c.heuristic) m.append(h("div",{class:"heur"},"HEURISTIC PREDICTION — part of this row is a rule-of-thumb guess, not a reconstructed state. It is marked on the steps below."));
  m.append(h("div",{class:"muted"},"Run integrity: "+c.provenance.status+" — "+c.provenance.message));
  const r=c.request; m.append(h("h3",{},"Request"));
  m.append(r?h("div",{},"Requested "+r.requested_at+"; the workflow claimed "+r.reported_status+" at "+r.reported_at+" (a claim, not proof). Cutoff (audit_at) "+r.audit_at+". Email ",h("code",{},r.request_email)):h("div",{},MISSING));
  const it=c.intent; m.append(h("div",{},it?("Intent: authorizes deletion = "+it.authorizes_deletion+", confidence "+it.confidence+", source "+it.source+". "+(it.reason||"")):"Intent: "+MISSING));
  m.append(h("h3",{},"Person"));
  const p=c.person;
  if(!p) m.append(h("div",{},MISSING)); else if(p.unresolved) m.append(h("div",{},"Not identified: "+p.unresolved)); else {
    m.append(h("div",{},h("code",{},p.user_id),"; the request email is a "+p.request_email_role+" identifier"));
    m.append(h("table",{},h("tr",{},h("th",{},"type"),h("th",{},"value"),h("th",{},"current / historical at the cutoff"),h("th",{},"source")),
      (p.identifiers||[]).map(i=>h("tr",{},h("td",{},i.type),h("td",{},h("code",{},i.value)),h("td",{},i.role),h("td",{},i.source)))));}
  m.append(h("h3",{},"Ownership"));
  const a=c.account;
  m.append(h("div",{},a===MISSING?"Account: "+MISSING:a===null?"Account: none attributed. Remaining candidates: "+(c.account_candidates.join(", ")||"none"):
    ["Account ",h("code",{},a.resource_id)," — tier "+a.tier+", deduced by "+(a.how||MISSING)+(c.account_source?" ("+c.account_source+")":"")]));
  const open=[...Object.entries(c.uncertain).map(([k,v])=>["Uncertain candidate (no step generated)",k,v]),
    ...Object.entries(c.excluded).map(([k,v])=>["Rejected link",k,v]),...c.ambiguities.map(x=>["Open question","",x])];
  if(open.length) m.append(h("details",{open:""},h("summary",{},"Uncertain candidates, rejected links, open questions ("+open.length+")"),
    h("ul",{},open.map(([t,k,v])=>h("li",{},t+": ",k?h("code",{},k):"",k?" — ":"",v)))));
  m.append(h("h3",{},"Resources: link, copies and state at the cutoff, policy"));
  if(!c.resources.length) m.append(h("div",{class:"muted"},"No resource decisions (nothing linked, or no deletion authorized)."));
  for(const x of c.resources){
    const d=h("details",{},h("summary",{},h("code",{},x.resource_id)," ("+(x.system_id||"?")+") — "+x.verdict+(x.heuristic?" — HEURISTIC":"")));
    d.append(h("div",{},"Link tier: "+x.tier+(x.tier==="explicit"?" (evidence names the person)":" (deduced from timing / one-to-one, not proof)")));
    d.append(h("div",{},"Linked by:"),h("ul",{},(x.links.length?x.links:[null]).map(o=>h("li",{},prov(o)))));
    d.append(h("div",{},"Policy: category "+x.category+" ("+x.category_reason+") → rule "+(x.rule||MISSING)+" → treatment "+x.treatment+". Verdict: "+x.verdict+" ("+x.reason+")"));
    d.append(h("table",{},h("tr",{},h("th",{},"copy"),h("th",{},"state"),h("th",{},"how"),h("th",{},"observation")),
      x.copies.map(cp=>h("tr",{},h("td",{},cp.copy),h("td",{},cp.state),h("td",{},cp.basis==="scope"?"inferred: a capture lacks the row":"direct observation"),h("td",{},prov(cp.obs))))));
    m.append(d);}
  m.append(h("h3",{},"Steps written to output.csv"));
  const groups=c.status==="COMPLETE"?[["VERIFICATION","Verification evidence (the state at audit_at)"]]:
    [["FINDING","Findings"],["REMEDIATION","Proposed remediation — not executed"],["VERIFICATION","Checks to run after remediation"]];
  if(!c.steps.length) m.append(h("div",{class:"muted"},c.status==="NOT_APPLICABLE"?"None (not applicable).":"No steps."));
  for(const [ph,title] of groups){const ss=c.steps.filter(s=>s.phase===ph); if(!ss.length) continue;
    m.append(h("div",{},h("strong",{},title)),h("table",{},h("tr",{},h("th",{},"#"),h("th",{},"operation"),h("th",{},"system / resource"),h("th",{},"state"),h("th",{},"evidence"),h("th",{},"basis")),
      ss.map(s=>h("tr",{},h("td",{},s.step_no),h("td",{},s.operation),h("td",{},s.system_id+" / ",h("code",{},s.resource_id)),h("td",{},s.state),h("td",{},s.evidence_id?h("code",{},s.evidence_id):"—"),h("td",{},s.basis)))));}
  m.append(h("details",{},h("summary",{},"Reasons and limits recorded by the run ("+c.reasons.length+")"),h("ul",{},c.reasons.map(x=>h("li",{},x)))));
}
function refresh(){
  const q=document.getElementById("q").value.trim().toLowerCase(), fs=document.getElementById("fs").value,
    fp=document.getElementById("fp").value, fh=document.getElementById("fh").checked;
  const hits=D.cases.filter(c=>(!fs||c.status===fs)&&(!fp||c.support===fp)&&(!fh||c.heuristic)&&(!q||HAY.get(c.case_id).includes(q)));
  const ul=document.getElementById("list"); ul.replaceChildren();
  document.getElementById("count").textContent=hits.length+" of "+D.cases.length+" cases";
  if(!hits.length) ul.append(h("li",{class:"muted"},"No case matches these filters."));
  for(const c of hits.slice(0,600)){const b=h("button",{type:"button","data-case":c.case_id},h("span",{class:"mono"},c.case_id),sbadge(c.status),pbadge(c.support),c.heuristic?h("span",{class:"badge p-unresolved"},"heuristic"):null);
    b.addEventListener("click",()=>{for(const x of ul.querySelectorAll("button")) x.removeAttribute("aria-current"); b.setAttribute("aria-current","true"); show(c); location.hash=c.case_id;
      if(window.matchMedia("(max-width:760px)").matches) document.getElementById("detail").scrollIntoView();});
    ul.append(h("li",{},b));}
}
const R=D.run; const sup=R.support||{}, st=R.status||{}, art=R.artifacts||{};
document.getElementById("runinfo").append(
  "Result: output.csv sha256 ",h("code",{},(art["output.csv"]||"?").slice(0,16)),"… · content ",h("code",{},D.content_sha256.slice(0,16)),"… · ",
  (R.rows||D.cases.length)+" cases · engine "+(R.engine||"?")+(R.model?" ("+R.model+")":"")+" · ownership "+(R.ownership||"?")+" · time policy "+(R.time_policy||"?"),
  h("br",{}),"Status: "+Object.entries(st).map(([k,v])=>k+" "+v).join(", ")+" · Support: "+Object.entries(sup).map(([k,v])=>k+" "+v).join(", ")+" · heuristic rows "+R.heuristic_rows+" · run integrity "+R.provenance.status+(R.provenance.status==="verified"?"":" — "+R.provenance.message));
for(const id of ["q","fs","fp","fh"]) document.getElementById(id).addEventListener("input",refresh);
refresh();
const start=D.cases.find(c=>c.case_id===decodeURIComponent(location.hash.slice(1)));
if(start) show(start);
</script>
</body>
</html>
"""


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args(argv)
    print(json.dumps(build(a.run, a.out), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
