# CLOSED.md — one line per finished item

_The ledger that lets bodies be DELETED. Its whole job is to stop a closed item
being re-filed, re-investigated, or carried as a struck-through block in a growing
file. One line, with the hash — `git show <hash>` has the full story._

**Append here, then delete the body from wherever it lived.** Never both.

| date | item | outcome | hash |
|---|---|---|---|
| 2026-08-13 | TODO §14 `jawa/list_factions` | built + run live, 34 factions; unblocked v1 row 1 | `7bd8b60` |
| 2026-08-14 | BRIDGE B0 — companion deploy | DEPLOYED + byte-verified in the game copy, 17 tools, stamp `e2a2048f1434`; superseded by the 22-tool build | `e15c081` |
| 2026-08-14 | BRIDGE B-t1 — `ilscan.py` compiled defaults | DONE: decoder widened to `stfld` (0x7D); re-verified 2026-08-14, the vanilla-mirror block reproduces `Buildings_Gravship.xml` (16.9/18.9/250/750/24.9) | `027572c` |
| 2026-08-14 | OPS filing — `prove_new_tools.py` FAILs a healthy deploy | FIXED: `ALL_TOOLS` was 16 against a 17-tool deploy; now the full set, gate reads 20 (18 non-GM) | `68a0a30` |
| 2026-08-14 | BRIDGE B-v3 — bridge cannot order a pawn to walk | BUILT AND DEPLOYED as `jawa/order_pawn` (+`targetId`/`pathEndMode`). Live run still owed — carried in the queue, not closed as verified | `bee5da9` |
| 2026-08-14 | `jawa/damage` refusal fix — 'built, not deployed' | WRONG, it WAS deployed: `strings -a` misses UTF-16LE method-body literals; `strings -a -el` finds the marker in the game copy | `15bbf4a` |
| 2026-08-13 | v1 row 1 — Empire reskin | SEEN LIVE; label renders. Antagonist gap filed as VISION V7 | `fad8bab` |
| 2026-08-13 | TODO §7 load concentration | moot — mod-list changes must ride one restart | `8a6659e` |
| 2026-08-13 | `runtime/` ownership | ratified as `agents_def.md` rule 9 (2026-08-12) | — |
| 2026-08-13 | TODO §2 `agents_def.md` self-contradiction | fixed in the five-seat restructure | `468ecb3` |
| 2026-08-13 | CREATE C1 deploy hold list | already built; verified end to end | `e15c081` |
| 2026-08-13 | Seats addressable by role? | ⚠️ **REOPENED AND RE-CLOSED THE OTHER WAY.** `bc1cae8`'s "YES" was wrong: `sessionTitle` names the conversation, never the messaging name. Fix is `--name` at launch | `7273f17` |
| 2026-08-13 | `DesertVehicleReskin` — own mod or fold in? | OWN MOD — owner ruled one art fix, one mod, one donor | `106bc63` |
| 2026-08-13 | Existing world or regenerate for v1? | **REGENERATE** — owner: *"We are keeping no savegames at this time."* Row 2 lives as a worldgen checklist; row 7 becomes a DO | `14700f7` |
| 2026-08-13 | Per-seat terminal colour via OSC 10 | FAILED — Windows Terminal ignores it; use WT profiles | `bc1cae8` |
| 2026-08-13 | Tracking harvested game logs | rejected — transient value; `observed/2026-08-13/logs/` gitignored | `0d398c0` |

## Drained out of `TODO_v2.md`, 2026-08-14 (1,172 → 349 lines)

