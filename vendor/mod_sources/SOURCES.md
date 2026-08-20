# `vendor/mod_sources/` — provenance

**Written 2026-08-20, from the files on disk, immediately before the stale Outer Rim
trees were deleted.** It exists because `infrastructure/output/audit_2026-08-20_research_vendor.md`
§4 found this directory holding 62 third-party trees with **zero committed provenance**
— no `MANIFEST`, no `SOURCE.txt`, no index — and that gap is why a stale-branch read of
`supportedVersions` cost six days and two wrong answers.

## 🔴 Read this before trusting any `supportedVersions` below

> **Never read `supportedVersions` off a GitHub `main` branch or a `*-main` zip.**
> Multi-version RimWorld mods branch per game version, and several authors here keep
> `main` stale. **The Workshop copy on disk is the authority**:
> `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\<id>\About\About.xml`

**Measured disagreements, 2026-08-20** — vendored zip vs. the Workshop copy actually loaded:

| packageId | this tree said | Workshop copy says | |
|---|---|---|---|
| `Neronix17.OuterRim.Core` | `1.4 1.5 1.6` | `1.4 1.5 1.6` | agrees (the control case) |
| `Neronix17.OuterRim.GalacticEmpire` | **`1.4 1.5`** | **`1.4 1.5 1.6`** | 🔴 **the trap** |
| `Neronix17.OuterRim.RebelAlliance` | **`1.4 1.5`** | **`1.4 1.5 1.6`** | 🔴 **the trap** |
| `Neronix17.OuterRim.GalacticDiversity` | `1.4 1.5 1.6` | `1.4 1.5 1.6` | agrees |
| `Neronix17.OuterRim.DroidDepot` | `1.4 1.5 1.6` | `1.4 1.5 1.6` | agrees |
| `Neronix17.OuterRim.GalacticRepublic` · `.Mandalore` · `.OldRepublic` · `.Separatists` | **`1.4 1.5`** | *not installed — no Workshop copy to check* | unresolved |

⚠️ **Four of the nine could not be settled either way**, because we do not have the
Workshop copy. That is the honest state: their `1.4 1.5` may be true or may be stale,
and the vendored tree cannot tell you which.

## What is and is not recoverable here

None of the 62 trees contains a `.git` directory, so **branch and commit are not
recoverable from the tree itself** in the general case. Two things partially rescue it:

- ✅ **9 trees carry a real commit SHA** in a GitHub zipball inner directory name
  (`Megafauna-3d781e1e…`). Those are hard provenance — the zipball naming convention
  is `<repo>-<full commit sha>`, and it is the commit, not the branch tip today.
- ⚠️ **A `-main` / `-master` folder suffix is INFERRED and is not proof of anything.**
  It records which branch was requested at fetch time, not which commit arrived, and
  the branch has moved since. Every "branch" line below is marked INFERRED for this reason.
- ❌ **Fetch dates are not recorded anywhere.** Directory mtimes survive (ranging from
  2025-03 to 2026-08) but a copy or a touch rewrites them, so they are a hint, not evidence.

**Nothing under `vendor/mod_sources/` is tracked by git** (`git ls-files` → 0). Deletions
here cost nothing in history and everything is re-fetchable from the upstreams below.

## Trees kept deliberately, despite thin provenance

- **`_speakup_src_1p6`** — 🔑 **do not delete.** No `About.xml`, no upstream URL, no
  commit: provenance is **unrecoverable**. But it is a **live build input**, read by
  `src/RimMandrake/Utils/build_jawavoice.py:40` and documented in
  `src/Jawa/JawaVoice/README.md:77` as *"input snapshot of SpeakUp's 1.6 Defs (do not
  edit)"*. It is a hand-curated snapshot, not a branch pull, and it appears to be the
  only copy. Losing it breaks a build.
- **`RimBridgeServer-main`** — read by `skills/rimbridge/SKILL.md` and
  `skills/rimbridge/references/extending.md`; upstream `https://github.com/pardeike/RimBridgeServer`.
- **`CustomQuestFramework-Old-src`** — no `About.xml` at any level; an `inner/` C#
  solution with no upstream URL in any file. **Provenance unrecoverable.** Kept because
  it is referenced and re-fetching it is not obviously possible.

## Deleted 2026-08-20

The nine `Outer-Rim-*-main` trees, on the ruling at `design/V2_DREAMS.md:539`
(*"All nine … are stale-branch pulls — delete or clearly mark them"*). Their rows are
retained below, marked **DELETED**, so this file remains the record of what was here.

