> ⛔ SUPERSEDED BY `CORRECT_ASHKARR_IDEOLOGY_1`. The trade below is a FALSE ONE: the
> "world creation only" clause in *Why this reaches you and not DECIDE* is wrong.
> `FactionIdeosTracker.ChooseOrGenerateIdeo` is an ordinary public method that assigns a
> faction's ideo on a running save, and `IdeoGenerator.MakeFixedIdeo` never sets the
> per-Ideo `classicMode` flag the leader-title route actually reads. Read the successor
> before acting on anything here; the readings of what IS in the world stay correct.

# ASHKARR_IDEOLOGY_MODE_CALL_1 — 🔴 for the OWNER. The twelve ideoligions are not in the world.

Measured live and on disk, 2026-08-26, seat CHECK.

## What is true

**Ash'karr was created with Ideology in CLASSIC mode.** The world holds **one** ideoligion —
vanilla's `Astropolitan`, carrying `Classic_DanceParty` / `Classic_DrumParty` — and all 95
non-player believers are in it. `<classicMode>True</classicMode>` is in **every Ash'karr save
back to 2026-08-24**, including `ASHKARR_WITHER_2026-08-26`.

⇒ *the Weight* · *the Balance* · *Meckgin* · *the Ascendant Genome* · *the Continuity Protocol*
and the other seven **do not exist in the world**, and every faction's leader is titled `leader`.

## What is NOT wrong

The content is authored and correct. All twelve FactionDefs carry `<fixedIdeo>true</fixedIdeo>`,
`<requiredPreceptsOnly>true</requiredPreceptsOnly>`, an `<ideoName>` and a written
`<ideoDescription>`. `src/Jawa/Jawa_Patches/Defs/CultureDefs/JawaLeaderTitles.xml` ships twelve
`CultureDef`s each with its own `leaderTitleMaker` — the exact route
`IdeoFoundation.GenerateLeaderTitle` uses, already built and already correct.

🔑 **Nothing needs writing. The world simply never used any of it**, because classic mode
short-circuits before the culture is consulted (`IdeoFoundation.cs:697`).

## Why this reaches you and not DECIDE

Your own ruling in `CLAUDE.md`: *"a faction, ideoligion or setting absent when he builds it is
absent from every player's game forever."* This is that case, and the setting is chosen **at world
creation only** — it cannot be retrofitted onto an existing world by any def, patch or bridge call.

The trade is yours alone:

* **Re-create the world with Ideology in full mode** — the twelve ideoligions and their leader
  titles come alive. ⚠️ Cost: the authored planet. Roads, rivers, the three seas, the Wither canyon
  rebuild, the hilliness pass, 13,655 mutator placements, 96 settlements, 72 named regions — many
  sessions of hand authoring, and the world CSV/bundle would have to be re-imported onto the new
  world. Whether that import is faithful is itself unproven (`WORLD_PORT_SURVIVES_BRIDGE_1`).
* **Ship classic mode** — one shared ideoligion, every leader titled `leader`, the twelve written
  religions unused. Cheap, and it is a real loss of authored content.

⛔ CHECK does not choose between these and has not touched the world. Everything above is a
reading.

Evidence: `infrastructure/state/evidence/leader_titles_and_classic_mode_2026-08-26_CHECK.md`

## What a rebuild would actually cost — measured, because the trade above is unfair without it

I checked which parts of the planet can be carried onto a NEW world by a **file import**, and which
would have to be re-authored by replaying scripts. This is the honest cost side of option 1.

**Restorable from a file, in one call each:**

| bundle | tool | takes |
|---|---|---|
| per-tile scalars — biome, elevation, temperature, rainfall, **hilliness**, swampiness, pollution | `jawa/world_tile_import` | `path`, `apply`, `expectTiles` |
| rivers and roads | `jawa/world_links_import` | `path`, `apply`, `clearFirst` |
| settlements | `jawa/world_settlements_import` | `path`, `apply`, `clearExisting` |
| named regions / features | `jawa/world_features_import` | `path`, `apply`, `clearExisting` |

A dry run of the tile import against the VIVIFIED bundle reports **21,872 rows, 21,872 applied,
0 skipped**, and the export→validate path is lossless at 21,872/21,872 on RAW fields
(`WORLD_PORT_SURVIVES_BRIDGE_1`).

**🔴 NOT restorable from a file — there is no importer for either:**

* **mutators** — **13,569 tiles carry them**. `jawa/world_mutators_set` takes `tiles` + `mutators`
  per batch, not a path.
* **landmarks** — **579 of them**. `jawa/world_landmarks_set` takes `def` + `tiles` per batch, not
  a path.

Both are reconstructible by re-running the authoring scripts against the CSV bundles — that is how
they were placed in the first place, and `world/audit_2026-08-26/` holds the working ones. ⚠️ **But
it would not come back identical.** A landmark's own `mutatorChances` roll fires when it is placed,
and the 2026-08-26 pass measured those rolls dropping `MixedBiome`, `AnimalLife_Decreased`,
`Stockpile`, `AnimalHabitat` and `WildPlants` onto tiles nobody chose. A replay rolls again.

⇒ **Option 1 is not "regenerate and repaint".** It is: create the world in full Ideology mode, run
four file imports, then re-run the mutator and landmark authoring and accept that the incidental
texture differs. Everything deliberate survives; some of the accidental character does not.

⛔ **And one thing I did NOT test:** the import half has never been run. §12.4 rule 3 forbids it with
a map instantiated, and one is. Until it runs at a world screen with no map, "four file imports"
is a plan, not a proven route. Its blocker is `BRIDGE_CANNOT_MAKE_A_WORLD_1` — the bridge cannot reach
the world-creation page, so that step is your hands either way.
