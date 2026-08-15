# HUMAN — pending questions, and Q/A(assumed) pairs from autonomous mode. REP reads.

## Q (CHECK, 2026-08-14): four companion-DLL tools the thruster move proved we need
Owner's standing instruction, given this session: **always raise DLL capabilities as an
option and let the owner judge.** These four are not speculative — each one is a gap that
cost real calls or left a claim unverifiable while relocating the thruster bank.

Ranked. 1 is the one that actually blocks CHECK from closing items.

1. **`jawa/inspect_string`** — `Thing.GetInspectString()` for any `thingId`. Already asked
   for by C13. **CHECK currently cannot answer "is this thruster functional" at all.**
   `get_cell_info` returns `className: "Verse.Building"` and stops; `list_alerts` carries
   nothing about it; the red-slash overlay was proved non-discriminating today (see
   `facts/LIVE.md`). Everything about thruster function is presently geometry + inference.
2. **`jawa/gravship_status`** — the engine's own launch validation in one call: thruster
   count, computed `GravshipRange`, fuel, and the blocking reason strings
   (`CannotLaunchNoThrusters`, `ThrusterBlockedBy`, …). This is the tool that would turn
   "the geometry mirrors a known-good thruster" into "the ship reports it can fly."
   Note `LIVE.md`: buildings from `spawn_batch` arrive **factionless** and the engine
   offers no Launch gizmo on a pawnless map, so this may need a claimed engine to answer.
3. **`jawa/set_thing_rotation`** — rotate a spawned building in place. Today the only way
   to change a thruster's facing is destroy + respawn, which discards hitpoints, stuff and
   quality. Harmless on a scratch map; **destructive on a colony that matters.**
4. **`jawa/can_place`** — `GenConstruct.CanPlaceBlueprintAt` with an **explicit rotation**,
   returning the `AcceptanceReport` text. Measured today: the stock
   `apply_architect_designator` `dryRun` returned `ok=true` for 25/25 cells under god
   mode, **including a cell already occupied by a thruster**. It is not a validator.

All four need the game DOWN to deploy, so they batch into one shutdown window with any
other BUILD companion work. item: (raised from the thruster relocation, no queue ID)

## Q (BUILD, 2026-08-14): B6 was deleted from `queue/BUILD.md` by `f249d67`
`f249d67` ("Every queue item carries a row:") added a `row:` field to every item and
removed `## B6 Deploy the MandrakeJawa xenotype + Jawa_IndigenousTribes set` outright.
It is the only item that commit dropped, and the subject does not claim a deletion, so
this reads as an accident rather than a ruling.

No work was lost: B6 is DONE — the four PawnKindDefs were repaired (`c06e89e`) and
`Jawa_Patches` is deployed `-> VERIFIED in sync`. The live half is carried forward as
`queue/CHECK.md` C31. Flagging it because if the deletion WAS deliberate, C31 should be
withdrawn; and because a mechanical field-adding pass that silently drops an item is
worth knowing about before the next one runs.

## Q (DECIDE, 2026-08-14): where v2 ideas go — A(owner): `design/V2_DREAMS.md`
Owner's standing instruction: any idea for new content that is deferred out of v1 goes
to `design/V2_DREAMS.md`, appended at the end. **Every seat, and the owner through any
seat, may append there directly** — no permission, no routing through DECIDE, no queue
item asking for it, no format and no field contract.

For REP specifically: when the owner throws out an idea that is not v1, append it and
say where it went. It is not a queue, nothing in it is scheduled, and the board derives
no state from it — so it needs no `derive_matrix.py` run. The point is offloading: write
it down, let it go, back to v1. item: (standing instruction, no queue ID)

## A (DECIDE, 2026-08-14) to BUILD's B6 question: the deletion was DELIBERATE
Not an accident. `f249d67`'s job was assigning `row:`, and its instruction (D0) said
items touching closed rows are almost certainly stale and should be deleted rather than
assigned. B6 claimed the MandrakeJawa set was "built and committed, NOT DEPLOYED"; the
deployed `Jawa_Patches` folder holds `MandrakeJawaXenotype.xml`, `OnlyMandrakeJawa.xml`
and `JawaXenotype_Repoint.xml`, so the claim was false and the item was stale.
⇒ **C31 STANDS** — the live half was never in doubt. The fair criticism is that the
commit subject did not name the deletion, and that is taken.

## FYI (DECIDE, 2026-08-14): the board now tracks the CHAIN, not the eight rows
Read `infrastructure/state/V1_CHAIN.md` before acting on anything below.

**Owner expanded v1.** It is now the 8 gate rows **plus the FULL faction roster** plus
one playable session. This supersedes `V1_SCOPE.md`, which deferred the 11 dossiers,
`pawnGroupMakers` and the ideoligions to v2. The cost was stated to the owner and taken.

**`V1.md`'s table is now 14 chain steps, and queue `row:` values key to it.** The eight
gate rows are still recorded there but carry no items — they are a scoreboard, not a
work breakdown. 15 items filed under the old numbering were remapped; the worldgen
cluster had been rendering under "Pawntypes".

**50 items, and step 9 is burnable today.** 13 BUILD items decompose
`design/Jawa/worldbuilding/FACTION_SPEC.md`: 3 reskin patches, 7 authored `FactionDef`s,
2 label patches, 1 fix to `Jawa_IndigenousTribes`. Every `pawnGroupMaker` kind named in
them was verified present in the 2026-08-14 def dump.

**The head of the chain has NO items yet** — steps 1-3 (item cherrypick -> normalize
weapons/armour/beasts -> equip the pawns). One open owner decision (granularity) blocks
them, and `B39` produces its input. `B53` (the 48 pawn kinds) is correctly `blocked` on
step 3.

**Rulings that change other seats' work:**
- Row 4 CLOSED (scrapfields ships at any density); row 3 REOPENED (resolution, not
  registration); **row 1 REOPENED** — it closed on a label seen live on
  `OuterRim_GalacticEmpire`, and the vessel is now vanilla `Empire` (B40).
- Starting goodwill is NOT a `FactionDef` field. All 12 dossier numbers are cut from v1,
  and inter-faction hostility is fiction only. Do not build a mechanism for either.
- Donor pawn kinds are FLAT species kinds at `combatPower 40`. Role differentiation does
  not exist to borrow, so the 48 authored kinds are required.
- The mod freeze is TWO files — `ModsConfig.xml` AND Cherry Picker's removal list, both
  at `deployed/config/v1_freeze/`. Two of the owner's gene picks had gone missing and are
  restored; they apply on the next cold load.

item: (status briefing, no queue ID)

---

## Is RimSort open right now?

**BUILD is blocked on this and nothing else.** `B25(a)` (pin the loadBottom/loadAfter
user rules) and `B25(d)` (enable `vanillaexpanded.vwel`) both WRITE
`ModsConfig.xml`. RimSort holds the mod list in memory and writes it on Save, so a
write into an open RimSort is silently lost on your next Save — and you are the only
reader who knows whether it is open.

- **RimSort is CLOSED** -> BUILD does the whole B25 pass in one go.
- **RimSort is OPEN** -> close it (or Save then close), then say so.

Live `ModsConfig.xml` mtime is 2026-08-15 11:58:30, 575 active. B25(b) `refresh.py`
does not touch the mod list and has been released to BUILD already.

item: B25(a), B25(d)
