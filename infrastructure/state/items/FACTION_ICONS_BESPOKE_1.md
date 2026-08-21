## spec
🔴 **Owner, 2026-08-21: he rejected the drawn concepts and supplied a reference image per
faction.** Twelve are converted, game-ready, and committed at
`design/Jawa/art/faction_icons/` — **128×128 RGBA, single flat white value with real alpha**,
which is the form `Settlement.Material` multiplies by `colorSpectrum`. Every one was checked
at 26px against desert ground before it was written.

⛔ **This SUPERSEDES `FACTION_ICONS_UNCOLLIDE_1`.** That item reassigned four factions to
*borrowed vanilla* glyphs under R17 (*"bespoke faction art is `[v2]`"*). The owner has
overruled R17. **Do not do both** — the borrowed reassignments are dead.

### 1. Copy the art in

`design/Jawa/art/faction_icons/*.png` ⇒
`src/Jawa/Jawa_Patches/Textures/World/JawaFactions/`

⇒ the texPath for each becomes `World/JawaFactions/<Name>`.
⚠️ `Jawa_Patches` already ships `Textures/Things/Item/Special/JawaClaimRumour.png`, so the
folder is a proven load path in this exact mod. No `LoadFolders` change is needed.

### 2. Eight of our own defs — edit the def, do not patch

`src/Jawa/Jawa_Patches/Defs/FactionDefs/` — replace the existing `<factionIconPath>` value:

| file | new value |
|---|---|
| `JawaTribes.xml` | `World/JawaFactions/JawaTradeMoot` |
| `JawaJunkers.xml` | `World/JawaFactions/Junkers` |
| `JawaHuttCartel.xml` | `World/JawaFactions/HuttCartel` |
| `JawaDeepwaterCompact.xml` | `World/JawaFactions/DeepwaterCompact` |
| `JawaFreeDroidEnclaves.xml` | `World/JawaFactions/FreeDroidEnclaves` |
| `JawaGeonosianFoundryHive.xml` | `World/JawaFactions/GeonosianHive` |
| `JawaWildsteamClan.xml` | `World/JawaFactions/WildsteamClan` |
| `JawaAscendantHelix.xml` | `World/JawaFactions/AscendantHelix` |

### 3. Four vessels — patch ops, and 🔴 THE ADD/REPLACE SPLIT IS THE TRAP

Go in each vessel's existing patch file, inside the `PatchOperationConditional` already there.

| target | patch file | op | why |
|---|---|---|---|
| `Empire` | `GalacticEmpire.xml` | **Replace** | the def writes it — `Data/Royalty/Defs/FactionDefs/Faction_Empire.xml:19` |
| `Pirate` | `BlackstarCompany.xml` | **Replace** | the def writes it — `Core/Defs/FactionDefs/Factions_Misc.xml:522` |
| `OutlanderCivil` | `HomesteadDefenseLeague.xml` | 🔴 **Add** | the def does **not** write it; it inherits `Expanding/Town` from `OutlanderFactionBase` (`Core/Defs/FactionDefs/Factions_Misc.xml:14`) |
| `TribeCivil` | `DeepDesertTribes.xml` | 🔴 **Add** | the def does **not** write it; it inherits `Expanding/Village` from `TribeBase` (`:227`) |

Values: `World/JawaFactions/GalacticEmpire` · `.../BlackstarCompany` · `.../HomesteadLeague`
· `.../DeepDesertTribes`.

⚠️ **A `Replace` where the node is absent matches nothing and logs a red error; an `Add`
where it is present creates a duplicate node.** Both fail quietly enough to ship.

✅ `ForgottenArsenal.png` is built and ready, but `Mechanoid` is `hidden`, holds no
settlement and is never drawn — patching it changes nothing a player can see. Ship the
texture; the def change is optional and costs one Replace on `Factions_Hidden.xml:88`.
⚠️ **It is drawn to the owner's reference rather than traced from it.** The line-art
original could not survive 26px: extracting it left either a shield outline with a dot, or
a solid shield whose gear had filled in. A heater shield with a gear punched out and a solid
hub is the same design and holds.

### 4. ⏸️ Two things are NOT resolved and must not be guessed

- ✅ ~~Ascendant Helix has no icon~~ **RESOLVED 2026-08-21** — the owner re-sent it (a DNA
  double helix) and it is built. ⇒ **there are no icon collisions left on the map.**
- 🔴 **The Jawa Trade Moot's icon is nearly invisible, and it is a COLOUR fault, not an art
  fault.** Its `colorSpectrum` is `(0.70,0.55,0.30)` — sand — and it is drawn tinted, on
  sand, on a desert planet. The hood silhouette is correct and reads fine in any other
  colour. ⇒ **do not redraw it.** See `FACTION_ART_SPEC.md` §2.5 for the proposed spectrum.

## verify
- `grep -rn factionIconPath src/Jawa/Jawa_Patches/` shows eleven `World/JawaFactions/…`
  values and no duplicates
- twelve PNGs under `src/Jawa/Jawa_Patches/Textures/World/JawaFactions/`, each **128×128**
  and each with an alpha channel whose extrema are `(0, 255)` — a fully opaque alpha means
  the mask was flattened and the icon will render as a filled square
- `validate_patch.py` clean, and each of the four vessel ops reports **1** hit
- ⛔ `FACTION_ICONS_UNCOLLIDE_1` is NOT also applied

## criteria
Every faction that holds a settlement draws its own mark, no two are alike, and none is
magenta.
