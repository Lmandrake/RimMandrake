# SUSPENSION_LIVE_DIAGNOSE_FIRST_REAL_RUN

First live run of `src/RimMandrake/FlowWorks/northstar/suspension_bridge_proof.py` (BENCH 2026-10-19, flowworks tier,
11 mods, FlowWorks DLL of ccf36a9af7 - NOTE: before a01c76fe25 UNDERPASS_REACH_FIX_DECK_VIEW_SAYS_NO). Fresh
TropicalRainforest quicktest, origin 140,140, no --river/--lake/--sea (no such sites given: W rows UNMEASURED SITE).
Result: `Transient/suspension_live/suspension_bridge_proof_20261019c.json`, log `Transient/suspension_live/run3.log`.
Harness fixed on the way (site clearing, numeric pawn ids, ProofSwing arg): commits on 2026-10-19.

PASS 12: drag 6 builds, drag 7 refused, rails on nobody falls, grate pour 500 dL, grate item stays, shallow trench is a
wall, item slides, shot through grate, jetty 2 ok / 3 refused / overload drops whole, LOOK Scrapper.

FAIL, presumed MOD unless noted (each needs its own trace):
- LOOK_Industrial/Modern/Futuristic_resolves: styled=0 of 8 parts, every path still Scrapper (d0b53e8c49 looks not applied?).
- SB_rails_off_some_fall: 0 of 20 production TryKnockOff rolls dropped (P = 0.3% at 25%).
- UND_shot_solid_deck: a shooter under a SOLID steel deck can hit a colonist on it (want False).
- SB_load_over_rating_whole_span_falls: span read Over (816/600 kg) - see detail for what did not fall.
- UND_crush_below_and_wreck: crushed=3 wrecks=3 but no injury hediffs read.
- UND_floor_path_walks_under / UND_both_arrive / UND_sunken_bridge_crossed: no floor path under the deck - the DLL
  predates a01c76fe25; re-run on a DLL that has it before diagnosing.
- SB_path_crosses_on_deck: path found, 10 cells, decked=0 - presumed SITE (a 6-square trench can be walked around).
- SB_vanilla_bridge_refused_over_dug: vanilla refused (good) but with vanilla's terrain reason, not ours - presumed HARNESS bar.
- GRATE_fire UNMEASURED: fire lit, 0 burns on either deck.