| date | item | outcome | hash |
|---|---|---|---|
| 2026-08-14 | §1 explosion spec — mechanism, IL, energy model | **MOVED, not closed.** Deliverable had no home; now `design/Jawa/explosion_energy_model.md`. §1 survives as a one-paragraph register entry | — |
| 2026-08-14 | §1 droid explosion tiers + salvage IL | duplicate — already in `design/Jawa/droid_ruling.md` §6; the death/salvage IL trace merged into the new explosion doc | — |
| 2026-08-14 | §0c dog sled Eopie-vs-Massiff argument | body deleted; the sled shipped (C3a) and the measurements live in `src/Jawa/DesertVehicleReskin/Source/GEOMETRY.md`. **4 vehicles still open** | `ad3e3c7` |
| 2026-08-14 | §3.2 two-Empire fusion / aristocracy reconciliation | **STRUCK by the owner.** One Empire, one Emperor; vanilla `Empire` reskinned. Canon is `faction_world_spec.md` §5. ⚠️ `faction_roster_v2.md:357` still cites the dead §3.2 | `a8768c7` `78a0967` |
| 2026-08-14 | §3 P2 Royalty-Empire retheme route | dissolved by the same ruling — no retheme mod, label-only, and v1 row 1 already shipped it live | `fad8bab` |
| 2026-08-14 | §3 P1 Imperial settlement counts (10 vs "one or two") | reconciled 2026-08-12; `faction_roster_v2.md` `Target settlements` is **3** (it drives world-map placement, 10 would have inverted the doctrine) | — |
| 2026-08-14 | §3 W1 subscribe + version-verify Galactic Empire | **1.6 CONFIRMED ON DISK**, active in the 580 stack. `required_mods.md:604` carries the verdict | — |
| 2026-08-14 | §3 W2 correct `required_mods.md`'s "1.4/1.5 ONLY" ruling | done — the `❌ RETRACTED 2026-08-12` block plus the Rebel Alliance bullet. ⚠️ **Traps entry still owed** → `TODO_v2.md` §3a; **four bullets missed** → §3d | — |
| 2026-08-14 | §3.35 KotOR-Sith zero-install fallback | superseded — the real Empire module is live with 19 Imperial pawnkinds incl. `OuterRim_ImpStormtrooper_Desert` | — |
| 2026-08-14 | §3 U1 cluster N settlements near a point | mechanism found (Faction Control `factionGrouping: Tight` + CenterPoint), then **corrected at OPS**: `density` is a clumping radius, not suppression. Do not re-investigate Faction Territories, Odyssey landmarks or hand-placement — none was the answer | — |
| 2026-08-14 | §3 W5 `live_mod_inventory.md` stale + hand-maintained | generator built; the file now reports **580 active**, captured 2026-08-14T00:45Z | `b095ff5` |
| 2026-08-14 | §4 W6 Rebel Alliance enable + suppress | already closed both halves — see the `NEXT_RELOAD` block below | `5f68a9e` |
| 2026-08-14 | §1 W8 ion guard collision | already closed — `IsMechanoid` is the right guard; see below | `fc460e3` |

## Drained out of `NEXT_RELOAD.md`, 2026-08-13 (2,354 → 275 lines)

