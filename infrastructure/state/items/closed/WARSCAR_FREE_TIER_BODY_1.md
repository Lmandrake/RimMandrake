# WARSCAR_FREE_TIER_BODY_1 — the free Warscar gets a body: chatrak, totchak, tetchik, wreck-lichen, pallbearer and scar roach to RM

From `WARSCAR_BEDAZZLE_SITTING_1`. Design source:
`design/Jawa/worldbuilding/biomes/warscar_turn3_development_2026-09-30.md` §3 and §5 rank 0, with the
turn-4 rulings in `warscar_bedazzle_cast_2026-09-30.md` §0. Turn 1 measured the free tier at
**zero owned species**; every other Warscar item lands on this cast.

## spec

1. **`RM_Chatrak`** (bs ~3.0, commonality ~0.25), the plated grazer and scaria host, inline in
   `RM_Warscar`. `AnimalThingBase`; high `ArmorRating_Sharp`; `ManhunterOnDamageChance 0` (it ignores
   gunfire and its own wounds); eats plants, `RM_WreckLichen` its preferred forage. Leather:
   **`RM_ChatrakPlate`** (turn-4 IN, "chatrak plate"): a leather/stuff with high sharp armour, heavy,
   **cannot be dyed**, the only light-armour leather that turns bullets. Balanced by weight and
   rarity, not by narrowing what it can make. Replaces `AA_SpinedGow` as the interim grazer (the
   interim row is flagged for the biome's sitting, not cut by sweep). The snap is `WARSCAR_SNAP_MARK_1`.
2. **`RM_Totchak`** (bs ~14), the colossus: race, kind, and both graphics (standing body; dormant
   wall-pose). Its behaviour is `WARSCAR_TOTCHAK_WAKES_1`; this item ships the body.
3. **`RM_Tetchik`** (bs ~0.1): inedible (no meat, butchers to nothing), herd spawns on glower cells
   (spawn-cell validator), flees everything. Its sound tag is `WARSCAR_GEIGER_CHOIR_1`.
4. **`RM_WreckLichen`**: a `Plant`, `fertilityMin 0`, `neverBlightable`, never sown, placed only by a
   ~80-line **`MapComponent_WreckLichen`** onto cells adjacent to ruins and wreck
   (`AncientFortifiedWall`, junk clusters, broken turrets, crane parts), never on open ground (bans 2
   and 3). Harvest: `RM_WreckLichenScrapings` (dye base, poor fuel). `RM_ScorchedStars` **stays** (ruled).
5. **Pallbearer and scar roach move to RM** (ruled): `RUT_MortuaryCrawler` → **`RM_Pallbearer`** inline in
   `RM_Warscar` with the done art `rutmortuarycrawler_v1` (3 facings, never wired); its corpse-eating
   leaves **`RM_Filth_PickedBones`** (or the vanilla dessicated state) so nothing vanishes.
   `RUT_ScarRoach` → **`RM_ScarRoach`** (already on `RM_EatCleanableExtension`; a file move + defName).
   The cathedral roach stays in RustCathedralRoaches.
   🔴 **Save check, done at commission (2026-09-30, `CANONICAL_ASHKARR_START_2026-09-12.rws`, python
   byte count, probe `<def>Human</def>` = 75):** `RUT_MortuaryCrawler` **0** occurrences anywhere;
   `RUT_ScarRoach` **0** spawned pawns (`<def>`/`<kindDef>` 0) but **3** list references (a thing
   filter list, a records list, an `<animal>` list). ⇒ the pallbearer's RUT defs retire outright; the
   scar roach keeps `RUT_ScarRoach` as a **hidden alias for one release** (turn 3 §3.3's rule), so
   those three references keep resolving. Re-measure before removal if the canonical save changes.
6. **Glower art wired:** `rutglower_v1` → `RM_Glower`, `rutglowercrust_v1` → `RM_GlowerCrust`
   (done in `infrastructure/artpipe/done/`, never wired); correct the stale *"art pending/failed"*
   header in `RM_WarscarFlora.xml`.
7. **Small fixes (ruled):** drop the fertile Soil band from `RM_Warscar`'s terrain list;
   `<label>the Warscar</label>` → `<label>Warscar</label>`.
8. Wire this commission's creature and flora art (cast bible §8) as it lands.
9. **Mod Settings:** a toggle per new species and the lichen seeder; interim donor rows on/off.

## criteria

- `RM_Warscar` lists chatrak, totchak, tetchik, pallbearer, scar roach inline; a quicktest Warscar map
  spawns chatrak and tetchik (tetchik only on glower cells) and wreck-lichen only beside ruins.
- No `RUT_MortuaryCrawler` def remains; `RUT_ScarRoach` loads as a hidden alias and the canonical save
  loads with no new reference error.
- `RM_Glower` renders its own art; no Soil cell on a Warscar map; the label reads "Warscar".
- A butchered chatrak yields `RM_ChatrakPlate`, which cannot be dyed.
