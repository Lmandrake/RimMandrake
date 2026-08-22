## spec
REP swept `infrastructure/state/BUILDABLE.md` on 2026-08-22 with a subagent. 40 entries verified
accurate; **six read as live warnings about things that have since changed.** A register that
over-warns is spent the same way one that under-warns is: seats stop reading it.

⚠️ **These are the SUBAGENT's findings, not REP's measurements.** Verify each before editing —
a wrong correction in the instrument register is worse than a stale warning.

| entry | says | the sweep found |
|---|---|---|
| def-dump collision (824 defs) | "does nothing until the dumper is redeployed" | deployed `d4bdad92`/`0a3c310b`; the 2026-08-21T22:44:59Z capture already carries `defTypes` + 13 `defTypeCollisions` |
| instrument row 3 | "✅ fixed d7cf154 (undeployed)" | deployed and captured; "(undeployed)" stale |
| instrument 12 `jawa/faction_name_get` | "undeployed until the next shutdown window; do not run clear" | deployed DLL dated 2026-08-22 10:26, after `37ac949` — only a LOAD is still owed, so the blanket "do not run clear" is over-broad |
| "nothing on the 155-tool bridge can order an attack" | 155 tools | stale in three directions at once — 119 distinct `jawa/` tools in companion source, 115 names cited in CLAUDE.md, 244 recorded 2026-08-21. 🔑 **Do not just pick one.** The substantive claim survives: only `fire_raid`, `order_pawn`, `raid_preview` exist and none issues an attack verb |
| "pawnGroupMakers on the ABSTRACT parent ⇒ five `Jawa_Homestead_*` spawn nowhere" | five kinds | superseded 2026-08-22 by `AUTHORED_KINDS_MUST_FIELD_1` (`38cabab0`): **nine** kinds fielded by nothing, and `Inherit="False"` is rejected as the fix |
| `validate_patch.py` row | "✅ fixed, selftest 36 cases" | the xpath fix is real (lines 596-602, `fc10b9a5`) but **no selftest for it exists** in the repo. The "36 cases" has no artifact behind it |

Also: the header banner still frames *"one hand-made world, frozen, then shipped"* as an existing
constraint. The owner is REMAKING the planet (`canon.yml planet.status: remaking`); the
no-worldgen ruling is untouched, the "frozen world exists" framing is not.
Entry 8 names `DefDump/defs.sqlite` with no root — the only such file is
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\defs.sqlite`.

## verify
Each row re-measured independently before the register is edited. A row that cannot be settled
offline stays as it is, marked UNMEASURED with what would settle it.

## criteria
No entry in `BUILDABLE.md` warns about a defect that is fixed, and no count in it is a number
nobody can reproduce.

## Watch out
🪤 **The bridge tool count is the trap.** Three numbers are already in circulation and `strings`
on the assembly cannot settle it — CLAUDE.md records that a byte scan found 16 of 115 names and
reported the shortfall as a clean answer. Either `measure` it or write UNMEASURED.
