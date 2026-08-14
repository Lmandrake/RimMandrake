# Save-Based World Authoring Pipeline — RimWorld 1.6 Jawa Gravship Campaign

_How we build an exceptionally hand-crafted world by editing files directly instead of grinding the in-game UIs. Grounded in a byte-level teardown of Mr Samuel Streamer's **Gravtasm** starting save (`.rws`, RimWorld 1.6.4633 rev1261, 587 mods, 14.2 MB / 412k lines) pulled 2026-08-03._

**Decision context:** save-based model chosen by user 2026-08-03 (see `Custom_World.md`). Goal = have CoWork do the high-volume authoring in files; reserve the mouse for the irreducible engine step.

---

## The headline finding

**A RimWorld `.rws` save is plain, human-readable XML, and every element we'd normally set by hand in the UI is an editable node with legible values.** It has ID cross-references, yes — but the *authoring-relevant* parts (scenario, pawns, research, items, xenotype refs) read like a config file, not an opaque memory dump. This makes the save-based pipeline not just viable but the *better* path for a hand-crafted world.

**Established evidence (verified in the Gravtasm save):**

- The **entire scenario is baked into the save** as an editable `<game><scenario>` node — name, summary, description, player faction, and an ordered `<parts>` list of `ScenPart`s. You do NOT need a separate ScenarioDef file; the save carries its own.
- Scenario parts are self-describing and legible. Real examples pulled from Gravtasm:
  - `ScenPart_ConfigPage_ConfigureStartingPawns` → `pawnCount=3`
  - `ScenPart_StartingResearch` → `project=BasicGravtech` (and `BiofuelRefining`)
  - `ScenPart_StartingThing_Defined` → `thingDef=Chemfuel count=250`, `GravlitePanel count=400`, `MedicineIndustrial count=40`, etc.
  - `ScenPart_PlayerPawnsArriveMethod` → `method=Gravship`
  - `ScenPart_GameStartDialog` → the opening splash text
  - `LoanMod.ScenPart_Loan` → a *modded* scenario part (initialLoanAmount=1000000) — proving modded ScenParts serialize the same way and are editable.
- **Starting crew are cleanly isolated and fully editable.** The 3 player pawns live in the player faction (`GravshipCrew`, loadID 16). Each pawn's `<story>` node exposes `childhood`/`adulthood` backstory defNames, `traits`, `bodyType`, `hairDef`, `headType`, `favoriteColorDef`; each `<skills>` node lists all 12 skills with `level` + `passion` per skill. All hand-settable. (Gravtasm's Crash Gunderson / Jiff / Pat are the model.)
- **Xenotypes:** Gravtasm's `customXenotypeDatabase` is empty because it uses *mod-defined* xenotypes referenced by defName on each pawn (`<genes>` + kindDef), NOT the in-game custom-xenotype editor. For us this is ideal — our Jawa xenotype is a mod def (Outer Rim / Outland Genetics), so pawns just reference it by name.
- **Factions** are a world-level list; each has a `<def>` + a custom `<name>` (Gravtasm reskins every faction: Empire→"Snifflax Imperium", Pirate→"Grabulon Marauders", etc.). Faction *naming/flavor* is trivially editable; faction *rosters/relations* are ID-linked (edit with more care).
- The save's `<meta><modIds>` is the exact load order — 587 mods for Gravtasm. Confirms Streamer's caution: **the save assumes its full mod environment.** We read Gravtasm as a *structural template*, never load it in our stack.

---

## The three-tier authoring model (what goes where)

The core principle: **put all authored intelligence into files the game reads; use save-editing only for what the UI makes painful; do the one thing only the engine can do, in-game.**

### TIER 1 — Author ahead of time as DEFS / PATCHES (I do this, high confidence)

This is where I'm strongest and where ~80% of the "UI grind" disappears. All reproducible, version-controlled in GDrive, no fragility.

- The Jawa **xenotype** (mod def / patch), **ideoligion** precepts + the adopted **Scavenger role**, **reskinned/curated factions**, **Cherry Picker** kill decisions, **biome/Map-Designer scarcity** tuning, the **compat mod** (trader buy-filter patch, No-Durability config, etc.).
- These load at world-generation time, so the generated world already embodies our rules before we touch a save.

### TIER 2 — Surgical SAVE-EDITING on an existing valid save (I do this, with backups + validation)

Now proven safe for well-scoped edits, because the target nodes are legible:

- **Scenario polish:** edit the baked `<scenario>` — rename it ("crashed Factory ship" flavor), rewrite the GameStartDialog text, set starting research (`BasicGravtech` etc.), tune `StartingThing_Defined` counts (fuel/components/meals), set `pawnCount`.
- **Crew authoring:** hand-set each starting Jawa's backstory defNames, traits, all 12 skill levels + passions, name, appearance. This is the single most UI-painful task in vanilla RimWorld and it becomes a clean text edit.
- **Faction flavor:** rename/reskin factions to the SW roster.
- **Method:** always read-modify-write with a parser (preserve every untouched node), operate on a **backup copy**, validate the XML parses + reload-tests before it's the real save. Never author a whole save from scratch; only modify an engine-generated one.

### TIER 3 — Irreducible IN-GAME step (only you can do; kept minimal)

- Subscribe the mod list, load our scenario, **generate the world** (worldgen produces the map/terrain/faction placement — no text editor can conjure a valid world grid), embark, save once.
- Because Tiers 1–2 pre-load all the authored content, this is minutes, not the hours of UI grind it'd otherwise be. The save is the *output* we then polish in Tier 2, not something we hand-write.

---

## Recommended workflow (end to end)

1. **(T1)** I finish authoring the defs/patches: Jawa xenotype, ideoligion+Scavenger role, curated factions, scarcity tuning, compat mod.
2. **(T1)** I write the scenario as far as a ScenarioDef can carry it (start method, research, starting things, pawn count) so the manual step is thin.
3. **(T3, you)** Subscribe mods → load scenario → generate world with our biome profile → embark → save. One guided pass.
4. **(T2)** You hand me that save; I do surgical edits — finalize crew (backstories/traits/skills), scenario text/flavor, faction names, item counts — against a backup, validated.
5. **(T3, you)** Load the edited save, sanity-check in-game, save again as the campaign seed.
6. Iterate 4–5 as the world evolves.

## Tradeoffs & risks (honest)

- **Upside:** most authoring becomes fast, reproducible file work; the brutal pawn-setup UI grind collapses to text edits; everything backed up in GDrive.
- **Risk:** save-editing is inherently fragile — ID cross-references mean a careless edit to roster/relations/thing-graph can corrupt a load. **Mitigation:** backups + parse-validation + reload-test + keep edits to the legible/low-linkage nodes (scenario, pawn story/skills, faction names). Avoid hand-editing the thing-ID graph or map cell data.
- **Irreducible manual step:** I can't drive the running game; worldgen + embark + load-test are yours. Kept to minutes.
- **Alternative (safer, less powerful):** pure Tier-1 def/scenario authoring, zero save-editing — accept more manual in-game pawn setup. Fallback if save-editing ever proves flaky on our specific mod set.

## Verified defName vocabulary harvested from Gravtasm (reusable examples)

- Gravship start: `ScenPart_PlayerPawnsArriveMethod method=Gravship`; player faction def `GravshipCrew`; surface layer `SurfaceLayerFixed`.
- Odyssey research defNames seen: `BasicGravtech`, `BiofuelRefining`.
- Starting-thing defNames seen: `Chemfuel`, `MealSurvivalPack`, `MedicineIndustrial`, `ComponentIndustrial`, `GravlitePanel`.
- Pawn story fields: `childhood`, `adulthood` (backstory defNames), `traits`, `bodyType`, `hairDef`, `headType`, `favoriteColorDef`, `birthLastName`.
- Skill node: 12 `<li>` each with `<def>` (Shooting…Intellectual), `<level>`, `<passion>` (None/Minor/Major + modded passions like `AS_IntimatePassion` from Vanilla Skills Expanded — confirm ours before use).

_All defNames above are from Streamer's 587-mod stack; **confirm each against OUR installed mods before use** — never feed a guessed defName to a scenario/save edit (standing engineering rule)._

---

## Next steps — Tier 1 authoring sequence (agreed order, not yet started)

When we resume authoring, work in this order (each step feeds the next; all are Tier 1 file work I can do, then confirm defNames against the installed stack):

1. **Scenario def for the crashed-Factory-ship start** — arrival method (`Gravship`), starting research, starting things + counts, `pawnCount`, GameStartDialog splash text. Modeled on Gravtasm's `<scenario>` parts. Makes the eventual in-game pass (Tier 3) thin. _Do this first — it's the spine everything else hangs on._
2. **Jawa founding crew personas** — Backstory Constructor: 3–5 named survivors with lore, backstory defNames, traits, skill/passion spreads, workDisables. Locks the characters; later injected via Tier 2 save-edit into the isolated player-faction pawn blocks.
3. **Curated/reskinned factions** — SW roster names + Sensible Factions allow-list + Empire fusion (per required_mods.md); confirm VGE-pursuer compat.
4. **Scarcity + world-shape tuning** — Choose Biome Commonality + Map Designer profile (ruins/ore UP, harsh planet), plus the animal-density mod (Choose Wild Animal Spawns).
5. **Compat mod contents** — trader buy-filter TraderKindDef patch, No-Durability config, any Cherry-Pick-as-patch items.

