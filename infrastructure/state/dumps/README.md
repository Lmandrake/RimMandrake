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

**The command, in full** — and it is the ONLY one that appends a freeze
(`freeze_dump.py` was folded into `refresh.py` and deleted, 2026-08-21,
`FREEZE_SHA_UNREPRODUCIBLE_1`, because two commands that both append a freeze are
two answers to one question):

```
python3 src/RimMandrake/Utils/refresh.py --freeze --by owner
```

Drop `--by owner` for a dry run that prints the line it would append and writes
nothing. 🔑 **`modlist_sha` comes from `refresh.dump_fingerprint()`**, so every
entry carries a number a reader can recompute. `OFFICIAL-2026-08-21` did not — it
was frozen with `e0f11692cf69e516`, which reproduces from nothing on this machine;
corrected in place to `5ef6eec3daf6c325` with a `shaCorrected` field. **A wrong
number made checkable is not a re-freeze:** the capture, the id and `capturedUtc`
are untouched.

## 🔴 WHAT A FREEZE COVERS — ruled 2026-08-21, BUILD, at the owner's request

The question: now that a dump has more than one representation, **is the freeze on
all versions of the same data, or on just one?**

### Just one: the CAPTURE. Never a derived form.

| what | frozen? | why |
|---|---|---|
| `manifest.json` | ✅ **yes** | cost a ~25-minute game load; a human chose it as the target |
| `defs/**`, `animals.json` | ✅ **yes** | same |
| `defs.sqlite` | ⛔ **never** | derived, deterministic, rebuilt in ~60 s |

🔑 **The test is the one CLAUDE.md already states: *could a machine regenerate this
without a human decision?*** The capture could not — it needs the game up, the mod
list loaded, and someone deciding this is the target. `defs.sqlite` is a pure
function of the capture, so **rebuilding it cannot move the target**, which is the
only thing a freeze exists to prevent.

⚠️ **And freezing a derived form would freeze its BUGS.** Measured the day this was
ruled: the db schema went v1 → v2 because v1 keyed rows on each record's concrete
subclass, so `count GeneDef` said 3845 while a `COUNT(*)` over its own rows said
3825 — one tool, two authoritative answers. A frozen db would have served that
disagreement forever, against a capture that was itself fine. `DumpDB` now refuses a
db built by an older schema and tells you to rebuild.

⇒ **The freeze is defined on the capture's contents, not on the directory.**
`defs.sqlite` lives inside the frozen path and is explicitly outside the freeze.

### One capture is official at a time. Archives are not frozen.

**Frozen means "do not re-capture over this".** An archived dump has nothing to
re-capture over, so freezing it is meaningless — it is history, and nothing
regenerates history. Exactly one entry carries `kind: official, frozen: true`.

### 🪤 A freeze that cannot detect REPLACEMENT is not a freeze

**Measured 2026-08-21, and it had already happened:** this file froze
`OFFICIAL-2026-08-20` at `capturedUtc 2026-08-20T15:08:30Z`, and the disk held
`2026-08-21T08:20:20Z`. **Both captures were 578 mods** — so the only quantity the
frozen branch compared had not moved, and the design target everyone authors
against had silently changed underneath them.

That is the exact failure this file's own warning names — *"silently moving the
target everyone is building toward, which is a far worse failure than a stale
warning, because nothing would announce it."* Nothing announced it.

✅ **Fixed:** `refresh.py` now compares the registry's `capturedUtc` against the
manifest's and reports **`REPLACED`** when they differ. A freeze is a claim about
an artifact, and a claim nobody measures is the thing this whole day was about.

⛔ **Only the owner resolves a `REPLACED`** — by re-freezing deliberately (new
entry, new id) or restoring the old capture. An agent must not re-freeze to clear
the warning; that is precisely how the target moves without anyone deciding.

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
