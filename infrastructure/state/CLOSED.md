# CLOSED.md — one line per finished item

_The ledger that lets bodies be DELETED. Its whole job is to stop a closed item
being re-filed, re-investigated, or carried as a struck-through block in a growing
file. One line, with the hash — `git show <hash>` has the full story._

**Append here, then delete the body from wherever it lived.** Never both.

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
| 2026-08-13 | Tracking harvested game logs | rejected — transient value; `observed/2026-08-13_pre-restructure/logs/` gitignored | `0d398c0` |

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
