# REPO_PRIOR — what RimMaster has already decided about dungeons

Compiled 2026-09-11. Every claim below is CONFIRMED (read from a cited file)
unless marked UNCERTAIN. Dates are the file's own or the ledger event's.

## (i) Standing rulings that constrain dungeon design

- **No worldgen, ever, permanently.** CLAUDE.md: *"There is no worldgen
  feature, in any version"*; *"Do not build anything that produces
  ALTERNATIVE planets"* (owner, 2026-08-18/08-15). Every dungeon/site is a
  FIXED tile hand-authored on the one frozen map, `design/Jawa/worldbuilding/
  the_one_map.md` (adopted 2026-08-22; "no generator... nothing that can
  produce a second planet"). `dungeons_arc_spec.md` §1 restates this per
  dungeon: "every site below is a FIXED tile... authored in place via the
  bridge's KCSG tools."
- **A dungeon is already a defined shape here** — restated from `03_deep_history.md`
  and `dungeons_arc_spec.md`: a **canon triad** for vaults — ① mechanoid
  garrison held, ② the enemy's flesh weapon loose, ③ frozen Rakata (rare,
  emotional). Owner-ruled **concentric grammar**, varied per type: outer ring
  states condition at a glance, garrison ring is the fight, core is the
  payoff (`VAULT_DUNGEON_CONCEPT_1`, closed 2026-08-30, point 2). A
  **thaw-gate** pattern (deliver an old power core → dormant flips to
  hostile/active, one-way) is now used identically for both the Assailant
  complex and vault V6 (`dungeons_arc_spec.md` §2.3, §3.9; `vault_thaw_quest_family.md`
  §2.1). A **wake/loot/leave** payoff ladder for the "frozen sleepers" content
  type, each branch with real authored consequence (`VAULT_DUNGEON_CONCEPT_1`
  point 3; canon.yml `rakata.woken_brutality`).
- **LARGE maps, floor 300×300, actual ruling 325×325** (owner, 2026-09-01) —
  the vanilla `initialMapSize` ceiling, still warning-free.
- **KCSG (`KCSG.StructureLayoutDef`/`SymbolDef`) is the confirmed authoring
  route**, already wired to the bridge (`jawa/kcsg_place`) — no new C# needed
  to place a template (`dungeons_arc_spec.md` §3.5).
- **Register guard**: tyranny/horror is REVEALED content, never ambient in a
  pre-reveal bio/tooltip (`03_deep_history.md`, owner 2026-08-20/08-29).
  "the Forsaken" exonym in narrator text; "Rakata" only in their own mouths.
- **Anomaly content is quarantined**: zero ambient Anomaly in v1 except
  inside the Assailant dungeon (and possibly the Sarlacc) — canon.yml
  `anomaly_content`, owner 2026-08-29. Vault dungeons are explicitly NOT
  covered by this exception.
- **Reveal channel is CARTOGRAPHY** (the Antiquities research tree): vault
  sites are revealed by reading urns, not stumbled on; V6 additionally needs
  VOICE (`vault_thaw_quest_family.md` §1.1, `antiquities_design.md`).
