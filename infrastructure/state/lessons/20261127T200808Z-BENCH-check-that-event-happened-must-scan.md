A check that an event happened must scan for the event since its start time, not read the last record at tick time: on 2026-11-26 a fresh Conductor window ended its first turn and the owner typed 0.8 s later, so no 2-min Dispatcher tick ever saw last_kind == assistant_end, and seat_restart failed a healthy window as never having ended its first turn (fix 31b5ccc3f2, tx_summary end_at).
item: OPS_RESTART_UNSTICK_BENCH_YCVY_ZEXY
home: src/RimMandrake/rimflow/seat_restart.py docstring
