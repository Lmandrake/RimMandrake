# Deploy window plan — measured 2026-08-21, game UP (plan-only, nothing written)

**One line:** only 2 of 22 mods have drift (Jawa_Patches: 4 XML files; DesertVehicleReskin:
4 Chariot PNGs) — **no `-` deletions anywhere, and no DLL is owed** unless the owner lifts
the DesertVehicleReskin hold, which is the single real shutdown-window item.

## The 22 deployable mods

`+` added · `~` changed · `-` would delete · `H` held

| mod | packageId | in ModsConfig? | DLL? | + | ~ | - | H |
|---|---|---|---|---|---|---|---|
| BlastDoorFrameAsyncFix | mandrake.blastdoorframeasyncfix | yes | – | 0 | 0 | 0 | 0 |
| CereanManeFix | mandrake.cereanmanefix | **NO** | – | 0 | 0 | 0 | 0 |
| DesertVehicleReskin | mandrake.desertvehiclereskin | yes | **yes** | **4** | 0 | 0 | 1 |
| GravshipAstronautFix | mandrake.gravshipastronautfix | yes | – | 0 | 0 | 0 | 1 |
| Inhabited | mandrake.inhabited | yes | **yes** | 0 | 0 | 0 | 0 |
| JawaFactionSlate | mandrake.jawafactionslate | yes | – | 0 | 0 | 0 | 0 |
| JawaIonWeapons | mandrake.jawaionweapons | yes | **yes** | 0 | 0 | 0 | 0 |
| JawaPlantGrowth | mandrake.jawaplantgrowth | yes | **yes** | 0 | 0 | 0 | 0 |
| JawaVoice | mandrake.jawavoice | yes | – | 0 | 0 | 0 | 0 |
| Jawa_Armoury | mandrake.jawa.armoury | yes | – | 0 | 0 | 0 | 2 |
| Jawa_Doctrine | mandrake.jawa.doctrine | yes | – | 0 | 0 | 0 | 0 |
| Jawa_Patches | mandrake.jawa.patches | yes | – | **1** | **3** | 0 | 0 |
| KotORBandolierNorthFix | mandrake.kotorbandoliernorthfix | **NO** | – | 0 | 0 | 0 | 0 |
| MSEDroidFix | mandrake.msedroidfix | yes | – | 0 | 0 | 0 | 0 |
| PhytokinBarkHeadFix | mandrake.phytokinbarkheadfix | **NO** | – | 0 | 0 | 0 | 0 |
| ResearchKitEastFix | mandrake.researchkiteastfix | yes | – | 0 | 0 | 0 | 0 |
| RimDefDump | mandrake.rimdefdump | yes | – | 0 | 0 | 0 | 0 |
| RimMandrake_StarWarsRaces | mandrake.starwarsraces | yes | – | 0 | 0 | 0 | 0 |
| SauridFrillFix | mandrake.sauridfrillfix | yes | – | 0 | 0 | 0 | 0 |
| StrandedQuest | mandrake.strandedquest | **NO** | – | 0 | 0 | 0 | 0 |
| ToolBeltFix | mandrake.toolbeltfix | yes | – | 0 | 0 | 0 | 0 |
| WreckedMachines | mandrake.wreckedmachines | **NO** (parked to v2) | – | 0 | 0 | 0 | 14 |

**Mods carrying an `Assemblies/*.dll`** — the only ones that need the game DOWN:
DesertVehicleReskin · Inhabited · JawaIonWeapons · JawaPlantGrowth.
Three of the four are already in sync; the fourth's DLL is HELD. So **no assembly is
currently owed**, and the window is only needed if the hold below is lifted.

Not a mod and not in ModsConfig, but a DLL and therefore window-shaped: the RimBridge
companion `JawaBench.BridgeTools.dll` at
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\JawaBench.BridgeTools.dll`
is **byte-identical to the repo artifact** (md5 `9e1e493e…`). Nothing owed.

## DO FIRST WHEN THE GAME GOES DOWN

Both drifting mods are XML/PNG only, so steps 1–2 do not actually need the game down —
run them now if you want. Only step 4 does. `--apply` without `--prune` deletes nothing.

```bash
cd /mnt/d/Luke/dev/Rimworld

