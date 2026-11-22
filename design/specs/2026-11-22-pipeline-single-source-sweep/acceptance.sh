#!/usr/bin/env bash
# Acceptance tests of the build order in report.md (this folder). Each line is one candidate: rc=1 is RED (the rival
# homes still disagree), rc=0 is GREEN. All nine read RED on 2026-11-22 (a1d3079d1b).
#   bash design/specs/2026-11-22-pipeline-single-source-sweep/acceptance.sh            all nine
#   bash design/specs/2026-11-22-pipeline-single-source-sweep/acceptance.sh SPEND      one candidate
# Run from the repo root. Reads only; it writes one temp folder and removes it.
set -u
R=$(pwd); P="sys.path[:0]=['$R/src/RimMandrake/rimflow','$R/src/RimMandrake/Utils','$R/src/RimMandrake']"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
# A claude-account that prints one warning line before its JSON (a planted fault of form).
printf '#!/bin/sh\necho "warning: refreshed token"\necho %s\n' "'{\"ok\": true, \"live\": \"lukas\"}'" > "$TMP/claude-account"
chmod +x "$TMP/claude-account"
ONLY=${1:-}
t() { name=$1; shift; [ -n "$ONLY" ] && [ "$ONLY" != "$name" ] && return 0
      out=$("$@" 2>&1); rc=$?; echo "$name rc=$rc $([ $rc -eq 0 ] && echo GREEN || echo RED) :: $(echo "$out" | grep -v SyntaxWarning | tail -1 | cut -c1-150)"; }

# NEXT: a mod the owner holds is never "automatic" (red while LeaningScrub is on mod_owner_hold.json; with no held mod,
# the fixer's fixture test decides).
t NEXT python3 -c "import sys;$P;from rimflow import maturation as M;n=M.next_step('$R','LeaningScrub')['next'];assert not n.startswith('NEXT (automatic'),n"
# ACCOUNT: two readers of claude-account read the same output the same way.
t ACCOUNT env RM_CLAUDE_ACCOUNT="$TMP/claude-account" python3 -c "import sys;$P;import slot_allocator as S,switching_plan as SP;a=S.live_login_name();b=SP.switcher_status().get('live');assert a==b,(a,b)"
# SPEND: a run record has one spend, whichever reader weighs it.
t SPEND python3 -c "import sys;$P;import role_launch as RL;r={'tokens':1000,'model':'claude-fable-5-2','at':'2026-11-15T10:00:00Z'};a=RL.run_spend(dict(r));b=RL.tokens_v2(dict(r))[0];assert a==b,(a,b)"
# MODEL: one alias table: the weigher and the pinner resolve 'fable' to the same id.
t MODEL python3 -c "import sys;$P;import role_launch as RL,mod_model as MM;assert RL.resolve_model('fable')==MM.pin_id('fable')"
# BRIDGE: no reader of who drives a game reads the BRIDGE glance file.
t BRIDGE sh -c "! git grep -n -E \"state', 'BRIDGE'|state/BRIDGE\" -- src/RimMandrake/Utils/preflight_bridge.py src/RimMandrake/Utils/running_now.py"
# SHELL: the hooks split one command line into the same simple commands.
t SHELL python3 -c "
import importlib.util,shlex,os
os.chdir('$R/.claude/hooks')
def L(f):
    s=importlib.util.spec_from_file_location(f,f+'.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def n(v): return [' '.join(t for t in x if t!='\x01') if isinstance(x,(list,tuple)) else ' '.join(shlex.split(x)) for x in list(v)]
c=\"cat > notes.md <<'EOF'\ngit add -A\nEOF\"
r={f:n(L(f).segments(c)) for f in ('block_blanket_git_stage','block_blind_scan','block_tmpfs_clone')}
assert len({repr(v) for v in r.values()})==1,r"
# PUBLISH: a ledger note can land its own shard.
t PUBLISH sh -c "python3 src/RimMandrake/rimflow/cli.py note --help | grep -q -- '--publish'"
# PUSH: the four push guards run once, from git's pre-push only.
t PUSH sh -c "! python3 -c \"import json;s=json.load(open('.claude/settings.json'));print([x['command'] for L in s['hooks']['PreToolUse'] for x in L['hooks']])\" | grep -q -E 'block_ledger_lint|block_dll_source_mismatch|block_orphan_item_prose|block_unledgered_texture'"
# TIME: one local-time format for the same instant.
t TIME python3 -c "import sys;$P;import control,maturation_dispatch as D,pipeline_pause as PP,red_dispatch as RD,pipeline_control as PC;t=1795400000.0;v={f(t) for f in (control.pac,D.pac,PP.pac,RD.pac,PC.pac_str)};assert len(v)==1,v"