⚠️ **Their upstream repository could NOT be determined and is not guessed here.** The
only URL any of the nine declares is the author's Patreon (`https://www.patreon.com/neronix17`);
no GitHub URL naming an Outer Rim repo appears in any file in any of the nine trees, and
no tracked doc records one. The recoverable route is **the Workshop copy on disk**, which
is the authority anyway — and for six of the nine, `design/Jawa/mods/outer_rim_cherrypick_list.md`
and `design/Jawa/mods/required_mods.md` refer to them by defName, not by file.

---

## The 62 trees

### `Adaptive-Storage-Framework-main`

- **size / files:** 2.1 MB (2,149,703 bytes) · 233 files
- **mod name:** Adaptive Storage Framework
- **packageId:** `adaptive.storage.framework`
- **supportedVersions (verbatim):** `<li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://github.com/bbradson/Adaptive-Storage-Framework`
- **referenced by repo files:** 0 — none

### `AlienRaces-HAR-main`

- **size / files:** 69.2 KB (70,835 bytes) · 25 files
- **mod name:** Humanoid Alien Races
- **packageId:** `erdelf.HumanoidAlienRaces`
- **supportedVersions (verbatim):** `<li>0.19</li> <li>1.0</li> <li>1.1</li> <li>1.2</li> <li>1.3</li> <li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://github.com/erdelf/AlienRaces/wiki`
- **referenced by repo files:** 1

### `AlphaBiomes_src`

- **size / files:** 1.4 MB (1,466,697 bytes) · 307 files
- **mod name:** Alpha Biomes
- **packageId:** `brrainz.harmony`
- **supportedVersions (verbatim):** `<li>1.6</li> <li>1.5</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** (zipball, branch not in name)
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 1

### `BiomesCaverns_src`

- **size / files:** 1.4 MB (1,422,128 bytes) · 440 files
- **mod name:** Biomes! Caverns
- **packageId:** `BiomesTeam.BiomesCaverns`
- **supportedVersions (verbatim):** `<li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** (zipball, branch not in name)
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 0 — none

### `BiomesCore_src`

- **size / files:** 519.6 KB (532,068 bytes) · 108 files
- **mod name:** Biomes! Core
- **packageId:** `BiomesTeam.BiomesCore`
- **supportedVersions (verbatim):** `<li>1.1</li> <li>1.2</li> <li>1.3</li> <li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** (zipball, branch not in name)
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 1

### `BiomesFossils_src`

- **size / files:** 158.1 KB (161,849 bytes) · 54 files
- **mod name:** Biomes! Fossils
- **packageId:** `BiomesTeam.BiomesFossils`
- **supportedVersions (verbatim):** `<li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: `63e3e223aa02936159f114c2c191d2296071d863`** — RECOVERABLE. GitHub zipball inner dir `BiomesFossils-63e3e223aa02936159f114c2c191d2296071d863` encodes the source commit.
- **branch (INFERRED from folder name):** (zipball, branch not in name)
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 1

### `BiomesFramework_src`

- **size / files:** 1010.4 KB (1,034,669 bytes) · 217 files
- **mod name:** Biomes! Framework
- **packageId:** `BiomesTeam.CoreFramework`
- **supportedVersions (verbatim):** `<li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** (zipball, branch not in name)
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 0 — none

### `BiomesPollutedLands`

- **size / files:** 660.4 KB (676,294 bytes) · 211 files
- **mod name:** Biomes! Polluted Lands
- **packageId:** `BiomesTeam.BiomesPollutedLands`
- **supportedVersions (verbatim):** `<li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** not inferable
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 5

### `CAI-5000-1p6-main`

- **size / files:** 9.0 MB (9,419,245 bytes) · 242 files
- **mod name:** CAI 5000 - Advanced AI + Fog Of War
- **packageId:** `Krkr.rule56`
- **supportedVersions (verbatim):** `<li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://github.com/mynameasjeff/CAI-5000-1.6`
- **referenced by repo files:** 1

### `CaravanAdventures_src`

- **size / files:** 2.9 MB (3,089,567 bytes) · 728 files
- **mod name:** Caravan Adventures
- **packageId:** `brrainz.harmony`
- **supportedVersions (verbatim):** `<li>1.2</li> <li>1.3</li> <li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: `939b3aba28d5fd3c0dd0118c77dd0221d6b34bee`** — RECOVERABLE. GitHub zipball inner dir `CaravanAdventures-939b3aba28d5fd3c0dd0118c77dd0221d6b34bee` encodes the source commit.
- **branch (INFERRED from folder name):** (zipball, branch not in name)
- **upstream:** `https://github.com/iforgotmysocks/CaravanAdventures` · `https://github.com/iforgotmysocks/CaravanAdventuresWiki`
- **referenced by repo files:** 0 — none