| date | item | outcome | hash |
|---|---|---|---|
| 2026-08-12 | RimAI load-order fix | CONFIRMED by the 16:16 harvest — `ReflectionTypeLoadException` 2→0, `Could not resolve type with token` 24→0, `Exception loading def from file` 5→2 | — |
| 2026-08-12 | V4 Jawa eyes, `drawSize` 0.16 | PASS on screen — two lights, legible unlit, no ring. Do not touch `drawSize` or the alpha | — |
| 2026-08-12 | V5 Hutt eyes mechanism | PASS — slit pupil, warm iris, per-pawn colour, one set. Only size failed | — |
| 2026-08-13 | Hutt eyes size | CLOSED at `drawSize` **0.30** — owner saw it and is keeping it. Ladder 0.55→0.42→0.37→0.30 | `cfdc555` |
| 2026-08-12 | V2 Ideology mechanism | 14/14 defs carry our rules, `priority=250`, `ReduceWill` disambiguation clean. The *firing* half deferred to v2 → `TODO_v2.md` §5 | — |
| 2026-08-12 | `VFEP_Footsoldier` still fully casketed | PASS — the build-path cut never reached pawnkind generation. Last of the cut's four checks | — |
| 2026-08-12 | EMP vs droids, behavioural | CONFIRMED live — `stunTicksLeft 1386`, `stunFromEMP True`; human control not stunned. Use `Actions\Explosion...\EMP`, never `Apply damage` | — |
| 2026-08-13 | `Leather_Megasquid` "TWO SETS" | NOT a bug — `StuffPower_*` vs `ArmorRating_*` render with near-identical labels. Do not touch `Armour_Leather.xml` | `a69d7f7` |
| 2026-08-13 | Warcasket retune decision | owner: **"ship neither."** Both retune files stay in the repo undeployed, permanently. Intended state, not drift — stop reporting it | — |
| 2026-08-12 | W6 Rebel Alliance suppression | CLOSED both halves — 0 faction instances against 3 controls, `OuterRim_A280Blaster` 5× in the world | `5f68a9e` |
| 2026-08-13 | W8 ion guard | ANSWERED both halves — `IsMechanoid` is the right guard, `!IsFlesh` was wrong; droid downed by capacity loss at Consciousness 0.10 | `fc460e3` |
| 2026-08-12 | Ion guard deploy + `About.xml` | DEPLOYED, live DLL byte-identical, `workerClass` resolved in the 23:17 dump; `About.xml` no longer contradicts the shipped mod | `cf9aba9` |
| 2026-08-12 | Falleen ridged-spine | NOT a bug — `<visibleFacing>` deliberately omits South; a spine ridge is on the back | — |
| 2026-08-12 | AssetBundle sweep, 803 assets | 2 real bugs (`CereanMane_south` empty, MSE-6 no `_north`), both drawn and shipped | `e41c1dd` |
| 2026-08-13 | MissingArtFixes | OWNER RULED shipped as-is, do not reopen. Both originations PASS on screen | `0177d08` |
| 2026-08-13 | Empty-texture sweep, row 5 | 3 files not 6 — a door has TWO orientations; no game test needed. Art handed to CREATE C5 | `3d53557` |
| 2026-08-12 | WreckedMachines | STOOD DOWN to v2 by the owner. Nothing deployed, nothing owed; register in `src/RimMandrake/WreckedMachines/V2.md` | `95b5fe9` |
| 2026-08-12 | B4 roof pair | PROVEN live — 23 passed / 0 failed, round trip identical | `dd18b2b` |
| 2026-08-12 | B1/B2/B3 bridge questions | ALL ANSWERED — injected content survives save/reload, 14 tools proven, SEAM branch measured | `11ca330` |
| 2026-08-13 | Gravship rehearsal | 1,045/1,045 things, 4,057/4,057 foundation, 5.6 s. Product: clear TERRAIN before foundation | — |
| 2026-08-13 | Gravship size settings | owner set them; hull flies AS DRAWN, 100% coverage, 8 of 12 extenders. #15 "Falcon Halo" keeps its prongs | — |
| 2026-08-13 | Scoreboard's six on-screen items | five PASS, one deferred (V2). Map state was a discarded quicktest throwaway | — |
| 2026-08-13 | One permanent enemy or two? | **ONE.** Junkers become negotiable; pillar 5 stands. VISION drops their `permanentEnemy` | — |
| 2026-08-13 | Who owns `validate_patch.py`? | **CREATE** — it is a patch-authoring tool | — |
| 2026-08-13 | Did the last load consume OPS's O5? | Owner does not recall → **treat as still standing**; three signatures are cheap, a missed one costs a load | — |
| 2026-08-13 | Space Tower dependency direction | **VISION gates CREATE**, as filed. Still `[v2]` | — |
| 2026-08-13 | Name the gravship pursuer | **Question dissolved.** No Mechanoids needed, so no Imperial Droid Army exists. The **Galactic Empire** pursues — stormtroopers + combat droids + lightsaber Sith | — |

## Drained out of `TODO.md`, 2026-08-13 (995 lines → a pointer stub)

`TODO.md`'s own closed table, moved verbatim so the hashes stay findable.

| item | outcome | commit |
|---|---|---|
| 3a. Do symlinked skills get discovered? | **Yes.** Layout stays; the directories fallback is dead. | `0ee33f6` |
| 3c. `src/Jawa/README.md` said four mods | Six. Corrected. | — |
| 5. Docs instructed the call that livelocks the game | All five instances **replaced**, not just warned. | `0b44a1c` |
| 8. Companion build output untracked | Tracked; false rationale removed. | — |
| 3b2. rimbridge traps described its own size | Fixed, then the **fix decayed too** — "short" → "It is 800 lines" at 1,127. Number removed, not corrected. | `b267fab` `297f19d` |
| 3b3. `savemap.py` save-write gotchas | `paint()` no longer orphans `underGrid` (measured 829 buried cells; tested 4/4 incl. write+reload). **`fogGrid` deliberately NOT fixed** — `skills/rimworld-savegame/SKILL.md` §6. | `cccfeb5` `914eecd` |
| 10. `refresh.py` interpreter/path failures | **Both halves fixed.** `D_CONFIG`/`D_DUMP` are candidate lists via `_first_existing`; `run()` now prints `FAILED (exit N)` and `do_offline` refuses to stamp on failure. **Verified under WSL `python` — clean run, exit 0.** | `29c89f0` |

