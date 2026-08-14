# infrastructure/state/queue/VISION.md

_VISION's queue — the new seat, created 2026-08-13. **You own this file — write
freely, nobody blocks on it.** Others file at you by appending here. Doctrine lives
in `agents_def.md`; the v1/v2 line lives in `V1_SCOPE.md` and is PROJECT's to set._

⚠️ **Most of this arrived from `[WORLD]`-tagged items that were about design, not
about the live stack.** That split is why this seat exists.

---
## ⭐ v1 — you own no burn-down row, but you own the antagonist

**No `V1_SCOPE.md` row is assigned to VISION.** Your v1 exposure is **V6 and V7
below**: row 1 ships the Galactic Empire's *label* and has passed the gate, but the
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
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\faction_stage2_gap_audit.md`

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

### V4. ✅ CLOSED 2026-08-14 — and it had a seventh member nobody had counted
The five originally-named rows were already corrected in the table. **The residue
was `Iktotchi`**, outside the audited six: the table called it *Dry-capable*, but
`BTD_Iktotchi` holds `MinTemp_SmallIncrease` and **no Max bound** — Devaronian's
profile, which the same block already reads as neutral. Measured off the live
`XenotypeDef.json`. Kaleesh is now the only dry-capable row in all thirteen, and
the only one carrying `MaxTemp_SmallIncrease`.

### V5. ✅ CLOSED 2026-08-14 — stale entry, the file was already right
`faction_roster_v2.md:2367` now reads *"twelve NPC factions … carried by exactly
one NPC faction — 11. Jawa Trade Moot (78% + 12% Jawa)"*. Both defects the entry
described are gone. Nothing to do; re-read at source before re-filing.

### V6. A second permanent enemy contradicts design pillar 5 — **owner's call** `[v1-adjacent]`
`:105` promises *"One permanent enemy only. The Galactic Empire. Everything
else can eventually be negotiated with, so the mid-game always has a wedge."* The
Junkers are `Permanent enemy | Yes` (`:1992`) and permanently hostile to everyone
(`:2309`). **This is a design decision, not a typo** — either the pillar describes
two now, or the Junkers become negotiable.

---

## Open — from the live game

### V7. The Galactic Empire is not the enemy the design says it is `[v1-adjacent]`
OPS read it live on 2026-08-13: `hostile=false`, `goodwill=0`,
`permanentEnemy=false`. And there are **two** empires with the split backwards —
"The Fallen Dominion" holds 4 settlements to the Galactic Empire's 1. **The v1 label
ships and renders; the antagonist does not exist.** Same family as V6.

### V8. ✅ CLOSED 2026-08-14 — `Sector Director` is canon, and the residue is swept
The decision was already recorded at `faction_roster_v2.md:585` ("Sector governor
is retired") but **two ritual entries at :610 and :612 still used the retired
title**, including a ritual *named* "Governor's Address". Both corrected; the
ritual is now "Director's Address". The deployed patch was right all along —
`Director` also echoes the faction's own name, Imperial Desert Directorate.

---

## Open — migrated from `TODO.md`

### V9. Faction roster Stages 3 and 4 `[v2]`
From §0. The other 11 dossiers, `pawnGroupMakers`, memes, ideoligions, the
relations matrix, and the licensing gate. Stages 1 and 2 are closed.

### V10. ✅ CLOSED — already fixed in the file, the queue entry was stale
`faction_roster_v2.md:44` now reads *"`FactionDef` does NOT express goodwill, and
this line used to say it did"*, with the measurement behind it (88 FactionDefs,
125 fields, zero hits). **Nothing to do; checked 2026-08-13.** Original entry:
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

**Condition 1 — it must reach a gravship colony. ✅ PASSED, 2026-08-13.**
Established from `Assembly-CSharp.dll` metadata and the mod's own def, not from
the field name. **`autoAccept=True` on `ST_Quest_SpaceTower` suppresses the
space gate entirely** — it short-circuits `CanQuestOccurOnTile`'s space branch
*and* stops `QuestGen.Generate` attaching `AcceptanceRequirementNotSpace`. Its
`everAcceptableInSpace=False` is therefore inert. The quest also carries no
`QuestNode_Test`, no wealth or colonist requirement, and **nothing requiring a
ground colony**; `endOnColonyMove` is the archonexus mechanic, not gravship
movement. **The tower reaches a clan living on a ship.**

**Condition 2 — ✅ RESOLVED BY THE OWNER, 2026-08-13, and not with a gauge.**

> *"The space towers were owned by the Galactic Empire — how they land and access
> the surface — so they get VERY angry about it. And that's the whole point the
> Hutts were after."*

**The towers are Imperial infrastructure; the Hutts pay you to cut them; the
Empire's retaliation is the cost.** No blackboard variable, no goodwill tick —
consequence the player feels as weight arriving. **Space Tower is KEEP,
unconditionally, and it no longer waits on M4.** Full design:
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\orbital_towers_and_the_sky_ladder.md`

