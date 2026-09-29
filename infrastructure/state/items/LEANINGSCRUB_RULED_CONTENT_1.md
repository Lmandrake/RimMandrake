# LEANINGSCRUB_RULED_CONTENT_1 — Build the Leaning Scrub ruled cast

From `LEANINGSCRUB_BEDAZZLE_SITTING_1` (volley closed 2026-09-28; every ruling is
an owner-typed or card-recorded ledger note there). Analysis:
`design/Jawa/worldbuilding/biomes/leaningscrub_bedazzle_review_2026-09-29.md`.
Cast bible from the commission agent: `leaningscrub_bedazzle_cast_2026-09-29.md`.
Mod: `src/RimMandrake/LeaningScrub/` (legacy label arid_shrubland — search both).
🔴 Trim law from the final ruling: creatures and ecology ship, but NO
warning-instrument framing — no radar features, no alarm buildings, no
early-warning UI. Flavor text stays ecological, not tactical.

## spec

1. **Four fills** (mixed registers ruled): `RM_Fuzzrunner` (tunnel-hare prey
   base), `RM_Thornhold` (venom nester, forbids rather than flees),
   `RM_Shokka` (wake-edge pouncer, medium 1.2), `RM_Zellik` (stall-hawk, TRUE
   FLYER — MaxFlightTime stats, Locust shape, never block on frames).
2. **The menagerie** (all swept 0-collision 2026-09-28, probe korrum 70):
   `RM_Fuzzviper` (run-ambusher) · `RM_Surrik` (crust-swimmer snake under the
   root mat) · `RM_Ribbonwhip` (canopy-top thread snake) · `RM_Vissler`
   (brittlestar: sheds a twitching arm decoy that regrows; arm is a harvestable
   hunter's lure; interlocking star mats in the Gale) · `RM_Dustflutter`
   (flutterer flocks — burst up when disturbed, resettle elsewhere; tiny
   MaxFlightTime, flight as displacement) · `RM_Shirrel` (big glider, rises on
   the Gale) · `RM_Crustweevil` (lichen-grazing bug) · `RM_Rollbug` (run
   janitor) · `RM_Tikkit` (clicking swarm bug — soundscape richness, NOT a
   warning device).
3. **The fuzz family** (flora): `RM_Whipfuzz` (grassy), `RM_Pillowmoss` (mossy,
   fog-condensing — vaporator synergy in MECHANICS), `RM_Tanglefuzz` (bushy den
   anchor), `RM_Cruststar` (lichen on the crust). All ban-9 compliant
   (fire-resistant living flora).
4. **The venomvine five-form showpiece**: base `RM_VenomvineThicket` (exists) +
   `RM_DrippingVenomvine` (beaded overproducer; harvest job → raw venom stock
   item: weapon coating / medicine precursor; risky unprotected) +
   `RM_TwitcherVenomvine` (one lash on approach then visible recovery droop —
   the lash is a MapComponent, ⛔ never a plant CompTick, plants only TickLong)
   + `RM_HollowVenomvine` (old tubular stands; runway nations thread them; a
   Jawa-sized pawn can crawl through — grown gates) + `RM_CrownVenomvine`
   (rare man-height-plus flowering landmark, mobbed by dustflutters when the
   wind drops — wind-keyed, ⛔ no day/night dependency, ban 3).
5. **Blurrg, TAMED-ONLY** (card decision 2026-09-28): never spawns wild —
   threads frozen ban 4 (large-band void) as written. Owed: `RSW_Blurrg` port
   on the Utinni/RSW layer per Q11, a `canon_references/` entry, own art.
   Trade/scenario/quest arrival wiring.
6. **Regen all art to become our own** (owner-typed): thunderstep, yanker,
   scrap-nest bird, tunnel snake and every other donor-reskin in this biome's
   cast get owned renders (commission agent queues). **Wire, don't regen**, the
   five validated renders already in artpipe under old RUT_ subjects
   (rutfuzz_v1, rut_grellbush, rut_grellspine, rut_wildhealroot,
   rmvenomvine_v1) onto the RM_ texPaths.
7. `VAEWaste_Hydra` dead roster row (wired nowhere): UNRULED — strike-candidate
   per the AA_SandLion precedent; confirm with the owner at art review, do not
   silently strike.

## criteria

- Free tier stands alone per Q11a (this biome shipped ZERO standalone
  creatures before this build); merged rosters parse by node NAME; Mod
  Settings coverage; every new def collision-proven; fuzz names keep the
  owner's live naming item (`ARIDSHRUBLAND_SHIPPING_NAMES_1`) untouched for
  the base fuzz.