- **Age-register ban**: never quote "ten thousand years"/"millennia" as bare
  fact in authored prose; use hedged belief language ("ages past," "believed
  to be... though little is known") — repo-wide, owner ruling 2026-09-11
  (`SCENARIO_DURATION_CUT_1`), 54-hit census, still 16 sanctioned exceptions.
- **Content lock-in still needs a live bench sitting** — `ASSAILANT_DUNGEON_BUILD_1`
  is explicitly BLOCKED (2026-09-06 ledger note) because "KCSG authoring/art/
  dialogue is a joint BENCH+owner session, not solo FOUNDRY build." Do not
  treat any HELD-FOR-OWNER line in `dungeons_arc_spec.md` as settled.
- **Faction Territories mod** is the intended answer for vaults sitting on
  another faction's ground (raids proportional to settlements) — identified,
  not yet built (`dungeons_arc_spec.md` §3.8, owner ruling point 4).
- **Tedium warning, adjacent but real**: "Quest-gating every gravlite panel
  would create administrative tedium rather than meaningful progression"
  (`Gravship_Campaign_Planning_Discussion_2026-08-02.md:403`) — the closest
  the repo gets to an explicit session-length/tedium ruling; no other hit
  found for dungeon pacing specifically.

## (ii) Prior art to build on

- **Two dungeons are ALREADY BUILT past spec into real, offline-validated
  XML**: `VAULT_THAW_QUEST_FAMILY_1` (2026-09-05) shipped eight
  `QuestScriptDef`s (`src/RimUtinni/VaultDungeons/`) wiring six fixed-tile
  vault Sites, a thaw mechanism (`RUT_VaultHeart`, a dead `CompPowerPlant`
  refueled by one `AIPersonaCore`), wake/loot/leave signal branches, a
  ship-claim-conflict chain, and a late-game Reclamation quest with a
  faction-goodwill flip. It documents its own gaps as filed findings (a
  casket-open signal sender, cross-map "everyone you woke" memory,
  dominated-neutral state) rather than guessing C#.
- **Six vault sites are sited and locked**: `vault_siting_prep.md` +
  `dungeons_arc_spec.md` §3.2 give exact tile IDs, biomes, landmarks, and
  conflict notes for V1–V6, chosen to keep contamination-class ground (①) and
  bioweapon-class ground (②) separate — a real environmental-storytelling
  rule (`ASHKARR_WORLD_DEFINITION.md` §6c).
- **A second dungeon family (non-vault) is in active build**: `ANCIENT_WAR_LAB_1`
  (a submerged war lab under a propane lake, live Assailant specimens under
  study, reachable only by a submerged route) and `SCALD_DARK_TOWER_1` (a
  Rakatan high-command tower in a crater lake, ocular-warped Assailant
  infiltrators) — explicitly ruled as separate, non-mergeable sites sharing a
  theme (owner, 2026-09-07/08).
- **A "permanent world scar" ending mechanism is scoped**: `WAR_LAB_CRATER_HOOK_1`
  proves `Tile.PrimaryBiome`'s public setter + the bridge's
  `world_tile_set`/`world_commit` cache-regen sequence can survive save/load —
  reusable for any dungeon with a destructible/permanent-consequence ending.
- **Site templates already exist as a library**: `design/Jawa/templates/*.lua`
  (dead beacon, crashed ship, droid battery bunker, krayt graveyard, imperial
  waystation, moisture farm ruined, podracer wreck, rakatan trace, etc.) —
  reusable scattered-site content, distinct from the vault/dungeon KCSG route.
- **`skills/rimworld-scene-composition/SKILL.md`** already encodes
  set-dressing/verticality doctrine and a 5-metric grading rubric (visual
  recognizability etc.) for exactly this content type — use it rather than
  re-deriving "how to make a ruin read as one place."
- **`skills/rimworld-quests/SKILL.md`, `rimworld-world-editing`,
  `rimworld-layout-layers`, `frozen-artifacts`** are the toolchain: quests
  are QuestScriptDefs firing once at offer time (signal-string wiring is
  fragile); world edits need `world_commit`; layered systems (power/roof/
  access) get checked per layer; frozen sheets need the freeze-worthiness
  test before locking content.
- **The Doctrine of the Unwritten / Antiquities tree** (`antiquities_design.md`,
  owner 2026-09-04) is the meta-progression gating dungeon discovery: reading
  urns unlocks LANGUAGE→RELIGION→CULTURE→CARTOGRAPHY→VOICE, and CARTOGRAPHY
  is literally what reveals vault coordinates.

## (iii) Dead/dropped approaches, and why

- **`ANCIENT_DANGER_GARRISON_1`** — dropped, "premise rejected by the owner;
  no live check is owed" (ledger).
- **The ancient-urban-ruins mod family** (mall/metro map generator,
  `xmb.ancienturbanruins.mo`+kin) — CUT 2026-09-09, owner verbatim: "strange
  mall maps and other nonsense that really isn't very star wars at all"
  (`ANCIENT_RUINS_FAMILY_CUT_1`/`_MOD_AUDIT_1`). Its generation TECH was
  explicitly reviewed for lessons before the cut, per the audit's step-3
  question — check that audit before reinventing procedural-ruin generation.
- **`OCULAR_OVERDRIVE_SITE_1`'s original "Overdrive" framing** — superseded
  same day it was filed; survives only as the Ashfall Research Base dungeon
  concept (Helix/Assailant genetics reveal).
- **Sarlacc pit-gate and "They!" giant-ant nests** — confirmed buildable but
  explicitly parked to v2 as "living-location dungeons" behind the Assailant/
  vault work (`FUTURE_VECTORS.md`); ants need a world-creation faction tick,
  so v2 needs a fresh save either way. Not dead, just sequenced after.
- **World-savegame-write pipeline for the map itself** — killed 2026-08-18;
  irrelevant to dungeons directly but explains why every site placement rides
  the live bridge (`world_commit`), never a save edit.

## (iv) Open questions the repo raises but does not answer

- No general taxonomy exists yet for "travel-to site map" vs. "sealed
  sub-structure in a colony map" vs. "chained dungeons linked by a key" — the
  repo's dungeons so far are all travel-to Sites (quest-generated) or fixed
  bridge-placed structures; nothing found matching your third shape (chained
  by key/coordinate/knowledge) except the Antiquities CARTOGRAPHY-reveals-
  coordinates mechanism, which is a reveal gate, not a chain of discrete
  dungeons.
- No repo-wide list of ALL sites/dungeons/landmarks intended for the frozen
  world — only per-item tile assignments (vaults, war lab, dark tower,
  Gaping Doom, Lightfall, Ashfall Research Base, player-start junkyard). No
  single roster file was found; `ASHKARR_WORLDMAP_landmarks.csv` (563 rows)
  is the closest thing to a master list but is data, not curated design.
- Difficulty/progression arc for dungeons specifically is undated: the
  campaign's broader arc order lives in `09_arcs_dungeons_quests.md`, but no
  file states dungeon-to-dungeon difficulty tuning or session-length targets.
- Whether a custom C# QuestPart/signal-sender is acceptable is repeatedly
  "HELD FOR OWNER" per-instance rather than ruled once in general — each
  dungeon item re-raises it.

Findings file: `research/game_design/findings/REPO_PRIOR.md`.
