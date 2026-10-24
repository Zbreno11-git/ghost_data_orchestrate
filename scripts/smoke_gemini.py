"""S0 C0.5 smoke: JSON schema output, one function-call round trip, one PNG extraction.

Run: .venv/bin/python scripts/smoke_gemini.py  (costs well under $0.05; every call is ledgered)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from google.genai import types  # noqa: E402

from ghostaudit.llm.gemini import Gemini  # noqa: E402

MODEL = "gemini-3.1-flash-lite"
g = Gemini(run_id="s0-smoke")
results = {}

# (a) structured JSON output
schema = {"type": "object", "properties": {"authorizes_deletion": {"type": "boolean"}, "language": {"type": "string"}},
          "required": ["authorizes_deletion", "language"]}
resp, m = g.generate(model=MODEL, purpose="smoke-json", est_input_tokens=200, contents=(
    "Classify whether this customer request authorizes deletion of their account data. "
    "Request: 'Intenté eliminar mi cuenta ayer, pero la página mostró un error. ¿Pueden completar la eliminación?'"),
    config=types.GenerateContentConfig(response_mime_type="application/json", response_json_schema=schema,
                                       max_output_tokens=200, temperature=0,
                                       thinking_config=types.ThinkingConfig(thinking_level="MINIMAL")))
results["a_json"] = {"parsed": json.loads(resp.text), **m}

# (b) function-call round trip (automatic calling disabled: we dispatch tools ourselves)
tool = types.Tool(function_declarations=[types.FunctionDeclaration(
    name="lookup_resource", description="Read-only lookup of a resource's observed state at the audit cutoff.",
    parameters_json_schema={"type": "object", "properties": {"resource_id": {"type": "string"}},
                            "required": ["resource_id"]})])
cfg = types.GenerateContentConfig(tools=[tool], max_output_tokens=300, temperature=0,
                                  automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                                  thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"))
history = [types.Content(role="user", parts=[types.Part(text=
    "Use the tool to check whether account_3136 still exists, then answer in one sentence.")])]
resp1, m1 = g.generate(model=MODEL, purpose="smoke-tool-1", est_input_tokens=300, contents=history, config=cfg)
calls = resp1.function_calls or []
model_content = resp1.candidates[0].content
has_sig = any(p.thought_signature for p in model_content.parts if p.function_call)
history.append(model_content)  # keeps thought signatures intact
history.append(types.Content(role="user", parts=[types.Part.from_function_response(
    name="lookup_resource", response={"resource_id": "account_3136", "status_code": 404, "observed_at": "2026-09-15T09:31:40Z"})]))
resp2, m2 = g.generate(model=MODEL, purpose="smoke-tool-2", est_input_tokens=400, contents=history, config=cfg)
results["b_tool"] = {"calls": [{"name": c.name, "args": dict(c.args)} for c in calls], "thought_signature": has_sig,
                     "final_text": resp2.text, "cost_usd": m1["cost_usd"] + m2["cost_usd"]}

# (c) PNG extraction
png = Path(__file__).resolve().parents[1] / "dataset/evidence/images/account_admin_console_20260926.png"
schema_c = {"type": "object", "properties": {"user_id": {"type": "string"}, "resource_id": {"type": "string"},
                                             "email": {"type": "string"}, "phone": {"type": "string"}},
            "required": ["user_id", "resource_id", "email", "phone"]}
resp3, m3 = g.generate(model=MODEL, purpose="smoke-vision", est_input_tokens=2500, contents=[
    types.Part.from_bytes(data=png.read_bytes(), mime_type="image/png"),
    "Extract the customer's user_id, account resource id, email and phone exactly as displayed."],
    config=types.GenerateContentConfig(response_mime_type="application/json", response_json_schema=schema_c,
                                       max_output_tokens=300, temperature=0,
                                       thinking_config=types.ThinkingConfig(thinking_level="MINIMAL")))
results["c_vision"] = {"parsed": json.loads(resp3.text), **m3}

results["ledger_totals"] = g.ledger.totals()
print(json.dumps(results, indent=1, default=str))