### `CaveBiome`

- **size / files:** 1.2 MB (1,276,486 bytes) · 120 files
- **mod name:** CaveBiome (Continued)
- **packageId:** `Mlie.CaveBiome`
- **supportedVersions (verbatim):** `<li>1.1</li> <li>1.2</li> <li>1.3</li> <li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** not inferable
- **upstream:** `https://github.com/RimSort/RimSort` · `https://github.com/emipa606/CaveBiome`
- **referenced by repo files:** 5

### `CaveworldFlora`

- **size / files:** 912.6 KB (934,503 bytes) · 134 files
- **mod name:** CaveworldFlora (Continued)
- **packageId:** `Mlie.CaveworldFlora`
- **supportedVersions (verbatim):** `<li>1.1</li> <li>1.2</li> <li>1.3</li> <li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** not inferable
- **upstream:** `https://github.com/RimSort/RimSort` · `https://github.com/emipa606/CaveworldFlora`
- **referenced by repo files:** 0 — none

### `Complementary-Odyssey-main`

- **size / files:** 370.9 KB (379,848 bytes) · 105 files
- **mod name:** Complementary Odyssey
- **packageId:** `MrHydralisk.ComplementaryOdyssey`
- **supportedVersions (verbatim):** `<li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://github.com/MrHydralisk/Complementary-Odyssey`
- **referenced by repo files:** 0 — none

### `CustomQuestFramework-Old-src`

- **size / files:** 559.0 KB (572,460 bytes) · 116 files
- **mod name:** ⚠️ no `About.xml` in tree — unknown
- **packageId:** ⚠️ unknown (no `About.xml`)
- **supportedVersions:** ⚠️ unknown (no `About.xml`)
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** not inferable
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 2

### `DragonsDescent_src`

- **size / files:** 3.8 MB (4,019,264 bytes) · 436 files
- **mod name:** Dragons Descent
- **packageId:** `onyxae.dragonsdescent`
- **supportedVersions (verbatim):** `<li>1.1</li> <li>1.2</li> <li>1.3</li> <li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** (zipball, branch not in name)
- **upstream:** `https://github.com/Aether-Guild/Dragons-Descent/`
- **referenced by repo files:** 1

### `Dubs-Mint-Menus-master`

- **size / files:** 2.6 MB (2,689,417 bytes) · 17 files
- **mod name:** Dubs Mint Menus
- **packageId:** `Dubwise.DubsMintMenus`
- **supportedVersions (verbatim):** `<li>1.0</li> <li>1.1</li> <li>1.2</li> <li>1.3</li> <li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** master — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://github.com/Dubwise56/Dubs-Mint-Menus`
- **referenced by repo files:** 0 — none

### `DubsBadHygieneLite_src`

- **size / files:** 4.9 MB (5,183,702 bytes) · 453 files
- **mod name:** Dubs Bad Hygiene Lite
- **packageId:** `Dubwise.DubsBadHygiene.Lite`
- **supportedVersions (verbatim):** `<li>1.3</li> <li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: `ea3c7d8c4577d978cf702808af46b04b6c19b2ef`** — RECOVERABLE. GitHub zipball inner dir `Dubs-Bad-Hygiene-Lite-ea3c7d8c4577d978cf702808af46b04b6c19b2ef` encodes the source commit.
- **branch (INFERRED from folder name):** (zipball, branch not in name)
- **upstream:** `https://github.com/Dubwise56/Dubs-Bad-Hygiene` · `https://github.com/Dubwise56/Dubs-Bad-Hygiene/wiki`
- **referenced by repo files:** 0 — none

### `DubsBadHygiene_src`

- **size / files:** 5.1 MB (5,327,495 bytes) · 455 files
- **mod name:** Dubs Bad Hygiene
- **packageId:** `Dubwise.DubsBadHygiene`
- **supportedVersions (verbatim):** `<li>1.0</li> <li>1.1</li> <li>1.2</li> <li>1.3</li> <li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: `044358d5501f650931a1083b8e0f38f079b23b2f`** — RECOVERABLE. GitHub zipball inner dir `Dubs-Bad-Hygiene-044358d5501f650931a1083b8e0f38f079b23b2f` encodes the source commit.
- **branch (INFERRED from folder name):** (zipball, branch not in name)
- **upstream:** `https://github.com/Dubwise56/Dubs-Bad-Hygiene` · `https://github.com/Dubwise56/Dubs-Bad-Hygiene/wiki`
- **referenced by repo files:** 0 — none

