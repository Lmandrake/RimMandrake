# PLACER_IDENTITY_REPLAY_1 — the setter half of the identity-grade export

Filed 2026-08-28T07:32:28Z, no spec/criteria attached. Decided and written here (owner
never asked), per FOUNDRY doctrine for a thin item.

## What was actually missing, checked against live code, not assumed

`jawa/export_things` (JawaBenchExportTools.cs, added 2026-08-28) reads quality, container
CONTENTS, bills, and storage settings. The item claimed all four need companion setter
tools. **Two of the four already had one, and predate this item:**

- `jawa/storage_settings` — priority + `disallowAll`/`allow`/`disallow` — added 2026-08-26.
  Sufficient to replay an exported `storage{priority, allowed[]}` row: `disallowAll=true`,
  `allow=<comma-joined allowed[]>`, `priority=<exported priority>`.
- `jawa/bill_add` / `jawa/configure_bill` — recipe, repeatMode, repeatCount, targetCount,
  storeMode, qualityMin/Max, suspended — added 2026-08-26. Covers every exported bill field
  **except `pauseWhenSatisfied`**, which neither tool exposes — noted, not fixed here
  (narrow, and not blocking a bill's core replay).

**The two real gaps, now filled** (`a36db094`):

- `jawa/set_quality` — CompQuality on any already-existing thing by id.
  `jawa/build_batch` already sets quality, but uniformly across the whole batch call; an
  exported payload has a DIFFERENT quality per row, so a per-thing post-placement setter
  was the actual gap.
- `jawa/container_fill` — insert freshly-made items (`ThingDef:stuff:quality:count`) into
  any `IThingHolder`. Nothing wrote container contents before this; `export_things`'
  `contents[]` field had no setter counterpart at all.

## criteria
- [x] Quality is settable on an individual already-placed thing, independent of a
      build_batch call.
- [x] Container contents are settable on any IThingHolder-implementing thing.
- [x] Bills and storage settings confirmed already replayable — named which tools, and the
      one field (`pauseWhenSatisfied`) that still has no writer.
- [ ] **Live round-trip, owed to the next bridge session** (game was DOWN this whole item):
      `jawa/export_things` a thing with quality+contents+bills+storage set, rebuild an
      equivalent via `build_batch` + `set_quality` + `container_fill` + `bill_add` +
      `storage_settings`, export the rebuild, diff the two rows.

## Watch out
⚠️ `jawa/container_fill` does NOT spawn the item on the map first — it goes straight into
the holder's `ThingOwner` via `TryAdd`. Do not confuse it with `jawa/build_batch`, which
always spawns.
⚠️ Compiled clean and deployed (`--gm --apply`, game was down) but **never called against a
live game** — first real invocation should read its own result carefully, same as any new
tool's first live call.