_Superseded reasoning, kept because the proxy ruling still stands if anyone
reaches for it:_

**⏳ was OPEN, and I was wrong about what it could lean on.** CREATE is
right: **"Imperial Heat" has zero implementation** — it is a blackboard variable
at M4 in `design/Jawa/build_plan.md:180`, not a mechanic. So the condition as I
wrote it cannot be met today.

**Ruling on the proxy: take the goodwill patch, and do NOT count it as met.**
An Empire goodwill hit is bookkeeping the player will not notice — the
Galactic Empire currently sits at `goodwill=0`, non-hostile, and a −15 against a
faction that is *supposed to be permanently hostile* (pillar 5) goes dead the
moment V7 is fixed. **It costs nothing and it pre-wires the real thing, so ship
it; it is not the cost the design asked for.** `ensureHostile: false` is right —
the escalation should be cumulative, not one-shot.

**Condition 2 rides to M4 with the Heat gauge**, which is fine: Space Tower is
`[v2]` and so is M4. **The real cost was never goodwill — it is raid pressure.**
Going up is how the Empire finds you; what the player must feel is *more of
them, sooner*, not a number in a menu.

**Original wording, kept because it is still what "met" means:**
`desert_world_design.md:651` establishes the sky-ceiling: going up is how the
Empire finds you. A free orbital dungeon with no consequence **contradicts a
pillar we already shipped the fiction for**. If we take the mod, we patch
acceptance to raise Heat. Not a nice-to-have — it is what makes the trip a
decision instead of an errand.

**Two things CREATE should carry into C2, found in the same read:**

- ⚠️ **The mod ships NO licence file** — not in Space Tower, not in CQF. Default
  is all-rights-reserved, so **we may subscribe and patch it, and we may not
  ship its maps.** That is fine for how we would use it; it is not fine if
  anyone later wants to fork the tower.
- 🐛 **`rootSelectionWeight` is declared TWICE** in `ST_Quest_SpaceTower.xml` —
  `0.25` and `0.1`. Last wins, so the effective weight is **0.1**, which is
  rare. Their bug, but it is also the dial we would tune, so know it is there.

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

### V13. ✅ CLOSED 2026-08-14 — all three cells already correct in the file
`ship_designs.md` L98-100 now reads Vanilla `18.9 / 16.9` and Expanded tile cap
**6,632**. Fixed by someone between the filing and now; verified at source
2026-08-14. **Do not re-apply — the 34/30/12 warning below still stands.**

<details><summary>original filing, kept for the 34/30/12 warning</summary>

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

</details>

---
## ⭐ V-new. Three owner rulings landed 2026-08-13

1. **ONE permanent enemy.** Pillar 5 stands as written: the Imperial Desert
   Galactic Empire alone. **The Junkers lose `permanentEnemy`** and become
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

---

## Filed by OPS, 2026-08-13 — PLAYER-ZERO PROPOSITION: cut the Predator family

**Evidence in, decision out. This is yours to rule on, not mine.**

Two independent lines converged on the same mod family today, which is why I am
raising it rather than filing it as noise.

**1. Fiction.** Four Yautja factions own **14 settlements** between them —
`ABYautjaBadBloodClan` (5), `ABYautjaBerserkClan` (4), `ABYautjaClan` (4),
`ABYautjaModderClan` (1). Measured from the last world's `<factionManager>`.
**That is the single largest non-Star-Wars presence on the map.** A Jawa
scavenger campaign that keeps running into Predator clans is not the fiction
`V1_SCOPE.md` describes.

