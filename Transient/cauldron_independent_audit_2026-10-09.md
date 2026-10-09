# Cauldron sheet — independent audit, 2026-10-09

Source of truth: `Transient/biome_ffar/cauldron_sheet_2026-10-04.decisions.json` (46 rows, owner snapshot
`55c4254b730defc3`, read from git at 8eaa2b252; the rebuilt snapshot e949b3f6 has identical shas for every
decided/picked/variant letter). Doers' log not trusted; every verdict below is from primary evidence.

**Result: 30 PASS · 15 FAIL · 1 UNMEASURED.**

## Method (what "PASS" means)
- **Picks:** every facing of the chosen column hashed against (a) the file the running mod list actually
  resolves — `ModsConfig.xml` activeMods parsed with ElementTree (614 active), each mod's LoadFolders/1.6/Common
  searched for `Textures/<texPath>_<facing>.png`, last in load order wins — (b) our `src/` copy and (c) the
  deployed copy under `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`. Donor texPaths checked
  from the donor ThingDef/PawnKindDef XML (alphaanimals, alphamemes, vgeneticse, horrors).
- **✕:** `artledger.Index().is_purged(sha)` and a sha256 sweep of every PNG in `src/` and in all 164 deployed
  `mandrake.*` mod folders.
- **Cuts / moves:** BiomeDef rosters parsed as XML elements (inline) plus every PatchOperation whose own xpath
  names the biome.
- **Redo:** the job JSON in `D:\Luke\dev\_artpipe\{pending,done,failed}` read for `owner_note`, `prompt`,
  `canon_reference`, `drawsize`.
- `art.py enact … ` dry run: **TODO 0, CONFLICTS 0** (confirmed). It also reports 4 FAILED redo jobs it would
  re-file (Neebray N/S, Silooth N/S) and 7 rows AWAITING OWNER PICK.
- `validate_patch.py` (Data + workshop + Mods as --defs, live ModsConfig): Cauldron_Rename.xml,
  WildAnimals_Cauldron.xml, RM_Cauldron.xml, RM_Contagion.xml, RM_CauldronFlora.xml, RSW_VentStalker.xml —
  **0 errors**, 12 advisory warnings (3 conditional-vs-inner xpath on the rename; 9 pre-existing missing
  Dewfall/AssayFlecks texPaths in RM_CauldronFlora.xml). Every rename op matches exactly 1 node.

## Cross-cutting findings
1. **None of the seven Cauldron override mods is in the live mod list.** `mandrake.rut.{ocularjelly,plasmorph,
   dryadcorruptor,dryadtumorous,beetlefleet,visceral,decaydrake}artoverride` are all absent from activeMods.
   About.xml valid (packageId, name, supportedVersions 1.6, correct loadAfter), deployed and in sync
   (`deploy_custom_mods.py --mod <m>` = "Everything in sync"), textures at the exact donor texPaths with the
   picked bytes — but the game resolves the donor art for every one of them. Every pick routed through them is
   therefore not what the game loads.
2. **The composed biomes deploy is still owed** (`deploy_custom_mods.py --compose biomes`, dry run: drift).
   Not yet in game: `RM_Cauldron.xml` (cuts + OcularJelly/Aerofleet removal), `RM_Contagion.xml` (their
   arrival), `RM_CauldronFlora.xml` (sarrowan), `MartyrTree_a.png`, `TwistingThornwood_a.png`. RimWorldWin64
   is running. The plan also shows `MartyrTree_b.png` and `TwistingThornwood_b.png` as "in game, not in repo;
   kept" — a plain `--apply` leaves the rejected `_b` style inside both Graphic_Random folders; it needs `--prune`.
3. UtinniPatches (`mandrake.rut.patches`, active) and SWBestiary: no `+`/`~` drift — Cauldron_Rename.xml and
   the VentStalker texPath/textures are deployed.

## Rows

