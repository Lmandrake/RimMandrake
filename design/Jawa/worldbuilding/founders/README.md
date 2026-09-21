# Founders export — FOUNDERS_EXPORT_TO_REPO_1

Exported 2026-09-20. This is the third of the three artifacts
`WORLD_REMAKE_FINAL_STEP_1` names as surviving the world remake (worldmap,
gravship, founders) — the founders were the one not yet in the repo.

## Source

- Save: `CANONICAL_ASHKARR_START_2026-09-12.rws`
- Path (Windows): `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\CANONICAL_ASHKARR_START_2026-09-12.rws`
- Size: 17,500,721 bytes
- mtime: 2026-09-20 07:28:55 (local)
- md5: `75be9ecd4764a397e9802d997bb9e0b9`
- A sibling backup, `CANONICAL_ASHKARR_START_2026-09-12.rws.bak-pre-founder-scrub-20260920T134157Z`
  (17,589,878 bytes, 2026-09-18 22:41), confirms the "founder scrub" the item
  flagged: the source save is 89,157 bytes *smaller* than its pre-scrub backup,
  consistent with a duplicate/dead pawn having been removed. **This export was
  taken from the post-scrub save**, i.e. the current, live founder roster —
  not the backup.
- The save itself, and the Saves folder, were not modified by this export.
  A read-only copy was made to scratch space, verified byte-identical by md5,
  and all extraction was read-only parsing of that copy.

## Founder count: 6 human colonists (+ 2 named colony animals, exported alongside)

**How determined:** parsed the save with `xml.etree.ElementTree` (no grep/regex —
this is a def-shortHash-bearing binary-adjacent file per the `rimworld-savegame`
skill, though the pawn list itself is plain XML). Steps:

1. `game/world/factionManager/allFactions` — found the faction with
   `<def>PlayerColony</def>`, `<loadID>21</loadID>`. This is the authoritative
   player faction (there is no `<isPlayer>` field in this save's schema; the
   `PlayerColony` def is the tell).
2. `game/maps[0]/things` — of 21 `Pawn`-class things on the single map, exactly
   8 carry `<faction>Faction_21</faction>` (the `Faction_<loadID>` reference
   format). The other 13 belong to other factions physically present on the
   map (Hutt Cartel raiders/visitors, a mechanoid militor/scorcher squad,
   wild Scavrats).
3. Of those 8, 6 have `<def>Human</def>` and `<guest><joinStatus>JoinAsColonist</joinStatus>`
   with `hostFaction`/`slaveFaction` both `null` — free colonists, not
   prisoners or slaves of the player faction. The remaining 2 are named
   non-human pawns (`AA_Eyeling` "Marquee", `RSW_Dewback` "Geonosis") — colony
   pets/mounts, not people, exported separately for completeness but not
   counted as "founders."
4. Cross-checked `game/world/worldPawns` (`pawnsAlive`/`pawnsMothballed`/`pawnsDead`)
   for other `Faction_21` members not on the map. Found several — including a
   **dead** pawn also named "Wim Twice-Kin Ateeka" (`Human470533`, in
   `pawnsDead`) distinct from the **live** on-map "Wim Twice-Kin Ateeka"
   (`Human632207`). This is direct evidence of the founder scrub: a broken/
   duplicate Wim was removed and the map now carries a clean replacement with
   the same name. Also found one live off-map `Faction_21` pawn, "Alyssa
   Sparkles Orchard" (`Human953`, generic vanilla `Colonist` kindDef, in
   `pawnsAlive`), and several more `Colonist`-kind `Faction_21` pawns in
   `pawnsMothballed`/`pawnsDead`. **These were excluded from the founder set**:
   none are on the starting map, none carry a Jawa-specific kindDef
   (`RSW_Jawa`/`RUT_Jawa_Colonist`/`RSW_RimMandrakeJawa_Kind`), and they read
   as leftovers from earlier/other saves merged into this world file, not
   members of the founding colony. This export follows the item's own framing
   — "the player-faction colonists of the starting colony" — i.e. who is
   actually on the start map, not every `Faction_21`-tagged pawn the save has
   ever touched.

**The 6 founders:**