### `IncidentDisabler-Continued-src`

- **size / files:** 103.8 KB (106,277 bytes) · 31 files
- **mod name:** Incident Disabler (Continued)
- **packageId:** `Mlie.IncidentDisabler`
- **supportedVersions (verbatim):** `<li>1.2</li> <li>1.3</li> <li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** not inferable
- **upstream:** `https://github.com/RimSort/RimSort` · `https://github.com/emipa606/IncidentDisabler`
- **referenced by repo files:** 1

### `JurassicDinosOnly_src`

- **size / files:** 1.1 MB (1,146,100 bytes) · 209 files
- **mod name:** Jurassic Rimworld - Dinosaurs Only (Continued)
- **packageId:** `Mlie.JurassicRimworldDinosaursOnly`
- **supportedVersions (verbatim):** `<li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** (zipball, branch not in name)
- **upstream:** `https://github.com/emipa606/JurassicRimworldDinosaursOnly`
- **referenced by repo files:** 0 — none

### `KotOR-WeaponsArmor-1p6`

- **size / files:** 1.3 MB (1,374,193 bytes) · 100 files
- **mod name:** Star Wars KotOR Weapons and Armor
- **packageId:** `guy762.KotORWeapons`
- **supportedVersions (verbatim):** `<!--li>1.4</li--> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** not inferable
- **upstream:** `https://github.com/guy1762/guy762-KotORWeaponsArmor`
- **referenced by repo files:** 0 — none

### `Megafauna_src`

- **size / files:** 410.3 KB (420,132 bytes) · 39 files
- **mod name:** Megafauna
- **packageId:** `Spino.Megafauna`
- **supportedVersions (verbatim):** `<li>1.3</li> <li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: `3d781e1e6a038eabcdd58e87ac03135052cddf64`** — RECOVERABLE. GitHub zipball inner dir `Megafauna-3d781e1e6a038eabcdd58e87ac03135052cddf64` encodes the source commit.
- **branch (INFERRED from folder name):** (zipball, branch not in name)
- **upstream:** `http://megafaunarimworld.wikia.com`
- **referenced by repo files:** 1

### `NWNRealFogOfWar`

- **size / files:** 2.0 MB (2,132,515 bytes) · 163 files
- **mod name:** (NWN) Real Fog of War (Continued)
- **packageId:** `Mlie.NWNRealFogOfWar`
- **supportedVersions (verbatim):** `<li>1.2</li> <li>1.3</li> <li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** not inferable
- **upstream:** `https://github.com/RimSort/RimSort` · `https://github.com/emipa606/NWNRealFogOfWar` · `https://github.com/lukakama/rimworld-mod-real-fow`
- **referenced by repo files:** 2

### `Outer-Rim-Core-main` — 🔴 **DELETED 2026-08-20** (stale-branch pull, `design/V2_DREAMS.md:539`)

- **size / files:** 15.3 MB (16,064,400 bytes) · 259 files
- **mod name:** Outer Rim - Core
- **packageId:** `Neronix17.OuterRim.Core`
- **supportedVersions (verbatim):** `<li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://github.com/pardeike/Harmony` · `https://github.com/sponsors/pardeike` · `https://www.patreon.com/neronix17`
- **referenced by repo files:** 3

### `Outer-Rim-Droid-Depot-main` — 🔴 **DELETED 2026-08-20** (stale-branch pull, `design/V2_DREAMS.md:539`)

- **size / files:** 18.3 MB (19,187,291 bytes) · 156 files
- **mod name:** Outer Rim - Droid Depot
- **packageId:** `Neronix17.OuterRim.DroidDepot`
- **supportedVersions (verbatim):** `<li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://github.com/pardeike/Harmony` · `https://github.com/sponsors/pardeike` · `https://www.patreon.com/neronix17`
- **referenced by repo files:** 1

### `Outer-Rim-Galactic-Diversity-main` — 🔴 **DELETED 2026-08-20** (stale-branch pull, `design/V2_DREAMS.md:539`)

