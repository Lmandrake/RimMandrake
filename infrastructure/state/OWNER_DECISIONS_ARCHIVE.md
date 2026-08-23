# OWNER_DECISIONS — ARCHIVE. Settled rulings and swept rows.

**Nothing here is waiting on anyone.** `OWNER_DECISIONS.md` says of itself: *"This file is
swept and each answered row deleted. Answered rows do not stay here struck through."* It
had stopped obeying that — two of its five Open rows declared themselves CLOSED in their
own first words, and four whole ruling sections sat below the list.

⛔ **Swept to here rather than deleted.** The rule says delete; deleting a ruling's wording
loses the authorization for what was built on it, and git history is not where anyone
looks. Everything below is byte-identical.

---

## Rows swept out of the Open table

| 10 | ⛔ **CLOSED, NOT ANSWERED — the question dissolved 2026-08-19.** ~~Is a DISCARDED world — generated purely to measure, then thrown away — permitted?~~ ⛔ DEAD — owner ruled 2026-08-19, all in-game worldgen hooks stripped; the route is the live bridge, see `ASHKARR_WORLD_DEFINITION.md` §12. The only thing a throwaway world was ever wanted for was rehearsing the sea gate against `JawaSeaShaper.dll`, and that assembly, `sea_seed_sweep.py` and `worldgen_sea_spec.md` are all deleted. There is no sea to measure and nothing to iterate, so the owner is not owed this call. | — | ✅ **The block it named is gone.** Rows 2 and 7 were recorded as blocked on the sea; they are not, and never need be again. Row 7 now rides the bridge import (`worldpaint-live-bridge-route-9d41c7`), row 2 rides `WORLDGEN_FACTION_CHECKLIST.md` at the owner's own screen. ⚠️ A quicktest world remains a perfectly good thing to test the IMPORT tools against — that use was never in question here and needs no ruling. | a retired seat, 2026-08-14 · dissolved by the owner's 2026-08-19 ruling |
| 11 | ✅ **CLOSED 2026-08-14 — one retired seat answered the deploy half, a retired seat the design half. No owner input needed; listed only so nobody re-raises it.** That seat's ruling: **stays inert, is not v1, and is not v2 as written** — its own header calls it *"deliberately NOT part of the Jawa campaign"*, it was the quests skill's build-gate, and v1's one quest slot is spent on *The Claim*. Keep the files (expensive provenance, costs nothing undeployed); the Jawa version is a **different quest** — a survivor arriving on a thirst world with no water, which is a water debt rather than a bed. ⚠️ `rootSelectionWeight 0.6` is not small: enabled casually it *will* fire. Detail: a retired seat's queue, item V29. ~~Original ask:~~ **`StrandedQuest` — enable it or leave it inert?** 3 files, deployed-but-not-enabled in `ModsConfig.xml`. A retired seat found it in a dry run and correctly declined to add an unannounced quest surface on no ruling. | Adding a quest surface to the campaign world is a design/scope call, not a deploy call. | 🔴 **Must land PRE-WORLDGEN** — but worldgen is HELD, so **no deadline tonight.** It costs nothing sitting inert. | a retired seat's dry run, 2026-08-14 |

---

## ANSWERED 2026-08-15 — map protection is REPEALED, not suspended

Raised because the rule died with `agents_def.md` and existed in no current
document while CHECK was acting on it. Owner, verbatim:

> **"There is no map protection! There's no protection of any asset not in the
> repo! Stop treating things as precious. I will absolutely tell you when we're
> really playing. It won't sneak up on you."**

This is wider than maps and wider than the old suspension. **Nothing outside the
repo is precious** — maps, saves, colonies, deployed mod folders, game state.
Do not preserve them, do not work around them, do not ask before destroying one.
The repo is the only thing that is protected, and the reactivation trigger is an
explicit announcement from the owner that play has started. Do not infer it from
v1 containing a playable session.

---

## 🔴 STANDING OWNER RULING — 2026-08-20. THE EMPIRE'S VESSEL IS VANILLA `Empire`.

Verbatim: *"I've been very clear. OuterRim_GalacticEmpire is no longer in the game, we
patch Empire."*

**The decision.** The Galactic Empire is authored on the **vanilla `Empire` FactionDef**
(Royalty). Every patch, spec, gate and run-sheet step targets `Empire`.
⛔ **`OuterRim_GalacticEmpire` is not the vessel and is not to be patched, cited as
confirmed, or used as a control faction.**

**Why.** It was a mod def behind `MayRequire="neronix17.outerrim.galacticempire"`. A
patch aimed at a def that is not loaded matches nothing and **logs nothing** — the whole
reskin reports success and does not happen. Vanilla `Empire` brings Royalty's titles,
permits, gear tiers and quest surface with no gate at all.

**What it supersedes.** `force_users_build_spec.md:241` ("Confirmed"), its `<li>`,
`defaultFactionDef` and xpath blocks; both faction gap audits (below); every
`WORLDGEN_FACTION_CHECKLIST` / `EXPECTED_FAILURES` / `NEXT_RELOAD` row that expects the
mod def; `load_session.py`'s control faction.

