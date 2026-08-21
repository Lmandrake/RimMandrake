# WORLD_REDRAFT_PROCEDURE_1 — write down how to rebuild the keeper, while the steps are true

## spec

🔴 **OWNER, 2026-08-21: "Write it now, while the steps are still true."** Offered
now vs after-the-Scald vs skip; he took now, over the objection that a Scald fix might
change the paint.

**The problem this closes:** the v1 keeper world was built tonight by a sequence of
commands that exists in a chat transcript and nowhere else. A keeper you cannot redraft is
a keeper you cannot fix — and per `CLAUDE.md` there is no worldgen feature and never will
be, so the owner rebuilding it BY HAND is the only route that will ever exist. This
document is that route.

**The sequence as it actually ran, 2026-08-21 01:06–01:43** — verify each step rather
than transcribing this list, which is REP's reconstruction and not authority:

1. Load the game on the **578**-mod stack. `dump_request.txt` armed if a fresh def dump is
   wanted; ⚠️ **the marker is not consumed — delete it afterwards.**
2. **Configure Factions by hand.** 🔴 Permanent at world creation, the owner's alone,
   and unrepeatable without regenerating.
3. Generate and save. World-only, no map — the keeper is **5.1 MB**, not the 19.7 MB a
   map-carrying save weighs.
4. 🔴 **`jawa/faction_create` for `Pirate`.** Worldgen SKIPS it: Biotech's `PirateWaster`
   declares `replacesFaction` at it with `requiredCountAtGameStart` 1. Without this, four
   Blackstar settlements refuse and stage 5 refuses all 72 rather than placing 68.
   ⇒ Once `PIRATE_VESSEL_RESTORED_1` ships, this step should DISAPPEAR — and the
   procedure must say so, or a future redraft will hand-create a faction it no longer
   needs to.
5. `python.exe src/RimMandrake/Utils/w9_run.py` — dry, then `--apply`. ⚠️ There is **no
   `--dry` flag**; dry is the default. Stage order is engine fact, not taste.
6. Rename the twelve dice-named factions.
7. `world_commit`, lint, screenshot — **and LOOK at the screenshot** against
   `world/view/ASHKARR_WORLDMAP.biome.equirect.png`.
8. **Back the save up into `world/`.** It is gitignored by `*.rws` and needs `git add -f`.
   ⚠️ It lived in exactly one Steam-Cloud-synced folder for an hour before anyone noticed.

⛔ **This is a REDRAFT procedure, not a generator.** Per the owner's 2026-08-18 ruling
there is ONE map. Do not turn this into a script that can roll a second planet, and do not
expose a seed or a parameter that would let it.

⚠️ **The Scald is unresolved as this is written** (`THE_SCALD_LOST_ITS_WATER_1`). Say so in
the document, at the step it affects, rather than writing a procedure that silently
encodes a defect.

**Where it goes:** `design/Jawa/worldbuilding/`, beside `the_one_map.md`, and linked from
it — per the superseding rule, the doc that describes the map should name the doc that
rebuilds it.

## verify

- Each step is checked against what the tools actually accept today, not against this
  spec's reconstruction. Any command quoted has been run.
- A reader who was not here could follow it start to finish.
- Step 4 carries its own expiry condition.
- `the_one_map.md` links to it.

## criteria

The keeper world can be rebuilt by the owner from this document alone, a year from now.
