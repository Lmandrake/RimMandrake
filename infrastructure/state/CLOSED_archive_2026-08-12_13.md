# CLOSED archive — 2026-08-12 and 2026-08-13

_Split out of `CLOSED.md` on 2026-08-14 when it hit its 150-line budget. **This
is still the ledger** — grep `infrastructure/state/` , not just `CLOSED.md`,
before re-filing anything. Nothing here is reopened by being moved._

| date | item | outcome | hash |
|---|---|---|---|
| 2026-08-13 | TODO §14 `jawa/list_factions` | built + run live, 34 factions; unblocked v1 row 1 | `7bd8b60` |
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