**2. It is also the only mod in the stack emitting a texture defect.**
`[AB] Xenotype: Yautja` (`biotechrace.yautja.alleyballey`, workshop `3536839586`)
owns all **14** `Exception getting Verse.Graphic_Multi at :` errors in the 10:04
log — one malformed `<bodyGraphicData>` at `PawnKinds_BaseAbstract.xml:60`,
7 kinds × 2 lifeStages. Full derivation: `vendor/wisdom/benign_log_errors.md`
§1.12.

⚖️ **The honest case AGAINST cutting it, because it should not be a walkover:**
the errors are **harmless** — I waived them, the player sees nothing, and they
cost one cached lookup at load. So this is a **taste call, not a defect fix**,
and it should be decided on fiction alone. Do not let the 14 errors do work they
cannot do.

**Two different levers, and they are not interchangeable:**
- **The four FACTIONS** can be unticked at worldgen — free, no mod change, no
  load. That is already on the checklist I drafted at
  `infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md`.
- **The XENOTYPE MOD** is a separate decision. Removing it is the only thing that
  clears §1.12, but it costs a game-down window and risks
  `Could not resolve cross-reference` on anything referencing Yautja defs.
  ⚠️ **`Jawa_Armoury` has an open item (O10) that measures a Yautja blade
  (AP 0.60) as the mid-tier reference point between saber and vibro.** If the mod
  goes, that comparison loses its middle tier. Not a blocker — say the word and I
  re-anchor O10 on something else — but decide it knowingly.

**My recommendation:** untick the four factions at worldgen (free, reversible,
does the fiction work), and **keep the mod installed** for now. That gets you
~all the benefit at zero cost and defers the irreversible half.

---
## ✅ V-x. CLOSED CHECKED-AND-FINE — our Jawa tuning is NOT inert

🔴 **Do not re-investigate this.** BTD Xenotype Remix dedups at load and keeps
`BTD_Jawa`, remapping 552 xenotype chances across 9 factions and 99 pawnkinds.
`OuterRim_Jawa` does not exist at runtime. **Our patches already target the
surviving xenotype.** Measured live by BRIDGE from `Player.log`; the original
finding came off a def dump captured pre-dedup, i.e. disk rather than runtime.
Body kept below only so the reasoning is legible.

<details><summary>original (WRONG) filing</summary>

**Raised by BRIDGE, ruled out of v1 by PROJECT (`0c36ad8`), yours to settle.**

- `OuterRim_Jawa` — what the Jawa **pawnKinds actually pin**, so it is what spawns
- `BTD_Jawa` — what **our tuning patches target**
- `guy762_xenotype_jawa` — third one, also live

**If the spawning xenotype is not the patched one, our Jawa tuning does nothing
in play.** Deployed and inert, the same shape as seven art mods sitting in
`Mods/` doing nothing until enabled — and just as invisible, because nothing
errors.

