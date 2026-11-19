## spec
Found by the owed sweep (RIMMANDRAKE_SWEEP_OWED_LIST_FOR_TRASH_MOST_ARE_LATE, 2026-11-19). Owed items are filed
`proposed`, and the sweep's brief says to park a CANNOT SUCCEED item with `rimflow wait`. `model.py` refuses a wait on
a `proposed` item with "only started work waits (ready or doing)" and names no way to pass, which breaks the rule that
a refusal carries its path to pass. The route that works (measured on three owed items that day): `claim`, then
`wait`, then `release` with the claim's token; the wait stays and the item reads `ready`, listed under WAITING in
`queue CONDUCTOR --owed`.

Fix: the refusal on a `proposed` item names that route, with the item id filled in. Other states keep the old text,
because `claim` is refused on a terminal item. Waits keep their meaning: only `ready` or `doing` work waits.

## verify
python3 src/RimMandrake/rimflow/selftest_model.py

## criteria
- A `wait` on a `proposed` item is still refused, and the message names `claim` and `release`.
- selftest_model.py stays green otherwise.

## acceptance
`python3 src/RimMandrake/rimflow/selftest_model.py` case `wait_on_proposed_names_its_path_to_pass`. Watched FAILING
on base e2b67a79e0 (74/75; "the message does not mention 'claim'"); 75/75 after the fix.