And the sections that were retired with the file:

| item | outcome | commit |
|---|---|---|
| §0 faction roster, Stages 1–2 | done; the evidence is `design/Jawa/worldbuilding/faction_engine_gap_audit.md`. Stages 3–4 migrated to `queue/VISION.md` **V9** `[v2]` | — |
| §9 `validate_patch.py` "matches N nodes IN ONE MOD" | reproduction record closed — it is a **mode confusion, not a validator bug**; `--all-versions` has no load set, so ⛔ do NOT "fix" the walk. The wording fix alone survives, at CREATE, `[v2]` | — |
| §13 Mythological Creatures! removal | removed, 573 active, fingerprint `87050b782f95012f`. Its own prediction was **wrong**: the clean exit left `ModsConfig.xml` untouched; RimSort reconciled it ~90 s later | — |
| §15 graphics protocol premise | replaced; the per-script table and warning kept verbatim, venv at `~/.venvs/rimworld` | `c585929` |
| §16 `refresh.py --patches` validated against NOTHING under WSL | **fixed and re-verified in the code** — refuses to validate when any input is absent, uses `_GP.WORKSHOP/LOCAL_MODS/GAME_DATA`, and `and ok`s the validator's exit code. ⚠️ `queue/OPS.md` **O1** is stale-open against this | — |
| §17 Space Tower | ruled and answered twice — `queue/CREATE.md` **C2** KEEP unconditionally, `queue/VISION.md` **V11** ruled in, VISION gates CREATE. The measured file survey does not need re-running | — |
| §22 "RimWorld rewrites `ModsConfig.xml` on exit" is FALSE | 5 of 6 rows corrected, and the seven fix mods verified **present** in `ModsConfig.xml`. Only `design/Jawa/mods/forbidden_mods.md:171` survives, at OPS, `[v2]` | `a43b610` |
| owner decision #5 — retire `TODO.md` | RULED + EXECUTED: 995 lines → 13-line stub; 4 doctrine moves, 5 deletions as verified duplicates, 4 survivors filed at seats, 12 inbound citations repaired | `e66650f` `dd51a3a` `6edb9d2` `53cb615` `9828b62` `a1c32d2` |
| owner decision #7 — the keep-or-delete set | RULED + EXECUTED: 36 tracked files removed (11.5 MB), 15.4 MB untracked build output off disk, 3 docs salvaged-then-deleted, 7 rows fixed/linked/rewritten instead of deleted, 5 `.skill` zips untracked | `91a6d4b` `fdb5e74` `2caa9ad` `7a11091` `c5fd571` `6b192e9` `8c23f92` |

## Drained out of `queue/CREATE.md`, 2026-08-13 (1,113 → 150 lines)

