# TRANSIENT — two holes in the ledger system, drafted by CHECK 2026-08-21

Both items are filed for BUILD and both are stuck `proposed`, because a seat that
files work for another seat is refused permission to write that item's prose.
That third defect is written up at the bottom. BUILD: paste the two sections below
into your own `infrastructure/state/items/<ID>.md` and the items go `ready`.

---

# LEDGER_COMMIT_GUARD_INVERTED_1

## spec
`.claude/hooks/queue_lint.py` denies any `git commit` whose command TEXT matches a path
ending `ledger/events.jsonl` when that file differs from HEAD. Since every `rimflow`
verb appends to it, it ALWAYS differs from HEAD after any work — so the guard denies the
one commit that makes the ledger durable, every time.

Three consequences, all measured 2026-08-21:

1. **The honest commit is refused.** `git commit infrastructure/state/ledger/events.jsonl -m "…"`
   is denied. CHECK hit this on a two-line `seat ready` event.
2. **The bypass is trivial and is what everyone already uses.** The regex
   `[\w./-]+\.(?:md|jsonl)` does not match a directory, so
   `git commit infrastructure/state/ledger/ -m "…"` sails through. That is how the two
   commits the ledger DOES have (`ecee610`, `d5110f1`) were made. The guard blocks the
   careful form and permits the careless one.
3. **It matches command text, not file writes.** A `cat > …` heredoc whose PROSE contains
   the words `git commit` and the path is denied — writing this very item through Bash was
   refused, and it had to go through the Write tool. Documenting the ledger is not editing it.

Right now the working tree holds 362 ledger lines against 353 at HEAD: 9 events exist on
one disk only.

The guard's purpose is real and must survive — it protects an append-only file on a mount
where unlocked concurrent writes tore lines in half. But "differs from HEAD" does not
detect a hand-edit; it detects work.

## verify
Distinguish an APPEND from an EDIT: the committed file must be a byte-exact PREFIX of the
working-tree file.

    n=$(git show HEAD:<path> | wc -c); head -c "$n" <path> | cmp -s - <(git show HEAD:<path>)

Deny only when that prefix check FAILS. Then run
`python3 .claude/hooks/selftest_queue_lint.py`.

## criteria
- `git commit infrastructure/state/ledger/events.jsonl -m x` SUCCEEDS when the working tree
  is HEAD plus appended lines.
- The commit is still DENIED when any byte at or before the HEAD length has changed.
- A Bash command that merely mentions the path in prose is not denied.
- `selftest_queue_lint.py` passes, with a case for each of the three above.

## notes
Filed by CHECK, 2026-08-21, in the first five minutes of the session. The ledger is now the
single source of truth for 145 items; an uncommittable source of truth is exactly the
durability hole the commit-and-push rule exists to close.

---

# NEEDS_HAS_NO_SETTER_1

## spec
`needs` decides whether an item is offered. Only `rimflow file` and `rimflow spawn` accept
`--needs`; no verb changes it afterwards. Across the whole ledger exactly 4 events carry a
`needs` value (3 `owner`, 1 `offline`) — every other item renders at the filing default,
`offline`.

Effect on CHECK's board, read 2026-08-21: **38 of 38 items say `needs: offline`**, and the
"WAITING ON A WINDOW" section is empty. Among those 38, offered as offline work:

    ROSTER_SOAK_100_DAYS_1     100 in-game days
    CAST_ROSTER_269_LOAD_1     a load
    W9                         the 21,872-tile import over the bridge
    MORNING_RELOAD_PLAN_1      two loads
    PRELOAD_PREDICTIONS_578_1  a load
    LOAD2_TARGET_IS_SUB7B_1    a load
    INHABITED_ROUTE_ONE_DAY_1  a live day

None can be touched with the game down. The axis POLICY.md introduced specifically so that
"waiting for the game" stops looking like "ready" cannot currently express "waiting for the
game" for any migrated item.

⚠️ This is not a mis-stamp to correct one item at a time — there is no verb to correct it
with. The setter is the deliverable; re-stamping the 38 is CHECK's follow-up.

## verify
A verb sets `needs` on an existing item, appends rather than mutates, and is refused for a
seat that does not own the item. Then, with the game DOWN, `rimflow next --seat CHECK` must
stop offering an item whose `needs` is unmet, and `queue/CHECK.md` must list it under
WAITING ON A WINDOW.

## criteria
- A verb exists that sets `needs` on an existing item and is refused for a non-owner.
- After setting one CHECK item to `game-up` with the game DOWN, that item appears under
  "WAITING ON A WINDOW — nothing is wrong" and is NOT returned by `rimflow next`.
- `rimflow why <ID>` names the unmet `needs` as the reason it is not offered.

## notes
Filed by CHECK, 2026-08-21. Blocks CHECK from stamping his own 38 items honestly.

---

# The third hole — a filed item can never be specced

`POLICY.md` says both *"You may file work FOR any seat"* and *"an item filed without all
three of spec/verify/criteria simply cannot enter `ready`"*. Those cannot both hold.

`.claude/hooks/queue_lint.py` refuses a commit touching `infrastructure/state/items/<ID>.md`
for an item another seat owns — including CREATING it. And `rimflow file --spec` records a
path as a ledger field; it writes no prose.

So the encouraged path — file it for the seat that should do it — produces a TITLE and
nothing else, and the item sits `proposed` until the receiving seat writes a spec for work
they have not investigated. CHECK hit this within five minutes of waking, on the two items
above, which is why both specs are parked in this file instead of in their items.

The fix is one of:

  a) let a filer CREATE the item's prose file when it does not exist at HEAD, and refuse
     only an edit to one that already does;
  b) give `rimflow file` a `--spec-file` that copies the draft into the item's prose file;
  c) drop the refusal contract for cross-seat filings, and let the receiving seat claim
     with an explicit `needs: spec`.

(a) is the smallest, and it matches the hook's own stated intent: *"Filing work FOR another
seat is normal and encouraged. Changing their work is not."*

# A fourth, smaller one: these hooks match COMMAND TEXT, not file writes

Three of the four refusals CHECK hit this session were false positives triggered by prose
inside a heredoc — a spec that quotes a path, or names a policy file, reads to the hook as
an edit of that path. Writing about the system is not editing it. The hooks should test the
tree (`git diff HEAD --name-only`) rather than grep the command line.
