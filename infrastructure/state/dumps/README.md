<!-- status: live -->
# `dumps/REGISTRY.jsonl` — which def dumps exist, and which are frozen

**Append-only, one JSON object per line.** Read by `src/RimMandrake/Utils/refresh.py`.

## The rule this file exists to encode

🔴 **A mod-count mismatch is NOT staleness for a frozen dump — greater or lesser.**

`refresh.py`'s whole job is flagging artefacts stale when the mod list changes, and
that is right for everything derived from the live game. It is wrong for exactly one
thing: the **official** dump, which is the **design target**. DECIDE and BUILD author
against it.

⚠️ Our own small custom mods move the count constantly — every new `Jawa_*` mod is
another one. If that read as `STALE`, the official dump would sit permanently red, and
someone would eventually re-freeze it just to clear the warning. That would silently
move the target everyone is building toward, which is a far worse failure than a stale
warning, because nothing would announce it.

⛔ **Only the owner re-freezes, deliberately.** Nothing automates it.

## `kind` answers two different questions — do not conflate them

| kind | answers | frozen? |
|---|---|---|
| `official` | *"what should I design against?"* | **yes** — immune to mod-list drift |
| `verification` | *"does the live game match?"* | **no** — staleness applies normally |

A verification dump taken on a 13-mod minimal list is not a worse official dump; it is
an answer to a different question. Asking the official dump whether the live game
matches is the same category error in the other direction.

## Fields

```json
{"id":"OFFICIAL-2026-08-20","kind":"official","frozen":true,
 "modlist_count":578,"modlist_sha":"…","path":"…/DefDump","by":"owner",
 "at":"2026-08-20","capturedUtc":"2026-08-20T15:08:30Z","note":"…"}
```

`path` is matched by suffix against the dump directory `refresh.py` is checking, so a
relative tail is enough and absolute paths from another machine still resolve.

⚠️ **A malformed line is REPORTED, never skipped silently.** A registry that quietly
drops a line lets a frozen dump lose its immunity, and the symptom — *"the official
dump went STALE"* — points nowhere near the cause.