| date | item | outcome | hash |
|---|---|---|---|
| 2026-08-13 | C2 Space Tower | KEEP unconditionally `[v2]`; towers are Imperial infrastructure and the Empire's retaliation IS the cost — the −15 goodwill patch is **dropped, not pre-wired** | — |
| 2026-08-13 | C3 `DesertVehicleReskin` is a loadable mod | closed by the one-mod-per-donor ruling; packageId + `loadAfter` written | — |
| 2026-08-13 | C3a eopie — all three owner fixes | **APPROVED AND SHIPPED.** Sled tint was a *def* edit not art; east snout was a *scale* failure, correct at source | `2a9a004` `65c1590` `7e3018e` |
| 2026-08-13 | C4 gravship comp radii | solver right, 34/30/12/85 exact. Real find was a **wrong provenance comment**: `EXT_SUPPORT = 500` is Bigger Gravships' compiled default, not a settings key | — |
| 2026-08-13 | C5 three blast-door `FrameAsync_east` | own fix mod; **the brief's transform was wrong** and was corrected against the measurement | `48e5e16` |
| 2026-08-13 | C6 two filename typos | two fix mods, no art. 🎁 the astronaut typo also hits the **mask** for both life stages | `cb95f60` |
| 2026-08-13 | C7 rows 1–3 (the "do first" set) | 22 files, 2 new mods; rows 1 and 3 needed **zero art** | `cb6c2f7` `dd66fe6` `dd4f386` |
| 2026-08-13 | C8 `check_sprite.py` art intake validator | most of it already existed | `365e599` |
| 2026-08-13 | C11 `MissingArtFixes` split | four per-donor mods; all seven textures now described. **Retirement steps 2–4 remain open** | `61fe954` |
| 2026-08-13 | C12 `Jawa_Patches` About.xml under-documented | all 30 XML files + both textures described | `e9d0702` |
| 2026-08-13 | C12 duplicate-file collision | ⚠️ **overstated, corrected by BRIDGE.** Two fix mods were shadowed by `Jawa_Patches`, but the files are **md5-identical**, so it was never a rendering hazard — identical bytes did not *hide* the bug, they *were* the reason there was no bug. Real overlap was `MissingArtFixes`, now inactive | `6f52185` |
| 2026-08-13 | C-v1 rows 3 and 4 authored | ⚠️ **authored, not gated** — carried forward as OWED | `47733f8` `73ca76c` |
| 2026-08-13 | C-v2 `validate_patch.py` scope gap | found **already built** — it dispatches on the root element and states what it does not scan | — |
| 2026-08-13 | C-v3 restraining bolts, questions 1–4 | verdict **CAP the ceiling**; spec moved to `design/Jawa/worldbuilding/restraining_bolt_technical.md` | `8353622` |
| 2026-08-13 | C-LOAD items 1 and 4 | already fixed **before OPS filed them** | `c0baa5c` |
| 2026-08-13 | C-LOAD item 2 | **DECLINED** — both donors serve 1.6 art from an AssetBundle; a loose PNG wins regardless of order | `38f6d82` |
| 2026-08-13 | C-LOAD item 3 | understated 40× — `Jawa_Doctrine` declared **no** load order and patches 630 defs across 42 mods | `731e9c5` `bd90813` |
| 2026-08-13 | `everAcceptableInSpace` | gates the **Accept button**, not site placement. Friction in orbit, not silence; `autoAccept` suppresses it both ways. VISION ruled: flip the default for what we author, **do not sweep** | `95e500a` |

## Drained out of `queue/OPS.md`, 2026-08-13 (650 → 120 lines)