| name | nickname | kindDef | pawn id | file |
|---|---|---|---|---|
| Wim Ateeka | Twice-Kin | `RSW_RimMandrakeJawa_Kind` | `Human632207` | `founder_WimTwice_KinAteeka_Human632207.xml` |
| Griz Utinn | The Hands | `RSW_Jawa` | `Human470527` | `founder_GrizThe_HandsUtinn_Human470527.xml` |
| Yeku Yeku | First-Hatched | `RSW_Jawa` | `Human470530` | `founder_YekuFirst_HatchedYeku_Human470530.xml` |
| Tobb Nkik | Keeper | `RSW_Jawa` | `Human470524` | `founder_TobbKeeperNkik_Human470524.xml` |
| Nekko Vok | Captain | `RSW_Jawa` | `Human470521` | `founder_NekkoCaptainVok_Human470521.xml` |
| Sekki Vosh | The Long Pot | `RUT_Jawa_Colonist` | `Human669116` | `founder_SekkiThe_Long_PotVosh_Human669116.xml` |

**Colony animals (exported, not counted as founders):**

| name | kindDef | pawn id | file |
|---|---|---|---|
| Marquee | `AA_Eyeling` | `AA_Eyeling669122` | `animal_Marquee_AA_Eyeling669122.xml` |
| Geonosis | `RSW_Dewback` | `RSW_Dewback669123` | `animal_Geonosis_RSW_Dewback669123.xml` |

## Export format chosen, and why the preferred options weren't used

The item's preference order was (a) CharacterEditor presets, (b) a
hand-authored def/scenario block, (c) a faithful XML extract of each
founder's `<li>` from the save. **(c) was used.**

- **(a) CharacterEditor presets — not done.** Character Editor and Character
  Editor Retextured are both active in this save's mod list (617 mods, see
  `_modlist_at_export.txt`), so the mod exists, but its own data folder
  (`…/RimWorld by Ludeon Studios/CharacterEditor/`) holds only `options.txt`
  and `pawnslots.txt` — no export tooling for it exists anywhere in this repo
  (checked `src/` and `skills/`), and producing a preset per founder is an
  interactive, in-game, per-pawn UI action. That requires loading this exact
  save into a running game and driving Character Editor's export button six
  times through the bridge/UI-automation — live-game work, out of scope for
  a read-only extraction task and a materially larger, riskier undertaking
  than parsing the save directly. Not attempted.
- **(b) hand-authored def/scenario block — not done.** A `ScenPart_ConfiguredPawns`-style
  reproduction would have to re-express, in a different XML schema, everything
  a raw pawn already carries — and would inevitably approximate rather than
  reproduce (health state, exact inventory items with their materials/quality/
  hit points, ideo certainty, precise relationship graph, mood/needs at save
  time, gene set with load-order-sensitive overrides). It is strictly lossier
  than option (c) for the same effort, so there was no reason to prefer it.
- **(c) raw `<li>` XML extract — done.** Each founder's (and each animal's)
  complete `Pawn` XML element was parsed straight out of the save copy and
  written verbatim (re-indented, otherwise untouched) to its own file. This
  is the actual Scribe-serialized object graph RimWorld itself would produce
  — story, skills, traits, health, needs, genes (`endogenes`/`xenogenes` fully
  inline), apparel and inventory (full embedded `Thing` sub-elements, not
  references), ideo, social relations, mechanitor/psychic state, and every
  mod-added component data blob (Vehicle Framework, Alien Races, Ascension,
  face controller comps, etc.) — everything the save itself holds for that
  pawn, losslessly.

## What round-trips and what does not

**Round-trips (fully preserved in each `founder_*.xml` file):** name, backstory,
traits, skills + passion, age, gender, health/hediffs, needs/mood snapshot,
genes (xenogenes + endogenes, inline with load IDs), apparel and equipment
(inline full `Thing` objects with material/quality/hit points/color), ideo
membership and certainty, work settings, outfit/food/drug policies, style,
mechanitor state, and every mod component's saved data for that pawn.

**Does NOT round-trip as a standalone file, and needs care on re-import:**

- **Cross-pawn references are by save-local Thing ID, not embedded.**
  `social/directRelations` points at other founders via strings like
  `Thing_Human470524` — e.g. Nekko Vok's relations reference Tobb Nkik, Griz
  Utinn, Yeku Yeku and Wim Ateeka by these exact IDs. Re-importing founders
  independently (not all together, with these same IDs preserved) breaks
  their relationship graph. Re-import all 6 files together, in one save, with
  IDs intact, to keep relations working.
