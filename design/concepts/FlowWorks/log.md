# FlowWorks Designer log

## 2026-11-04 turn 1 (run rm-role-designer-1793793891), sent

## Asks (at most three, each answerable in a phrase)

1. **ask_root:** Is the paragraph above FlowWorks? Correct any word, or say "yes".
2. **ask_defense_story:** Picture the raid FlowWorks must win. My guess at the scene: a tar canal crosses the raiders'
   approach and stays empty until they are spotted. Then you open it, it fills, and you light it
   as they cross. Is that the scene? Or is it a canal that stays full all the time (water or slime), or something else?
3. **ask_irrigation:** On 2026-09-16 you wrote that plants near a canal act *"as though watered"*, and ruling 36
   said that effect stays, just not drawn. It is not built in FlowWorks yet (with default settings nothing in FlowWorks
   waters crops; CrackedLands has a version we can copy). How far from the bank should a full canal water crops:
   1, 3 or 5 squares?

Reviewed by rm-judge ab76299400ce54ecc: all three pass; ask_irrigation narrowed to the reach (whether it waters is settled by his 2026-09-16 words and ruling 36).

## 2026-11-04 his answers to turn 1 (recorded on the ledger by BENCH)

- **ask_irrigation** (OWNER:1793794389686592719): "1) Two squares away from the canal should become "wetted" using the same technique the Stillsand is already developing for spilled water on the sand. This isn't the same as flood water: flood water is above and beyond wetting, though of course it also wets what it passes over. Wetted ground means the plants have access to water. If they explosively grow, they will use up the wetted ground until it is reapplied. They will also take in more water than that if it's available, reducing any flooded water level above them."
- **ask_defense_story** (OWNER:1793794392567351532): three raid scenes (moat drain and burn; covered pit trap onto spikes with a makeshift-ladder rescue under arrows; island bridges with a double drawbridge, winch destroyed, raiders escape). Full text on the ledger event.
- **ask_root** (OWNER:1793794915205594887), answering the Conductor's suggested correction ("deadly earthworks: pits, moats, traps and drawbridges that you fill, drain and set alight at the moment you choose"): "Sorry, strike the "not today" comment. It was meant that the raiders get away this time, but the defense was successful. Ok, now for your suggested correction: even one more step: Filled water moat has raiders swimming across it (getting tired swimming in deep water), then water drains and they become Prisoners in a prisoner pit for awhile (prisoner mechanic), then chemfuel gets pumped in from above and the burning moat mechanic. All with a drawbridge on top that's raised."
- Budget (OWNER:1793796507483890758): concept budgets are advisory.

Run rm-role-designer-1793796539 wrote the root from these (record.json `root`, with its derivation). Stage 1 done.

## 2026-11-04 turn 2 (run rm-role-designer-1793843896), sent

Text: design/concepts/FlowWorks/turn_02.md. Asks sent: ask_prisoner_click, ask_match. Struck by rm-judge a2dc4250bd4478b4a:
ask_rescue_ladder (answered by his pit-trap words; recorded as decision d_raider_fetch_fallen). c_spec_stale and
c_proof_stale resolved as not his decisions (record.json).

## 2026-11-05 his answers to turn 2 (by card, recorded on the ledger by BENCH)

- **ask_prisoner_click** (OWNER:1793862531058884117): "(b) you click 'capture' from the rim as now, but a drained moat (or pit) counts as a prison without a bed." → decision d_prison_no_bed (owed).
- **ask_match** (OWNER:1793862534552097818): "a new order where a colonist walks to the rim and tosses a flame onto the square the player picks." → decision d_toss_flame (owed).

Run rm-role-designer-1793862763: no ask sent, no core contradiction open. Stage 2 done.
