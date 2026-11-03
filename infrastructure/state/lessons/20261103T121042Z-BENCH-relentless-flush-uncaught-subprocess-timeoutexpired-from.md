Relentless flush(): an uncaught subprocess.TimeoutExpired from ./publish crashes the whole tick and fails rm-relentless.service; any subprocess with timeout= inside a tick must catch TimeoutExpired and return a retry reason.
home: src/RimMandrake/rimflow/relentless.py
