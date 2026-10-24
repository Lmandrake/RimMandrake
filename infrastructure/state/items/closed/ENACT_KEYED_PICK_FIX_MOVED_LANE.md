# ENACT_KEYED_PICK_FIX_MOVED_LANE

## spec
Found by the ENACT_SCHEMA1_MOVE_VET_UNREVIEWED review of 3ff777b26a (FOUNDRY, 2026-10-24).

In `art/enact.py` `build_plan`, the schema-1 picks loop sets
`intended = g if keyed.get(g) == letter else (gof_resolved(...) if same else None)`.
A KEYED pick (`picks{<lane g>: L}`) therefore takes `intended = g` without either guard that a
pick derived from a decision gets:
- the "moved between two lanes that both exist today -> refuse" guard, and
- the `same` check (the letter shows the same pictures on the clicked sheet and on today's sheet).

So a keyed letter that a rebuild re-filed under ANOTHER lane that exists today still installs at
the old keyed lane. That is a wrong texture at the path of a lane he did not click. The commit says
schema 1 now agrees with the schema-2 slot guard; for keyed picks it does not.

## Real cases (dry run of the real records, offline)
- greentide RSW_Hawkbat G: keyed to `_flip:swanimals/Hawkbat/Hawkbat_Flying_` (adult flying). On the
  clicked sheet (built 2026-10-08T20:58) G was in that lane. Today G is filed under
  `Hawkbat_j_Flying_`, and both lanes exist. The pick is routed to the adult path; ONLY an owner
  keep stops the install today.
- RSW_PekoPeko E: keyed to `f_Flying_`, filed under `m_Flying_` today. Same class.
- Count: 173 keyed picks, 25 of them in a different lane today:
  /home/mandrake/.seat-tmp/FOUNDRY/enact_vet3_scan.txt
- No real install happens today (every case is keep-blocked or refused elsewhere). That is why it
  was filed and not hot-fixed, following the precedent of ENACT_SCHEMA1_MOVE_FIX_OLD_LANE.

## verify (failing-test sketch for selftest_enact_stale_lane.py)
Use case 4's setup (the Kite adult lane AD and the young lane, both existing today; Y filed under
young today):
```
history = [older({"A": AD, "B": AD, "C": AD, "Y": AD})]
p = plan({"schema": None, "picks": {AD: "Y"}})
# expect: Y named in conflicts as refused; no install of Y at the AD path or at the young path;
#         Y not in lane_resolved
# today:  Y installs at the AD path
```
Add a second case: keyed `{AD: "Y"}` where Y is still filed under AD today but shows DIFFERENT
pictures (`same` is False). It must be refused too.

## Fix shape
Apply the decision-route guards to keyed picks as well: compute `ruled_lane` from the clicked
sheet, then refuse when `lane_today != keyed lane` and both lanes exist, or when `not same`.
Keep the `all_live` exemption.

## Also (minor, same function)
`ruled_snapshot` takes git log order as build order: it stops at the first revision with
`built <= click`. If commits from different clones land out of build order, it could pick an older
build than the newest one at or before the click. Fix: scan the bounded window and take the max
`built <= click`, or assert that the order is monotonic and refuse when it is not.