- **size / files:** 14.7 MB (15,455,858 bytes) · 107 files
- **mod name:** Outer Rim - Galactic Diversity
- **packageId:** `Neronix17.OuterRim.GalacticDiversity`
- **supportedVersions (verbatim):** `<li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://github.com/pardeike/Harmony` · `https://github.com/sponsors/pardeike` · `https://www.patreon.com/neronix17`
- **referenced by repo files:** 2

### `Outer-Rim-Galactic-Empire-main` — 🔴 **DELETED 2026-08-20** (stale-branch pull, `design/V2_DREAMS.md:539`)

- **size / files:** 20.6 MB (21,611,208 bytes) · 888 files
- **mod name:** Outer Rim - Galactic Empire
- **packageId:** `Neronix17.OuterRim.GalacticEmpire`
- **supportedVersions (verbatim):** `<li>1.4</li> <li>1.5</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://www.patreon.com/neronix17`
- **referenced by repo files:** 0 — none

### `Outer-Rim-Galactic-Republic-main` — 🔴 **DELETED 2026-08-20** (stale-branch pull, `design/V2_DREAMS.md:539`)

- **size / files:** 62.3 MB (65,301,609 bytes) · 1979 files
- **mod name:** Outer Rim - Galactic Republic
- **packageId:** `Neronix17.OuterRim.GalacticRepublic`
- **supportedVersions (verbatim):** `<li>1.4</li> <li>1.5</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://github.com/pardeike/Harmony` · `https://github.com/sponsors/pardeike` · `https://www.patreon.com/neronix17`
- **referenced by repo files:** 0 — none

### `Outer-Rim-Mandalore-main` — 🔴 **DELETED 2026-08-20** (stale-branch pull, `design/V2_DREAMS.md:539`)

- **size / files:** 51.9 MB (54,431,236 bytes) · 595 files
- **mod name:** Outer Rim - Mandalore
- **packageId:** `Neronix17.OuterRim.Mandalore`
- **supportedVersions (verbatim):** `<li>1.4</li> <li>1.5</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://github.com/pardeike/Harmony` · `https://github.com/sponsors/pardeike` · `https://www.patreon.com/neronix17`
- **referenced by repo files:** 0 — none

### `Outer-Rim-Old-Republic-main` — 🔴 **DELETED 2026-08-20** (stale-branch pull, `design/V2_DREAMS.md:539`)

- **size / files:** 1.8 MB (1,915,801 bytes) · 249 files
- **mod name:** Outer Rim - Old Republic
- **packageId:** `Neronix17.OuterRim.OldRepublic`
- **supportedVersions (verbatim):** `<li>1.4</li> <li>1.5</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://www.patreon.com/neronix17`
- **referenced by repo files:** 0 — none

### `Outer-Rim-Rebel-Alliance-main` — 🔴 **DELETED 2026-08-20** (stale-branch pull, `design/V2_DREAMS.md:539`)

- **size / files:** 2.3 MB (2,463,125 bytes) · 283 files
- **mod name:** Outer Rim - Rebel Alliance
- **packageId:** `Neronix17.OuterRim.RebelAlliance`
- **supportedVersions (verbatim):** `<li>1.4</li> <li>1.5</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://www.patreon.com/neronix17`
- **referenced by repo files:** 1

### `Outer-Rim-Seperatists-main` — 🔴 **DELETED 2026-08-20** (stale-branch pull, `design/V2_DREAMS.md:539`)

- **size / files:** 496.5 KB (508,424 bytes) · 53 files
- **mod name:** Outer Rim - Separatists
- **packageId:** `Neronix17.OuterRim.Separatists`
- **supportedVersions (verbatim):** `<li>1.4</li> <li>1.5</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://www.patreon.com/neronix17`
- **referenced by repo files:** 0 — none

### `PickUpAndHaul-main`

- **size / files:** 168.2 KB (172,196 bytes) · 56 files
- **mod name:** Pick Up And Haul
- **packageId:** `Mehni.PickUpAndHaul`
- **supportedVersions (verbatim):** `<li>1.0</li> <li>1.1</li> <li>1.2</li> <li>1.3</li> <li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://github.com/Mehni/PickUpAndHaul` · `https://ludeon.com/forums/index.php?topic=35832`
- **referenced by repo files:** 0 — none

### `ReinforcedMechanoid2-main`

- **size / files:** 30.3 MB (31,768,588 bytes) · 528 files
- **mod name:** Reinforced Mechanoid 2 (Continued)
- **packageId:** `Mlie.ReinforcedMechanoid2`
- **supportedVersions (verbatim):** `<li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://github.com/RimSort/RimSort` · `https://github.com/emipa606/AssetBuilder` · `https://github.com/emipa606/ReinforcedMechanoid2`
- **referenced by repo files:** 1