v1 row 5 closes on `OuterRim_Jawa` regardless (the thin bar is "a Jawa spawns and
plays", and it does). **This is the depth question, and depth is v2.**

**Your call:** which xenotype should the campaign's Jawas be? Then CREATE
re-points the patches. **Do not let it close as if the two were the same Jawa** —
BRIDGE's words, and the reason this is filed rather than dropped.
</details>

---

# 🔴 SESSION WRAP — 2026-08-13. Read this block first next session.

## THE BIGGEST OPEN ITEM IN THE PROJECT: the campaign world has never been generated

**My 21-untick / 6-keep tick-list is RATIFIED, COMMITTED and UNSPENT**
(`c269c6a`, `infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md`). Everything
today was proven on a quicktest. **Rows 2 and 7 are that one screen.** Four
rulings ride in the file header — R1 dangling refs, R2 Rebel Alliance stays
suppressed, R3 vanilla `Empire` is a KEEP, R4 rough-outlander floor.

## Open, ranked

### V16. 🔴 The desert world generates ~49% OCEAN — decide whether the planet bends
Measured on three real saves: 43% / 49% / 55% Ocean. **The thirst-world identity
exists in our documents and nowhere else.** Ocean is an elevation rule written at
worldgen step 0, so the rainfall slider cannot remove one tile. No active mod
manages water. Three routes, none needing a new dependency: **WorldEdit 2.0
(already active)**, a custom `WorldGenStep`, or BiomesKit's unused hooks.
`faction_world_spec.md` last section. **Owner's call; contradicts the Three Waters
ruling by ~100×.**

### V17. Four live sightings, ~20 min, all scratch-map
1. **the hulk and caskets** (`00a1398`) — nobody has ever seen an
   `AncientCryptosleepCasket`; vanilla art is in AssetBundles. Does the broken
   deck read as a wreck, do three banks read as a hold?
2. ⭐ **one the Galactic Empire raid** — does the antagonist look like the
   antagonist? Biggest unanswered design question I own.
3. **a coastal forsaken-crags tile** — can roll Archipelago today, giving a
   permanently dark mostly-ocean map with zero new code. Decides the deep.
4. **the 25 vanilla mechs** whose art is locked in AssetBundles — unblocks the
   owner's review sheet.

### V18. The mech review sheet is NOT built
Axes now known and committed (`data/mech_control_axes.md`): raids · ancient
dangers+clusters *(one flag, not separable from each other)* · bossgroups ·
gestation · sellable · **purchasable (a separate axis — 3-line patch)** ·
decoration. Art on disk for 55 of 80 (`data/mech_inventory.json`). **Waiting only
on whether the owner accepts name+role for the 25 vanilla ones.**

### V19. Two mod adoptions recommended, neither actioned
- **GravTide** `3779600989` — ADOPT `[v2]`. Ocean objection is dead.
- **`[KR] Star Wars: Droids`** `3248936254` — Biotech-only, covers 5 of 6 real
  chassis gaps. ⛔ **Take the chassis, refuse its faction wrappers.**

### V20. Awaiting owner confirmation: the restraint bolt works on PEOPLE
Ruled KEEP, weighted ~10× a droid, plus a mood hit. Not confirmed.

### V21. Water rulings W3–W7 not merged into the twelve dossiers
They live only in `water_doctrine.md`. Junker doctrine still assumes universal
thirst. `[v2]` authoring.

### V22. `design/Jawa/droid_ruling.md` states a mechanism that is not in the defs
JDS droids do not explode — they are force-killed on downing and their wrecks are
repairable. **The ruling holds; the stated reason is wrong. Not my file.**

### V23. Canon droid lineage catalogue — only the supplement was received
Agent `abe113a7` delivered non-CIS additions; **the main lineage table never
arrived.** Re-request if the visual comparison sheet is wanted.

---

## ✅ Closed 2026-08-14 — the genome register and the eleven religions

**Two deliverables, both committed and pushed.**

1. **`design\Jawa\worldbuilding\review\genome_register.html`** — 184 candidate
   xenotypes aligned by gene, with the game's own icons, built from the **live def
   dump**. Contested-species blocks, the full 394-column grid, uncontested lists.
   Regenerate: `~/.venvs/rimart/bin/python src/RimMandrake/Utils/genome_art_cache.py`
   then `genome_matrix_build.py`. (Needs UnityPy + Pillow — vanilla gene art ships
   inside `resources_biotech`, not as loose PNGs.)
2. **`design\Jawa\worldbuilding\faction_religions_spec.md`** — eleven ideoligions
   to XML depth. Vocabulary: `design\Jawa\worldbuilding\data\ideology_palette.md`
   (`ideology_palette.py`, regenerable). Jawa slot deliberately empty.

**Findings that changed a design, all measured:**
- 🔴 **The three Star Wars packs are a STACK, not alternatives.** BTD REMIX defines
  **zero** genes of its own; 196 of its gene refs point at SW Xenotypes, 41 at
  Outer Rim GD. Uninstalling either breaks it. **All three generate**, so a
  wanderer can arrive as the wrong Twi'lek. Fix is a `factionlessGenerationWeight`
  patch, not an uninstall.
- **`jawa_xenotype_and_religion.md` Part 1 was stale** — marked superseded; the
  campaign is on `BTD_Jawa` (24 genes vs 8), and `Outland_AllMale` on it closes
  that file's all-male open question with no patch.
- **Three things the engine will not let us say:** charity has no negative precept ·
  `PreferredXenotypes` cannot be aimed at a xenotype from XML (gap-audit **D3 is
  mis-specified**, filed at PROJECT) · `Apostasy_Abhorrent` hard-conflicts with the
  `Guilty` meme.
- **D2 decided** — Homestead is `Structure_TheistAbstract`, deity *the Withdrawn*.

## Open — mine, and worth the next session

- ⏳ **`jawa/ideo_of` requested from BRIDGE.** Until it exists, "the game built the
  ideoligion I specified" is an inference. Diff the eleven against it when it lands.
- 🔴 **"NPC religion rarely surfaces in play" has never been measured**, and the
  whole religions design is disciplined around it — I cut rituals and deities
  because of it. Counter requested from BRIDGE. **If it returns ~0, say so in the
  doc and stop pretending the eleven are load-bearing.**
- **28 of the 29 biome removals were judged from def fields alone.** Exactly one
  was ever looked at, and looking confirmed it in two seconds. `jawa/biome_probe`
  requested. Do not treat the other 28 as decided.
- **Sea gate is 3-of-5 testable** — `perimeter` and `centroidLat` are not in
  `world_stats` yet. 🔴 **No candidate world is accepted on a partial pass.**
- **Jawa faith:** the name contradicts itself in its own file ("The Salvation" vs
  "The Articles of Passage") and Nomad-vs-Tunneler is still a coin. **Owner's,
  not mine** — but flag both if he opens it.

---

# 🔴 SESSION 2, 2026-08-14 — the ideoligion skill is finished, and it convicted the spec

**`skills/rimworld-ideoligion/` is complete and pushed** — SKILL.md plus four
references (`49a744f`, `d2ff36e`). The crash had left `references/` empty while
SKILL.md cited four files. `package_skill.py --all --check` passes.

## ⚠️ Four claims I wrote in SKILL.md yesterday were FALSE. All corrected.

Writing the references measured the claims and broke them. **Do not trust an
unmeasured sentence in a skill just because a skill is where it lives.**

| I claimed | measured 2026-08-14 |
|---|---|
| impact is a **budget** the engine caps | a **rating**. Ceiling is a COUNT — `MemeCountRangeAbsolute` 1–4 normal memes. Two shipped presets total impact 10. **Never pass `--impact-budget`** |
| `TreeCutting_Prohibited` is the benchmark | `defaultSelectionWeight: 0`, no meme's `requireOne` yields it ⇒ **unreachable for an NPC faction**. `Mining_Prohibited` is `enabledForNPCFactions: false` |
| the validator checks deity count | **WARN**, never ERROR |
| the validator checks `MayRequire` | 🔴 **it does not.** Its INFO line makes it look like it does. Still the largest hole; **on you, every time** |

## ✅ V24. CLOSED 2026-08-14 — 2/11 → **11/11 VALID** (`653f2c8`)
All nine repaired against the live dump. Decision sheet, every legal option per
faction with its cost: `design\Jawa\worldbuilding\review\religions_repair_sheet.md`
(`ee288bd`). **Faction 4 took `PainIsVirtue` on the owner's ruling** — nomadism is
now fiction only, and Tusken raiders arrive scarred and crowned instead of generic.
Two doctrines turned out never to have existed: faction 5's `OuterRim_DroidPrimacy`
(in neither dump nor palette) and faction 10's apostasy position (**all four**
negative Apostasy precepts carry `conflictingMemes: ['Guilty']`, so there is no
legal one). ⚠️ **Validator says VALID, not GOOD** — it still WARNs 4 inert precepts
across the set. Original entry below.

