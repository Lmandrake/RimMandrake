# GSS follow-ups progress — 2026-10-06

Owner decisions 22:08 on design/RimMandrake/gss_gpt_source_read_2026-10-06.md: B9, A12/B15, A7.

## Step 1 — A7 census tool built (SelfTest/UnroutableCensus.cs); fuzz 120 seeds/1723 worlds: 0 unroutable
## Step 2 — A7 classified
- fuzz 43,270 worlds: 0 unroutable; live records: 0 of 60
- vanilla-hookup random bases (2000 maps, 5670 leads): 221 unroutable — a 0, b water 11, c-wall-conduit-elsewhere 121, c-wall (no conduit in wall) 89; constructed c-building 1
- verdict: owner's premise false (vanilla hooks through walls, 6-cell rule, no wall test); model works only if dive point = where lead meets barrier. Dive-through NOT built; README + 11 PNGs in Transient/gss_unroutable_examples_2026-10-06/
## Step 3 — B9 (adapter links device->transmitter node, wire patch suppresses its cable) + A12 (sprawlCap -> loopBudget, old key read on load) coded; selftest 738/738
## Step 4 — source committed 7a97be555; DLL rebuilt clean
## Step 5 — push refused (behind origin; rebase blocked by other writers' unstaged files, no stash allowed). Local shas: 931d453fc 7a97be555 
