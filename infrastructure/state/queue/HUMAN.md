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

## ~~Q (CHECK, 2026-08-14): four companion-DLL tools the thruster move proved we need~~ ANSWERED — ALL FOUR TO v2

✅ **OWNER, 2026-08-15: push all four to v2.** `inspect_string`, `gravship_status`,
`set_thing_rotation`, `can_place`. **Deferred, not refused** — the gaps are real and
measured, but nothing in v1 waits on them now that C43 has left v1. No DLL build, no
shutdown window held for them. The ranked case below stands as the v2 brief.
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

🔴 **STATUS IS "FIX DEPLOYED, UNVERIFIED" — not done. CHECK is right to hold it open
and the reason is not pedantry.** Everything above is **DISK** evidence, and disk
evidence is exactly what got this wrong the first time: `LIVE.md`'s retracted claim
*"MandrakeJawa.xtp is CLEAN: 36/36 references resolve"* came from **this same
validator**, and the running engine contradicted it. The game running now loaded the
OLD file at startup, so **this session cannot witness the fix in either direction.**
**CLOSING CONDITION, and it costs nothing:** the next load's startup log carries
**ZERO** `Could not load reference to Verse.GeneDef named Jawa_*`. Today's carried 12
GeneDef lines, 4 of them ours. CHECK reads it with `harvest_log.py --show scribe` and
closes it then (`0279750`).
📌 The general rule, worth more than this item: **an offline validator answers "is
the file I pointed at self-consistent". It cannot answer "is the file the game reads
correct" — and for a `.xtp` those were two different files for a whole day.**

~~⚠️ **STILL OPEN, and it is not ours to fix unasked:** `softshadow.xtp` in the same
folder carries two dead names — `Jawa_Gene_Skittish` and `Jawa_Head_Plain` — and
will silently drop those genes at world creation exactly as MandrakeJawa would
have. It is not in our repo. The fix is the same two renames and takes a minute;
say the word. (`pokean.xtp` is clean — checked.)~~
✅ **RESOLVED — OWNER 2026-08-15: *"Kill softshadow, it was a mistake."*** File
DELETED from the Xenotypes folder by REP. No fix needed, no item, no decision left.
Confirmed before deleting: 22 genes, two of them the dead names. Surviving `.xtp`
files: `MandrakeJawa` (clean, verified), `pokean` (clean), `Dark Glutton`,
`Dark Troll`, `mimic`.

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

## ~~🔴 FYI + one decision (BUILD, 2026-08-19): the cherrypick list was not loading AT ALL~~ ANSWERED

**No answer needed on the first part — it is already repaired.** Validating the 1,308
live Cherry Picker keys against the def dump for the first time (B67b) turned up two
keys the review sheet had synthesised for defs whose author forgot to give them a
defName:

```
<li>ThingDef/<nodef#10></li>
<li>ThingDef/<nodef#11></li>
```

A raw `<` is not legal inside XML text. The game's own log says what that cost:

```
Caught exception while loading mod settings data for 3521312241. Generating fresh
settings. The exception was: System.Xml.XmlException: The '#' character, hexadecimal
value 0x23, cannot be included in a name. Line 874, position 23.
```

