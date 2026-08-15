# HUMAN — pending questions, and Q/A(assumed) pairs from autonomous mode. REP reads.

## ~~Q (DECIDE, 2026-08-15): a cherrypick session~~ ANSWERED — FROZEN, and CLOSED for v1

🔴 **OWNER, 2026-08-15:** *"I have completed armor, weapons, items, beasts, and a few
other things. Let's freeze cherrypicking for right now and close out that item
completely for v1. We can return to it later as needed. No need to review mechs
either."*
⇒ **D27 closes. Chain step 1 is DONE for v1** — it is no longer the head of the chain
and no longer blocks steps 2 and 3. The remaining categories (plants, mechs, drugs,
incidents, traits, ideology styles) are **not v1 work** and nobody schedules them.
The "granularity" owner decision named in the briefing below is **moot**.
⚠️ B67 still stands on its own merits: ~1,300 keep-judgements are gitignored on one
disk, and `cherrypick_build.py` has never validated one of the 1,308 live keys. Freezing
the picking does not make the decisions safe.

<details><summary>the original question</summary>
Chain step 1 is the head of the chain: it blocks step 2 (normalize), which blocks step 3
(equip the pawns), which is why `B53`'s 48 pawn kinds are `blocked`. It is the only step
that needs the OWNER rather than a seat, and it needs him **not playing** — which is now.

**Five categories are already decided and live** (1,308 Cherry Picker keys): weapons
183 cut of 799 · apparel 132 of 820 · animals 338 of 1,239 · items · buildings.
**Seven remain**: armour · plants · mechs · drugs · incidents · traits · ideology styles.

⚠️ **`design/Jawa/mods/CHERRYPICK_AGENDA.md` is stale and will waste his time.** It still
reads *"No list exists at all today"* for armour and leaves weapons and apparel unticked,
though both were decided at 07:19 today and are deployed. Correcting it is inside D27.

Two things a session needs first, both offline and both filed as BUILD **B67**:
the decision files are **gitignored** so ~1,300 keep-judgements sit on one disk, and
`cherrypick_build.py` has never validated a single one of the 1,308 live keys.

✅ **ANSWERED — OWNER 2026-08-15: cherrypicking is FROZEN and the item is CLOSED for
v1.** *"Armour, weapons, items, beasts and others are done; the rest returns later if
needed."* No category runs now; the seven un-run ones are not debt. D27 closed.
🔑 The consequence is the useful part: **the surviving item set is FIXED**, which
un-blocks chain steps 2 and 3 and removes `B53`'s stated blocker. item: D27
</details>

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

## ~~Is RimSort open right now?~~ ANSWERED — the question was never valid

🔴 **Owner's ruling, 2026-08-15: never ask this again.** *"You NEVER have to ask if
RimSort is open. It does not autosave, and I will never save without asking. Nobody
blocks on RimSort or game close for config files of any kind."* Written into
`POLICY.md`, `CLAUDE.md`, `NEXT_RELOAD.md` §1b and the three skills that said
otherwise. BUILD unblocked; B25 proceeds.

~~**BUILD is blocked on this and nothing else.**~~ `B25(a)` (pin the loadBottom/loadAfter
user rules) and `B25(d)` (enable `vanillaexpanded.vwel`) both WRITE
`ModsConfig.xml`. RimSort holds the mod list in memory and writes it on Save, so a
write into an open RimSort is silently lost on your next Save — and you are the only
reader who knows whether it is open.

- **RimSort is CLOSED** -> BUILD does the whole B25 pass in one go.
- **RimSort is OPEN** -> close it (or Save then close), then say so.

Live `ModsConfig.xml` mtime is 2026-08-15 11:58:30, 575 active. B25(b) `refresh.py`
does not touch the mod list and has been released to BUILD already.

item: B25(a), B25(d)

---

## ✅ ANSWERED + DONE (owner, 2026-08-15): the shipping Jawa xenotype drops four of our own genes

**OWNER'S RULING: fix it, #1 priority.** Done by BUILD the same hour, and it turned
out to need no risky edit at all.

