systemd-run expands ${VAR} in the command it is given, so a bash -c body with ${PIPESTATUS[0]} becomes a bare 'exit' and a failed winbuild read exit 0 inside a walled unit (WP-02 selftest_relentless_checkbox E4, 2026-11-06). In a toolchain/probe command use set -o pipefail, or write $$, never ${...}.
home: src/RimMandrake/rimflow/relentless_wall.py
