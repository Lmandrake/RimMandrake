# spending-a-load.md — the three habits, in full

The headlines are in `SKILL.md` §2. This is the reasoning behind each — open it
when you are actually planning a load: deciding what can ride along in a batch, or
deciding what to harvest once the game is up.

## Verify everything verifiable offline, first

Defs, About.xml, ModsConfig.xml and the whole Workshop tree are ordinary files
sitting on disk right now. Run `scripts/validate_patch.py`, parse every XML you
touched, confirm the load order in `ModsConfig.xml` rather than trusting the
manager's UI, and cross-check def references by grepping the mods themselves.
Anything you can establish from files, establish from files. A restart should be
confirming a prediction, not conducting an experiment.

## Batch by risk, not by count

The one-change-at-a-time rule exists to keep attribution possible when something
breaks — it is about *ambiguity*, not about quantity, so batch anything whose
effects are distinguishable. Config-level changes (load order, mod settings,
un/subscribes) carry near-zero attribution risk and should always ride along. A
pure-XML patch that validated clean and has named log strings to check is also
safe to include, because you know exactly what evidence would convict it. Keep
genuinely ambiguous changes solo: a mod that patches broadly, or two changes that
touch the same system. Say out loud which bucket each pending change is in before
proposing a batch.

🔴 **A new C# assembly USED to be on that solo list, and the owner waived it — see
`rimworld-load-round/SKILL.md` §3, which is the live rule.** Three assemblies batch,
on one mandatory condition: **write the three expected-failure signatures down
BEFORE launching**, in `infrastructure/state/EXPECTED_FAILURES_next_load.md`. A
signature invented after reading the log is a story that fits, not evidence. ⛔ Do
not re-litigate the waiver and do not quietly split the load out of caution.

## Harvest the whole log, not just your change

After a restart, read the entire `Player.log` and update the triage list — the mod
that just broke unrelatedly, the new unresolved reference, the count that moved.
You paid for a full load; a single yes/no answer is a poor return on it. Keeping a
running "next restart" queue between loads is what makes this cheap: changes
accumulate in a list, and each load clears the list and refills the evidence.

*(Triage order once you have the log: `references/player-log-triage.md`.)*

---

## Why hot-reload is retired — the full incident (SKILL.md §2)

**Why it was retired — measured, on the full 589-mod list, 2026-09-03:**

* The call **ran** (the first time it was ever observed to complete through the
  bridge — the earlier full-list trial was killed at 4–5 min). It hung the bridge
  for **~5 minutes**, then answered normally.
* Afterwards **no pawn of any kind could be generated.** `jawa/spawn_pawn` returned
  `NullReferenceException` for Muffalo, Hare, Colonist, Tribesperson and Villager
  alike — animals included, faction or none. Vanilla's own
  `Actions\Spawn Pawn...\Colonist` gave the real message the bridge swallows:
  **`The given key 'RimWorld.HairDef' was not present in the dictionary`.**
* 🔴 **It is not the def database and nothing reports the damage.**
  `HairDef/Shaved`, `BodyTypeDef/Male`, `ThingDef/Human` all still resolved; a
  Type-keyed index the pawn generator walks did not. The game reads healthy
  (`programState: Playing`, `playable: true`, `mapDataReady: true`) right up until
  something tries to make a pawn. Full evidence:
  `infrastructure/state/items/closed/HOT_RELOAD_DEFS_BREAKS_PAWNGEN_1.md`.
* ⚠️ **The 2026-09-02 minimal-list PASS was real** (Core `Campfire` description
  edited, reloaded in 0.04 s, read back live, reverted clean) — and it is exactly
  why this is retired rather than merely gated. A capability that passes cleanly on
  19 mods and silently destroys pawn generation on 589 cannot be trusted by the
  seat that has to decide which situation it is in.
* Independent corroboration is **weak, and that changes nothing** — the owner
  retired it on our own measurement. What the web has: community unease about
  patch/load-order fidelity across a reload, third-party mods existing to replace
  the built-in button, and a Steam thread titled *"Don't push that botton called
  'Hot Reload Defs'"* with no developer reply. Nobody has published this defect.
