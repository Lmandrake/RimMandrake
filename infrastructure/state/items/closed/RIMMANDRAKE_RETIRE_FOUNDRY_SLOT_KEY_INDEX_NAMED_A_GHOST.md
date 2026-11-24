# RIMMANDRAKE_RETIRE_FOUNDRY_SLOT_KEY_INDEX_NAMED_A_GHOST

## spec

`src/RimMandrake/Utils/slot_rules.json` still makes RELENTLESS "the one autonomous builder" that "gets the whole machine
total" and keeps a FOUNDRY key; `scratch_clone.SEATS` and `mirror.SEAT_CLONES` still list the retired FOUNDRY seat clone
(`/home/mandrake/rm/foundry`, which on 2026-11-19 is a leftover directory, not a git repository); `scratch_reap.PROTECTED`
and `.claude/hooks/block_agent_over_slots.py` name it too, and the Dispatcher publishes helper budgets for seats
CONDUCTOR/FOUNDRY (`dispatcher_schedule.json` `helper_budget`). The retired-eras index named this work
`SLOTS_RENAME_FOUNDRY_KEY_RELENTLESS_READS_IT`, an item that never existed (corrected 2026-11-19 to this id).

Do: give the allocator's autonomous share to the key today's launches actually draw on (the Maturation Pipeline's
helpers), drop FOUNDRY from `slot_rules.json`, `scratch_clone.SEATS`, `mirror.SEAT_CLONES`, `scratch_reap.PROTECTED`,
`block_agent_over_slots.py` and the helper-budget seats, and move `/home/mandrake/rm/foundry` to
`D:\ClaudeWork\retired-trees\`. `model.SEATS` and `cli.RETIRED_SEATS` keep FOUNDRY and RELENTLESS so old events replay.

Found by `RIMMANDRAKE_FINISH_RETIRED_ERA_REMAINS_TWENTY_ONE_NO_TICKETS` (2026-11-19, BENCH); index: `design/RimMandrake/retired_eras_index_2026-11-18.md`.

## verify

Acceptance test, run from the repo root:

    python3 /path/to/slot_keys.py      # text below, run from the repo root

    import json, re, sys
    sys.path.insert(0, "src/RimMandrake/Utils")
    def strip(x):
        if isinstance(x, dict): return {k: strip(v) for k, v in x.items() if not k.startswith("_")}
        if isinstance(x, list): return [strip(v) for v in x]
        return x
    s = json.dumps(strip(json.load(open("src/RimMandrake/Utils/slot_rules.json"))))
    hits = len(re.findall(r"RELENTLESS|FOUNDRY", s))
    import scratch_clone, mirror
    seats = [x for x in scratch_clone.SEATS if x.lower() == "foundry"] + [p for p in mirror.SEAT_CLONES if p.endswith("/foundry")]
    ok = hits == 0 and not seats
    print(("PASS" if ok else "FAIL") + ": slot_rules non-doc RELENTLESS/FOUNDRY=%d, foundry seat clones listed=%r" % (hits, seats))
    sys.exit(0 if ok else 1)

Expected PASS, exit 0 (1 check). Watched failing 2026-11-19 BENCH at `fbdf50a5b2`: "FAIL: slot_rules non-doc
RELENTLESS/FOUNDRY=2, foundry seat clones listed=['foundry', '/home/mandrake/rm/foundry']", exit 1. Plus
`selftest_slot_allocator*.py` green.

## criteria

- A1: the allocator's rules name no RELENTLESS or FOUNDRY key outside `_doc` text (the test above).
- A2: no seat-clone list names /home/mandrake/rm/foundry, and the directory is moved to retired-trees.

## refs

file: src/RimMandrake/Utils/slot_rules.json
file: src/RimMandrake/Utils/slot_allocator.py
file: src/RimMandrake/Utils/scratch_clone.py
file: src/RimMandrake/Utils/mirror.py
