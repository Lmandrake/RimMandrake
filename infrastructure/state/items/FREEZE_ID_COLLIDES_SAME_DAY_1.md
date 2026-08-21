## spec
**Measured 2026-08-21 16:0x by DECIDE, from `refresh.py --freeze`'s own dry run.**

The default entry id is `OFFICIAL-<capture date>` (`refresh.py:445`). Two captures taken on
the same calendar day therefore get the **same id**. The dry run for the evening capture
prints, verbatim:

    "id": "OFFICIAL-2026-08-21", ... "capturedUtc": "2026-08-21T22:44:59Z",
    "supersedes": "OFFICIAL-2026-08-21"

⇒ **an entry that supersedes itself by id.** After such a freeze, `REGISTRY.jsonl` holds two
`frozen: true` entries with one id and different `capturedUtc`, and any lookup by id is
ambiguous — including "which capture is the design target", which is the single question the
registry exists to answer. **This has not happened yet**; the owner has not re-frozen, and
this item exists so that it does not happen silently when he does.

**Do:** make the id unique per capture, not per day — e.g. append the capture time
(`OFFICIAL-2026-08-21T2244`) — or refuse to write an id that already exists and say so,
naming `--freeze-id`. ⛔ Do not silently overwrite the existing entry: a freeze is append-only
by design, and superseding is how the history stays readable.

⚠️ **Until it is fixed, the safe owner command carries an explicit id:**

    python3 src/RimMandrake/Utils/refresh.py --freeze --by owner --freeze-id OFFICIAL-2026-08-21-2244

## verify
`selftest_frozen_dumps.py` gains a case: freezing two captures whose `capturedUtc` fall on
one date produces two entries with **distinct** ids, and no entry's `supersedes` equals its
own `id`. A scan of `REGISTRY.jsonl` finds no duplicate `id` among `kind: official`.

## criteria
Offline; no game needed.

## notes
Found by running the documented dry run, not by reading the code. The dry run is safe by
construction — it refuses to write without `--by owner` — which is why it was worth running
before recommending the command to the owner.