- **These are fragments, not loadable save files.** A bare `<li Class="Pawn">`
  element is not something RimWorld's Scribe can load on its own — it expects
  the pawn inside a map's `things` list (or `worldPawns`), inside a full save
  with its own `<meta>`, faction manager, unique-ID manager, etc. Re-import
  means splicing these `<li>` elements back into a save's `things`/`worldPawns`
  list (or writing an importer that does the equivalent through the game's own
  object model), not double-clicking the file.
- **The faction reference (`Faction_21`), the ideo reference (`Ideo_20`) and
  the map reference (`<map>0</map>`) are save-local indices**, not stable
  identifiers — they only mean what they mean inside *this* save. Splicing into
  a different save requires remapping all three.
- 🔴 **Every `<loadID>` in these files is save-local too, and a collision does
  not error — it resolves to the WRONG object.** Gene loadIDs run 329–2035,
  hediff 286–1773, job 36107–36112. A destination save that has already issued
  gene loadIDs in that range makes each founder's `Wimp` trait — the only trait
  they carry with a non-null `<sourceGene>` — point at one of the destination's
  own genes, and the trait is silently dropped with nothing in `Player.log`.
  MEASURED 2026-09-21: 5 of 6 founders lost it; the sixth (Sekki, `Gene_2009`,
  above the destination's `nextGeneID`) kept it. **Reallocate every `<loadID>`
  above the destination's issued range and rewrite the `Gene_<n>` references with
  it** — `import_founders.py` does this, computing the base per destination. A
  fixed constant (the +1,000,000 of the proving run) is correct only for
  destinations that happen to sit below it.
- **The destination's `<uniqueIDsManager>` counters must be raised past every id
  the fragments carry** — `nextThingID`, `nextGeneID`, `nextHediffID`,
  `nextJobID` — or the receiving game hands out ids that collide with the
  imported pawns.
- **Mod-set dependency.** These files were extracted from a save built against
  the exact 617-mod set in `_modlist_at_export.txt`. Every `<def>` reference
  (kindDef, hediffs, gene defs, apparel defs, trait defs, mod component types)
  resolves only if the destination save/game loads a mod set providing the
  same defNames. No shortHash-encoded binary grids are involved here (this is
  the plain-XML pawn list, not a map terrain grid), but def *identity* is
  still mod-set-dependent per the savegame skill's general rule.
## The round trip, MEASURED 2026-09-21

Proven in game. All 8 fragments were spliced into a *foreign* save — different
world, player faction `Faction_17`, ideo `Ideo_12`, 69 colonists of its own — with
the four remaps above applied, and loaded on the full 618-mod list. All 8 pawns
arrived. Compared field-by-field against the same pawns read live from the
canonical world beforehand (name, backstories, body/head/hair/beard, gender, ages,
kindDef, apparel with hit points, equipment, hediffs, all 12 skills with passion,
all traits, all genes, all relations): **5 of 8 identical in every field**, the
other 3 differing only by `ageChronologicalYears` +1 (the destination sits at a
different in-game date) or by one hediff the receiving game *adds*. The five-way
relation clique and both animal bonds resolved by name.

Without the `<loadID>` offset the load still "succeeds" and quietly costs a trait —
see the bullet above. Evidence and method:
`Transient/founders_roundtrip_2026-09-21.md`; item:
`infrastructure/state/items/closed/FOUNDERS_EXPORT_TO_REPO_1.md`.

## The importer — `import_founders.py`

```
python3 design/Jawa/worldbuilding/founders/import_founders.py <destination.rws>
python3 design/Jawa/worldbuilding/founders/import_founders.py <destination.rws> --dry-run
```

One command, all four remaps, no prose to rediscover. It reads the destination's
own PlayerColony faction, its primary ideo, its map uniqueID and size, and the
**highest id it has actually issued** in each class, then allocates the fragments'
gene / hediff / job / ability ids above those and rewrites every reference with
them — including the `Gene_<n>` refs that cost the `Wimp` trait. It raises
`nextThingID`/`nextGeneID`/`nextHediffID`/`nextJobID`/`nextAbilityID` past
everything it imported, lands the eight pawns in a row beside the destination's own
colonists, writes in binary mode only, backs the destination up first, and
**refuses by name to write to `CANONICAL_ASHKARR_START_*` or `ASHKARR_FALLLINE_*`**.

Thing ids are left as exported — the closed 62-reference relation graph is what
makes the founders arrive as a family — unless the destination already holds one,
in which case all 22 are reallocated together.

Regression guard: `src/RimMandrake/Utils/selftest_import_founders.py`, 28 cases,
calibrated against both evidence saves from the 2026-09-21 run.
