<!-- status: live -->
# Prose rescued from `infrastructure/state/queue/CHECK_CLOSED.md`

🔴 **GENERATED ONCE, by `rimflow/importer.py preserve()`, on 2026-08-20 — then hand-edited.**
✅ Edit it freely: `preserve()` refuses to overwrite a file that exists, so your
changes are safe from the only thing that could have taken them.
⚠️ *This banner used to claim the file was hand-written and that nothing regenerated
it. Both halves were false — the function printing it was the generator, opening with
`"w"`. Corrected 2026-08-22.*

These 1 sections carried no fields, so the ledger has nowhere to put them —
an event holds scalars and an item file holds spec/verify/criteria, and a briefing
is neither. They were moved here verbatim when `queue/CHECK_CLOSED.md` became a generated
view, on 2026-08-20. ⚠️ Some are still unanswered.

---

## B0+B1 The 30 bridge tools are deployed — nothing is live until the next load
row:      10
from:     BUILD, 2026-08-15, shutdown window
spec:     `python.exe src/RimMandrake/bridgetools/build.py --gm --apply` run with
          the game DOWN. Deployed to
          `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\JawaBench.BridgeTools.dll`.
offline verify (BUILD, passed):
          ```
          == deployed tool count ==   30
          == canaries ==              jawa/fire_incident
                                      jawa/send_letter
          == source census (.cs) ==   30
          == md5 ==                   f0d4e6e78233
          ```
          Build reported `0 Warning(s) 0 Error(s)` and
          `*** GM TOOLS INCLUDED ***` with both canaries in the DLL.
notes:    · **The md5 in B0 is dead.** B0's verify wanted `d7e7c6c1`; `--apply`
            rebuilds at the current commit (`0459627`), so the bytes are
            `f0d4e6e7` and always will differ after any commit. Count + canaries
            are the gate, per B1. Do not read the mismatch as a bad deploy.
          · **RimBridgeServer discovers companions only at startup.** The deploy
            changes nothing until RimWorld restarts — a `list_tools` run against
            a session started before 2026-08-15 12:14 measures the OLD DLL.
criteria: `rimbridge/list_tools` counts 30 `jawa/` names. Five tools respond live —
          `jawa/set_faction_relation` (unblocks v1 L3), `jawa/inspect_string`
          (reads `Thing.GetInspectString()`: `WarningThrusterInside`,
          `ThrusterBlockedBy`, power, breakdown), `jawa/world_stats` unit fix
          (`perimeterTiles`, `raggedness` from tiles, `centroidLatNorm`),
          `jawa/ideo_of`, `jawa/biome_probe`. `TicksGameSafe()` rides along: def
          reads must work at `programState: Entry` instead of throwing a bare NRE
          on every tool at the main menu.
state:    ✅ DONE — CLOSED 2026-08-15 on evidence collected this session, owner approved.
          `tools/list` on the live bridge returned **155 tools, 30 of them `jawa/`** —
          the census criterion, met. `fire_incident` and `send_letter` both present, so
          the `--gm` build deployed correctly.