| Row | Ruling | Verdict | Evidence |
|---|---|---|---|
| AA_BedBug | redo; note "Redo based on (b) render … six eyes that glow red … stabbing proboscis" | **FAIL** | Job `enact_be511e0a_bedbug_v1` (done ×3, awaiting pick) carries the note verbatim, but its `canon_reference` is `44b8d127…` = column **A** south (donor), not the B render he named. |
| AA_CrystalMit | redo; "truly alien crystal creature … tangle of crystals, connective tissue, claw-like manipulators" | PASS | Job `enact_f2b850a2_crystalmit_v1` done ×3, note verbatim in prompt; awaiting pick. |
| AA_DecayDrake | B | **FAIL** | B bytes match in `src/RimUtinni/DecayDrakeArtOverride` and deployed copy, but mod inactive → live winner sarg.alphaanimals (79f72610…/35089a54…/e68cc3a3…). |
| AA_GiantCrownedSilkie | redo; picks baby C, female D, female_baby E; "Good start, but more alien … silk trailing to the ground" | UNMEASURED | Picks C/D/E are in-game donor columns: live bytes match all 9 facings (PASS). Job `enact_4d78432e` done ×3, note verbatim; but `canon_reference` = A east (donor `254ee2f5…`) while "good start" most plausibly means the B render — intent of the reference cannot be settled without him. |
| AA_Helixien | B | **FAIL** | B bytes exist only as `RM_Bileworm_*` in `src/RimMandrake/Scarlands` (Warscar). The RM_Cauldron roster still spawns `AA_Helixien`, whose live texture is the donor (fb72d818…/5cefccb8…/d95f5af4…). enact counts it "already live" by sha, not by the Cauldron's def. |
| AA_InfectedAerofleet | redo; ✕ B×3; "floating ball of gas… no feet … move to the Contagion … Redo description" | **FAIL** | ✕ ×3 purged (ledger) and on disk nowhere — PASS. Job `enact_d3c59886` done ×3, note verbatim — PASS. Moved: gone from RM_Cauldron, inline in RM_Contagion (0.5, MayRequire sarg.alphaanimals) — PASS in src, not deployed (finding 2). **"Redo description" not done**: description is still Contagion_Rename.xml's "blistered bulloo" text; deferral is in the doers' log only, no item. |
| AA_LuciferBug | hold + "No longer needed, cut" | PASS | Absent from RM_Cauldron inline roster and from every RM_Cauldron patch (XML parse). (Campaign twin RUT_Cauldron, frozen, untouched by scope.) |
| AA_OcularJelly | B; "belongs in the Contagion … move" | **FAIL** | Move: PASS in src (removed from RM_Cauldron, added to RM_Contagion), deploy owed. Pick B: bytes match `src/RimUtinni/OcularJellyArtOverride` + deployed, mod inactive → live donor (b3c58819…). |
| AA_Plasmorph | B | **FAIL** | B bytes in PlasmorphArtOverride (src+deployed), mod inactive → live donor (dd3688a8…). |
| AA_Radyak | redo; picks female B, male C, byname D; "more alien please. Rename and regen description." | **FAIL** | Picks B/C (in-game donor) live-match. Job `enact_f3decf4d` done ×3 (ref = A south, donor). **No rename or new description exists** for AA_Radyak anywhere in src. |
| AA_RipperHound | hold + "cut" | PASS | Absent from RM_Cauldron roster and patches. |
| AM_Dryad_Corruptor | B; "Recreate name and description from art" | **FAIL** | Rename PASS: Cauldron_Rename.xml → **rhossak**; LOOKED at pick B — root-stag with split red seed-husks — the description fits; validate 1 match per op. Pick B bytes in DryadCorruptorArtOverride, mod inactive → live donor (6ed0e7bb…). |
| AM_Dryad_Ocular | hold + "Cut" | PASS | Absent from RM_Cauldron roster and patches. |
| AM_Dryad_Tumorous | B; "Regenerate name and description … tumorous version of the above" | **FAIL** | Rename PASS: **galled rhossak**, tied to the rhossak; LOOKED — moss-hung stag covered in fleshy galls — fits. Pick B bytes in DryadTumorousArtOverride, mod inactive → live donor (125790b7…). |
| GR_Beetlefleet | B; ✕ B-north; "North … needs regen … named Garsulix that Hungers. A floating, hungry, chitinous, insect-like ball of gas … Regen description." | **FAIL** | Rename PASS: **garsulix**, description covers every clause of the note; LOOKED at B east — fits. North ✕ `1353dead…` purged, on disk nowhere. North regen PASS: `enact_c8bcd172_garsulix_north_v1_north` done (derive_from the B east; LOOKED: same individual), awaiting pick. Pick B east/south bytes in BeetlefleetArtOverride, mod inactive → live donor (0beaebad…/aa08a14b…). |
| RM_BloodBouquet | B | PASS | Live winner mandrake.rm.biomes = B sha; src Cauldron matches. |
| RM_CrystalFlower | B | PASS | Same. |
| RM_DarkCrust | A | PASS | Live = A. |
| RM_Eskith | A | PASS | Live = A, 3 facings. |
| RM_Fexxil | A | PASS | Live = A. |
| RM_GiantAgariTox | A | PASS | Live = A. |
| RM_GiantToxicFlower | A + byname pick B | PASS | Single graphic; per-graphic B wins (enact rule); live `RM_GiantToxicFlower_a` = B sha. |
| RM_Ixalith | A | PASS | Live = A. |
| RM_KeeningCordax | A | PASS | Live = A. |
| RM_Kissaveth | A | PASS | Live = A. |
| RM_Mullgoth | A | PASS | Live (SWBestiary) = A, 3 facings. |
| RM_RavenNettle | A | PASS | Live = A. |
| RM_RedBugloss | A | PASS | Live = A. |
| RM_Selvix | A | PASS | Live = A. |
| RM_Sessarix | A | PASS | Live = A. |
| RM_Suush | A | PASS | Live = A, 3 facings. |
| RM_TreeMartyr | B; "Redo name and description" | **FAIL** | Rename PASS in src: **sarrowan**, description (rope-trunk rosette, pale bell-flower stalk) fits pick B (LOOKED). Pick B = `src/…/RM_TreeMartyr/MartyrTree_a.png` (c6190158…). **Game still loads A** (`66b3a5c0…`) plus `MartyrTree_b.png` from `RimMandrake.Biomes/Biomes/Cauldron` — compose deploy owed and needs --prune (finding 2). |
| RM_Tsevrix | A | PASS | Live = A. |
| RM_TwistingThornwood | B | **FAIL** | src `TwistingThornwood_a.png` = B (d92285d8…); game still loads A (`e5fafd12…`) + `_b` — same deploy/prune gap. |
| RM_Vexxiss | A | PASS | Live = A. |
| RM_Xithess | A | PASS | Live = A. |
| RM_Zisska | A | PASS | Live = A. |
| RSW_GraniteSlug | A | PASS | Live (SWBestiary) = A. |
| RSW_Lylek | A | PASS | Live = A. |
| RSW_Mynock | A | PASS | Live = A. |
| RSW_Neebray | redo; flying pick B; "Try again? No canon redo?" | **FAIL** | Flying B (12 frames) live-match. Job `enact_cabe4675`: east done, **north and south FAILED and are not pending** (enact dry run would re-file). Its `canon_reference` is the in-game sprite A east, not the canon library entry `design/RimStarWars/canon_references/neebray/` (wookieepedia images exist) that "No canon redo?" asks for. |
| RSW_Screecher | hold + "cut"; flying pick C | PASS | Absent from RM_Cauldron roster and patches (pick moot). |
| RSW_Skalder | A + Swimming B | PASS | Live A body ×3 and B swimming ×3 match. |
| RSW_VentStalker | C; ✕ D×3 | PASS | Def texPath now `swanimals/VentStalker/VentStalker` (own slot); src + deployed SWBestiary files = C shas; SWBestiary active and in sync. ✕ ×3 `is_purged` True and on disk nowhere (2 of them still list Greentide keep rulings in `protected` — ledger cosmetic, no file). |
| Silooth | redo; pick Silooth_j C; "make this 8 cells wide. Follow canon more closely. … acid-spitting." | **FAIL** | Pick C (juvenile, donor AssetBundle) — no loose override anywhere, so unchanged; bytes UNMEASURED (bundle). Job `enact_7a2b5db5`: east done, **north/south FAILED, not pending**; `drawsize 1.0`, reference = donor A south, not the canon entry `design/RimStarWars/canon_references/silooth/`. **No drawSize-8 change and no acid-spit verb/ability** for Silooth in any def or patch, and no item filed for either. |
| Visceral | B; baby C, teen D | **FAIL** | All 9 facings' bytes match in `src/RimUtinni/VisceralArtOverride` + deployed (C/D are our copies of the donor pictures he kept). Mod inactive → game uses mlie.horrors' AssetBundle art. |