### `ResearchReinvented-main`

- **size / files:** 1.3 MB (1,368,725 bytes) · 522 files
- **mod name:** Research Reinvented
- **packageId:** `PeteTimesSix.ResearchReinvented`
- **supportedVersions (verbatim):** `<li>1.3</li> <li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://github.com/PeteTimesSix/ResearchReinvented` · `https://github.com/pardeike/HarmonyRimWorld`
- **referenced by repo files:** 2

### `RimBridgeServer-main`

- **size / files:** 3.5 MB (3,720,249 bytes) · 84 files
- **mod name:** RimBridgeServer
- **packageId:** `brrainz.rimbridgeserver`
- **supportedVersions (verbatim):** `<li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://github.com/pardeike/Achtung2` · `https://github.com/pardeike/DecompilerServer` · `https://github.com/pardeike/GABS` · `https://github.com/pardeike/RimBridgeServer`
- **referenced by repo files:** 5

### `RimBridgeServer.Annotations-main`

- **size / files:** 18.6 KB (18,998 bytes) · 10 files
- **mod name:** ⚠️ no `About.xml` in tree — unknown
- **packageId:** ⚠️ unknown (no `About.xml`)
- **supportedVersions:** ⚠️ unknown (no `About.xml`)
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://github.com/pardeike/RimBridgeServer.Annotations`
- **referenced by repo files:** 0 — none

### `RimHUD-main`

- **size / files:** 1.2 MB (1,250,175 bytes) · 202 files
- **mod name:** RimHUD
- **packageId:** `Jaxe.RimHUD`
- **supportedVersions (verbatim):** `<li>1.1</li> <li>1.2</li> <li>1.3</li> <li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://github.com/Jaxe-Dev/RimHUD`
- **referenced by repo files:** 0 — none

### `RimWorld_CommonSense-master`

- **size / files:** 1.3 MB (1,380,129 bytes) · 243 files
- **mod name:** Common Sense
- **packageId:** `avilmask.CommonSense`
- **supportedVersions (verbatim):** `<li>1.0</li> <li>1.1</li> <li>1.2</li> <li>1.3</li> <li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** master — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://github.com/catgirlfighter/RimWorld_CommonSense` · `https://github.com/pardeike/HarmonyRimWorld`
- **referenced by repo files:** 0 — none

### `Rimefeller_src`

- **size / files:** 3.8 MB (3,975,260 bytes) · 203 files
- **mod name:** Rimefeller
- **packageId:** `Dubwise.Rimefeller`
- **supportedVersions (verbatim):** `<li>1.0</li> <li>1.1</li> <li>1.2</li> <li>1.3</li> <li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: `8124e55f4436fa43414b5a79d7a777a34df6c837`** — RECOVERABLE. GitHub zipball inner dir `Rimefeller-8124e55f4436fa43414b5a79d7a777a34df6c837` encodes the source commit.
- **branch (INFERRED from folder name):** (zipball, branch not in name)
- **upstream:** `https://github.com/Dubwise56/Rimefeller/wiki`
- **referenced by repo files:** 0 — none

### `RimworldAllowTool-main`

- **size / files:** 1.3 MB (1,325,928 bytes) · 202 files
- **mod name:** Allow Tool
- **packageId:** `UnlimitedHugs.AllowTool`
- **supportedVersions (verbatim):** `<li>1.0</li> <li>1.1</li> <li>1.2</li> <li>1.3</li> <li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://ludeon.com/forums/index.php?topic=17218.0`
- **referenced by repo files:** 0 — none

### `ScenarioAmender-litteram-1p6-src`

- **size / files:** 10.9 KB (11,199 bytes) · 10 files
- **mod name:** Scenario Amender [1.5 - 1.6]
- **packageId:** `katana.scenarioamender`
- **supportedVersions (verbatim):** `<li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** not inferable
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 1

### `StarWarsAnimalCollection_src`

- **size / files:** 7.0 MB (7,375,823 bytes) · 40 files
- **mod name:** Star Wars Animal Collection (Continued)
- **packageId:** `Mlie.StarWarsAnimalCollection`
- **supportedVersions (verbatim):** `<li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** (zipball, branch not in name)
- **upstream:** `https://github.com/emipa606/StarWarsAnimalCollection`
- **referenced by repo files:** 1

### `StarWarsFullyFunctionalLightsabers-main`

