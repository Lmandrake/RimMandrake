# BMT_FAUNA_ABSORPTION_1 — BLOCKED: donor mod and creature count don't match, escalating

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