# 1. Jawa_Patches — the only XML drift (1 new patch, 3 changed defs/patches)
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Jawa_Patches --apply

# 2. DesertVehicleReskin — 4 Chariot textures (the held DLL is skipped automatically)
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod DesertVehicleReskin --apply

# 3. prove it: this must print "in sync" for both, exit 0 except for the HELD lines
python3 src/RimMandrake/Utils/deploy_custom_mods.py

# 4. ONLY IF the owner has ruled on `Seed` (see HELD ON PURPOSE) — game must be DOWN:
#    delete the DesertVehicleReskin/Assemblies line from src/DEPLOY_HOLD.txt, then
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod DesertVehicleReskin --apply
```

Deployed is not loaded: defs and textures are parsed once at startup, so the next launch
is what makes any of this visible.

## DANGEROUS

**Nothing.** The plan produced **zero `-` lines** across all 22 mods — no file in the game
copy is absent from the repo, so no deploy would delete anything. (`-` only ever deletes
with `--apply --prune` in any case; the commands above omit `--prune`.)

## HELD ON PURPOSE

| file | reason, verbatim from `src/DEPLOY_HOLD.txt` |
|---|---|
| `DesertVehicleReskin/Assemblies/DesertVehicleReskin.dll` | `BUILD: game up + Seed ruling open, 2026-08-21` |
| `GravshipAstronautFix/Textures/Things/Structures/GravshipGenebank/GravshipGenebank_north.png` | `owner: pulled pending art verification, 2026-08-14` |
| `Jawa_Armoury/Patches/Warcasket_HazardRetune.xml` | `owner: SHIP NEITHER, 2026-08-12` |
| `Jawa_Armoury/Patches/Armour_Ratings.xml` | `owner: SHIP NEITHER, 2026-08-12` |
| `WreckedMachines/*` (14 files incl. `About/About.xml`) | `owner: parked to v2, 2026-08-12` |

The DesertVehicleReskin hold is on **two** counts, per the file's own note: (1) the game was
up when the DLL was built, so deploying mid-session risks the next launch loading a DLL
nobody watched attach; (2) the rule accepts `Plant | VegetableOrFruit | Meal` and therefore
**rejects RawRice**, whose foodType is the standalone `Seed` flag (16) — while the item's own
spec lists RawRice as qualifying. Adding `Seed` is one token and is **the owner's call**.
⇒ Count (1) is discharged by the shutdown window itself. Count (2) is not. **Do not lift
this hold on the strength of the game being down alone.**

The other three holds are owner rulings with no pending question — leave them.

## DEPLOYED BUT NOT LOADED

Four mods are fully deployed into the game's Mods folder and **absent from ModsConfig.xml**,
so they load nothing at all. Silent no-op; nobody would notice.

- `mandrake.cereanmanefix` — CereanManeFix (2 files deployed)
- `mandrake.kotorbandoliernorthfix` — KotORBandolierNorthFix (**21 files** deployed)
- `mandrake.phytokinbarkheadfix` — PhytokinBarkHeadFix (2 files deployed)
- `mandrake.strandedquest` — StrandedQuest (3 files deployed)

A fifth, `mandrake.wreckedmachines`, is also absent — that one is **correct**: the mod is
parked to v2 and its whole tree is held, including its `About.xml`.

⚠️ Whether the four above *should* be enabled is the owner's call, not a defect to fix
silently. Two of them (Cerean, Phytokin) are art fixes and may be deliberately out under the
2026-08-14 "stop fixing art until the premise is verified" directive — the DEPLOY_HOLD note
says two such fixes "rode out via ModsConfig". KotOR and StrandedQuest have no such note.
