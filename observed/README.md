# `observed/` — the REPO ROOT one. There are TWO, and they are different places.

🔴 **You are in `/mnt/d/Luke/dev/Rimworld/observed/`.** The other is
`/mnt/d/Luke/dev/Rimworld/infrastructure/state/observed/`. They have the same name, both
hold dated directories, and confusing them has produced a **false "evidence is missing"
verdict three times** — once in `EXPECTED_FAILURES_next_load.md` itself, and twice in
audits that had been explicitly told to check both.

| | |
|---|---|
| **`observed/`** — here | harvested logs, `Player.log` snapshots, `*_harvest_*.txt`, `verify/` |
| `infrastructure/state/observed/` | per-experiment captures — `<date>/<subject>/README.md` — plus `LIVE.md`, `build/`, `logs/` |

🔑 **THE CITATION RULE: a bare `observed/…` path in a `rimflow` evidence string means
THIS directory, the repo root one.** That is the convention every existing `verify` event
follows. When you cite the other tree, write the path in full from the repo root:
`infrastructure/state/observed/2026-08-22/lightsaber_ap/README.md`.

✅ **`rimflow verify` checks both roots** and warns only when a path resolves under
neither, so a correct citation is never flagged. ⛔ **Before declaring any evidence
missing, look in both.** That check is one command:

```
ls observed/<name>  infrastructure/state/observed/<name>
```

⚠️ **Do not "tidy" this by merging the trees.** Nine `verify` events and several docs cite
paths under each; a merge rewrites history that is supposed to be append-only. If the
split should end, that is the owner's call and it needs a migration, not a `mv`.
