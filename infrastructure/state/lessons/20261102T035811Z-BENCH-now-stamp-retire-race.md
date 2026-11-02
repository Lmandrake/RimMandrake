Deleting a watched trigger file after judging it spent races its writer: re-read-then-unlink still loses a replacement. Rename it aside atomically, judge the moved bytes, os.link back (never overwrites); and sweep old .tmp/.aside leftovers or a PathExistsGlob unit re-fires for ever.
home: src/RimMandrake/rimflow/seat_restart.py
