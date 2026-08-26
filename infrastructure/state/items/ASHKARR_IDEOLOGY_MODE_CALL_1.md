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