## Six new override mods (src/RimUtinni)
| Mod | packageId | loadAfter | Textures at def path | Active | Deploy |
|---|---|---|---|---|---|
| OcularJellyArtOverride | mandrake.rut.ocularjellyartoverride | sarg.alphaanimals | 3/3 match B | **no** | in sync |
| PlasmorphArtOverride | mandrake.rut.plasmorphartoverride | sarg.alphaanimals | 3/3 | **no** | in sync |
| DryadCorruptorArtOverride | mandrake.rut.dryadcorruptorartoverride | sarg.alphamemes | 3/3 | **no** | in sync |
| DryadTumorousArtOverride | mandrake.rut.dryadtumorousartoverride | sarg.alphamemes | 3/3 | **no** | in sync |
| BeetlefleetArtOverride | mandrake.rut.beetlefleetartoverride | vanillaexpanded.vgeneticse | east+south (north ✕, by design) | **no** | in sync |
| VisceralArtOverride | mandrake.rut.visceralartoverride | mlie.horrors | 9/9 | **no** | in sync |

## Informational (not failures)
- RUT_Cauldron (frozen campaign twin, UtinniPatches) still lists AA_InfectedAerofleet, AA_OcularJelly,
  AM_Dryad_Ocular, RSW_Screecher — outside this sheet's scope (RM_Cauldron).
- 7 redo rows have finished renders AWAITING OWNER PICK (BedBug, CrystalMit, Silkie, Aerofleet, Radyak, Neebray
  east, Silooth east) plus the garsulix north.
