# BMT_FAUNA_ABSORPTION_1 — donor corrected to biomesteam.*, ready to port

## Owner ruling, 2026-09-11 (question-card sitting)

Given the choice between (a) retargeting the item's donor to `biomesteam.*`
since the 71/41/30 figures are real and already ruled, (b) filing a fresh
keep-or-port sitting on the real `mlie.beastsoftherim`, or (c) leaving it
blocked — the owner picked **(a)**: the 71/41/30 figures are correct and
already ruled (`decisions_propagated.json`); the item named the wrong donor.

**Corrected scope for this item:** port the 71 `BMT_`-prefixed creatures (38
clean "in" + 30 "move" + `BMT_ChemSnail` resolved OUT per `biome_findings.md`
= 68 unique defNames landing; the "41 in" in the old queue line becomes 38
clean-in + `BMT_ChemSnail`'s conflict resolved as detailed below) from the
**`biomesteam`** family — `biomesteam.biomescaverns`, `biomesteam.biomescore`,
`biomesteam.biomespollutedlands` — into our own tier per the SWBestiary
donor-retirement pattern, then retire those three `biomesteam.*` mods.

`mlie.beastsoftherim` (the real 19-species/64-def donor) is UNAFFECTED by
this item — it stays exactly as it was in the Wave 2 stat-normalization audit
listing (its own keep-or-port sitting is separate, not required before this
item proceeds).

---

## FOUNDRY port pass, 2026-09-11 — 68/68 ported, retirement BLOCKED (see escalation)

Read directly from the three donor mods on disk (`BiomesTeam.BiomesCaverns`
2969748433, `BiomesTeam.BiomesCore` 2038000893, `BiomesTeam.BiomesPollutedLands`
3390196656 under the Steam workshop content folder) — not guessed, not
grepped from a stale dump. Cross-checked `decisions_propagated.json` (833
rows) against `biome_findings.md`: only one conflict exists system-wide
(`BMT_ChemSnail`, "in" at `the_cracked_lands` / "out" at `the_rot`) — see the
escalation below, this resolution is now in question.

**Port mechanics** (script-driven reference closure, not hand-typed): started
from the 68 target defNames, walked every `ParentName`, `Name=` (abstract
defs), leaf-text, and **dictionary-style XML tag** (`<butcherProducts><BMT_X>`
— the tag itself is the ref) reference until closed. Landed on **274** total
defs (68 species + 206 dependencies: bodies, eggs, leather/chitin/silk,
sounds, hediffs, damage types, life stages, one FactionDef for the pustule
hornet hive, one RulePackDef). Renamed `BMT_` → `RSW_` throughout (defName,
`Name=`, `ParentName=`, dictionary tag names, leaf-text refs — all four
reference shapes, verified zero leftover `BMT_`/`BiomesCore.` tokens outside
free-text tradeTags strings, which carry no def and were left alone).
Stripped every `modExtensions`/`comps`/`compClass`/`hediffClass`/`needClass`
field naming a C# class in `BiomesCore.*`, `BMT_PollutedLands.*`,
`PathfindingFramework.*` (inactive on this mod list) or
`VEF.AnimalBehaviours.*` (presence unconfirmed) — the creature keeps its
stats/body/art, not the donor-framework-only behaviour (pack defense,
lure-prey AI, filth trail, water-walker, dig-periodically, hermaphroditic-mate
job giver, corpse spawner, etc.); each def falls back to its vanilla base
class. Two non-resident adult forms (`RSW_RoyalRhino`, `RSW_ShatterjawBeetle`)
are ported as back-end `evolveIntoPawnKindDef` targets for their resident
larva/pupa stages — "out" for biome residency per the ruling, but required so
the vanilla evolve mechanism (confirmed vanilla, not donor C#) doesn't dangle.
440 texture files + all referenced sound-clip folders copied verbatim from
the donor's own `Textures`/`Sounds` trees, texPaths repathed to
`swanimals/BiomesTeam/<original path>` (audio to `Sounds/BiomesTeam/...`);
vanilla-Core reuse paths (`Things/...`, `World/...`) left untouched by design.

Output: `src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/{ThingDefs_Races,
ThingDefs_Items,Bodies,SoundDefs,Support}/RSW_BiomesTeamPort_*.xml`.
`validate_patch.py --defs <Data> --defs <Workshop> --defs <Mods>`: **0
errors** on 4/5 files; the 5th (`ThingDefs_Items`) flagged 2 as ERROR
(`RSW_Filth_Acidic_Snail_Slime`/`RSW_Filth_Snail_Slime` reusing vanilla
`Things/Filth/Spatter`) — **verified false positive**: that exact path is
used by vanilla's own `Filth_Blood`/`Filth_BloodInsect`/`Filth_Slime`
(`Data/Core/Defs/ThingDefs_Misc/Filth_Various.xml`); the validator mis-treats
`Things/` as claimed by this mod because SWBestiary already carries other
content under `Textures/Things/...`. 3 WARN on `RSW_Yooka` reusing vanilla
`Dessicated_Alpaca` — expected caveat (validator can't see packed
asset-bundle textures), Alpaca is a real vanilla animal.

### Live wiring found and repointed (NOT part of the original brief — found
while checking for dangling donor references)

The three donor mods turned out to be **already load-bearing** in already-
shipped RimUtinni content, gated with `MayRequire="biomesteam.*"` — retiring
them blind would have silently dropped these from the live game. Repointed
every occurrence whose defName is one of the ruled 68, `BMT_X
MayRequire="biomesteam.*"` → `RSW_X MayRequire="mandrake.rsw.swbestiary"`
(mirrors the pattern `SandFishing_CrackedLands.xml` already uses for
`RSW_DuneCrawler`): **27 wildAnimals/butcherProducts entries across 12 hand-
authored files** (`RUT_CrackedLands/Miasma/AridShrubland/Desert/FeverWood/
Greentide/Scarlands/PoisonForest/TheRot/Webwork/Wasteland.xml` +
`RUT_RotSporeKit_MantisScythe.xml`'s `BMT_FungalMantisClaw` butcher product),
plus **26 rows in `design/Jawa/fauna/cast_assignment.csv`** (defName + `mod`
column repointed to `RimMandrake: SW — Bestiary`, reason field annotated).

## ESCALATION — retirement is NOT safe yet, three open items

1. **`src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml` is
   GENERATED** (`design/Jawa/fauna/gen_cast_patch.py` from
   `cast_assignment.csv`, header says "do not hand-edit"). It still carries
   ~10 `PatchOperationConditional MayRequire="biomesteam.*"` blocks for
   in-scope species. The CSV source is now fixed (above), but regenerating
   correctly requires the generator's own packageId resolution, which reads
   `defName → packageId` from a **live def dump** — `RSW_*` won't resolve
   until SWBestiary's new defs are deployed and the dump refreshed. That's a
   deploy + dump cycle (CHARTER expensive-list territory), not something to
   run unattended from an isolated worktree. **Next step: deploy, refresh the
   dump, re-run `gen_cast_patch.py`, diff the result.**
2. **7 defNames are live and marked "keep"/"import" in hand-authored biome
   files but are NOT in the ruled 68** — `BMT_ChemSnail` (kept at BOTH
   `the_cracked_lands` AND `the_rot`, contradicting this item's own read of
   `biome_findings.md` as an "OUT" ruling — the_rot's "departure" list may
   only mean departs-from-the_rot, not cut-from-the-game, and the
   cracked_lands copy was never touched by the round-2 review at all),
   `BMT_CaveSpider`, `BMT_GiantSlug`, `BMT_GiantSnail`, `BMT_Pillbug`
   (all "departures" from `the_rot` per `biome_findings.md` but still live
   with `MayRequire` gates on the donor — the live wiring in `RUT_TheRot.xml`
   predates the round-2 review and was never updated to match it),
   `BMT_GlowBat` (biome_findings.md: "flier extracted" from `the_rot` — a
   different subsystem, possibly still needing a home). Left untouched
   (still gated on the retiring donor — will silently stop spawning, not
   error) rather than guessed into the port. **Needs an owner/BENCH call**:
   either these are genuinely cut (fine, the entries can be deleted) or the
   round-2 census undersold them and they need adding to the port.
3. **Two mechanisms this port cannot carry over at all**:
   `RUT_RotSporeKit_SporeCloud.xml`'s `conditionClass
   MayRequire="biomesteam.biomescaverns">BiomesCaverns.GameCondition_SporeCloud`
   reuses the donor's own **compiled C#** GameCondition (no data-only
   substitute; needs a real replacement class or the mechanism is lost with
   the donor) — and `SandFishing_CrackedLands.xml`'s `BMT_Rocktooth`/
   `BMT_Boneblade` freshwater_Uncommon catch items, which are fish LOOT
   ITEMS never covered by the fauna census at all (`decisions_propagated.json`
   is fauna-only).

**Until these three are resolved, do not flip `ModsConfig.xml`** — matching
this project's own `bbf66830` precedent ("ModsConfig deliberately UNTOUCHED
— unticking is the owner's action"), and this item's brief said the same.
The mechanical def-port itself is complete and clean; only the retirement
half is blocked.

---

## Original escalation (superseded above, kept for provenance) — donor mod and creature count don't match

## What this pass found (measured, not guessed)

The queue line (`infrastructure/state/queue/FOUNDRY.md`) reads: *"Port the 71 cast
Beasts of the Rim creatures (41 in + 30 move per decisions_propagated) into our
tier per the SWBestiary donor-retirement pattern, then retire
mlie.beastsoftherim - owner ruled 2026-09-11 (Wave 2)."* Picking this up to
execute, the donor mod named and the 71-creature figure cited do not describe
the same mod. This is not "which 30 is ambiguous" — it is two different mods
under one item, so nothing was ported and nothing was retired this pass.

### The real `mlie.beastsoftherim` (verified against the actual Steam Workshop
folder, not a doc)

Workshop item `2194018641` (`packageId Mlie.BeastsoftheRim`, "Beasts of the Rim
(Continued)"), read directly from
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2194018641`:
**19 species, 64 total defs** (ThingDef + PawnKindDef pairs + eggs + leathers +
one wool), parsed from its own `1.6/Defs/**/*.xml` with `xml.etree` (not grepped
— this repo's own rule against blind scans applied even though the file set is
small): AlligatorMan, Armadillo, Bardelot, BlackBear, BlackBearMan, Giantala,
Worm (Giant Earthworm), Gigantelope, Jerbal, Mandrill, MandrillMan, Megasquid,
Neanderthal, Penguin, Rabbuck, Toraton, Yippa, Zarander, Zebra. **None of these
19 defNames carry a `BMT_` prefix, and none appear anywhere in
`decisions_propagated.json`.** (`design/Jawa/mods/stat_normalization_audit_
2026-09-09.md` cites "45 defs" for this mod from an earlier def-dump count —
close enough to be the same mod, still nowhere near 71, and the discrepancy
doesn't matter for the point below.)

### What `BMT_` actually is in this repo's own data

`design/Jawa/worldbuilding/data/beast_census.csv` (header: `defName,mod,
package_id,...`) is unambiguous: every `BMT_`-prefixed defName's `mod`/
`package_id` columns read **`Biomes! Caverns` / `biomesteam.biomescaverns`**,
**`Biomes! Polluted Lands` / `biomesteam.biomespollutedlands`**, or
**`biomesteam.biomescore`** — the "Biomes!" mod family by `biomesteam`, an
entirely different author from Mlie. `BMT` is this codebase's own census
abbreviation for "**B**io**m**es!**T**eam", not for "Beasts of the Rim" — the
initials coincide, the mods do not.

`design/Jawa/worldbuilding/review/round2/decisions_propagated.json`
(generatedAt `2026-09-10T14:20:34Z`) confirms the same set: 124 `BMT_`-prefixed
rows, decision counts **41 in / 30 move / 53 out at the row level** — this is
exactly the queue line's own "41 in + 30 move" citation, and
`design/Jawa/mods/stat_normalization_audit_2026-09-09.md`'s "BMT had 124
sitting rows (41 in / 30 move / 53 out)" line matches it precisely. At the
unique-defName level (121 names; 3 appear in 2 biome rows each) that's 38
clean "in" + 30 "move" + 1 conflicted (`BMT_ChemSnail`: "in" at
`the_cracked_lands`, "out" at `the_rot` — resolved to OUT by the later, more
current `biome_findings.md`, which lists it under `the_rot`'s departures) + 52
clean "out" = 53 out once resolved, matching the audit doc's own "53 out"
exactly. **So the 71/41/30 figures are real, measured, and fully traceable —
they just belong to `biomesteam.biomescaverns` / `biomesteam.biomescore` /
`biomesteam.biomespollutedlands`, not to `mlie.beastsoftherim`.**

Cross-checked directly: zero overlap between the 121 `BMT_` defNames in
`decisions_propagated.json` and the 19 real `mlie.beastsoftherim` defNames
above.

### Why this can't just be executed as written

`design/Jawa/mods/stat_normalization_audit_2026-09-09.md`'s Wave 2 table (the
audit this item's own queue line cites as "owner ruled 2026-09-11, Wave 2")
lists `mlie.beastsoftherim | 45 defs` as one of nine keep-or-port mods —
`biomesteam.biomescaverns`/`biomescore`/`biomespollutedlands` are **not** on
that Wave 2 (or any wave's) retirement list at all; per `biome_findings.md`
they are live, currently-active donors that multiple biomes are actively
receiving `BMT_` arrivals from as of the 2026-09-10 sitting (e.g. `the_rot`
arrivals include `BMT_Thrumbungus`, `BMT_Yooka`; `the_scarlands` arrivals
include `BMT_CrystalFairyMole`, `BMT_MegaphoridLarva`, `BMT_Stoneback`, etc.).

Executing the item literally — port the 68 unique `BMT_` "in"/"move" species,
then retire `mlie.beastsoftherim` — would: (1) leave `mlie.beastsoftherim`'s
own real 19 species/64 defs completely unported, silently deleting them from
every biome and save the moment it's retired, the exact `WEAPONS_DONOR_
RETIREMENT_1`-style incident this project's own doctrine exists to prevent;
and (2) leave the actual `biomesteam.*` donors of the ported content fully
active and untouched, so the "port" would just duplicate content already live
under two different defName sets, retiring nothing.

## Not done this pass, deliberately

No defs generated, no art extracted, no `ModsConfig.xml` edit, no retirement —
`ModsConfig.xml` writes and mod retirements are this project's own "expensive
list" (`CHARTER.md`), and executing either on a self-contradictory brief is
strictly worse than waiting. This matches this item's own instruction to
escalate rather than guess when the "which 30" split is unclear — here the
ambiguity is one level up: which MOD.

## Escalation — needs an owner/BENCH call

1. **If the intent was the `biomesteam.*` "Biomes!" family** (which the
   measured 71/41/30 figures actually belong to): correct this item's donor
   mod name away from `mlie.beastsoftherim` to `biomesteam.biomescaverns` +
   `biomesteam.biomescore` + `biomesteam.biomespollutedlands`, confirm those
   three are actually intended for retirement (they appear nowhere in the
   ruled stat-normalization waves), and re-file/rename the item accordingly
   before any port work starts.
2. **If the intent was really `mlie.beastsoftherim`** (consistent with its
   Wave 2 audit listing): the 71/41/30/decisions_propagated figures do not
   apply to it at all — its own 19 species have never been through a
   keep-or-port sitting. A new review pass (`skills/review-sheets`, per this
   project's own established pattern for exactly this kind of call) is needed
   to decide which of its 19 species come along before any port/retirement
   work, not a straight "port 71 and retire."

No defs, patches, or `ModsConfig.xml` changes accompany this file — this is a
findings-only commit.
