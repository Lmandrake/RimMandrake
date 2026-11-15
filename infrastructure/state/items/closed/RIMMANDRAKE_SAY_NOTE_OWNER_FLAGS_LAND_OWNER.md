## spec
A helper added --per-ruling to a plain note and it was written into OWNER.jsonl as seat OWNER (lesson 20261115T202149Z;
note 584622027d on STEVE_LANE_UNSTICK_BRAKED_UNOWNED_EB2A). Decided: the routing is INTENDED. cli.py resolve gives
--owner-said, --by-card and --per-ruling OWNER's authority by the owner's card of 2026-10-11 (one field per kind of
authority; "--per-ruling: act as OWNER under a standing ruling"), so the event is his and belongs in his shard; an agent's
own note takes --why alone. Changing it would contradict that ruling. The fix is the help text where the trap is hit.

## criteria
A1 L0: selftest_cli t_note_with_an_owner_flag_is_his_and_help_says_so: a note with --per-ruling lands as seat OWNER, one with
--why stays the agent's seat, and `rimflow note --help` names OWNER.jsonl, --per-ruling and --why (red on the base commit).
