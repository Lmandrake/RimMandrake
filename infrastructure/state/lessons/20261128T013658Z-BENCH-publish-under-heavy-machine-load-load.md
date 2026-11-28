A ./publish under heavy machine load (load ~35) waited 25 to 55 min for a tree-check slot on 2026-11-27. A plain Bash call moved it to the background and killed it at 10 min with the commit still unlanded. Start every ./publish in a helper under waitalive.py run, never as a plain Bash call.
item: RIMMANDRAKE_CONFIRM_FLOWWORKS_CYCLE_FIVE_EXIT_MET
home: skills/clone-landing-commits
