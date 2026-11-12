#!/usr/bin/env python3
"""Offline selftest of infrastructure/whittle_claude/gate.py (the wrong-machine guard of the Claude Whittle loops).

    python3 src/RimMandrake/Utils/selftest_whittle_claude_gate.py

Cases: game words inside a commit message or grep pattern are not a game command; a real game command still is refused on
an offline loop; a steve.sh word in a LATER segment does not whitelist an earlier Archmagi bridge take; steve.sh's quoted
remote command (with && and |) is allowed on the steve lane; the archmagi lane refuses SteveDesktop.
"""
import importlib.util
import sys
from pathlib import Path

p = Path(__file__).resolve().parents[3] / "infrastructure/whittle_claude/gate.py"
spec = importlib.util.spec_from_file_location("wc_gate", p)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

CASES = [
    ("offline", "infrastructure/whittle_claude/steve.sh up", False),
    ("steve", "./game down # whittle_claude/steve.sh", False),
    ("offline", "find . -maxdepth 0 -exec ./game down \\;", False),
    ("offline", "grep -F '$(./game down)' README.md", True),
    ("offline", "find . -name '*.md' | head", True),
    ("offline", 'git commit -m "fix rimbridge --live"', True),
    ("offline", "grep -rn rimbridge src", True),
    ("offline", "python3 x.py --live", False),
    ("offline", "ls; ./game a up", False),
    ("offline", 'echo "a;b" && ./game a up', False),
    ("steve", "python3 cli.py bridge take --host archmagi; ./infrastructure/whittle_claude/steve.sh up", False),
    ("steve", 'infrastructure/whittle_claude/steve.sh run "cd x && ./rw_game.sh up | tail"', True),
    ("steve", "FOO=1 python3 cli.py bridge take --host stevedesktop", True),
    ("steve", "python3 cli.py bridge take", False),
    ("steve", "infrastructure/whittle_claude/steve.sh status && ./game down", False),
    ("offline", 'rimflow note X --text "$(./game down)"', False),
    ("archmagi", 'rimflow note X --text "$(infrastructure/whittle_claude/steve.sh down)"', False),
    ("offline", "git commit -m \"$(cat <<'EOF'\nfix rimbridge --live\nEOF\n)\"", True),
    ("archmagi", "ssh mandrake@stevedesktop-wsl x", False),
    ("archmagi", "cd x && python3 x.py --live", True),
]
bad = [(l, c, a) for l, c, a in CASES if g.verdict(l, c).startswith("ALLOW") != a]
for b in bad:
    print("FAIL", b)
print("PASS" if not bad else "FAILED %d" % len(bad))
sys.exit(1 if bad else 0)
