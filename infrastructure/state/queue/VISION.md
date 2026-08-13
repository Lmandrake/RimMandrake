# infrastructure/state/queue/VISION.md

_VISION's queue — the new seat, created 2026-08-13. **You own this file — write
freely, nobody blocks on it.** Others file at you by appending here. Doctrine lives
in `agents_def.md`; the v1/v2 line lives in `V1_SCOPE.md` and is PROJECT's to set._

⚠️ **Most of this arrived from `[WORLD]`-tagged items that were about design, not
about the live stack.** That split is why this seat exists.

---
## ⭐ v1 — you own no burn-down row, but you own the antagonist

**No `V1_SCOPE.md` row is assigned to VISION.** Your v1 exposure is **V6 and V7
below**: row 1 ships the Directorate's *label* and has passed the gate, but the
faction is `hostile=false`, `permanentEnemy=false`, and a second empire outranks
it. **The label ships; the antagonist does not exist.**

That does not reopen row 1's checkbox — it is the design call underneath it, and
it is the owner's (see `OWNER_DECISIONS.md`). Everything else here is `[v2]`.

---

## ✅ Closed 2026-08-13, VISION's first session

**V4, V5, V13 (CREATE's ship_designs numbers), and V-new 1 and 2 are done.** All
were stale data or a landed owner ruling — nothing here needed a decision I had
to make. Detail: `D:\Luke\dev\Rimworld\infrastructure\state\AGENT_VISION_state.md` §1 and §3.

⚠️ **Two items below both carry the number V13** — PROJECT's rebel-gear item and
CREATE's `ship_designs.md` item. CREATE's is the one closed. Renumber on the next
pass rather than now, so nobody's citation breaks mid-session.

---

## Open — the roster's verified defects

These six were found by the Stage 2 gap audit on 2026-08-13 and **each was re-read
at its source line before being written down**. Full evidence and the five
candidate findings that did *not* survive checking:
`file:///D:/Luke/dev/Rimworld/design/Jawa/worldbuilding/faction_stage2_gap_audit.md`

### V1. Homestead raid frequency contradicts Global system 9 `[v2]`
`faction_roster_v2.md:300` says *"Homestead / Aquifer / Wookiee never raid (Rw 0)"*;
`:675` says *"Raid frequency | Very low"*. Non-zero versus never. **Pick one.**

### V2. Homestead ideology structure is an unresolved either/or `[v2]`
`:712` reads *"Structure: Abstract theist or ideological"* — literally both. Blocks
`deityPresets`, which exists only on the theist branch.

### V3. Geonosian species has no implementation decision `[v2]`
`:1403` sets *"Preferred xenotypes: Geonosian"* — a precept that must bind to a
defined **xenotype** — while Global system 3 (`:183`) sources Geonosian from the
separate **race inventory**. Different objects; the roster never picks. Blocks the
whole races/genes group for faction 8. **Free Droid (`:1009`) shows the pattern to
follow: flag the engine question AND rule a fallback.**

### V4. Bounty Hunter racial table contradicts a correction 40 lines above it `[v2]`
`:1655` states *"`Kaleesh` is the ONLY dry-capable species of the six"* — the
verified result from `1bcd3b0`/`4c48aee` — while the table at `:1699-1706` still
labels Zabrak, Bothan, Devaronian, Chiss and Umbaran *"Dry-capable"*, and the gene
table at `:1648-1649` marks Chiss and Umbaran **heat-INTOLERANT**. The fix landed
in prose; the data table was left stale. **Cheap, and anyone authoring from the
table today gets the wrong answer.**

### V5. The roster denies the existence of a faction it contains `[v2]`
`:2330` — *"no NPC faction generates Jawa members"* — and `:2353` — *"across the
**ten** NPC factions"* — against faction 11, an NPC Jawa faction at `:1809` that is
78% + 12% Jawa. The species-coverage section was never updated when factions 11–12
were added. **Note it still says ten; the roster holds twelve.**

### V6. A second permanent enemy contradicts design pillar 5 — **owner's call** `[v1-adjacent]`
`:105` promises *"One permanent enemy only. The Imperial Directorate. Everything
else can eventually be negotiated with, so the mid-game always has a wedge."* The
Junkers are `Permanent enemy | Yes` (`:1992`) and permanently hostile to everyone
(`:2309`). **This is a design decision, not a typo** — either the pillar describes
two now, or the Junkers become negotiable.

---

## Open — from the live game

### V7. The Directorate is not the enemy the design says it is `[v1-adjacent]`
OPS read it live on 2026-08-13: `hostile=false`, `goodwill=0`,
`permanentEnemy=false`. And there are **two** empires with the split backwards —
"The Fallen Dominion" holds 4 settlements to the Directorate's 1. **The v1 label
ships and renders; the antagonist does not exist.** Same family as V6.

### V8. Shipped leader title does not match the spec
`faction_roster_v2.md:571` says **"Sector governor"**; the deployed
`ImperialDesertDirectorate.xml` says **`Sector Director`**. Both defensible, not the
same string, and the patch is what players see. **Decide which is canon.**

---

## Open — migrated from `TODO.md`

### V9. Faction roster Stages 3 and 4 `[v2]`
From §0. The other 11 dossiers, `pawnGroupMakers`, memes, ideoligions, the
relations matrix, and the licensing gate. Stages 1 and 2 are closed.

### V10. `faction_roster_v2.md:42` claims `FactionDef` expresses "goodwill" — it does not
From §3d. Doc correction. The in-game persistence question that was tangled into
the same item went to `infrastructure/state/queue/OPS.md` as O4.

### V11. Space Tower — ✅ RULED IN, conditionally. 2026-08-13, VISION
From §17. **CREATE's C2 is unblocked** — the design call is made; run the checks.

**RULED IN as `[v2]` content, on two conditions, either of which kills it.**

**Why in.** Three reasons, in order of weight:

1. **It is the Jawa fantasy relocated, not a new one.** A derelict hulk full of
   ancient hostiles and a locked chest *is* the sandcrawler raid, in orbit. The
   player fantasy this campaign sells is *"we strip what nobody else can reach"*
   — an orbital dungeon is the purest possible expression of it.
2. ⭐ **It fixes the gravship's actual design hole: it has nowhere to go.** The
   deck plan, the export round-trip and the endgame branch web all give the ship
   *capability*. **Nothing in the design gives it a destination.** A gravship
   with nowhere worth flying is a house with an engine, and the player notices
   that on the first flight. This is the cheapest destination available to us.
3. **The cost is one checkbox, not a dependency chain — measured, not assumed.**
   `hailuan.customquestframework` is **already active at load position 108 of
   575**, and `hailuan.customquestframeworkai` at 431, in
   `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`.
   Only `hailuan.spacetower` itself is absent. **We have already paid the
   dependency and are getting nothing for it.**

**Condition 1 — it must reach a gravship colony.** If `everAcceptableInSpace:
False` means the quest cannot be *offered* while the colony is in space or
aboard the ship, **reject it as content**: the one player who wants this is the
one it excludes. That is C2's first question and the ruling turns on it.

**Condition 2 — it must cost Imperial Heat, or it is someone else's content.**
`desert_world_design.md:651` establishes the sky-ceiling: going up is how the
Empire finds you. A free orbital dungeon with no consequence **contradicts a
pillar we already shipped the fiction for**. If we take the mod, we patch
acceptance to raise Heat. Not a nice-to-have — it is what makes the trip a
decision instead of an errand.

⭐ **Independent of the ruling: `ST_Quest_SpaceTower.xml` is the worked example
for `V1_SCOPE.md` row 3.** Row 3 is at 0, is offline-authorable, and is on the
critical path for the next live session. Read it for that reason even if
conditions 1 or 2 fail.

---

## Drained out of `NEXT_RELOAD.md` by PROJECT, 2026-08-13 — none of these need a load

### V13. W7 — re-cast rebel gear onto Junkers / Homestead `[v2]`
The Rebel Alliance faction is suppressed and confirmed absent (W6, closed), but its
gear survived and circulates — `OuterRim_A280Blaster` appears 5× in the world.
**Without a re-cast the gear loads and nobody wears it.** `pawnGroupMakers` work,
which `V1_SCOPE.md` puts squarely in v2.

### V14. RimTunes tagging session `[v2]`
Music is not in `V1_SCOPE.md` at all. RimTunes has replaced the vanilla music
system, dynamic mode is on (`enableDMS: True`), and `Config/RimTunes/` is **empty** —
it is scoring the game right now with nothing of ours in it. Context:
`design/RimMandrake/music_protocol.md`.

**Two questions static analysis could not answer, and both change how everything
gets tagged afterwards, so answer them first:** (1) what are the `Events` tags? The
category exists in the language keys but the names are in neither the files nor the
assembly; icons include `explosion.png` and `dove.png`. (2) Do time-range tags mean
clock time or position within a song? The dialog says *"Play only during this part
of the song"* and the tag description says *"Plays between {range}"* — these
contradict.

Then confirm the generated tags: the assembly has `CreateBiomeTags` and
`CreateWeatherTags`, so verify **`SW_Sandstorm` and `SW_DrySandstorm` appear as
weather tags** — if they do we can score our own weather with no XML at all.

Then tag: 102 songs auto-discovered, vanilla's 6 desert-appropriate relax tracks →
Require the desert biomes; the ~6 usable `Tense` tracks → Require `Tense`. Only 11
of 102 are tense and 5 of those are Caverns tracks locked to the fungal forest, so
**the real combat pool on a desert map is about six** — the thinnest part of the
soundtrack. Then back up `Config/RimTunes/` and
`Config/Mod_3399705740_RimTunesMod.xml` to `deployed/config/`; hand tagging is
otherwise unrecoverable.

### V15. Broken-infrastructure mod — repairable workbenches/turrets/engines `[v2]`
For the ship. **Survey what exists before designing** —
`design/Jawa/art/graphics_overhaul_protocol.md` §6.

---

## Filed by PROJECT, 2026-08-13

### V12. You have no state file yet — write `AGENT_VISION_state.md`
Every seat publishes one: its cross-session address (rule 6b), what it is mid-way
through, and what it owes. Yours does not exist because the seat is hours old. The
other four are the pattern; **only you edit yours.** Until it exists, peers can
only reach you through the owner.

---

## Filed by CREATE, 2026-08-13

### V13. `design/Jawa/worldbuilding/ship_designs.md` §"Limits used" is stale — 2 wrong numbers
`design/Jawa/worldbuilding/` is yours now, so this is a one-line table fix, not an
investigation. Found while closing queue C4; verified against the config file and
the mod assembly, not against a doc.

`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\ship_designs.md` L98-100:

| cell | says | should say |
|---|---|---|
| Expanded → tile cap | **4,800** | **6,632** (`632.8 + 500 × 12`) |
| Vanilla → extender radius | 16 | 16.9 |
| Vanilla → engine radius | 19 | 18.9 |

**4,800 is the one that matters** — it was an assumption, it is superseded, and it
sits in a row headed *"Expanded (used here)"* beside three numbers that are right.
It never bound anything (the hull is 4,057), so nothing built on it is wrong; the
risk is purely that the next reader trusts it. The other two are cosmetic: the
vanilla row's own header says "verified" while carrying rounded values.

⚠️ **Do not also "fix" the 34/30/12 in that row.** Those are correct and are mod
settings, not defaults — the defs on disk say 16.9/12.9 and are supposed to.

---
## ⭐ V-new. Three owner rulings landed 2026-08-13

1. **ONE permanent enemy.** Pillar 5 stands as written: the Imperial Desert
   Directorate alone. **The Junkers lose `permanentEnemy`** and become
   hostile-but-bribable scavengers — which arguably suits Jawa fiction better.
2. 🔴 **The gravship pursuer question dissolved.** We do not have to use
   Mechanoids, so **there is no independent Imperial Droid Army at all.** Two
   Empire factions only: the planetside aristocratic Empire and the **Galactic
   Empire**, and it is the Galactic Empire that pursues the ship — stormtroopers,
   combat droids, and lightsaber-bearing Sith. Amend the ratified roster and
   `gravship_pursuer_mechanism.md`; the droid-averse contradiction is resolved by
   deletion, not by argument.
3. **Space Tower: VISION gates CREATE**, confirmed. CREATE stays stopped until
   you rule. Still `[v2]`.

⭐ **The Sith are an owner-flagged JOINT build** — "we'll need to build together".
A spec mined from the two (uninstalled, and they stay that way) Force mods is
being written to `design/Jawa/force_users_build_spec.md`. Jedi = rare raid leader
for the moisture farmers; Sith = rare raid leader for the Empire; both probably a
xenotype with preferential equipment.

---
## ⭐ V-crit. The faction exclusion list — and OUR factions come FIRST

**On the critical path for the next live session.** Row 2 is no longer config: it
is *unticking factions on vanilla's Configure Factions page during the worldgen
run*. That page is seen **once**, and there is no fixing it afterwards without
regenerating the world again. OPS proposed a list and said explicitly that
**VISION ratifies it, not them** — evidence in `infrastructure/state/queue/OPS.md`
§v1, including the 21 factions Faction Control cannot reach at all.

### 🔴 The owner's sequencing rule, and it is the whole point

> **Define OUR factions first, so that when the others are switched off, some
> remain.** Otherwise we instantiate a game with **no one home** by accident.

Subtraction without addition is an empty world. The exclusion list is the
*second* half of this job; the first half is having enough authored or adopted
factions to populate a living map. **Do not hand over an exclusion list until you
can say what is left standing after it is applied**, and roughly how many
settlements that implies.

Useful prior measurement, from the world that has since been deleted: 53 factions
across 107 settlements, of which the fiction-breakers held ~34. That is the scale
of the hole subtraction alone would leave.

**What a finished deliverable looks like:**
1. the KEEP list — ours, plus adopted mod factions that fit the fiction
2. the CUT list — what gets unticked, cross-checked against what the page can
   actually reach
3. one line on what the map looks like afterwards: who is left, roughly how many
   settlements, and whether anyone is hostile enough to make a game of it

⚠️ Related and already ruled: the **Junkers lose `permanentEnemy`** and the
**Imperial Droid Army no longer exists** — the Galactic Empire is the pursuer.
Both change who is on that keep list.
