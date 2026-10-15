# W4 donor-off gate: preflight (offline), live load NOT run

Item `DONOR_DEFS_PORT_TO_OURS_1`, wave W4. FOUNDRY, 2026-10-15 ~05:00Z.

## Why no live load
The bridge was held by BENCH (Ratchet pilot): shared lock "BENCH holds it from another clone
(/home/mandrake/rm/bench, touched 29-31 min ago)", driver lock HELD by BENCH pid 1045 (alive);
`/home/mandrake/rm/bench/infrastructure/state/BRIDGE` = `HELD BENCH since 2026-10-15T04:28:16Z`.
The live ModsConfig is BENCH's 23-mod swap (`modlist_swap.py --status`: LIVE 23 active,
md5 d065795f79503e5907a834a9a2ff20d0, UNRECOGNISED). Nothing was swapped, launched or deployed.

## Deploy dry runs (no --apply)
Mods touched by the 15 `Donor pack port` commits: SWBestiary (Defs, Textures), UtinniPatches (Defs, Patches).
- SWBestiary: the port's defs/art are already in the game copy; only drift is 3 `-` lines,
  `Textures/Things/Pawn/Animal/RSW_Khorrak/RSW_Khorrak_{east,north,south}.png` (retired by
  KHORRAK_STEEL_DIET_TIER_1, 144a8b47d, not the port).
- UtinniPatches: 6 `~` FactionDefs (JawaAscendantHelix, JawaDeepwaterCompact, JawaFreeDroidEnclaves,
  JawaGeonosianFoundryHive, JawaHuttCartel, JawaWildsteamClan). UtinniPatches is in BENCH's round
  list, so applying mid-sitting would change BENCH's baseline; held for the load round.

## Static checks
`donor_pack_port.py check` (exit 1):
`roster RSW_ rows resolved 371; unresolved 0; unresolved texPaths 1; unguarded donor-only refs 0; donor-served sw* texPaths 1`
- `BAD RSW_Bullet_AnimalToxbomb Things/Projectile/Acid`: NOT donor-caused (inference). The donor's own
  `Bullet_AnimalToxbomb` uses the same texPath and the donor folder 3497316713 ships no Projectile
  texture, so it is served by Biotech's packed assets, which the offline checker cannot see. Confirm in the live log.
- `DONOR_TEX .../RSW_DesertPortB_Plants.xml swplants/Nysillin`: known, owner art (tracker W4a).

## Finding: two About.xml still hard-depend on the donor
Parsed `<modDependencies>` / `<loadAfter>` as XML in every `src/*/*/About/About.xml`:
- **DEP (hard):** `SWBestiary`, `Shokk` (both also loadAfter).
- loadAfter only (harmless donor-off): Doctrine, UtinniPatches, AshkarrLandmarkArt, ShokkweaveEconomy,
  PawnFlavor, TrophyCraft, Armoury, StarWarsPatches, GizkaStowaway, MandrakePatches.
A donor-off list with these two deps unresolved loads with a missing-dependency warning, and
`modset_builder.py` pulls the donor back in transitively through them (its own comment at the
weepingstones tier says so). The W4 tier cannot be built donor-free until both entries go.

## Owed for the live W4 run
1. Drop `mlie.starwarsanimalcollection` from `<modDependencies>` in SWBestiary and Shokk About.xml.
2. When the bridge is free: deploy SWBestiary + UtinniPatches, build a tier with SWBestiary,
   UtinniPatches, their deps and all five DLC but not the donor; load; read the first exception and
   every cross-ref/Config error/texture miss on RSW_/RUT_/RM_ or sw* paths; spawn the ported species;
   generate AridShrubland, TheRot, Webwork; flight by Pawn_FlightTracker/MaxFlightTime state read only;
   restore ModsConfig md5-verified.
