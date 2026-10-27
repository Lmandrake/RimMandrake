"""RimMandrake wire contracts (CONTRACTS_BUILD_COMMON_READER_FIVE_RECORDS).

  contracts.jsonl   stdlib line policy: every JSONL line -> Row | Fault (never raises, never drops). Safe anywhere.
  contracts.models  Pydantic v2 models (compat checks wired into the readers + strict shadow contracts). ~50 ms import.
  contracts.replay  old-vs-new reader replay over real stores and fixtures; 100k commissioning run.
  contracts.export  JSON Schema export (arbiter verdict for `claude -p --json-schema`).

This __init__ imports nothing, so `from contracts import jsonl` never pays for pydantic.
Callers put src/RimMandrake on sys.path (as arbiter_pending already does) and import `contracts.<module>`.
"""
