## spec
### Bring each working mod's tests and lists level with the rules that just landed (item RIMMANDRAKE_SYNC_MOD_TESTS_WITH_LANDED_RULES_BEFORE_JUDGING)

Owner, 2026-11-18: "we should ensure that any acceptance tests or other mod-specific lists that might need to be upgraded to correspond to these new changes are achieved at this time, so that they don't waste a judgement round realizing they are out of sync rather than flawed."

Mods in play: Pyrelands, Graffiti, ExplosiveKnockback, FlowWorks, GimmeSomeSlack (concepts under `design/concepts/<Mod>`; state: `python3 src/RimMandrake/rimflow/maturation_dispatch.py status`). All are paused; you release nothing and launch no stage or judge look. Everything here is zero-judge, offline preparation.

What changed since each mod's last judge look (read each commit and its ticket): judge-card rules `dbd5c89339` (a polish gap blocks on no look; a repaired carried gap closes with no claim form) · re-pin anchored to the commit that recorded the pin `e881b97715` · scope_source must cite a real ledger event `895f0834c3` · advance verdicts are submitted and a calibrated `maturation_advance` family can now stop a mod `13db68e8ed` · Graffiti T_FUZZ kernel6 family `0755474953` · EK validation `--selftest` `9a437178d8` · worker map gate `ab3cb4372d` · standing rulings: `standing_rulings.md` §A passing bar is an experience and §The judge refuses flaws, not polish (the four judge rules do NOT bind yet; note what each mod would need when they do, change nothing for them).

For EACH mod:
1. Run every zero-token check the pipeline will run before or at its next look and record the reading: `designer_stage.py` status/check for the concept, `coverage_judge.py status`, the mod's test table rerun, `bar_rule.py` on its bars, its offline selftests and plant-faults suite, the pin check. Find the real command names by reading the tools; never guess a flag.
2. List every place the mod is OUT OF SYNC with the landed rules rather than flawed: a test table or tree.json that does not list a new test or family, a pin or stage.json without the recorded pin sha, a scope_source citing an id that is not a ledger event, a carried gap or claim form the new rules close or no longer need, a bar that pins a tuning number, a stale hash. Fix each one that is mechanical; one commit per mod, published.
3. Graffiti specifically: its re-pin is refused (`locked_change_cites_his_cards`) because commit 6c7d175b5270 is not tied to the owner's card. He approved that fix by card 2026-11-17 5:25 PM PST (item RIMMANDRAKE_REPIN_GRAFFITI_SOAK_FIX_AFTER_WEDNESDAY_RESETS). Find that card's item and ledger event, and make the tie the refusal names as its smallest fix (a ledger note on the card's item naming the sha, with `--per-ruling` citing his card event). Then confirm with the tool that the re-pin WOULD now pass; do not spend the granted look.
4. Anything that needs a judgement, a new promise wording or the owner: do not do it; list it with evidence.
Write `D:\ClaudeWork\rimmandrake\conductor\mod_sync_20261118.md`: per mod, readings, what was out of sync and fixed (sha), what remains and who owns it.


## verify
test -s /mnt/d/ClaudeWork/rimmandrake/conductor/mod_sync_20261118.md

## criteria
Each of the five mods has its zero-token readings recorded, every mechanical out-of-sync place fixed and published, and the rest listed with an owner. No ceiling released, no look spent. Acceptance test: none, an audit across five mods.