- **size / files:** 704.9 KB (721,776 bytes) · 172 files
- **mod name:** Star Wars - Fully Functional Lightsabers (Continued)
- **packageId:** `Mlie.StarWarsFullyFunctionalLightsabers`
- **supportedVersions (verbatim):** `<li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://github.com/RimSort/RimSort` · `https://github.com/emipa606/AssetBuilder` · `https://github.com/emipa606/StarWarsFullyFunctionalLightsabers` · `https://github.com/jecrell/JecsTools`
- **referenced by repo files:** 2

### `VFE-Deserters-main`

- **size / files:** 2.7 MB (2,800,711 bytes) · 212 files
- **mod name:** Vanilla Factions Expanded - Deserters
- **packageId:** `OskarPotocki.VFE.Deserters`
- **supportedVersions (verbatim):** `<li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 0 — none

### `VFE-Insectoids2-main`

- **size / files:** 1.1 MB (1,109,788 bytes) · 274 files
- **mod name:** Vanilla Factions Expanded - Insectoids 2
- **packageId:** `OskarPotocki.VFE.Insectoid2`
- **supportedVersions (verbatim):** `<li>1.5</li><li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 2

### `VFE-Pirates-main`

- **size / files:** 799.6 KB (818,801 bytes) · 190 files
- **mod name:** Vanilla Factions Expanded - Pirates
- **packageId:** `OskarPotocki.VFE.Pirates`
- **supportedVersions (verbatim):** `<li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 0 — none

### `VQE_DroneFactory_src`

- **size / files:** 1.1 MB (1,126,585 bytes) · 199 files
- **mod name:** Vanilla Quests Expanded - Drone Factory
- **packageId:** `brrainz.harmony`
- **supportedVersions (verbatim):** `<li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** (zipball, branch not in name)
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 0 — none

### `VSIE_src`

- **size / files:** 600.6 KB (614,966 bytes) · 148 files
- **mod name:** Vanilla Social Interactions Expanded
- **packageId:** `VanillaExpanded.VanillaSocialInteractionsExpanded`
- **supportedVersions (verbatim):** `<li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** (zipball, branch not in name)
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 0 — none

### `VanillaChemfuelExpanded_OdysseyPatch-main`

- **size / files:** 17.6 KB (18,021 bytes) · 12 files
- **mod name:** Vanilla Chemfuel Expanded - Odyssey Patch
- **packageId:** `Bulldog.VanillaChemfuelExpandedOdysseyPatch`
- **supportedVersions (verbatim):** `<li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 0 — none

### `VanillaEventsExpanded-main`

- **size / files:** 530.0 KB (542,747 bytes) · 144 files
- **mod name:** Vanilla Events Expanded
- **packageId:** `VanillaExpanded.VEE`
- **supportedVersions (verbatim):** `<li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 0 — none

### `VanillaEventsExpanded_src`

- **size / files:** 530.0 KB (542,747 bytes) · 144 files
- **mod name:** Vanilla Events Expanded
- **packageId:** `VanillaExpanded.VEE`
- **supportedVersions (verbatim):** `<li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: `25a09c16fcd301069c0aa87d01514b37c014bca9`** — RECOVERABLE. GitHub zipball inner dir `VanillaEventsExpanded-25a09c16fcd301069c0aa87d01514b37c014bca9` encodes the source commit.
- **branch (INFERRED from folder name):** (zipball, branch not in name)
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 0 — none

### `VanillaExpandedFramework-main`

- **size / files:** 5.9 MB (6,233,873 bytes) · 1456 files
- **mod name:** Vanilla Expanded Framework
- **packageId:** `OskarPotocki.VanillaFactionsExpanded.Core`
- **supportedVersions (verbatim):** `<li>1.0</li> <li>1.1</li> <li>1.2</li> <li>1.3</li> <li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://github.com/Vanilla-Expanded/VanillaExpandedFramework`
- **referenced by repo files:** 0 — none

### `VanillaFurnitureExpanded-Factory-main`

- **size / files:** 563.0 KB (576,531 bytes) · 107 files
- **mod name:** Vanilla Furniture Expanded - Factory
- **packageId:** `brrainz.harmony`
- **supportedVersions (verbatim):** `<li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 3

### `VanillaGeneticsExpanded_src`

- **size / files:** 3.3 MB (3,464,835 bytes) · 214 files
- **mod name:** Vanilla Genetics Expanded
- **packageId:** `brrainz.harmony`
- **supportedVersions (verbatim):** `<li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** (zipball, branch not in name)
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 0 — none

