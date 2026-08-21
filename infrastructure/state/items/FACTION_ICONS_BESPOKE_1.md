## spec
> ✅ **THE ART IS ACCEPTED AND THE DESIGN IS CLOSED — owner, 2026-08-21:** *"Those are
> exceptional icons! Please fully accept them and mark them DESIGN done... now they need to
> be built into the game factions."* ⛔ **Nothing below is a proposal.** Do not restyle,
> re-derive or substitute any of the thirteen; if one looks wrong in game, report it, do not
> redraw it.

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

### 5. 🔴 FOUR `colorSpectrum` changes, and they SHIP WITH the icons — not optional

**Owner, 2026-08-21:** *"See if you can improve the other icons with similar tricks."*
⇒ **Seven of the thirteen textures are now value-modelled** (two or three tones, not a flat
mask). For four of them the faction colour is **part of the drawing**, because a multiply
has one hue: an accent can only be the *brightest tone of the faction's own colour*.

| file | def | new `colorSpectrum` | why the colour moved |
|---|---|---|---|
| `Defs/FactionDefs/JawaTribes.xml` | `Jawa_IndigenousTribes` | `(0.98,0.72,0.16)` → `(0.86,0.56,0.08)` | amber, so white eyes read as **lit** and the `108` hood as a dark robe |
| `Defs/FactionDefs/JawaJunkers.xml` | `Jawa_Junkers` | `(0.72,0.26,0.15)` → `(0.56,0.19,0.10)` | rust red, so the `255` skull sigil reads **red** on a `132` plate. Scrap brown could only make it a brighter brown |
| `Patches/DeepDesertTribes.xml` | `TribeCivil` | `(0.72,0.66,0.58)` → `(0.58,0.53,0.46)` | bone-grey, so the lenses and mouth grille read as **metal** against darker wrappings |
| `Patches/HomesteadDefenseLeague.xml` | `OutlanderCivil` | `(0.68,0.56,0.40)` → `(0.54,0.43,0.29)` | mid tan — the adobe dome it always wanted to be, and the three tones **straddle** the sand so it does not wash out |

⚠️ **The two patch-file ones are Adds or Replaces depending on the vessel** — check the same
way as `factionIconPath` in §3. `OutlanderCivil` **writes** its own `colorSpectrum`
(`Core/Defs/FactionDefs/Factions_Misc.xml:188`) ⇒ **Replace**. `TribeCivil` also writes its
own (`:446`) ⇒ **Replace**. ⭐ Unlike the icon path, both of these are Replaces.

🔑 **Texture and colour are one design in all four cases.** Ship a value-modelled texture
with the old spectrum and you get a muddy blob; ship the new spectrum with a flat mask and
you get a uniformly bright blob.
⛔ **Do not flatten any texture to a single value to "match" the others.** Seven are
deliberately multi-tone; this is vanilla's own convention — every one of the fifteen shipped
world icons measured 2026-08-21 is greyscale spanning 0–255 with 10–200 distinct luminances.
⛔ **Do not change the other nine factions' `colorSpectrum`.** They pass as they are.

Reasoning and the per-icon value tables: `design/Jawa/art/FACTION_ART_SPEC.md` §1, §2.5, §2.6.

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
