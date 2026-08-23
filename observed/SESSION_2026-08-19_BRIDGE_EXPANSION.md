# Session handoff — the bridge expansion, 2026-08-19/20

**Seat:** CHECK. **Start:** 32 `jawa/` tools. **End: 106.** Everything below was proven
against a live game; nothing is compiled-and-hoped.

## Where to look, in order

| for | read |
|---|---|
| what the tools ARE and how to drive them | the `rimbridge` skill (+8 references) |
| how to ADD one | the `rimbridge-companion` skill |
| 🔴 what will silently not work | `skills/rimbridge/references/silent-failures.md` |
| the world element census + every API signature | `design/Jawa/worldbuilding/WORLDMAP_BRIDGE_SURFACE.md` |
| ~95 more candidate tools, already researched | `design/Jawa/bridge/BRIDGE_CAPABILITY_ROSTER.md` |
| the living-NPC mod concept (DECIDE owns it) | `design/Jawa/bridge/LIVING_NPC_TEMPLATES.md` |
| live facts BUILD/DECIDE would need a game for | `observed/LIVE.md` |
| what passed and how | `infrastructure/state/queue/CHECK.md` — W1-W8, M1-M4, P1-P4, E1-E3 |

## What made it possible

**A 22-second cold load** on a 13-mod list, against ~25 minutes on the owner's 578. The
full edit → build → deploy → launch → test cycle is about **one minute**, run ~30 times.
`src/RimMandrake/Utils/modlist_swap.py`.

## The one item left in v1

**W9 — the owner builds his real 21,872-tile world.** Three preconditions only he can
supply: the full 578-mod list, his one-shot hand-tick pass at Configure Factions, and the
`ScenarioDef` (V1 chain row 12 gates row 10). Everything on CHECK's side is built and
calibrated.

🔴 **The machine is on the 13-mod MINIMAL list** at his explicit instruction. Restore with
`modlist_swap.py --restore --apply` before he plays.

## Guards this session added, and why

* `skills/validate_skills.py` — checks every `jawa/` name in every skill against the
  companion source. Written because **I fabricated `world_objects_add` in the very skill
  that warns against fabricating tool names.** (The tool now exists, so the claim is true.)
* `skills/repack.py` — the folder is tracked, the `.skill` ZIP is what installs.
* `src/RimMandrake/bridgetools/launch_and_wait.sh` — `Player.log` persists between runs, so
  grepping for the bridge marker matched the PREVIOUS session and returned instantly.

## Corrections I made to my own work — kept deliberately

Errors are cheap to repeat if only the fixes are recorded.

1. **Fabricated a tool name** in a skill (`world_objects_add`). Guard written; tool built.
2. **A bare `catch {}`** in my zone builder silently swallowed 25 of 36 refused cells —
   the exact anti-pattern this session documents.
3. **Claimed funerals were Ideology-only.** Wrong: `FuneralBase` is `<classic>true</classic>`.
4. **Claimed 583 active mods.** It is 578 — the other 5 were `<knownExpansions>`.
5. **Said "47 tools"** without counting; it was 57.
6. **Assumed maps are square.** One quicktest was 100x400.
7. **Guessed `PsychicShock` was a DamageDef.** It is a HediffDef.
8. **Guessed four defNames** that do not exist. Read the dump; never guess.