🔴 **The question's framing was wrong, and the wrong half was being guarded.** It
asked whether to migrate a shipping save artifact — the dangerous-sounding option.
In fact **the repo copy was already correct** and had been since `c57f347`, the
commit that did the rename. **Only the GAME copy was stale**, at
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Xenotypes\MandrakeJawa.xtp`,
mtime 2026-08-14 15:52. So this was never "migrate an artifact"; it was **a file
that was never deployed** — the project's oldest failure mode, in a folder nobody
thinks of as a deploy target because it is not `Mods/`.

**What was done:** game copy backed up to `MandrakeJawa.xtp.bak-2026-08-15`, repo
copy written over it, md5 verified equal (`d5795edf…`).
**Evidence, against the dump refreshed at THIS load (62,515 defNames):** all four
new names — `RimMandrake_Jawa_Eyes_HugeAmber`, `RimMandrake_Jawa_Eyes_HugeOrange`,
`RimMandrake_Jawa_Head_Plain`, `RimMandrake_Jawa_Skittish` — are LIVE; all four old
names are ABSENT. `validate_save_artifact.py`: **36/36 references resolve, zero
dangling.** Option 1 shipped, with the `Gene_` case correct.

⚠️ **STILL OPEN, and it is not ours to fix unasked:** `softshadow.xtp` in the same
folder carries two dead names — `Jawa_Gene_Skittish` and `Jawa_Head_Plain` — and
will silently drop those genes at world creation exactly as MandrakeJawa would
have. It is not in our repo. The fix is the same two renames and takes a minute;
say the word. (`pokean.xtp` is clean — checked.)

<details><summary>the question as originally filed</summary>

## 🔴 Q (CHECK via REP, 2026-08-15): the shipping Jawa xenotype drops four of our own genes — migrate it, or ship as-is?

**This one blocks worldgen, and it was found by the running game after an offline
verdict said the opposite.**

`MandrakeJawa.xtp` — the v1 xenotype you approved — silently drops **4 GeneDefs**
every load. All four were renamed on our side and the saved file never followed:

| in the .xtp | live name today |
|---|---|
| `Jawa_Eyes_HugeAmber` | `RimMandrake_Jawa_Eyes_HugeAmber` |
| `Jawa_Eyes_HugeOrange` | `RimMandrake_Jawa_Eyes_HugeOrange` |
| `Jawa_Head_Plain` | `RimMandrake_Jawa_Head_Plain` |
| `Jawa_Gene_Skittish` | `RimMandrake_Jawa_Skittish` — ⚠️ **also lost `Gene_`** |

🔴 **A blind "prefix everything" migration fixes three and breaks the fourth.**

Nothing is missing from the game — all four new names are live in today's dump. The
failure is that **the `.xtp` bakes at world creation** and the drop is **silent in
play**: a Jawa comes out without its head type and eye colours and nothing says so.

**The question is yours because migrating a shipping save artifact is not a seat's
call.** Options, recommendation first:

1. ⭐ **Migrate the four names in `MandrakeJawa.xtp` before you generate.** Cheap,
   reversible, and it is the only option that ships the xenotype you actually
   approved. Needs the `Gene_` case handled by hand, not by sed.
2. Regenerate the xenotype from scratch in-game and re-save it. Safer against other
   drift we have not found, costs you a sitting.
3. Ship as-is and accept Jawas without their head type and eye colours.

**Also affected, not yet judged:** `softshadow.xtp` and `pokean.xtp` carry some of
the same dead names.

⚠️ **Doctrine correction already made by CHECK:** `LIVE.md` carried *"MandrakeJawa.xtp
is CLEAN: 36/36 references resolve"* — an **offline** verdict the running game
contradicts. An offline validator **cannot** catch this class: Scribe resolves saved
names at load; a dump check answers a different question. C42's "dangling-reference
question is CLOSED offline" is **falsified for the `.xtp` half**.

Filed to DECIDE as `the-shipping-xenotype-drops-four-of-our-own-genes-7e31aa`.
CHECK did not touch the artifact.

</details>

---

## ~~🔴 Q (CHECK via REP, 2026-08-15): your lightsaber test cannot be run without you — how do you want it collected?~~ ANSWERED — MOVED TO v2, C43 CLOSED

✅ **OWNER, 2026-08-15:** *"Move the lightsabre position bug to v2."*
⇒ **C43 is CLOSED and out of v1.** Do not collect it, do not spend a load on it, do
not stage a swing for v1. Parked in `design/V2_DREAMS.md` as "Lightsabre position
during melee — v2" with everything learned attached, so v2 does not repeat the
attempt blind. The three options below are moot; kept as the record of why it could
not be collected. Yayo stays OFF and re-enabling it is still ruled out.

🔴 **Nothing is missing from the build.** 14 lightsaber ThingDefs are live, verified
against this load's own dump, and one equipped and rendered correctly in game today.
The only open question was ever how the weapon SITS mid-swing. **Nobody goes hunting
a missing weapon.**

---


**C43 is blocked, and the blocker is the bridge, not the art.** The equip half is
solved and verified off the pawn's own Gear panel (*"Equipped: Lightsaber (normal)"*).
**The attack half cannot be staged: nothing on the 155-tool bridge orders an attack.**

- Drafted pawns hold at `Wait_Combat`.
- `jawa/order_pawn` issues a GOTO even when given a `targetId`.
- Spawned hostiles have no lord and idle.
- "Spawn large enemy raid" + 5,600 stepped ticks never produced an engagement.
- The four sith pawnkinds spawn **unarmed**.

CHECK declined to photograph a pawn standing still and call it active melee. That is
the right call — the test you wrote says *during active melee combat*.

**Options, recommendation first:**

1. ⭐ **Stage it yourself in two minutes at the keyboard** — draft, order the attack,
   F10 at the swing. You are the verdict on this one anyway ("more reasonable" is a
   judgement no seat will award itself), so doing the capture costs you almost
   nothing extra.
2. **Add a bridge tool that orders a melee attack** — filed to BUILD as
   `bridge-cannot-order-a-melee-attack-3f8c21`. Fixes it permanently and unblocks
   every future combat test, but needs a DLL build and the next load.
3. Drop C43 from v1.

⚠️ **Whichever you pick, this load can only ever produce the Yayo-OFF arm.**

✅ **ANSWERED — OWNER, 2026-08-15: *"There absolutely is a lightsaber remaining in
the game."*** ⇒ **Every "the lightsaber is missing" thread is CLOSED. Do not open
another.**

⚠️ **Scope of that ruling, corrected 2026-08-15 so the record is accurate.** CHECK's
thread never claimed a lightsaber was missing from the build — it equipped
`Force_Lightsaber_Custom` on this map and verified it off the pawn's own Gear panel
("Equipped: Lightsaber (normal)", Customize/Throw gizmos on the command bar). Its
screenshot question was only ever whether a **Yayo-ON comparison arm** exists for
the owner's *"more reasonable THAN WHAT"*.
📌 **The inference worth keeping is general, not a criticism of that thread:** *"I
checked the two most recent — neither shows a lightsaber"* is a statement about
**two screenshots**, not about the game. Absence from a frame is not absence from
the build.
**Confirmed against this load's own def dump: 14 lightsaber `ThingDef`s are LIVE** —
`Force_Lightsaber_Custom`, `_Dual`, `_Curved`, `_Crossguard`, `_Shoto`,
`_Inquisitor`, `_BuildYourOwn`, `_UniqueObi`, `_UniqueAnakin`,
`Force_Ezra_BlasterLightsaber`, plus the throw/whip/projectile defs. `lee.theforce.lightsaber`
is active. **Nothing about lightsabers is missing from the game.**

⚖️ **What is still genuinely open is NARROWER, and it is not the weapon:** C43 needs
a pawn photographed *mid-swing*, and nothing on the bridge can order an attack. The
three options above stand. **A Yayo-ON comparison shot would still be useful if one
exists — but its absence is now a gap in our screenshots, not evidence about the
build, and no seat should go looking for a missing lightsaber again.**

<details><summary>the screenshot thread as originally filed — superseded</summary>

Still unanswered from earlier: **did your lightsaber complaint come from a screenshot?** If
one of the eight unexamined shots from 04:16–10:08 today shows a Yayo-ON mid-swing,
that is the comparison arm and C43 closes as a real A/B. I checked the two most
recent — neither shows a lightsaber.

</details>
