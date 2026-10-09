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

## Re-audit (2026-10-09 09:15, after c09fdaea5 / 0917fe9a2 / acc91cb8f)

**Result on the 16 prior FAIL/UNMEASURED rows: 13 PASS · 0 PASS-PENDING-RESTART · 3 FAIL · 0 UNMEASURED.** 5 prior PASS rows
spot-checked: 5 still PASS, no regression. Primary evidence only; the doers' log was not trusted, and it is wrong in one place (see FAIL block).

State found: another window ran the composed biomes deploy (with the prune) between 09:00 and 09:03 and relaunched RimWorld at ~09:01
(a cold load was in progress, Player.log not yet past load, no `Bridge token`). `deploy_custom_mods.py --compose biomes` is now "Everything in sync (3244 files)";
`MartyrTree_b.png` and `TwistingThornwood_b.png` are gone from the game folder. So the biomes deploy is DONE, not pending.

Method: ModsConfig.xml activeMods parsed with ElementTree (622); each texPath resolved across active mods in load order (last wins) and hashed;
art ledger `art.py status`; artpipe job JSON + manifests read in `D:\Luke\dev\_artpipe`; `validate_patch.py` (Data + workshop + Mods as --defs);
`art.py enact` dry run: CONFLICTS 0, TODO 0, 3 failed Silooth jobs would be re-filed, 6 rows AWAITING OWNER PICK.

### Rows that were FAIL / UNMEASURED

| Row | Verdict | Evidence |
|---|---|---|
| AA_BedBug | PASS | `cauldronfix_bedbug_v2` east/north/south done; `canon_reference` = `_artstore/29/2900a6a7…` which the sheet HTML lists as letter **B** (his named render); prompt says "The attached image IS the (b) render he named", note verbatim incl. six glowing red eyes + stabbing proboscis; manifest east/south graded pass. Old v1 withdrawn. Awaiting his pick. |
| AA_DecayDrake | PASS | Override mod at index 410, loadAfter sarg.alphaanimals at 407; resolved winner for AA_DecayDrake_east = override `ba98737e…`, = src = deployed. Active in the cold load that started after the 08:54 ModsConfig edit; in-game load not yet confirmable. |
| AA_Helixien | PASS | `HelixienArtOverride` at 411 after sarg.alphaanimals 407, loadAfter correct; 3 facings `7778ee23…/fb0a4cae…/7dec0571…` = the Scarlands `RM_Bileworm_*` B shas, = deployed; resolves as winner over donor (`fb72d818…`). Caveat: the ledger has no Cauldron-specific B ruling (decision B == prefill B); the install cites the Warscar keep. |
| AA_InfectedAerofleet | **FAIL** | Moves/✕/redo job unchanged and PASS (RM_Contagion deployed: Aerofleet present, absent from RM_Cauldron). New "no feet … unfortunate visitor" description is correct in `src` (c09fdaea5) but the DEPLOYED `UtinniPatches/Patches/Contagion_Rename.xml` (mtime 2026-10-07 22:20, differs from src at line 131) still carries the old "blistered bulloo" text. |
| AA_OcularJelly | PASS | Override at 408 after 407; winner `57a29333…` = src = deployed over donor `b3c58819…`; move to Contagion deployed (roster parse). |
| AA_Plasmorph | PASS | Override at 409; winner `d45640c2…` over donor `dd3688a8…`. |
| AA_Radyak | **FAIL** | Rename to **ossrith** + new description exist in `src` (validate_patch: 0 errors, each op 1 match) but the DEPLOYED `UtinniPatches/Patches/Cauldron_Rename.xml` is the older 5,227-byte copy with no Radyak block (mtime 08:51:19), so the game loads "radyak". |
| AM_Dryad_Corruptor | PASS | Override at 53 after sarg.alphamemes 52; winner `77b4614d…` over donor `6ed0e7bb…`; rename "rhossak" is in the deployed Cauldron_Rename.xml block that predates the Radyak add (unchanged). |
| AM_Dryad_Tumorous | PASS | Override at 54; winner `6b077510…` over donor `125790b7…`. |
| GR_Beetlefleet | PASS | Override at 503 after vanillaexpanded.vgeneticse 502; east/south winners `15cd4c22…/77647aab…` over donor `0beaebad…/aa08a14b…`; north ✕ purged; garsulix north render `enact_c8bcd172…` still done. |
| RM_TreeMartyr | PASS | Game `MartyrTree_a.png` = `c6190158…` = src (B); `_b` pruned, folder holds only `_a`; sarrowan def in the in-sync compose. |
| RM_TwistingThornwood | PASS | Game `TwistingThornwood_a.png` = `d92285d8…` = src (B); `_b` pruned. |
| RSW_Neebray | PASS | `cauldronfix_neebray_v2` east/north/south done (the 3 old failed jobs withdrawn); `target_canon neebray`, `canon_reference` = the 3 `canon_references/neebray/*.webp` images, prompt "A CANON redo … not from the old in-game sprite", note verbatim; manifest graded 5, all pass. Flying B pick unchanged. Awaiting his pick. |
| Silooth | **FAIL** | (1) Art: `cauldronfix_silooth_v2` east **failed again** (canon check: "legs remain thick and compact rather than long, thin"), north/south `master_failed`; they sit in `failed/`, not pending, and the enact dry run would re-file them. Intent is right (canon refs, canvas 512, drawsize 8.0, note verbatim) but there is no render. (2) Def: `Silooth_Warbeast.xml` drawSize adult 3→8, juvenile 2→5; validate_patch 0 errors, 7/7 ops 1 match against the donor's `lifeStages/li[3]`/`li[2]` and `abilities/li[SW_AcidSpew]`; `RSW_SiloothAcidSpit` parses, field names match vanilla Odyssey `SludgeSpew` (`aiCanUse true`, `CompProperties_AbilitySprayLiquid`), swapped into `abilities`. Correct in src, but **neither new file is deployed**: `SWBestiary/Defs/AbilityDefs/RSW_SiloothAcidSpit.xml` and `Patches/Silooth/Silooth_Warbeast.xml` are absent from the game Mods folder. |
| AA_GiantCrownedSilkie | PASS | Was UNMEASURED. His typed answer settles the reference: `cauldronfix_giantcrownedsilkie_v2` done ×3, `canon_reference` = one side-by-side (LOOKED: left donor with blue head/grey crest/red wattle, right the flowing-silk render), prompt names donor palette + silk to the ground + both notes verbatim. Picks C/D/E are in-game donor columns, unchanged. Awaiting his pick. |

