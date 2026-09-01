# Retire the 6 weapon donor packs — AdditionalMods gap found and closed first

Owner, verbatim: *"Yup. This is a major item. File it and work it thoroughly.
I want those mods retired."* Supersedes `WEAPONS_ABSORPTION_WAVE_1`'s one
remaining criterion (all 6 packs OFF, full-list load proves zero missing-def
errors). Full absorption history: `infrastructure/state/items/WEAPONS_ABSORPTION_WAVE_1.md`.

## spec
Turn off `maincrep.eweb`, `rpgwanderer.opturret`,
`m3.continued.jangodsoul.starwars.bti` (JDS Armory), `guy762.kotorweapons`,
`Sov.Sith`, `guy762.mm.kotorcore` in `ModsConfig.xml` — `mandrake.rsw.armoury`
already carries their `1.6/Defs/` content, defNames preserved, deployed and
active alongside them right now (a real, current risk this item was filed to
close, not a hypothetical). Do it only once the gap below is closed — do not
just flip the mod-list switch on the absorption as it stood before this item.

## 🔴 A real gap found before touching anything: `1.6/AdditionalMods/` was never absorbed
`gen_kotorcore_absorption.py` and `gen_kotorweapons_absorption.py` both hard-code
`SRC_DEFS = WORKSHOP_FOLDER/1.6/Defs` — neither ever walked
`WORKSHOP_FOLDER/1.6/AdditionalMods/`, where RimWorld packs keep content gated by
their own `LoadFolders.xml` (`IfModActive`/`IfModNotActive` conditions). Read
both packs' actual `LoadFolders.xml` and cross-checked every gate condition
against the live 593-mod `ModsConfig.xml` (not guessed) — these subfolders
actually gate OPEN on this exact mod list today:

**`guy762.mm.kotorcore`** (`_DroidsBase`/`_BnSDroidsBase` correctly excluded —
Droidworks' territory per the original item's rule 2, not re-litigated):
| folder | gate (active on this list) | contents | verdict |
|---|---|---|---|
| `VEF` | OskarPotocki.VFE.Core | 4 Defs + 1 Patch (`OptionalPatches.xml`, targets `SWPotF_RaceDef_ysalamir` — our own absorbed def, and vanilla `AsteroidBasic` genstep/RimNauts2 — foreign) | absorb + copy patch |
| `MHC` | Killathon.ArtificialBeings | 1 Patch (5 ion `DamageDef.workerClass` overrides, our own absorbed defs) **+ `guy762_IonizationABF.dll`** (6.6 KB, distinct from the already-ported `guy762_Ionization`) | copy patch + **port DLL** |
| `ATC` | Killathon.ArtificialBeings.SynCore | 1 Patch, targets ABF's own Synstruct race (foreign, stays active) | copy patch verbatim |
| `ShowMeYourHands` | Mlie.ShowMeYourHands | 1 Def | absorb |
| `NO_DBH` | Dubwise.DubsBadHygiene absent | 2 Defs | absorb |
| `AdaptiveStorageFramework` | adaptive.storage.framework | 1 Def | absorb |
| `SharedCodeFromShun` | (ShunTheWitch and Pandora both absent) | `taranchuk_homingprojectiles.dll` | **already deliberately excluded in pass 4** (needs a live-behavior check, `IgnoresAccessChecksToAttribute`) — retiring drops it, consistent with the already-blocked `Bullets_Special.xml`/`Bullets_HomingProjectiles.xml`, not a new gap |
| `_BTDKotORGravships` | btd.gbp.shippack.kotor.vge | 7 Defs (gravship interior pieces, research) | absorb |
| `EBSG` | EBSG.Framework | 10 Defs (implant system) | absorb |
| `ModularWeapons2` | kaitorisenkou.ModularWeapons2 | 9 Defs (upgrade parts) | absorb |

**`guy762.kotorweapons`**:
| folder | gate | contents | verdict |
|---|---|---|---|
| `ShowMeYourHands` | Mlie.ShowMeYourHands | 2 Defs | absorb |
| `BiomesCaverns` | BiomesTeam.BiomesCaverns | 1 Def | absorb |
| `_TheForceLightsabers` | lee.theforce.lightsaber | 3 HiltPartDefs (crystals) + 4 Patches (hilt/tip/edge tool slots, part slots, recipes, hand-mod positioning — all target `lee.theforce.lightsaber`'s and `Mlie.ShowMeYourHands`' OWN defs, foreign, both stay active) | absorb defs + copy patches verbatim |

**Why the patches don't need xpath rebasing.** Every absorbed def keeps its
EXACT original defName (the absorption's own rule 1). A `PatchOperation`
matches by defName against the post-merge unified tree, not by which mod
defined it — so a patch targeting `defName="guy762_RangedDamage_ion"` keeps
matching once that defName is defined by `mandrake.rsw.armoury` instead of
`guy762.mm.kotorcore`. The only real requirement is that the PATCH FILE ITSELF
still gets loaded by an active mod — hence "copy the file forward", not
"rewrite it". Confirms the same mechanism `SABER_GUARD_NAMES_WRONG_MOD_1`
already established.

**4 simple packs spot-checked, confirmed clean** — `maincrep.eweb`,
`rpgwanderer.opturret`, `m3.continued.jangodsoul.starwars.bti`, `Sov.Sith` have
**no** `AdditionalMods/` folder at all. No gap for these four.

## verify
1. Extended generator(s) absorb all ~44 XML files above (Defs → `Defs/`,
   Patches → `Patches/`) plus port `guy762_IonizationABF.dll` (class-for-class,
   same discipline as pass 4's 11 DLLs) into `JawaArmoury.dll`.
2. `validate_patch.py --defs` (Data + Mods + Workshop root + Armoury) — expect
   the same pre-existing defect count as pass 4 (10 errors/10 warnings), zero
   NEW errors from this pass's additions.
3. Turn off the 6 packs in `ModsConfig.xml`, redeploy `mandrake.rsw.armoury`.
4. **Full 593-mod cold load, read `Player.log` for real** — zero "could not
   find class", zero missing-def, zero duplicate-defName errors touching any
   absorbed content. This is the mechanism nobody has watched run yet; a live
   check is owed here per CHARTER.

## criteria
- [ ] AdditionalMods gap absorbed (44 files + 1 DLL), validated clean.
- [ ] 6 donor packs OFF in `ModsConfig.xml`.
- [ ] Full-list cold load: zero new errors, screenshot or log excerpt as evidence.
- [ ] `SharedCodeFromShun`'s dropped homing-projectile content stated explicitly
      in the closing note (known, accepted loss, not silently lost).

## Watch out
🔴 **`mandrake.rsw.armoury` was already deployed live, active alongside all 6
donors, before this item existed** — the original item's rule 5 ("do not
touch ModsConfig", deploy only after retirement) was violated by an
unrecorded deploy sometime after the last `WEAPONS_ABSORPTION_WAVE_1` note
(2026-08-31T00:55Z). Whoever deployed it never closed the item or noted the
deploy. Not investigated further (not this item's job), but worth the
owner's attention as a process gap — an item can say "not deployed" in its
own record while the live game already carries it.
