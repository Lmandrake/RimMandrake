## spec
Left from redesign_2026-11-06 §3.4 item 4 after RIMFLOW_SYNC_STORE_LEDGER_DIFF_NIGHTLY refused a NEW kind=other block at write. (a) The 180 open kind=other blocks get a one-time sweep into item edges or `--kind owner`. (b) New judge/external blocks also name their lift event. (c) `python3 src/RimMandrake/rimflow/relentless_block.py stale` lists 35 stale item-blocks (mostly ended, still on the books; they offer no harm but read as waits): clear them.

Done when: `relentless_block.py stale` prints none and the open kind=other count is 0.