**What it does NOT change.** Royalty stays. Other `OuterRim_*` defs — pawn kinds, gear,
the droid factions — are untouched; **this ruling is about the Empire's vessel only.**
⚠️ Do not sweep by the `OuterRim_` prefix or you will take defs that are staying.

**Test.** `git grep -n 'OuterRim_GalacticEmpire'` returns only struck rows and past-tense
provenance — no live patch xpath, no gate, no `defaultFactionDef`, no control.

⚠️ **One thing the owner must still settle** — see `queue/HUMAN.md`: does *"no longer in
the game"* mean **the Outer Rim Galactic Empire MOD is being removed from the 578-mod
list**, or only that we stop using its def as the vessel? Measured 2026-08-20: the mod is
still active in the campaign list (10 `neronix17.*` entries in
`ModsConfig.PRESWAP.20260819_212256.xml`), and three saved world files already name
`OuterRim_GalacticEmpire`. The answer decides whether the dead patches get deleted or
merely retargeted.

## ⛔ Both faction gap audits are RETIRED — 2026-08-20, same ruling

*"I'm not sure we need either of those gap audits... we may instead need to perform a
new one."*

`faction_engine_gap_audit.md` and `faction_stage2_gap_audit.md` were two independent
audits of the same Stage 2 question, reaching the same conclusion, neither citing the
other — and both reasoned from the wrong vessel. **Quarantined, not deleted.** A fresh
audit against vanilla `Empire` is queued to DECIDE.

## 2026-08-20 — the sector occupier's old name is STRUCK

> *"Strike The Directorate from the records. Doesn't exist anymore."*

**There is one Empire and it is the Galactic Empire** — `FACTION_SPEC.md` §1, a patch on
vanilla `Empire` (Royalty), `label` and `fixedName` both "Galactic Empire".

⛔ **The earlier name for it is gone from every design doc, queue file, state file and
source comment** (69 references across 29 files, swept 2026-08-20). It survives only in
`infrastructure/archive/`, `infrastructure/output/` and generated HTML, which are
historical records nobody acts on.

🔑 **If you meet the old name in an archived doc, it means the Galactic Empire.** Do not
reintroduce it, and do not "restore" it when editing an old file.

✅ **Build note, DISCHARGED 2026-08-20.** The rename left the OLD file sitting in the
deployed Steam copy while the new one had never been deployed — so the game was loading
the retired patch and not the current one. `deploy_custom_mods.py --mod Jawa_Patches
--prune --apply` deleted it and shipped `GalacticEmpire.xml`. The game folder now holds
exactly one Empire patch.
🪤 **A rename is a DELETE plus an ADD, and the deploy tool will not delete on its own** —
it reports the orphan as a `-` line and keeps it, so a renamed file leaves both versions
live until someone passes `--prune`. Check for a `-` line after every rename.


---

## Rows 8, 9 and 12 — answered by the owner 2026-08-23, removed from the Open table

| 8 | **Dinosaurs — owner wants to REVIEW THEM NEXT TO THEIR IMAGES** and pick "the wildest and weirdest". Not a keep/cut ruling: a request for a new deliverable, an image-backed review sheet of the roster. | Taste, and it cannot be exercised from defNames alone. | The fauna roster §3–§4. `[v2]`, but the deliverable is now specified. | `design/Jawa/worldbuilding/biome_and_fauna_roster.md` §7 |
| 9 | **The xenotype keep/reflavor set** — how "pure SW" versus "populated galaxy" should the roster feel? | Pure taste; there is no technical answer to find. | The Cherry Picker §2 deletions. `[v2]` | `design/Jawa/mods/cherry_picker_killlist.md` |
| 12 | 🔴 **O12 — droid raids are broken and it is our patch that broke them. Three routes, pick one.** (1) **Drop the KotOR flesh type from `DroidsAreMachines.xml`** — restores tending, loses vanilla EMP on them, **does not touch our ion weapon** (its guard moved to `IsMechanoid` on 08-13); (2) **~5 lines of Harmony** in an assembly we already ship, giving Humanlike pawns a relations tracker regardless of `IsFlesh`; (3) **accept broken droid raids.** ⛔ Retargeting to vanilla `Mechanoid` is EXCLUDED — it would make our own ion weapon block them. | A trade between three kinds of loss, none of them technical: tending vs EMP vs shipping a broken antagonist. | 🔴 **`guy762_KotORFaction_RogueDroids` raids — a v1 KEEP and the quest-critical antagonist of the KotOR distress call.** ✅ Worldgen is clear on four independent grounds; this does not block a world. | **CONFIRMED LIVE 2026-08-14** — a retired seat ran it: 1st `KotORDroidGood_3C` spawned clean, **2nd threw NRE, 0/1 spawned**, exactly as the chain predicted. |

> ⤴ Ruled in one pass. Verbatim: *"O12 droid raids: ~5 lines of Harmony. Dinosaurs: v1, build the sheet now. Xenotypes: Pure SW - cut the non-canon."* Filed as `DROID_RAIDS_HARMONY_RELATIONS_1`, `DINOSAUR_IMAGE_REVIEW_SHEET_1` and `XENOTYPE_ROSTER_PURE_SW_1`.
