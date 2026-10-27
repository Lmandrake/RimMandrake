#!/usr/bin/env python3
"""Export the Arbiter verdict contract as JSON Schema (contracts/schemas/), for `claude -p --json-schema`.

    python3 src/RimMandrake/contracts/export.py           # (re)write the schema files
    python3 src/RimMandrake/contracts/export.py --check   # exit 1 when a committed file differs from the models

Two files:
  arbiter_verdict.schema.json  -- one verdicts.jsonl line (contracts.models.ArbiterVerdict);
  arbiter_batch.schema.json    -- {"verdicts": [ArbiterVerdict, ...]}: what a batch run would return as its
                                  structured output, because one Arbiter run judges several claims and
                                  --json-schema constrains the ONE final result of a `claude -p` run.

The handoff, when wired (not yet: ARBITER_VERDICT_WIRE_JSON_SCHEMA_HANDOFF), is
    claude_bounded.sh -p <msg> ... --output-format json --json-schema "$(cat arbiter_batch.schema.json)"
and the launcher, not the model, appends result["structured_output"]["verdicts"] to verdicts.jsonl after
re-validating each against ArbiterVerdict. Today role_launch.launch_argv passes --output-format json only and the
Arbiter appends its own lines (roles/arbiter.md); arbiter_pending reads them through contracts.compat.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from pydantic import BaseModel, Field  # noqa: E402

from contracts.models import ArbiterVerdict  # noqa: E402

OUT = os.path.join(HERE, "schemas")


class ArbiterBatch(BaseModel):
    """The structured output of one Arbiter batch: one verdict per judged claim, in judging order."""
    model_config = {"extra": "forbid", "strict": True, "frozen": True}
    verdicts: list[ArbiterVerdict] = Field(description="one advisory verdict per claim judged this batch")


def schemas():
    return {"arbiter_verdict.schema.json": ArbiterVerdict.model_json_schema(),
            "arbiter_batch.schema.json": ArbiterBatch.model_json_schema()}


def text(doc):
    return json.dumps(doc, indent=1, sort_keys=True) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    os.makedirs(OUT, exist_ok=True)
    stale = []
    for name, doc in schemas().items():
        p = os.path.join(OUT, name)
        want = text(doc)
        have = open(p, encoding="utf-8").read() if os.path.exists(p) else None
        if have != want:
            if a.check:
                stale.append(name)
            else:
                with open(p, "w", encoding="utf-8", newline="\n") as f:
                    f.write(want)
                print("wrote", p)
    if stale:
        print("stale schema file(s): %s -- run contracts/export.py" % ", ".join(stale))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
