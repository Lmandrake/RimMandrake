# Ideoligion icons: repoint plan (apply ONLY together with the art install, after the owner's accept)

Owner decision 2026-10-15 (by card): "Draw new icons" for the six donor icons held in the donor-free save
(`Transient/phase0_p6_save_census.md`, `Transient/phase0_p6_save_renames.md` lines 2453-2458).
Commission: `design/RimMandrake/ideo_icons_commission_2026-10-15.json` (item DONOR_DEFS_PORT_TO_OURS_1).
Vanilla Ideology icons measured: 94 textures under `UI/Ideoligions/`, all 128x128 RGBA (resources_ideology bundle),
white glyph tinted in game by the ideo colour. The donor's were 256x256 (bundle index).

## The six (save = `CANONICAL_ASHKARR_START_2026-09-12_donorfree.rws`, ideoManager/ideos)

| donor IdeoIconDef (mlie.starwarsanimalcollection) | ideo id | ideoligion | faction(s) | job id | new IdeoIconDef | new iconPath |
|---|---|---|---|---|---|---|
| `sw_Pentastar` | Ideo_19 | the Contract (RUT_Jawa_Culture_Blackstar) | Blackstar Company (Pirate) | `ideoicon_contract_v1` | `RUT_IdeoIcon_Contract` | `UI/Ideoligions/RUT_contract` |
| `sw_OnderonRoyalty` | Ideo_20 | the Ascendant Genome (RUT_Jawa_Culture_Helix) | Ascendant Helix, PlayerColony | `ideoicon_ascendantgenome_v1` | `RUT_IdeoIcon_AscendantGenome` | `UI/Ideoligions/RUT_ascendantgenome` |
| `sw_JediNova` | Ideo_21 | the Balance (RUT_Jawa_Culture_Deepwater) | Deepwater Compact | `ideoicon_balance_v1` | `RUT_IdeoIcon_Balance` | `UI/Ideoligions/RUT_balance` |
| `sw_SithExarKun` | Ideo_25 | the Weight (RUT_Jawa_Culture_Junkers) | the Junkers | `ideoicon_weight_v1` | `RUT_IdeoIcon_Weight` | `UI/Ideoligions/RUT_weight` |
| `sw_Bantha` | Ideo_28 | the Sun-Debt (RUT_Jawa_Culture_DeepDesert) | Deep Desert Tribes (TribeCivil) | `ideoicon_sundebt_v1` | `RUT_IdeoIcon_SunDebt` | `UI/Ideoligions/RUT_sundebt` |
| `sw_JediGray` | Ideo_18 | Astropolitan (culture Astropolitan, no memes) | Ancients, Voidborn Bazaar, Comet Party, hostile generics | `ideoicon_astropolitan_v1` | `RUT_IdeoIcon_Astropolitan` | `UI/Ideoligions/RUT_astropolitan` |

Mod: `mandrake.rut.patches` (`src/RimUtinni/UtinniPatches`), where the RUT_Jawa cultures live.

## Edit list (all in one change, after accept)

1. **Install the six PNGs** with the art ledger (never a hand copy), one per accepted render:
   `art.py install RimUtinni/UtinniPatches Textures/UI/Ideoligions/RUT_<key>.png <sha> --ruling <accept event>` for
   key in contract, ascendantgenome, balance, weight, sundebt, astropolitan (install_to in each job).
2. **New file** `src/RimUtinni/UtinniPatches/Defs/IdeoSymbolDefs/RUT_IdeoIcons.xml`, six defs of this shape
   (no `MayRequire`: every DLC is assumed). `cultures`/`memes` only bias random ideo generation; the save's
   ideos reference the def directly, so the lists are kept to the owning ideo's own culture:

   ```xml
   <IdeoIconDef>
     <defName>RUT_IdeoIcon_Contract</defName>
     <iconPath>UI/Ideoligions/RUT_contract</iconPath>
     <cultures><li>RUT_Jawa_Culture_Blackstar</li></cultures>
   </IdeoIconDef>
   ```
   Same for AscendantGenome/RUT_Jawa_Culture_Helix, Balance/RUT_Jawa_Culture_Deepwater,
   Weight/RUT_Jawa_Culture_Junkers, SunDebt/RUT_Jawa_Culture_DeepDesert, Astropolitan/Astropolitan.
   Verify each culture defName against the Defs before writing (do not trust this table).
3. **Save rename map**: add to `EXPLICIT` in `src/RimMandrake/Utils/save_donor_rewrite.py`:
   `"sw_Pentastar": "RUT_IdeoIcon_Contract", "sw_OnderonRoyalty": "RUT_IdeoIcon_AscendantGenome",
   "sw_JediNova": "RUT_IdeoIcon_Balance", "sw_SithExarKun": "RUT_IdeoIcon_Weight",
   "sw_Bantha": "RUT_IdeoIcon_SunDebt", "sw_JediGray": "RUT_IdeoIcon_Astropolitan"`.
   The tool renames an `iconDef` only when the port exists as an IdeoIconDef under src/ Defs (step 2 first).
4. **Re-run the rewrite on a copy** (never in place; back up Saves first):
   `python3 src/RimMandrake/Utils/save_donor_rewrite.py <donorfree.rws> <out.rws> --table Transient/phase0_p6_save_renames.md --dry-run`,
   confirm six `iconDef` rows move HOLD -> rename (one hit each), then without `--dry-run`.
5. **Deploy** `deploy_custom_mods.py --mod UtinniPatches` (plan, then `--apply`) at a game-down window; a load
   with the donor absent must log no `Could not load reference to IdeoIconDef`.
