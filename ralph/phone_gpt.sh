#!/bin/bash
# Phone for help: one call to a different model per pass (owner 2026-11-07). Question and answer land beside this loop's logs.
# bash ralph/phone_gpt.sh stuck|broaden <ask.md> [-f file]... [-i image]...     run it in the background: it can take minutes
[ -d "$LOGS" ] || LOGS=$(sed -n 's/^LOGS=//p' ralph/loop.sh | head -1 | tr -d '"')
[ -d "$LOGS" ] || { echo "REFUSED: no log folder from ralph/loop.sh: $LOGS"; exit 2; }
mode=$1
case "$mode" in stuck|broaden) shift;; *) mode=stuck;; esac
ask=$1; shift
[ -s "$ask" ] || { echo "REFUSED: write the question file first: $ask"; exit 2; }
n=$(ls "$LOGS"/pass_*.jsonl 2>/dev/null | wc -l)
out=$(printf '%s/gpt_help_pass%03d.md' "$LOGS" "$n")
[ -e "$out" ] && { echo "REFUSED: this pass has already phoned: $out"; exit 1; }
[ -e "$out.asking" ] && { echo "REFUSED: this pass's call is still running: $out"; exit 1; }
touch "$out.asking"
cat > "$out.ask" <<'EOF'
You are an outside reviewer, a different model, consulted by an AI agent working alone on a game. Read everything it tells you sceptically. Its explanations, confidence and arguments are evidence of how it is thinking and where its blind spots may be, not facts about the work, so don't let them persuade you. Separate what it measured or saw from what it concluded, and say so where a claim has no measurement or image behind it. Attached images are the best evidence you have: look at them yourself. Spend your effort on what it hasn't considered.

EOF
cat "$ask" >> "$out.ask"
if [ "$mode" = broaden ]; then cat >> "$out.ask" <<'EOF'

What to give back: this agent has to stand in for real players it can only imagine, so it tends to test what it built, the way it built it. From what it has tested and what it plans next, find what it hasn't imagined. Think of real people: someone new who has read nothing; an experienced player who carries expectations from this game and others; someone who ignores the feature entirely; someone who tries to break or exploit it; someone on day 60 of a messy lived-in colony rather than a tidy test site. What would they do first, expect, misread, miss or be annoyed by, across what they see, how it unfolds over time, how it reacts to them, and what surprises them? Give 5 to 8 concrete things to try in the game, most revealing first. For each: the player's situation, what they do, what they would expect, and why the agent's tests so far would not have shown this. Suggest things to try and look at, not new rules, features or test suites.
EOF
else cat >> "$out.ask" <<'EOF'

What to give back: 3 to 5 truly different hypotheses for what is going on, at least one that contradicts the agent's own theory, each with the one cheap observation that would test it, most informative first.
EOF
fi
python3 src/RimMandrake/Utils/gpt_consult.py --prompt-file "$out.ask" "$@" --out "$out" --timeout 900
rc=$?
rm -f "$out.asking"
[ "$rc" -eq 0 ] && [ -s "$out" ] && { echo "ANSWER: $out"; exit 0; }
rm -f "$out"; echo "FAILED rc $rc: no answer, and it doesn't count against this pass"; exit "$rc"