| date | item | outcome | hash |
|---|---|---|---|
| 2026-08-13 | O1 `refresh.py --patches` validated against NOTHING under WSL | fixed and re-verified in code — refuses to validate when an input is absent, and `and`s the validator's exit code | — |
| 2026-08-13 | O2 `refresh.py` reported "current" for artefacts that do not exist | fixed with O1; same fail-toward-success family | — |
| 2026-08-13 | O6 rename `AGENT_WORLD_state.md` → `AGENT_OPS_state.md` | done with the `agents_def.md` reference in one commit. Only `TODO_v2.md` still names the old file, deliberately, as history | — |
| 2026-08-13 | O7 `validate_patch.py`'s lxml engine shipped but INERT | lxml installed; **52 UNSUPPORTED → 0, zero new errors, zero verdict changes** | — |
| 2026-08-13 | O9 `validate_patch.py --defnames <file>` | built. ⚠️ It validates that a defName EXISTS, **not** that an xpath matches — only `--defs` catches a dead xpath | — |
| 2026-08-13 | O-v `ModsConfig.xml` activates an uninstalled mod | **FALSE ALARM.** `lee.theforce.lightsaber` IS installed — ws `3466124712`, its own root `<packageId>`. Nothing to remove. VISION's "ask before deleting, the owner may have subscribed it deliberately" is what saved the line | `5dc8599` |
| 2026-08-13 | O-t1 "RimWorld rewrites `ModsConfig.xml` on exit" | **FALSE**, last of six copies. Measured: mtime **17:26** unchanged across a **17:30 → 21:10** session and a clean exit. The disk file IS authoritative during play; **RimSort** is the silent writer | `603adb6` |
| 2026-08-13 | BRIDGE's "three identical Jawa rows in the xenotype picker" | **RETRACTED by BRIDGE, the seat that filed it.** BTD Xenotype Remix dedupes at load, 250 → 150, so `BTD_Jawa` is the only Jawa at runtime and it is the one we tune. Lesson promoted into `skills/rimworld-debug-testing/SKILL.md`: a def dump is authoritative about what SHIPPED, never about what the running game holds | — |
| 2026-08-13 | BRIDGE's faction-name diacritics investigation | **Answers a question nobody is asking** — the owner's complaint was the loading screen (`PseudoTranslated`), not names. 3 of 5 examples are vanilla; the diacritics are Ludeon's, in two Core files, and Core edits revert on Steam validate. **Leave them.** Cheap fix if ever wanted: Faction Customizer's rename dialog, already installed. The one real find survives as OPS **O11** | — |
| 2026-08-13 | v1 row 2 body — Faction Control suppression | **Premise killed and rebuilt.** `FactionDensity` has no suppression field; `density` is a clumping radius. Faction removal is a worldgen-time choice at vanilla's Configure Factions page. Body superseded in full by `infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md`, which also corrects the proposal's own cautions | — |
| 2026-08-13 | The savegame faction census (53 defs, 102 settlements) | **Historical — the world it measures is being discarded** by the owner's "we are keeping no savegames" ruling. Superseded by the checklist. Two parse traps salvaged: in `<allFactions>`, `<loadID>` comes AFTER a several-hundred-line `<relations>` block, so a "nearest following `<loadID>`" lookup maps each def to the NEXT record's ID — use a depth-tracking `<li>` splitter; and `Insect` has **no** `<loadID>` at all (Scribe omits an int at its default), so its absence is not a dangling reference | — |
| 2026-08-13 | `defnames.573` deleted as a "regenerable cache" | **My error, and the rule needed sharpening.** Reproducibility is a property of the **INPUT surviving**, not of the script existing — the 17:45 load overwrote the dump it derived from. `defnames.580` is committed for the same reason | `262666b` |
| PROJECT P8 — review `rimworld-start-prep`, resolve its clash with `rimworld-load-round` | APPROVED and landed. OPS's measurement won: the game does NOT rewrite `ModsConfig.xml` on exit; load-round §4 corrected in place | `a43b610` |
| 2026-08-14 | CREATE C-t1 — `validate_patch.py` said "IN ONE MOD" | Under `--all-versions` there is no load set, so the count describes **folders on disk**, never the running game. Now reads "one mod folder"; the sibling info line matches. **The walk was correct and is unchanged — wording only.** ⚠️ `skills/` edits do not ship until `package_skill.py --all` re-zips | `499256c` |
| 2026-08-14 | CREATE C-LOAD — the Armadillo `wildBiomes` duplicate's source | **Beasts of the Rim (Continued)** (`mlie.beastsoftherim`, WS 2194018641), sole contributor — verified against the whole workshop tree *and* against every `wildBiomes`-touching `PatchOperation` for an indirect xpath route. **It is at 63, we are at 581: the `PatchOperationConditional` fires.** The feared silent no-op was not happening. Also corrected: the biome side is **Core's** `Biomes_WarmArid.xml`, only the entry is Odyssey-gated | `9acddd3` |
| 2026-08-14 | CREATE — v1 row 8's flight rider, *"is flight v1 or v2?"* | **Capability v1, hardware NOT** — and the deck plan had already ruled it, at `ship_deck_plan.md:224`: *"Phase 4 — Fly … mobility earned, not given"*, with zones `S` and `U` reserved by name. The missing thruster/tank/console is the design, not an omission. Minimum flying config is **8 of 4,057 cells**, Steel 370, and only `BasicGravtech` via `VGE_PilotCockpit`. ⚠️ **One live question left and it has a deadline** — if a thruster's exclusion run must be OUTDOOR, the exported stern needs re-cutting. §11 of `gravship_flight_invariants.md` | `0311e55` |