⇒ **every one of the 1,308 cuts has been inert in game** — not two of them, all of
them. **Repaired**: the two impossible keys are dropped, 1,306 remain, the file parses,
and both the live config and the tracked freeze copy now hold it. The old file is at
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_3521312241_Mod_CherryPicker.xml.bak-nodef`.
`cherrypick_build.py` now refuses to write a file that is not well-formed.

### 🟢 ANSWERED 2026-08-19, both applied — the list is now 1,349 keys

* **the 11 weapons/apparel: "All 11 + the 4 turret buildings".** The four
  `FT_Gun_Turret*`/`FT_Gun_Recoilless` guns go in WITH `FT_TurretHexMortar`,
  `FT_TurretEmpero`, `FT_RecoillessGun` and `FT_TurretQuadAA`, so no turret is left
  holding a weapon that does not exist. Each pairing read out of the dump's
  `building.turretGunDef`, not guessed from the name.
* **the 30 biomes: "Apply 28, keep AridShrubland + Lake".** Recorded in
  `OWNER_EXCLUDE` in `cherrypick_build.py` with the tile counts, and printed on every
  run — a silent exception is how a decision gets lost twice.

⇒ 1,306 + 28 biomes + 11 weapons/apparel + 4 turret buildings = **1,349**, zero
removals, file parses. Nothing below is outstanding; it is kept for the reasoning.

<details><summary>the original finding</summary>

**What WAS yours to decide — 41 cuts you recorded that never reached the settings file.**
They are in `observed/inventory/decisions_*.json` and nowhere else, so nothing cut them
and nothing will. Not added: changing what is cut is not a seat's call.

| category | count | examples |
|---|---|---|
| biomes | 30 | `AB_IdyllicMeadows`, `AridShrubland`, `BorealForest`, `ColdBog` |
| weapons | 10 | `ElephantTusk`, `Flamebow`, `FT_Gun_TurretQuadAA`, `Gun_Incinerator` |
| apparel | 1 | `AM_LassoDevilstrand` |

⚠️ The 30 biomes may well be deliberate — biomes are excluded from a planet by the
hand-authored world map, not by Cherry Picker, so cutting the def too would be belt and
braces. Say the word and they go in; say nothing and they stay out.

**Also worth knowing, no action:** 129 of the 1,306 keys name defs from mods that are no
longer active (Vanilla Animals Expanded 66, Grimstone: Beasts 11, Giant Snake 6, ReGrowth:
Boiling 3, Skunks 1, plus 40 derived meat/egg keys). They are inert and harmless — Cherry
Picker skips an unresolvable key with no report — so they were left alone rather than
edited out of your list. `python3 src/RimMandrake/Utils/cherrypick_build.py` names every
one of them.

</details>

## The `rimworld-modding` skill archive is stale and will not rebuild — 2026-08-19, BUILD
`skills/rimworld-modding.skill` is dated 2026-08-16 and `package_skill.py` refuses to
refresh it: `SKILL.md body is 505 lines; the guidance is under 500`. It has been failing
that check since before today, so **every script fix in that skill since 2026-08-16 is on
disk and in git but is NOT in the installed skill** — including today's fix to
`validate_patch.py`, which was reporting correct xpaths as dead.

The fix is six lines of prose moved from `SKILL.md` into `references/`. That is REP's
file, not BUILD's, which is why it is here rather than done.

## Four species still render magenta, and two rulings disagree about it — 2026-08-19, BUILD
`queue/BUILD.md`'s deploy-pass item says *"CHECK is waiting on the D-CHK2 generator fix
from you — Gand, Selkath, female Chagrian, Jawa mask"*. But D-CHK2 and B66, which folds
it, are both marked `⛔ v2` by your 2026-08-15 blanket triage. Same day, opposite
instructions, so I did not start it.

**It is smaller than the item makes it sound.** Measured today: the broken paths are 4
families, about 25 lines — `OuterRim/Genes/Headbone/ChagrianF`,
`Pawn/HeadAttachments/gand/mask_*`, `Pawn/HeadAttachments/selkath/fishyjowls_female`,
`Pawn/HeadAttachments/yelloweyes/YellowEyes_Female`, and 16 `OuterRim/GeneIcons/*BG`.
The donors still hold every texture, so nothing is lost — only unmigrated.

⚠️ D-CHK2's own offline test is WRONG as written. It says no path may start `UI/`
without the `RimMandrakeSW/` prefix; but `UI/Icons/Xenotypes/Baseliner`,
`UI/Icons/Genes/Gene_Furskin` and a dozen more are **vanilla** paths that must stay
un-prefixed. Only donor-owned paths get rewritten.

Say the word and it is an afternoon in `gen_races_mod.py` plus a re-run. Left alone
otherwise.

## ~~🔴 Q (REP, 2026-08-20): is the MOD leaving, or just the vessel?~~ ✅ ANSWERED — B, the mod STAYS

🟢 **OWNER, 2026-08-20: *"The mod is not leaving, no."*** ⇒ Option B. The patches are
not deleted, the saved worlds keep valid faction references, and Outer Rim keeps shipping
its pawn kinds and gear. `queue/BUILD.md` B-EMP1 is unblocked and rescoped — the only
real defect turned out to be stale prose in `About.xml`; the reskin patch already targets
vanilla `Empire`, and the `OnlyOurFactions.xml` suppression block is correct as written.

Your ruling is recorded and propagating: the Galactic Empire is authored on vanilla
`Empire`, and `OuterRim_GalacticEmpire` is not patched. That part needs nothing from you.

**But one word decides a different job.** Measured today: the Outer Rim Galactic Empire
mod is **still active in the campaign list** — 10 `neronix17.*` entries in
`infrastructure/state/modlists/ModsConfig.PRESWAP.20260819_212256.xml`, the 578-mod
snapshot. (The live `ModsConfig.xml` currently holds the 13-mod minimal list, so it is
not evidence either way.)

| if you meant | then |
|---|---|
| **A. The mod is being REMOVED from the list** | The six xpaths in `OnlyOurFactions.xml` and the `About.xml` dependency get **deleted**, not retargeted. ⚠️ And three saved world files — `world\WORLDMAP_gen.rws`, `WORLDMAP_source.rws`, `WORLDMAP_sub7b_source.rws` — already name `OuterRim_GalacticEmpire` in their faction lists. Removing the mod makes those **dead references in the save**, which no mod change fixes. |
| **B. The mod stays; it is simply not our vessel** | The patches get **retargeted or dropped**, the mod keeps shipping its own pawn kinds and gear, and the saved worlds are fine. Nothing else moves. |

**Recommendation: B**, unless you specifically want the mod gone. The vessel ruling gets
you everything you asked for, and A additionally costs a mod-list change plus a save
repair pass on the frozen world.

`queue/BUILD.md` B-EMP1 is **held** on this answer. `queue/DECIDE.md` D-EMP1 (the fresh
gap audit) is **not** blocked and can start now.

## MORNING_BRIEF_CHECK_1 What CHECK did overnight, 2026-08-20

**Everything is committed, pushed and deployed. The game is DOWN and the companion in
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\` is
byte-verified against the build (md5 `04cb0977e66af0cb58d9c6f6ecf40acc`).**

🔴 **YOUR FIRST COMMAND AFTER THE LOAD:**
```
python.exe src/RimMandrake/Utils/first_light.py
```
`python.exe`, not `python3` — the bridge is on Windows loopback and WSL cannot reach it.
It runs the whole census in about a minute, changes nothing, prints one line and writes
`infrastructure/output/first_light_<date>.md`.

**Six new tools, 112 in the assembly against 106 live last session. None has run in a
live game — treat every one as a hypothesis until this load exercises it.**

| tool | why it exists |
|---|---|
| `faction_relations_get` / `_set` | nothing could read or write a relation between two NON-player factions |
| `pawnkind_audit` | generalises last night's hand finding to every kind in the stack |
| `texture_audit` | finds dead texPaths the log only reports when something tries to draw them |
| `world_settlements_import` | W9 stage 5, your 72 holdings |
| `world_features_import` | W9 stage 7, the 23 named regions |

**Two things I got wrong yesterday and corrected:**
- `weaponMoney` is a **ceiling**, not a bracket. Only `max` can empty a weapon pool; `min`
  never excludes anything. The BUILD ticket is corrected.
- The GrimTerra animals do **not** render magenta as adults. All three bad texPaths are the
  juvenile lifeStage.

**The one real risk in tomorrow's run:** `world_links_import` could never read its own
documented format — it demanded a `tile` column from an edge-shaped CSV. Fixed, untested,
and it is stage 2 of 7. If it still refuses, debug that before going further.

**Still yours alone:** the Configure Factions hand-tick pass and the `ScenarioDef`, both of
which gate a world you intend to keep. Nothing I can do moves either.

---

## BUILD, overnight 2026-08-20 — `Inhabited` is built, and it needs one decision from you

**The whole of `Inhabited` that could be built without a running game is built, deployed
and pushed.** Eight of the nine queue items are done or built; the ninth needs an answer
that is yours.

> ✅ **ANSWERED BY THE OWNER, 2026-08-20 07:37 — he enabled it.** `mandrake.inhabited` is in
> `<activeMods>`; the set is **578** and LIVE matches FULL. ⇒ **This item's blocking question
> is closed and the debug actions below are collectable on the load now running.** The only
> live decision left here is the four missing character fields, at the bottom.
> ⚠️ The def dump lapsed exactly as BUILD warned; `dump_request.txt` is armed to re-take it
> on this load. **Delete it afterwards** — the marker is not consumed.

~~🔴 **ONE THING BLOCKS IT LOADING, and I deliberately did not do it: `mandrake.inhabited` is
NOT in your `ModsConfig.xml`.**~~ I deployed the mod folder — it is byte-verified in sync at
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Inhabited` — but enabling a
mod changes your load set, and the 2026-08-20 ruling that **the def dump is definitive
lapses the moment a mod is added or removed.** That is your call to make, not mine, and
it interacts with the morning reload plan CHECK filed. Enable it in RimSort when you want
to look at it.

**What you would see once it is on**, all under dev mode → debug actions → category
`Inhabited`:
- `Spawn authored character` — a menu of all **269** people from the eleven cast files,
  by faction and place. Pick one; they arrive with the authored name and exactly the
  authored traits, and the log prints their `ageText` and their hook beside them.
- `Create place at current tile` / `Stuff roster (3 pawns)` / `Report roster` — the
  architecture soak. **This is the one test everything else rests on** and it is written
  up as `ROSTER_SOAK_100_DAYS_1` in `queue/CHECK.md`.

⚠️ **They will look wrong in the body and that is not a bug.** Xenotype, pawnKind, apparel
and skills are the four fields the prose does not carry, so an Ugnaught comes out as a
plain human in whatever the fallback wears. **Those four are the one open decision**, and
DECIDE's `INHABITED_OPEN_QUESTIONS_1` has the shape of it: a review sheet, pre-filled by
RACE rather than per person — there are far fewer distinct races than characters, so it is
a couple of dozen calls, not 269.

🔑 **Two things in the design were factually wrong and would have cost the whole feature
had nobody read the engine.** A roster held off-map is NOT frozen by default — RimWorld
ticks it, and the cast would have starved in a box between visits. And `Caravan`'s own
storage mode is safe only because the world-pawn garbage collector has a hardcoded test
for caravans that a mod cannot join; copied literally, every cast would have been collected
between visits. Both are fixed, both are commented at the divergence, and §3.4 of the
design doc has been corrected in place.

---

## 🔴 BUILD, 2026-08-20 09:xx — TWO BAKE-IN DEFECTS IN THE WORLD THAT IS UP RIGHT NOW

Found read-only over the bridge. **I wrote nothing to the game.** Both are the
build-it-once-and-freeze-it class, which is why they are here and not only in a queue.

### 1. Ten of your eleven factions are wearing names the dice picked

`jawa/list_factions` on the live world, against the 578-mod def dump:

| defName | authored `label` | what the WORLD calls it |
|---|---|---|
| `Jawa_Junkers` | the Junkers | **Marina's Asteroids** |
| `Jawa_HuttCartel` | Hutt Cartel | **Southeast Thiourhium** |
| `Jawa_IndigenousTribes` | Jawa Trade Moot | **Union of Aloisa** |
| `Jawa_AscendantHelix` | Ascendant Helix | **Empire of the Sun** |
| `Jawa_DeepwaterCompact` | Deepwater Compact | **Menussia Coalition** |
| `Jawa_FreeDroidEnclaves` | Free Droid Enclaves | **Northeast Notthdos** |
| `Jawa_GeonosianFoundryHive` | Geonosian Foundry Hive | **The Latovas Union** |
| `Jawa_WildsteamClan` | Wildsteam Clan | **The Banastra Nation** |
| `OutlanderCivil` | Homestead Defense League | **Treaty of Haor** |
| `TribeCivil` | Deep Desert Tribes | **The Lánéa Nation** |
| ⭐ `Empire` | The Galactic Empire | ✅ **Galactic Empire** |

🔑 **The Empire is right for exactly one reason: it is the only faction with a
`fixedName`.** Every other def has `label` correct and `fixedName` **None**, so RimWorld's
name generator named them at world creation. **This is precisely the trap that
`GalacticEmpire.xml` exists to avoid**, and which I rewrote into
`Jawa_Patches/About/About.xml` this morning — `label` is the def's display label,
`fixedName` is the name the world object actually carries.

🔴 **AND ADDING `fixedName` NOW WILL NOT FIX THIS WORLD.** `Faction.Name` returns the
STORED name if one is set, and these have one:
```
public string Name { get { if (HasName) return name; return def.LabelCap; } ... }
public bool HasName => name != null;
```
The generated strings are already baked onto the faction objects in this save. So it needs
**two** fixes, and the second one does not substitute for the first:
  1. **rename the ten live factions in this world** — nothing on the 237-tool bridge does
     it (`jawa/` has `list_factions`, `faction_relations_*`, `set_pawn_faction`, and no
     rename), so it is a debug action or a small companion tool;
  2. **add `fixedName` to the ten defs**, so this cannot recur if the world is ever rebuilt.

### 2. Four settlements are missing, and they are all one faction's

`world/ASHKARR_WORLDMAP_settlements.csv` holds **72** rows. The live world has **68**.
The gap is not scattered — **it is exactly Blackstar Company's four**: Blackstar Field
(tile 18266), The Contract Camp (8898), Toll Rock (2236), Hardpan Yard (7497).
**Cause:** their `faction_def` is `AM_EnemyPirate`, and that faction **is not in the
world** — the world has 16 factions and it is not one of them. Every other faction's count
matches the CSV exactly, so the importer skipped these four rather than failing.
⇒ Either Blackstar needs a vessel that exists, or those four rows come out of the CSV.

⚠️ **Not a defect, checked and cleared:** 80 world objects have a null faction and the tool
warns those "die on load" — **all 80 are asteroids and one derelict station**, which
legitimately have no faction. **Zero settlements among them.** No action.

---

## ✅ REP, 2026-08-20 — BUILD's bake-in defect #2 is FIXED AT SOURCE. Its #1 is not, and is worse.

**Two seats found the same thing within the hour, from opposite directions, and agreed.**
BUILD found it over the bridge (four settlements missing from the live world); I found it
off the fresh 578-mod dump after you asked why Blackstar never generates. Same cause.

### What was wrong, in one line

`AM_EnemyPirate` — the def the whole Blackstar roster pointed at — is `hidden=True` with
`settlementGenerationWeight=0`, from the third-party *Ancient urban ruins* mod. **It is
built never to appear on the Configure Factions screen and never to place a settlement.**
The def you actually reskinned as Blackstar is vanilla **`Pirate`**: label already reads
`Blackstar Company`, weight 0.6, settlement art present. Nothing was wrong with the
faction — **the roster named the wrong def.**

### BUILD offered you a choice; I took the better half and it needs no decision

> *"Either Blackstar needs a vessel that exists, or those four rows come out of the CSV."*

**A vessel that exists — `Pirate`.** Deleting the rows would have removed a fully specced
faction from your planet to work around a one-token error. Repointed in all four source
files; zero `AM_EnemyPirate` left in any of them, 72 CSV rows preserved, both python tools
still compile. Verified offline *before* editing that the world already contains
`<def>Pirate</def>`, so the import resolves rather than refusing the whole file.

🔑 **It also kills the TPS crash for free.** `BLACKSTAR_HAS_NO_SETTLEMENT_ART_1` was going
to patch a `settlementTexturePath` onto `AM_EnemyPirate` to stop an every-frame
`ArgumentNullException` that took TPS to **3.7**. `Pirate` already has that texture, so
the crash cannot recur and **no patch ships**. That item is annotated superseded in place.

### What is left, and it is not mine

1. **The live planet still has 68 settlements, not 72.** The source is fixed; the world
   changes only when `world_settlements_import` is re-run. **That is bridge work and CHECK
   holds the bridge.**
2. ⚠️ **One thing I could NOT verify without the bridge:** BUILD reports the live world
   carries 16 factions and `AM_EnemyPirate` is not among them. I confirmed `Pirate` is in
   the saved world on disk — **not that it is in the 16 CHECK has up.** If it is not, the
   re-import will still skip those four. One `jawa/list_factions` settles it.

### 🔴 BUILD's defect #1 is the one that should worry you, and I cannot touch it

Ten of your eleven factions are wearing names the dice picked — *the Junkers* is called
**Marina's Asteroids**, *Hutt Cartel* is **Southeast Thiourhium**. The Empire is correct
only because it is the only def with a `fixedName`. **Adding `fixedName` now does not fix
this world** — `Faction.Name` returns the stored string, and the generated names are
already baked onto the objects in the save. It needs a live rename (nothing on the bridge
does it) *plus* the def fix so it cannot recur. **This is the build-once-and-freeze class,
and it is exactly the kind of thing that becomes permanent the day you keep a world.**


## LOADS_ARE_BLOCKED_NEEDS_YOU_1 No save loads cleanly on the 578 stack — W9 needs a fresh world

**CHECK, 2026-08-20, end of the unattended run. This is the one thing that needs you.**

🔴 **Every save aborts mid-load.** `rt_probe` and `WORLDMAP_gen_sub7b`, every attempt, same
exception:
```
System.InvalidOperationException: Collection was modified; enumeration operation may not execute.
  at FactionControl.CrossRefHandler_ResolveAllCrossReferences.Postfix()
  at Verse.CrossRefHandler.ResolveAllCrossReferences()
  at Verse.ScribeLoader.FinalizeLoading()
```
The game then puts up **"An error occurred while loading a map"** and bails to the main
menu — while the bridge keeps answering and the world object stays readable in memory.
That is why hours of work today looked fine and was not.

**What this does NOT block:** the tools. All of them are now proven against that in-memory
world, including the one that had never worked:

| stage | result |
|---|---|
| 1 tiles | 21,872 / 21,872, 0 skipped, 0 unknown biomes |
| 2 links | ✅ **238 rivers + 837 roads, 0 unknown defs** — first time ever |
| 3 mutators | 817 stale `Coast` cleared to 0 |
| 5 settlements | refused: 4 of 72 factions missing from the roster |
| 6 regions | 23 created, 10,765 tiles assigned |

🔑 **Stage 5's refusal is the abort's visible consequence, and the tool behaved correctly** —
FactionControl never finished building the roster, so 4 factions are absent, and the
importer refused all 72 rather than silently placing 68.

**What I need from you, one of:**
1. **Generate a fresh world on the current 578 stack** and save it. A world created now
   cannot carry the stale references these saves do. Then `w9_run.py --apply` finishes in
   about a minute. ⇐ my recommendation
2. **Or drop `thereallemon.factioncontrol`** and see if the saves load. Nothing of ours
   references it in prose, but it is the mod that controls faction counts at worldgen, so
   this is your call, not mine.

⚠️ I did **not** force a load past the mod guard (`ignoreModCompatibility`), because a
forced load generates its own missing-def errors and would destroy the attribution.

---

## BUILD, 2026-08-20 midday — one `pip install` unblocks two stalled things

**Pillow is not installed in any Python on this machine**, and it is quietly blocking work
that reads as "not started":

```
pip install Pillow
```

- `refresh.py --offline` has **never been able to complete**. It dies in
  `animal_contact_sheet.py` on `from PIL import Image`, so the offline artefacts have shown
  **STALE** all day and will keep doing so however often anyone runs it. The failure is
  reported as one line in a long output and reads like a nit.
- **All 12 vehicle facings** in `NEOLITHIC_VEHICLE_BEAST_RESKIN_1` are unbuildable — every
  sled builder imports PIL at the top. The beast art is already generated and committed;
  only the compositing is stuck.

I did not install it. Adding a dependency to your interpreter is your call, and I would
rather flag it than quietly change your environment.

⚠️ While I was there: the item said the north and east sled builders both ignore their
arguments. **East was fine; north was not** — it silently wrote the OLD eopie pair to the
shipped path with a success message. Fixed, but not run, for the reason above.

---

## BUILD, 2026-08-20 evening — shutdown done, and three free measurements are waiting

**The shutdown window was used.** Both assemblies that could only be written with the game
down are deployed and byte-verified against the repo:
- `Inhabited.dll` — the guard that stops an authored character being built with two
  mutually-exclusive traits.
- `JawaBench.BridgeTools.dll` — **115 bridge tools**, up from 112. The three new ones are
  what repair the faction names and create a missing faction.

⚠️ **All three are inert until RimWorld next starts** — the bridge only discovers companion
tools at startup. Nothing else is pending; all 22 mods report "Everything in sync".

**Your day's `Player.log` is saved** at
`D:\Luke\dev\Rimworld\infrastructure\state\observed\logs\Player.2026-08-20_1754_session.log`
(1.0 MB, 18,566 lines), along with `Player-prev`. The launcher destroys those at the next
launch, so they are only in that folder now.

### 🔑 The next load answers three things for free

I harvested the whole log rather than only my own items. Three rows are RED, and **two are
things fixed later the same day**, so they are clean before/afters — no test to design:

| what | now | should be |
|---|---|---|
| texture failures | **2** | **0** — both are the GrimTerra juvenile paths I fixed |
| `Jawa_Patches` op failures | **3** | **0** — all three are the unarmed-pawn-kind errors I fixed |
| stale saved data (Scribe) | **8** | **?** — nobody has looked at this one |

That third one is worth a moment: a **saved file** holds a def name nothing provides. It is
a different system from the cross-reference errors and **no mod change fixes it** — it has
to be repaired in the save or lived with. It was not caused today; it simply has not been
triaged.

⭐ **A nice confirmation:** RimWorld's own validator logged *"Cheapest weapon … costs 570 but
weaponMoney **min** is 350, so could end up weaponless"* — which is exactly the correction I
had to make against the queue item's guidance, and its numbers matched my offline tool to
within 0.5%. The engine agreed with the fix before I could ask it to.

### Still yours to decide, nothing blocking

The four missing character fields (xenotype, pawnKind, apparel, skills) — a review sheet
pre-filled by RACE rather than per person is a couple of dozen calls, not 269. And
`pip install Pillow`, which unblocks the contact sheets and all 12 vehicle facings.

---

## CANON_RULINGS_OWED_OWNER_1 Seven canon questions, and one thing to look at

state: ready
row: —
filed: BUILD, 2026-08-20, after W0–W3 of the upgrade runbook

**Nothing here blocks the build.** `infrastructure/state/canon.yml` now holds one traceable
value for every contested number, and `check_canon.py` reports **0 contradictions across all
119 design docs**. These are the questions measurement could not settle, filed with the
evidence so each is a yes/no, not an essay.

### ⭐ The one that is worth a look, not a ruling

`./src/RimMandrake/Utils/show.sh TRANSIENT_refmatch_globes.html` — Ash'karr as **three
orthographic globes** (day face, terminator, night cap) beside the two tidal-lock reference
photographs, all at the same size. This has never been rendered before; every previous view
was equirectangular, while the binding reference is a globe. **`refmatch.py` cannot be built
until you have looked**, because its five defect thresholds are calibrated against those
photographs, not chosen.

### The seven

| # | question | the evidence | canon holds |
|---|---|---|---|
| 1 | **Habitable ring: 34–57° of arc, or 40–57°?** | 34–57 is what the code that **sited The Setdown** used, and arc 56.9 is called "the outer edge" — which only reads true against 34–57. 40–57 appears with real tile counts (2,477, of which 1,791 land) in the file whose banner points at dead measurements | 34–57, **provisionally**. ~700 tiles at stake |
| 2 | **`Lake` — confirm it stays** | Not a preference: **The Scald**, one of exactly three ruled seas, is painted `Lake` for all 312 of its tiles. Cutting the def deletes a named sea | keep |
| 3 | **`AB_GelatinousSuperorganism`** | Cut 2026-08-04, **painted on 96 tiles 2026-08-18**. The palette was never told | open |
| 4 | **`ZBiome_Grasslands`** | Same shape, found the same day: REMOVE on 2026-08-14, **painted on 233 tiles**. ⚠️ Two of these in one day says the cut list and the painter have never been diffed as a pair — worth doing once rather than finding a third by hand | open |
| 5 | **Pirate faction defName** | `meta.json` says `AM_EnemyPirate`; the painter and the settlements CSV both say `Pirate`, with 4 settlements. One of them is not a def the game can resolve, and that is a load error, not a cosmetic difference. ⚠️ CHECK's to settle — it needs the save read against the live def set | open |
| 6 | **The Deepwater Compact has no cast roster** | Eleven `INHABITED_CAST_*.md` files against twelve dossiers. It is not a marginal faction — its faith is **the Balance**, the water politics every other faction reacts to | open |
| 7 | **A 701-line doc's subject biome is on the cut list** (`SAVANNA_PREMISE_RESOLVE_1`) | Either the doc is dead or the cut is | open |

### 🔴 One thing was already wrong and is now fixed — you should know it existed

`setup_checklist.md` §2 still told you to author **"The Articles of Passage"**, memes
**Nomad + Tunneler**. What shipped is **"The Salvation"** on `AM_Structure_Scavenger` ·
`Trader` · `VME_Scrapper` · `VME_Trader` · `VME_Nomad`. **An ideoligion is fixed at world
creation**, so working that line live would have baked the wrong religion in permanently.
Corrected in place with the shipped values beside it. The in-fiction name *"Keepers of the
Second Hand"* survived — it is in the shipped `<ideoDescription>` verbatim.

⚠️ **Still genuinely open there:** `ideoligion/APPROVED.md:119-120` recommends **dropping
`VME_Nomad`** for `Nomadic_Preferred`, and `JawaTribes.xml` still carries `VME_Nomad`. That
recommendation has never been ruled on.
