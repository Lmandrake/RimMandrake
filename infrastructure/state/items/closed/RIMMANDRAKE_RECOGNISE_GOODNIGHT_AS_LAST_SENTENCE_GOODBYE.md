## spec
At 2026-11-19T07:23:10Z the owner wrote "Afk. Goodnight." in the Conductor window (session 48b8b4bd, delivered mid-turn as
a queued_command attachment). At 07:27:23Z `seat_restart.py request` answered "REFUSED: no goodbye of his within 3600 s
of his last message" (transcript line 513) and the window stayed open all night. The time window was not the cause: his
goodbye WAS his last message. `last_goodbye()` found no goodbye at all [measured, offline on the real transcript]:
`goodbye_phrase.is_goodbye` matches the whole message against goodbye_phrases ("afk goodnight" is not one), and as a last
sentence it accepted only `TRAILING = ("goodbye", "good bye")`, so "Goodnight" ending a longer message did not count,
although "goodnight"/"good night" are goodbye phrases as a whole message. conductor.md: "His goodbye (his whole message,
or its last sentence)". Fix: "good night" and "goodnight" also end a longer message.

## refs
file: src/RimMandrake/rimflow/goodbye_phrase.py
file: .claude/hooks/selftest_conductor_goodbye.py

## criteria
- `python3 .claude/hooks/selftest_conductor_goodbye.py` exits 0, its YES list holding "Afk. Goodnight." and
  "Keep going. Good night!".

## verify
python3 .claude/hooks/selftest_conductor_goodbye.py   # exit 0
Acceptance test: watched failing 2026-11-19 on 473d14755c: 2 failures (the two new YES cases).