### `VanillaGravshipExpanded-main`

- **size / files:** 2.0 MB (2,095,850 bytes) · 529 files
- **mod name:** Vanilla Gravship Expanded - Chapter 1
- **packageId:** `brrainz.harmony`
- **supportedVersions (verbatim):** `<li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 1

### `VanillaQuestsExpanded-DroneFactory-main`

- **size / files:** 986.7 KB (1,010,361 bytes) · 198 files
- **mod name:** Vanilla Quests Expanded - Drone Factory
- **packageId:** `brrainz.harmony`
- **supportedVersions (verbatim):** `<li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 1

### `VanillaVehiclesExpanded_src`

- **size / files:** 685.0 KB (701,408 bytes) · 152 files
- **mod name:** Vanilla Vehicles Expanded
- **packageId:** `OskarPotocki.VanillaVehiclesExpanded`
- **supportedVersions (verbatim):** `<li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: `638c441bbf5c6930f2dea1f459f282d8241f5130`** — RECOVERABLE. GitHub zipball inner dir `VanillaVehiclesExpanded-638c441bbf5c6930f2dea1f459f282d8241f5130` encodes the source commit.
- **branch (INFERRED from folder name):** (zipball, branch not in name)
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 0 — none

### `VehicleFramework_src`

- **size / files:** 4.4 MB (4,610,583 bytes) · 967 files
- **mod name:** Vehicle Framework
- **packageId:** `SmashPhil.VehicleFramework`
- **supportedVersions (verbatim):** `<li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: `fd5ed722ce214836d4c283832865dfa5966f1e4e`** — RECOVERABLE. GitHub zipball inner dir `Vehicle-Framework-fd5ed722ce214836d4c283832865dfa5966f1e4e` encodes the source commit.
- **branch (INFERRED from folder name):** (zipball, branch not in name)
- **upstream:** `https://github.com/SmashPhil/Vehicle-Framework` · `https://github.com/SmashPhil/Vehicle-Framework.git`
- **referenced by repo files:** 0 — none

### `_speakup_src_1p6`

- **size / files:** 615.5 KB (630,270 bytes) · 22 files
- **mod name:** ⚠️ no `About.xml` in tree — unknown
- **packageId:** ⚠️ unknown (no `About.xml`)
- **supportedVersions:** ⚠️ unknown (no `About.xml`)
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** not inferable
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 2

### `gravship-water-systems-main`

- **size / files:** 27.0 KB (27,636 bytes) · 17 files
- **mod name:** Gravship Water Systems
- **packageId:** `tefnut.gravship.water.systems`
- **supportedVersions (verbatim):** `<li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream: unknown** — no URL in any `About.xml`, `.csproj`, `.sln`, `README` or NuGet file.
- **referenced by repo files:** 2

### `kNumbers-main`

- **size / files:** 576.3 KB (590,164 bytes) · 119 files
- **mod name:** Numbers
- **packageId:** `Mehni.Numbers`
- **supportedVersions (verbatim):** `<li>1.0</li> <li>1.1</li> <li>1.2</li> <li>1.3</li> <li>1.4</li> <li>1.5</li> <li>1.6</li>`
- **commit: unknown, unrecoverable** — no `.git`, no zipball SHA in any path.
- **branch (INFERRED from folder name):** main — ⚠️ a zipball folder suffix is not proof of the commit.
- **upstream:** `https://github.com/Mehni/kNumbers` · `https://github.com/koisama/kNumbers`
- **referenced by repo files:** 0 — none

---

## Method

```
find <tree> -iname About.xml            -> name, packageId, supportedVersions (verbatim), url
find <tree> -type d -regex '.*-[0-9a-f]{40}'  -> GitHub zipball commit SHA, where present
grep -rhoE 'https?://(github|gitlab)\.com/[^/]+/[^/ ]+' --include='*.csproj' --include='*.sln' \
     --include='*.md' --include='*.txt' --include='*.props' --include='*.gitmodules'  -> upstream
grep -rIl -- '<dirname>' design/ src/ skills/ infrastructure/ vendor/wisdom/ CLAUDE.md   -> references
du -sb / find -type f | wc -l           -> size, file count
git ls-files vendor/mod_sources | wc -l -> 0 (nothing here is tracked)
```

⚠️ **Reference counts exclude `infrastructure/output/audit_2026-08-20_research_vendor.md`**,
which names most of these trees and would otherwise give every one a false hit.
