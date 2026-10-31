arena signing (arena_eventlog._check_entrypoint) reads the script from /proc/self/cmdline; under systemd-run there is no PWD, so a RELATIVE script path (python3 src/.../arena.py) resolves to '' and every signed write is Rejected 'got None'. Always launch harness entrypoints by absolute path from units.
home: NONE