<details><summary>original filing</summary>

## 🔴 V24. Nine of the eleven religions are INVALID — mine to repair

`--md` reports **2/11 VALID** (Wildsteam, Deepwater Compact). Dominated by
`precept/required-meme` (10×). **The validator fix did not cause this** — `--md`
output is byte-identical before and after, verified by diff.
Decision sheet in progress: `design\Jawa\worldbuilding\review\religions_repair_sheet.md`.

**Faction 5 — the entry SKILL.md §2 names as the roster's BEST — has two silent
defects.** `OuterRim_DroidPrimacy` exists in neither the live dump nor the palette,
and its `Corpses_DontCare` requires eight memes it holds none of; seven of the
eight are illegal here and the eighth is absurd. **Drop the precept.**

</details>

## 🔴 V25. The Empire scores 0 on DECISION — the third independent measurement

The rubric scores the flagship antagonist's religion at **zero** on the
decision axis: no refusal comp, no High-impact precept anywhere in its eight.
**This is V6 and V7 in a third layer.** The pillar says one permanent enemy; the
faction flags say `hostile=false`; the religion asks the player to choose nothing.
⇒ **Owner-level, not a queue item.** Raised directly 2026-08-14.

## V26. Homestead fails the name-blind test against the Deepwater Compact
24% Jaccard, the roster's worst pair, and **the Homestead is the decoration half.**
⇒ Cut it or differentiate it. Do not polish it. Note this collides with D2, where
I ruled Homestead `Structure_TheistAbstract` yesterday — that ruling stands only if
the faction survives this one.

