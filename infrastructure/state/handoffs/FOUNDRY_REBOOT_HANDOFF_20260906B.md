## spec

**READ FIRST on wake.** Session wrap before an owner-requested agent reboot,
afternoon of 2026-09-06 (follows the morning's `FOUNDRY_REBOOT_HANDOFF_20260906`).
Everything below is committed and pushed; nothing is sitting uncommitted in the
working tree from this session. Bridge is FREE, game is DOWN, live ModsConfig
matches FULL.LATEST (598 mods, md5 `a62d0338`).

## What happened this session, newest first

1. **`rimworld-scene-composition` skill, round 2** (`b385bd8c`) — a fresh
   critical-reviewer pass on the three Deep Desert templates found real,
   still-open defects. See "Still open" below — this is the most actionable
   next work in the whole handoff.
2. **Two mods added + scene-composition skill created** (`1dad3345`,
   `f9f6f69c`, `9ce6f734`) — owner-requested: SimpleStairs (fork,
   `rw.mod.simplestairs`) and Simple Visual Stairs (`Kutte.Stairs`) added to
   both FULL and MINIMAL mod lists (already-downloaded workshop items, no
   Steam action needed). New skill `skills/rimworld-scene-composition/`
   built from scratch: a 5-metric scoring rubric (relevance, recognizability,
   coherence, interest, distraction) plus doctrine for using these stairs
   mods and the already-active Decorative Cliffs mod
   (`Mlie.DecorativeCliffs`) to make scattered site content read as one
   authored place. Grounded in real live-tested findings, not guesses — see
   the skill's own §1 and §6.
3. **`CREATURE_ART_REVIEW_SHEET_1` owner ruling recorded** (`45d52403`) — the
   owner reviewed a 6-creature art sheet and ruled: REJECT the
   "reskin-a-terrestrial-with-glowing-plates" approach entirely (Enhydriodon,
   Gorilla) as a solution class, not just those two rows; APPROVE
   AA_Behemoth/`AA_FrostboundBehemoth` (with a "might suit the nightside
   beasts" casting note for BENCH); **CANCEL AA_Atispec and Revenant art
   work outright** — not parked, not queued for another attempt, per his own
   words ("dropped and no longer reskinned. Unneeded."). Full quotes in the
   item file. Capybara left at `revise` (agent pre-fill, no owner override
   note). 6 other `replace`-flagged creatures (GR_Catbear, BMT_SandPillar,
   Horax, BMT_BiliousVarog, BMT_ShatterjawBeetle, DA_BlackScribe) still have
   no stated owner rationale — do not generate art for them without asking.
4. **Deep Desert biome injections: 3 new rimplace templates** (`7664b739`,
   `9ce6f734`) — `waste_camp.lua`, `boneyard.lua`, `long_crossing.lua` under
   `design/Jawa/templates/`. Extend `structure_injection_roster.md`'s
   coverage of the ExtremeDesert/Desert biome per `deep_desert.md`. All
   three lint/verify clean, all live-quicktest-proven via rimplace's
   bridge-call compile path (not the mapgen GenStep path — that wiring is
   still owed, see below).
5. **`VAULT_DUNGEON_BUILD_1` quicktest-proof + a real crash fixed**
   (`b5483674`) — placing the Type-1 mechanoid-garrison KCSG template threw
   a `NullReferenceException` live; root-caused to KCSG's own pawn-generation
   code (bare `Mech_Lancer`/`Mech_Centurion` symbols default
   `spawnPartOfFaction=true`, which requests a pawn against
   `map.ParentFaction` — null on any factionless map, in every KCSG call
   site, not just this bridge). Fixed with explicit `SymbolDef`s bound to
   the world's real Mechanoid faction. All three vault templates now place
   without crashing; Type 1 and Type 3 screenshot-verified complete.

## Still open — ranked by how actionable it is right now

1. **Scene-composition round 3, three named fixes** (no live game needed to
   start, but the fixes need a live rebuild+screenshot to confirm):
   - Boneyard: a bone-fragment prop at the skeleton's tail end (probably
     `AB_AncientVerticalBone` or `AB_AncientBrokenBone` — not yet pinned
     down) has its own sprite art close enough to the real skull's that it
     still reads as "a second head." Swap it for something without that
     silhouette, or remove it.
   - Boneyard: `TreeDead` (the silverbole stand-in) does not spawn at all
     via the live bridge path — a silent failure. Leading theory
     (unconfirmed): a terrain-fertility refusal, same family as the
     mined-rock CLEAR gap already documented in the template's own notes.
   - Long Crossing: the Decorative Cliffs dune-lip links correctly now
     (round 1 fixed the zigzag by reorienting to a horizontal run — see the
     skill's §1) but a ONE-CELL-THICK run reads as a wooden fence rail, not
     a dune. Needs 2-3 rows of depth. Also the sand-drift paint function
     varies only with x, never z, so it bands across the WHOLE rect
     regardless of the hull's actual z-span.
   - Full detail and the exact fix directions are in
     `skills/rimworld-scene-composition/SKILL.md` §6 — read that before
     touching any of the three `.lua` files, it's the authoritative account.
2. **Deep Desert templates: not yet registered as real roster promises.**
   The three templates are proven mechanisms, not shipped content. Still
   owed: a row each in `structure_injection_roster.md`, a
   `GenStepDef`/`TileMutatorDef` pair wiring each to the ExtremeDesert biome
   (the established pattern — see `RSW_KraytGraveyard`/`RSW_MoistureFarm`
   for working examples), and an actual `world_commit` onto a real Ash'karr
   tile. That last one is explicitly "the owner's pen" per the roster's own
   rule (§0, composition law #1) — a candidate tile (70, region Glare,
   ExtremeDesert, flat, dry, unclaimed) was identified earlier in the
   session from `world/ASHKARR_WORLDMAP_tiles.csv` but never committed.
3. **Animal art, terrestrial three.** Owner's ruling (item 3 above) means
   Enhydriodon/Gorilla/Capybara need a genuinely DIFFERENT redraw concept —
   not a material/plate reskin of the existing terrestrial shape. No new
   concept has been proposed yet.
4. **The 6 unexplained `replace`-flagged creatures** — still waiting on
   owner rationale before anyone generates art for them.

## Process notes worth carrying forward

- **`jawa/build_batch` silently no-ops when a defName genuinely doesn't
  exist in the currently-loaded mod set** (`"no ThingDef 'X'"` — that part
  is a real, correct refusal), but `rimplace verify`'s own def-dump check
  can pass anyway if the dump was captured under a DIFFERENT mod list than
  what's actually running live. Always confirm a just-added mod is in
  BOTH `ModsConfig.FULL.LATEST.xml` AND `ModsConfig.MINIMAL.xml` before
  trusting an offline verify pass against it — this cost a full extra
  restart cycle this session (Decorative Cliffs was FULL-only).
- **A wide review screenshot cannot be trusted to isolate "what this
  template built" from "what was already on the quicktest map."** See the
  scene-composition skill's new §5 note — a fresh critical-reviewer agent
  mistook ambient map scatter for part of a build and scored it accordingly.
  Frame tightly, or tell the reviewer explicitly which defNames are yours.
- **When the owner says a screenshot/path "doesn't resolve," he may be on a
  different device than the one the files live on.** `SendUserFile` on the
  actual `/mnt/c/...` path fixed it immediately this session — don't just
  repeat the same Windows path a second way.