### Why the three FAILs are deploy regressions, not missing work
The fixes log says "Deployed 15 file(s), VERIFIED in sync" for UtinniPatches + SWBestiary + HelixienArtOverride. Now: Cauldron_Rename.xml mtime 08:51:19 with the pre-fix content, Contagion_Rename.xml is the 10-07 copy, SWBestiary lacks the 2 new files. Something deployed UtinniPatches from a clone without c09fdaea5 after the doers' deploy (the foundry clone sits at 985bf6b18). Dry runs now: UtinniPatches `~ Patches/Cauldron_Rename.xml`, `~ Patches/Contagion_Rename.xml`; SWBestiary `+ Defs/AbilityDefs/RSW_SiloothAcidSpit.xml`, `+ Patches/Silooth/Silooth_Warbeast.xml`; exactly those 4, nothing else. They are XML only and the game is loading, so they will count as PASS-PENDING-RESTART once this is run, with the game closed or at the next launch:
`python3 src/RimMandrake/Utils/deploy_custom_mods.py --apply --mod UtinniPatches --mod SWBestiary` (from a clone at or after acc91cb8f; do NOT run from foundry before it pulls). Silooth art also needs the 3 failed jobs re-filed (`art.py enact … --apply`) and a canon-passing render.

### Prior PASS rows, spot-checked
| Row | Verdict | Evidence |
|---|---|---|
| RM_BloodBouquet | PASS | Game file `e49e6550…` = ledger LIVE B. |
| RM_Suush | PASS | 3 facings `84463d0f/11b91823/9316d677` = ledger LIVE = game. |
| RSW_VentStalker | PASS | SWBestiary east/north/south `bef5081e/e2a32b17/4b122f0c` = ledger LIVE C, protected. |
| RSW_Skalder | PASS | Body `14213f8c…` and swimming `086e7012…` east = ledger LIVE in the game folder. |
| AA_LuciferBug / RSW_Screecher cuts | PASS | Parsed deployed RM_Cauldron roster (16 animals) and Contagion (23): absent from both; `WildAnimals_Cauldron.xml` names no Screecher element. |

Also checked: the owner's other notes for the 6 override mods and Helixien are unchanged and `loadAfter` in each About.xml names its donor package; every override sits AFTER its donor in activeMods (dryad ×2 53,54 vs 52; visceral 157 vs 156; ocular/plasmorph/decaydrake/helixien 408–411 vs 407; beetlefleet 503 vs 502). The mod-list edit is a game-side file (not in git); the game launch read it only if it started after 08:54, which the log timing supports but a mod-list line in Player.log has not yet confirmed.
