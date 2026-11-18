# RIMMANDRAKE_MOVE_SEAT_CLONE_WRITERS_INTO_OWN_POOL_CLONES

## spec

Every role row in `src/RimMandrake/rimflow/dispatcher_schedule.json` (BENCH, Conductor, Auditor, Operations,
Producer, Innovator, Designer, DesignerCodex, Artist: 9 of 9) sets `"clone": "/home/mandrake/rm/bench"`, so every
Dispatcher role launch runs IN the Conductor's seat clone (role_launch.py `--cwd role["clone"]`), and the art daemon
`rm-artpiped.service` (artpiped.py -N 5) runs there too. Measured 2026-11-16: their writes were most of the 150 dirty
paths found there — 14 filed items' prose never landed (Designer/DesignerCodex stage runs file items; the harvest's
`designer_stage.land_state` lands only design/concepts/<Mod>/), 5 SCRUB_PROVE_* edits by run
rm-role-designercodex-1794840775, Pyrelands' lock stage.json (run rm-role-designer-1794790336), 9 art_eval briefs
(artpipe cards.py, 2026-11-05). seat_dirt.py (RIMMANDRAKE_ALARM_SEAT_CLONE_DIRT_OLDER_THAN_AN_HOUR) now lands the safe
classes and alarms on the rest, which bounds the damage; this item removes the cause.
Not done in the run that found it: the harvest reads each run's concept files from `cfg["clone"]`
(role_launch.py ~2008) after the unit exits, the stage-chain and run-now paths assume one clone per role, and a pool
clone returned at ExecStopPost (detached_helper.return_clone) would be gone before the harvest reads it. Moving it
needs the run record to carry its own clone, the harvest to read and publish from it, and the return to wait for the
harvest. artpiped needs its own long-lived clone (like /home/mandrake/rm/dispatch) that publishes the briefs it writes.

## verify

Acceptance test (fails on the base 2026-11-16, 9 role rows + 1 unit in the seat clone; passes when 0):

    python3 -c "import json,sys,re; d=json.load(open('src/RimMandrake/rimflow/dispatcher_schedule.json')); r=[];
    w=lambda x:(isinstance(x,dict) and (('clone' in x and r.append(x['clone'])) or [w(v) for v in x.values()])) or (isinstance(x,list) and [w(v) for v in x]);
    w(d); u=open('/home/mandrake/.config/systemd/user/rm-artpiped.service').read();
    bad=[c for c in r if c.rstrip('/')=='/home/mandrake/rm/bench']+(['rm-artpiped'] if re.search(r'/rm/bench\b',u) or 'WorkingDirectory=%h/rm/bench' in u else []);
    print(len(bad),'writers in the seat clone'); sys.exit(1 if bad else 0)"

plus `run_selftests.py --only selftest_role_launch selftest_seat_dirt` green, and `seat_dirt.py report` reading
`"stale": 0` a day after the move with role runs having happened.

## criteria

- No Dispatcher role launch and no daemon has its cwd in /home/mandrake/rm/bench; each runs in its own clone and
  publishes what it wrote from there.
- The Designer harvest reads and lands from the run's own clone, item prose included.
