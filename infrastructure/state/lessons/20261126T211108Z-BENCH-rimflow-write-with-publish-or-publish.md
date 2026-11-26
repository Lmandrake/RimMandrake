A rimflow write with --publish, or ./publish, can wait over 10 minutes in the publish queue when other helpers publish at the same time. Run each one in the foreground under waitalive.py run. A Bash call moved to the background is killed at 10 minutes, and then the commit is left unlanded.
item: LIGHT_LEDGER_ONE_1
home: skills/clone-landing-commits
