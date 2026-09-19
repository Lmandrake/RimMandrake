# JAWA_TOOLS_ALL_DARK_DUPLICATE_ALIAS_1 — every jawa/ bridge tool was dark, all session, on a duplicate alias

Found 2026-08-29 right after the owner's "Game is up" — first live proof pass this
session hit ZERO `jawa/` tools in `rimbridge_client.py --list-tools` (125 core
`rimworld/*` tools only). Player.log named the cause immediately:

```
[RimBridge] Failed to register annotated extension provider 'extension.global/global/jawa-bench.-bridge-tools':
System.InvalidOperationException: Capability alias 'jawa/bill_add' is already registered for
'extension.global/global/jawa-bench.-bridge-tools/jawa-bench-terrain-tools/bill-add'.
```

## Spec

`jawa/bill_add` was declared TWICE — two independently-written tools, same alias:
- `JawaBenchBillTools.cs` (older) — `RecipeDef.MakeNewBill()` + `IBillGiver.BillStack.AddBill()`.
- `JawaBenchZoneTools.cs` (2026-08-26, Group H of `BRIDGE_TOOLS_MEDIUM_BLOCK_1`) —
  `new Bill_Production(recipe)` + `BillStack.AddBill`, paired with `jawa/configure_bill`,
  and the one `PLACER_IDENTITY_REPLAY_1.md` documents actually using (repeatMode,
  repeatCount, targetCount, storeMode, qualityMin/Max, suspended).

🔴 **RimBridge's capability registry refuses the WHOLE provider on ONE duplicate
alias — not just the colliding tool.** That is why this was not a "one tool missing"
bug, it was "every jawa/ tool absent" — the extension provider `jawa-bench.-bridge-tools`
never registered at all, so all 253 (then 275) tools were dark, silently, all session,
until this load surfaced the log line. `bill_list`/`bill_remove` (siblings of the older
`bill_add`, unique names) are the trio's other two-thirds and were NOT the cause.

🔑 **How this slipped through**: two different sessions each wrote a `bill_add`
independently and neither checked the live tool list first (the skill's own step 0),
or checked and named-searched a DIFFERENT alias than what shipped. Neither `build.py`'s
own guards NOR the C# compiler catch a duplicate alias — the compiler sees two
different STRING LITERALS on two different methods, which is legal C#; only the
RUNTIME registry (inside a running RimWorld) throws on the collision, and only for the
whole provider, not per-tool. **This class of bug is invisible to every check this
project has except an actual live load.**

## Fix, this pass
Renamed the OLDER `JawaBenchBillTools.cs` tool to `jawa/bill_add_legacy` (kept, not
deleted — some caller might rely on its specific `RecipeDef.MakeNewBill()` path; its
Description says so and points callers to the newer `jawa/bill_add` instead). Scanned
the ENTIRE tool surface (`grep -A1 '\[Tool(' *.cs`, restricted to the line right after
the attribute open, not any string literal) for any other duplicate alias — none found.
Builds clean, 0 errors 0 warnings.

## Verify
**Deployed and confirmed live, 2026-08-30.** Deployed with `build.py --gm --apply`
while the game was DOWN, then launched (full 585-mod list, ~15 min cold load) and ran
`prove_new_tools.py --census`: **301 of 302 `jawa/*` tools in the deployed DLL are
registered live** on the running bridge (426 tools on the bridge overall, counting the
125 core `rimworld/*`). The one apparent gap, `jawa/revoke`, is not a regression —
grep confirms it was never implemented (`JawaBenchPawnKitTools.cs:212`: "there is no
revoke tool yet"); the census script's own expectation list is stale, not the tools.

## criteria
- [x] Root cause named from the log, not guessed.
- [x] Fixed: the older duplicate renamed, the documented/relied-upon one keeps the name.
- [x] Whole tool surface re-scanned for any OTHER duplicate alias — none found.
- [x] Builds clean.
- [x] Deployed and live tool count confirmed non-zero. 301/302 registered live, 2026-08-30.

## Watch out
Add a duplicate-alias check to `build.py` itself so this cannot happen a third time —
not done in this pass (time-critical fix first), but worth its own item: grep every
`[Tool("jawa/...")]` string across all files at build time and refuse a duplicate
before it ever reaches a live load.

--- history ---