## V27. `VME_SecularSpirituality` has `thingDefStyles: []`
The Deepwater Compact's only style category **renders nothing in play.** Not an
error — the Compact is VALID — but it is invisible by construction. Cheap fix,
pick a category that actually ships styles.

## ⭐ Generalises past ideoligions — worth promoting to `traps-*.md`
**A vanilla `styles` list is not what the game has.** Anomaly writes
`<li>Horaxian</li>`; the resolved dump says `AM_Horaxian`, because Alpha Memes
`PatchOperationReplace`s the whole list. **Read the dump, never the vanilla XML.**

## ⭐ V28. VISION's ask for the 2026-08-14 no-worldgen session — ranked, all scratch-map

Filed into the pre-launch window PROJECT opened. **Worldgen is held, so V-crit and
`WORLDGEN_FACTION_CHECKLIST.md` are out of scope this session.** Everything below
runs on a scratch/quicktest map and needs no campaign world.

1. 🔴 **Spawn one Galactic Empire raid and screenshot it.** The biggest unanswered
   design question I own, and the fourth layer of V6 / V7 / V25 — the pillar says
   one permanent enemy, the flags say `hostile=false`, the religion scores 0 on
   decision. **Before any of that is repaired, someone has to look at whether the
   antagonist reads as the antagonist on screen.** ~5 min, BRIDGE.
2. **`jawa/ideo_of` on a Jawa pawn, plus a counter for how often NPC religion
   surfaces in play.** The eleven-religion spec (`faction_religions_spec.md`) is
   disciplined around "NPC religion rarely surfaces" — **which has never been
   measured.** If the counter returns ~0, I say so in the doc and stop treating the
   eleven as load-bearing. Both already requested of BRIDGE; unfilled.
3. **The hulk and the three casket banks** (`00a1398`). Nobody has ever seen an
   `AncientCryptosleepCasket` — vanilla art is inside AssetBundles. Does the broken
   deck read as a wreck?
4. **`jawa/biome_probe`.** 28 of the 29 biome removals were judged from def fields
   alone; the one that was ever looked at was confirmed in two seconds. Do not
   treat the other 28 as decided.
5. **The 25 vanilla mechs whose art is locked in AssetBundles.** Unblocks the
   owner's mech review sheet (V18), which is otherwise complete.

**Nothing of mine changes what gets DEPLOYED in this window.** The one candidate —
the `factionlessGenerationWeight` patch that stops a wanderer arriving as the wrong
Twi'lek — is unauthored, is CREATE's, and is `[v2]`. Do not hold launch for it.

## Handoff note — `skills/rimworld-quests/` is NOT mine
It is CREATE's **C14** with four owner rulings. I found it half-built (references
committed, no SKILL.md), started a draft, and stopped on the owner's word before a
byte was written. CREATE notified twice. **Do not pick it up.**