Then: Tier 3 in-game generation pass (user) → Tier 2 surgical save polish (me) → seed save.

**Blocked/parallel:** the Outer Rim §19.5 weapon-balance audit is independent source work that can run anytime and unblocks the No-Vanilla-Weapons + SW-gear Cherry-Pick decisions.

---

## Future-discussion items (parked, not yet designed)

- **Live map "enhancement" via save-editing a newly-landed map (FUTURE — explore together, 2026-08-03).** Idea: after landing on a fresh map, use save-editing to *enrich* that specific map — inject extra creatures, structures, ruins, loot, set-piece encounters, etc. — to hand-craft a more interesting arrival than worldgen produced. This is a distinct capability from the Tier-2 work above (which edits the legible low-linkage nodes: scenario, pawn story/skills, faction names). Adding things to a *live map* means writing into the map's thing-list / cell data — the higher-linkage, higher-fragility region the current pipeline deliberately avoids. **Not decided, not scoped** — recorded as a future exploration. When we take it up, the open questions are: (1) which map entities are safe to inject by hand vs. which corrupt a load; (2) whether a mod-assisted route (e.g. dev-mode spawn + save, or a placement mod like Map Designer / a set-piece mod) is safer than raw save-injection; (3) how to backup + reload-test each injection. Likely lands as a new "Tier 2b — live-map enrichment" once researched.

- **🅿️ Save-scouting: how legible is the world/tile map in a live save? (PARKED, probed 2026-08-05 on the Gravtasm save; user asked "can you 'see' the tile map his savegame currently occupies … as scouting info").** Verdict: **the world layer is highly legible; the per-tile biome grid is the one part that needs work.** Concrete findings, all [evidence] from the Gravtasm `.rws`:
  - **World objects / settlements / factions — trivially readable.** A single regex scan over `<worldObjects>` enumerated all **135** objects with Class / ID / tile / faction / name intact. **The player colony = `id=134`, `tile=9581`, surface layer `0`, `Faction_16`, name `"Colony"`.** Neighboring settlements (Ithna, Palo Pinto, …), 34 space settlements, and asteroid map-parents are all plain-text. So a save read can answer "where is the colony, who are the neighbors, which factions are placed where" **directly, no decoding** (method: `skills/rimworld-savegame/SKILL.md`).
  - **The map itself is bound to that world tile** via `mapInfo`: colony map `<parent>WorldObject_134</parent>`, `<size>(225, 1, 225)</size>`. Tile↔map linkage is explicit.
  - **The per-tile biome grid IS present but encoded in two stacked layers.** It lives in `<tileBiomeDeflate>` = base64 of **raw DEFLATE** (decompress with Python `zlib.decompress(base64.b64decode(blob), -15)`; wbits 15/31/47 all fail "incorrect header check"). Surface layer 0 → 43,744 bytes = **21,872 tiles** as little-endian `uint16`. Tile 9581's value = **4740**.
  - ### ✅ Biome/terrain codes ARE reversible offline — corrected 2026-08-12

    **Tile 9581 is `Savanna`** (Advanced Biomes (Continued)). The earlier claim
    that codes "cannot be reversed from the save text alone" rested on testing
    `StableStringHash & 0xFFFF`, which is not the operation RimWorld uses.

    ```python
    def short_hash(defName):                      # RimWorld's ShortHashGiver
        h = 23
        for ch in defName:
            h = (h * 31 + ord(ch)) & 0xFFFFFFFF   # StableStringHash, 32-bit wrap
        if h >= 0x80000000: h -= 0x100000000      # ...as SIGNED int32
        return int(math.fmod(h, 65535)) & 0xFFFF  # % 65535 (NOT 65536, NOT a mask),
                                                  # C# truncating %, cast to ushort
    ```

    **The rule, the three ways to get it wrong, and the measured accuracy per def
    type are in `skills/rimworld-savegame/SKILL.md` §5.** Do not restate them here.

    The safe discipline, borrowed from Rimmap (`docs/SAVE_FORMAT.md`), is
    **compute the hash locally, then confirm it already appears in the save's
    grids before writing** — that catches a collision-bumped def without needing
    the load order at all. Prefer the live dump's own `shortHash` field, which is
    the engine's authoritative value rather than a computed one.

  - **Still true, and still the cheap route for most questions:** the
    world-object/faction/settlement layer is plain text and answers "where am I,
    who's around me, what's placed" with no decoding at all. Reach for the grids
    only when you actually need per-cell semantics.

---

**Artifacts:** raw save at `~/GDrive/Personal/Rimworld/observed/2026-08-13/savegame/03_Gravtasm__starting_save.rws` (moved here from the Fetcher delivery 2026-08-05; kept as structural reference, do NOT load in our stack). Analysis performed 2026-08-03.
