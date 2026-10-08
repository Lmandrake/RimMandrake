# Shared object store — trial with telemetry (2026-10-08)

Item `SEAT_MEMORY_CLONES_DRIVES_1`, phase 2 of `memory_clones_drives_2026-10-08.md` (§4 items 1–2,
§7 "Store", headline finding #8). Owner, 2026-10-08: *"try it out, but let's wire it to keep data on
its operation so we can judge if it was a good idea later."*

## What was built

| Piece | Where |
|---|---|
| The store: bare repo, owned by no working tree, fed only by `git fetch` from `mirror.git` | `/home/mandrake/rm/store.git` |
| The one entry point for throwaway clones | `/home/mandrake/rm/bench/src/RimMandrake/Utils/scratch_clone.py` |
| Hourly sampler | `rm-objstore.timer` / `.service` (own user timer, not memwatch: memwatch runs every minute and must stay cheap; a fsck does not) — source `src/RimMandrake/Utils/systemd/rm-objstore.{service,timer}`, installed in `~/.config/systemd/user/` |
| Selftest | `src/RimMandrake/Utils/selftest_scratch_clone.py` (temp store under `/home/mandrake/rm/scratch/<SEAT>/`) |

Use it:

    python3 src/RimMandrake/Utils/scratch_clone.py clone "<purpose>" [--name N] [--checkout | --sparse PATH...] [--fetch] [--dissociate]

The clone lands in `/home/mandrake/rm/scratch/<SEAT>/<name>`, `--no-checkout` by default, `origin`
set to GitHub and `core.hooksPath` set. Its `objects/info/alternates` names the store. `--fetch`
brings it up to the minute from GitHub; `--dissociate` makes an independent copy (hard-linked packs,
no alternates) for anything meant to outlive the trial. Deleting a scratch clone is `rm -rf`; nothing
else depends on it.

**Why a gc can no longer corrupt a borrower.** Borrowers point at the store, never at bench or
foundry. The store sets `gc.auto=0`, `gc.pruneExpire=never`, reflogs kept forever and
`core.logAllRefUpdates=always`, so every tip it ever held stays reachable and even a manual `git gc`
there drops nothing. Its packs are hard links to the mirror's (init cost ~0 bytes, 0.06 s); when the
mirror repacks, the store's links keep the data, and the store then costs its own ~6 GB.

## Where the data lives (outside git)

`~/.local/state/rm-objstore/` — `uses.jsonl` (one record per `clone` call: seat, purpose, path,
clone/checkout/wall seconds, bytes the clone owns vs a full clone, objects borrowed, ok/error),
`samples.jsonl` (hourly: store size, borrowers on store / on a seat clone / other, per-borrower object
check plus one sampled `git fsck --connectivity-only`, disk free), `incidents.jsonl` (a borrower whose
objects stopped resolving), `baseline.jsonl` (a measured full copy: 60.6 s, 6.13 GB on 2026-10-08,
`clone --no-local` — a lower bound, since a GitHub clone also pays the network).

## Was this a good idea? — the judge

    python3 /home/mandrake/rm/bench/src/RimMandrake/Utils/scratch_clone.py report

Read the verdict line, and judge on these:

- **Corruption incidents must be 0.** Any incident is a borrower that lost objects, exactly the failure
  the store exists to stop → BAD; read `incidents.jsonl` before anything else.
- **Clone failures under 10%** of calls. Above that the tool costs more than it saves → MIXED.
- **Used at all.** Zero clones after a week means nobody needed scratch clones; the store is then
  6 GB of insurance for nothing and can go (`rm -rf store.git`, disable the timer).
- **Time and disk saved** against the baseline: each borrowed clone saves ~60 s and ~6 GB.
- **Borrowers on a seat clone must fall to 0.** On 2026-10-08 there were 10, all under
  `/home/mandrake/rm/_quarantine/2026-10-08/`. They were not rewired here: they are in quarantine for
  deletion, and rewiring means copying in the objects only the seats hold and `fsck`-ing each first
  (§7, GPT #12). If any survive quarantine, that is the next step.

Not done from §4/§7: the seat clones still carry their own objects (not re-pointed, by instruction);
no expiry registry or daily cleanup of scratch clones yet; the store is fed from `mirror.git`, not a
re-purposed `mirror.git` itself.
