# Giant-worm mod survey for the krayt-leviathans ruling (2026-09-02)

Ruling under audit: `swt:krayt-leviathans`, `design/Jawa/proposals/sw_mod_concepts_triage.md:34`
— "Keep the giant Krayt dragon just as it is, but create a NEW massive dune-style
sandworm with its own mythos... Feel free to borrow from the giant worm mod to
build another version for the Krayt."

Read-only web + repo research. No ModsConfig changes, no commits.

---

## 1. Candidate "giant worm mods" on Steam Workshop

| Mod | packageId | Author | RW version | Open source | How it implements bigness/burrowing |
|---|---|---|---|---|---|
| **LEVIATHANS:SANDWORM** — the mod already installed and named in our own docs (see §2/§3) | `chezhou.creature.sandworm` (requires `chezhou.chezhoulib.lib`) | Workshop page credits `嘎笑司机`; the `ChezhouLib` dependency is credited to `追踪虫` — two Chinese Steam handles, spelling not independently verified beyond search snippets | 1.6, requires Biotech | No public GitHub found for either the mod or ChezhouLib — Workshop-only, custom C# | **Not an animal at all.** `SandWorm_Thing` is a ThingDef with no `<race>` — a terrain-scale entity — plus a separate `SandWorm_HitProxy` hit surface (bigger than one tile), a `WorldObjectDef`, a `QuestScriptDef`, its own `WeatherDef` and `SongDef`. Play loop per Steam blurb: it "lies dormant" under a Deep Sand Echo Zone; a craftable **Sandhammer** device replicates the seismic vibration of a sandworm's mating cycle to summon it. Per player reports it can one-shot pawns — a set-piece encounter, not a wandering wildlife spawn. |
| **SandWorm** (Steam id 3105413080) | not confirmed (Steam rate-limited before author/packageId could be pulled) | UNKNOWN | UNKNOWN, page references Pertam (implies 1.4/1.5-era content) | UNKNOWN | Per Workshop blurb: spawns a **group** of ordinary-scale sandworms on the Pertam biome that spit acid at pawns and damage terrain grids nearby; built on the **MES creature spawner** framework, config-file tunable. Multiple smaller worms, not one giant entity — closer to a hostile-wildlife pack than a VAST creature. |
| **SHAI HULUD (Dune sand worm)** (Steam id 2792203277) | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | Turns out to be a **player-drivable vehicle**, not a creature: WASD to move, E to end, Q to fire saw/magnet parts. Likely built on the Vehicle Framework (already in our mod list as `smashphil.vehicleframework`). Not a burrowing-AI implementation — a controls scheme, not a mythos creature. Wrong shape for "another version of a giant beast," but the vehicle-framework route is a legitimate alternate technical path if the new sandworm were ever rideable. |
| **Alpha Animals — Mammoth Worm** (`AA_MammothWorm`, already in our cast, "ours") | `sarg.alphaanimals` | juanosarg (Alpha Animals author) | 1.5–1.6 | **Yes** — public GitHub, `juanosarg/AlphaAnimals` | Ordinary single-tile `PawnKindDef`/`ThingDef` race (per our own `animal_census.csv`: bodySize 3, standard animal fields). Its "big" is stat-scaling and a bonus-damage-vs-walls siege mechanic (bred as a living siege engine vs mechanoid structures), **not** multi-tile geometry or burrow/tunnel AI. Useful as an open-source reference for *big-animal stat curves*, not for the VAST-tier mechanism. |
| **Space Worms (Continued)** (`Scuttlebug`, already in our cast, "dormant") | `mlie.spaceworms` | mlie (maintainer) | 1.6 | Likely yes (mlie's "Continued" ports are generally open, not independently confirmed here) | Tiny (bodySize 0.2) parasitic worm that infects downed pawns via escape pods and later erupts — a body-horror spawn mechanic, not a giant/burrowing one. Wrong scale for this ruling; noted only because it's already active. |

Krayt Dragon's own mod (`mlie.starwarsanimalcollection`, "Star Wars Animal Collection
(Continued)") was **not** treated as a worm-mod candidate — see §2, it is an ordinary
large `Animal` racial, not a VAST/terrain entity, so it has nothing to "borrow" from
itself.

### What the owner's named candidates turned out to be
- "Dune - Shai-Hulud" → real mod, but it is a **vehicle**, not a wild creature.
- "Sandworms" → best match is Workshop id 3105413080, a **pack of acid-spitting
  ordinary worms** on Pertam via the MES spawner, not one giant entity.
- Alpha Animals' giant creatures → present (`AA_MammothWorm`), open source, but
  mechanically an ordinary big-animal racial, no burrow/tunnel/multi-tile code.
- Mashed's Ashlands lava worms / SOS2 / "Big Worms" → no matching Workshop item
  surfaced under those names in this search pass; **UNKNOWN**, not ruled out.

---

## 2. Krayt Dragon provenance (confirmed from repo, no web needed)

- Both `KraytDragon` and `GreaterKraytDragon` trace to **`mlie.starwarsanimalcollection`**
  ("Star Wars Animal Collection (Continued)"), confirmed active in
  `/mnt/d/Luke/dev/Rimworld/infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`.
- GitHub mirror `emipa606/StarWarsAnimalCollection` — **MIT-licensed, open source**,
  1.6-compatible, maintained by emipa606 (mlie), continuing Beasstmann's original
  with "the excellent work of Delta" adding creatures. Krayt Dragon and Greater
  Krayt Dragon both confirmed present in the animal roster.
- Both are in our own fauna cast at SUPER tier, flagged `ours`:
  `/mnt/d/Luke/dev/Rimworld/design/Jawa/fauna/animal_census.csv:484` (KraytDragon)
  and `:535` (GreaterKraytDragon); allocated into
  `/mnt/d/Luke/dev/Rimworld/design/Jawa/fauna/BiomeCast_Ashkarr.xml:522,607` at
  0.2/0.008 commonality into desert-family biomes.
- **This is an ordinary `Animal` ThingDef/PawnKindDef** (has a `<race>`, appears
  in normal wildlife-spawn tables) — nothing like the VAST/terrain-object
  construction described in §3. The ruling's "keep it just as it is" is
  therefore keeping a normal (if SUPER-tier) big-animal racial, while the new
  sandworm is asked to be built as something categorically different.

---

## 3. Borrow vs. original — what's portable

1. `chezhou.creature.sandworm` (already installed, MIT-status unconfirmed but
   Workshop-only) is our own repo's **already-designated reference implementation**
   for VAST creatures — see `design/Jawa/worldbuilding/setting_physics.md` Part 5.
2. Portable *pattern*, no code needed: model the new sandworm as a
   **`WorldObjectDef` + `QuestScriptDef` + its own `WeatherDef`/`SongDef`**, not a
   spawn-table `PawnKindDef` — this is pure XML/def authorship, fully in our reach.
3. Portable *pattern*: gate the encounter behind a **craftable summoning item**
   (their Sandhammer) rather than random wildlife roll — also pure XML + recipe def.
4. **Needs original C#** (their `ChezhouLib`, closed/Workshop-only, not forkable):
   the actual `SandWorm_Thing`'s no-`<race>` rendering/collision handling and its
   separate `SandWorm_HitProxy` hit-surface — i.e., anything that makes the
   creature occupy and be damageable across multiple tiles as one coherent body.
   That has to be written fresh, or reuse a different framework we already carry
   (e.g. Vehicle Framework's rideable/steerable-parts model from the Shai-Hulud
   mod, if a driveable/latched interaction is ever wanted) rather than depend on
   an inaccessible third-party DLL.
5. Alpha Animals gives an open-source-checkable pattern for *big-animal stat
   curves* (bodySize, lifespan, market value) if any part of the new sandworm is
   ever expressed as an ordinary animal rather than a world object — but it does
   not solve the multi-tile/burrow problem either.

---

## VERDICT

- **Best borrow source: `LEVIATHANS:SANDWORM` (`chezhou.creature.sandworm`)** —
  it is already installed, already active in our mod list, and our own
  `setting_physics.md` already names it as the reference template for VAST-tier
  creatures (world object + weather + music + quest script, not a spawn). The
  portable part is the *architecture* (world object, quest gate, dedicated
  weather/song, craftable summoning item) — all pure-XML work we can do
  ourselves. The non-portable part is its custom `ChezhouLib` C# that gives the
  worm a real multi-tile body (`SandWorm_Thing` + `SandWorm_HitProxy`); that
  library has no public source, so the multi-tile/burrow mechanic itself must be
  written original or built on a framework we already carry (e.g. Vehicle
  Framework, if a rideable form is wanted).
- **Krayt Dragon provenance:** `mlie.starwarsanimalcollection` ("Star Wars Animal
  Collection (Continued)"), MIT-licensed and open-source on GitHub
  (`emipa606/StarWarsAnimalCollection`), confirmed active in
  `ModsConfig.FULL.LATEST.xml` and present in the fauna cast at SUPER tier
  (`animal_census.csv:484,535`, `BiomeCast_Ashkarr.xml:522,607`). It is an
  ordinary `Animal` racial — the ruling's "keep it as is" leaves that untouched;
  the new sandworm is asked to be architecturally different (terrain-object, not
  wildlife-table).

## UNKNOWN

- Author/packageId/exact version support for Workshop id 3105413080 ("SandWorm",
  Pertam acid-worm pack) and id 2792203277 ("SHAI HULUD") — Steam Workshop pages
  were rate-limiting WebFetch for the whole session; only WebSearch snippets were
  available, not the full pages.
- Whether `chezhou.creature.sandworm` / `chezhou.chezhoulib.lib` has any private
  or semi-public source (no GitHub found in this pass; absence of evidence, not
  confirmed closed).
- No Workshop item matching "Mashed's Ashlands lava worms," "SOS2," or "Big
  Worms" surfaced under those names — not confirmed to exist, not confirmed
  absent.
- Exact license terms for `mlie.spaceworms` (Space Worms (Continued)) were not
  independently checked beyond the general pattern of mlie's "Continued" ports.
