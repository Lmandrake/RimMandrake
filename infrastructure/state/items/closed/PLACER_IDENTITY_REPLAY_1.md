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
- [x] **Live round-trip DONE, 2026-08-30** — 4 rows, all four fields, byte-identical after
      normalising id and position. See the section below.

## ✅ LIVE ROUND-TRIP 2026-08-30 (FOUNDRY) — identical, and the comparator is proven sensitive

Fresh 585-mod quicktest, game paused. Rect A `28,58,14,10`, rect B `48,58,14,10`
(the same rect shifted +20 in x). Four subjects chosen so **each of the four exported
fields is non-empty on at least one row**, because a round-trip over nulls proves nothing:

| row | field under test | value set in A |
|---|---|---|
| `Gun_Revolver` | `quality` | Legendary (via `set_quality`) |
| `Grave` | `contents` | `MealSurvivalPack ×3` + `Silver ×50` (via `container_fill`) |
| `ElectricSmithy` | `bills` | `Make_MeleeWeapon_Gladius`, TargetCount 7, DropOnFloor, qualityMin Good |
| `Shelf` | `storage` | priority Important, `disallowAll` then allow Steel/Silver/Gold (3 of 4588) |

Rect B was rebuilt from the exported payload with exactly the five tools this item names —
`build_batch` + `set_quality` + `container_fill` + `bill_add` + `storage_settings` — then
both rects re-exported and compared with `id` dropped and B's `x` shifted back by 20:

```
count A=4  B=4
IDENTICAL after dropping id and shifting x: True
```

⇒ every field survives the export → rebuild → export cycle unchanged, including the
Grave's inherited 88-entry corpse filter and the revolver's `hitPoints 1000` (derived from
Legendary, not set directly).

### 🔑 Negative control — the diff is not vacuously true
`IDENTICAL: True` is worthless if the comparator cannot fail, so one field was perturbed
on B afterwards and the same comparison re-run:
```
jawa/set_quality {thing: Gun_Revolver87763, quality: Good}  -> was Legendary, now Good
IDENTICAL after perturbation: False
  DIFF Gun_Revolver quality   A=Legendary  B=Good
  DIFF Gun_Revolver hitPoints A=1000       B=175
```
It caught both the field changed and the derived one. The pass above is real.

### First live invocations of the two new tools, read carefully as this item asked
Both had only ever been compiled and deployed. Their first real calls:
- `jawa/set_quality` — `{was: "Normal", asked: "Legendary", now: "Legendary"}`, a genuine
  before/after triple rather than a bare success. ✅ And it **refuses honestly**:
  `ElectricSmithy` / `Shelf` → *"has no CompQuality - it cannot carry a quality."* — a real
  reason, not a silent no-op. (Worth recording: neither a workbench nor a shelf carries
  quality here, so the round-trip's quality row had to be a weapon.)
- `jawa/container_fill` — added 3 meals + 50 silver into a `Grave`'s `ThingOwner` and echoed
  `contentsAfter`. ✅ Per-entry honesty confirmed by a deliberate malformed entry:
  `"Silver::,:50"` came back in `failed[]` with `why: "bad quality ','"` while the valid
  entry in the same call still applied — it does not fail the batch, and it does not
  silently swallow the bad row either.

⚠️ `pauseWhenSatisfied` still has no writer (as this item already recorded). It round-tripped
as `false` on both sides only because `false` is the engine default — **that is not evidence
the field can be replayed**, and a bill needing it set true still cannot be rebuilt.

## Watch out
⚠️ `jawa/container_fill` does NOT spawn the item on the map first — it goes straight into
the holder's `ThingOwner` via `TryAdd`. Do not confuse it with `jawa/build_batch`, which
always spawns.
✅ Both were first called live on 2026-08-30 and both read correctly — see the round-trip
section above for their raw results, including the honest refusal and the honest per-entry
failure that prove neither is a silent-success tool.

## 2026-08-30 (FOUNDRY) — live round-trip still not run; the game is wedged

The one open criterion is the live round-trip (`export_things` → `build_batch` +
`set_quality` + `container_fill` + `bill_add` + `storage_settings` → `export_things` → diff),
and it needs a map. RimWorld (pid 33580) is stuck on a **"Loading world." long event that
never completes**: `mapCount 0`, `ticksGame` frozen at 9252 for ~35 minutes,
`go_to_main_menu` answers with its own NRE, `Root_Play.UIRootUpdate` throws every frame on a
null `Find.WorldGrid`. Three `start_debug_game_ready` calls and one `load_game` all failed —
the first two aborted inside `BetterRomance.SettingsUtilities.ChildAge` during **starting-pawn**
generation, before anything had been spawned. The bridge answered normally throughout, so this
is a dead game rather than a dead bridge, and it needs an owner restart.

⚠️ `jawa/set_quality` and `jawa/container_fill` are still in the state this item's own
"Watch out" section warns about: **compiled and deployed but never once called against a live
game.** Their first real invocation is still ahead, and it should read its own result carefully
rather than trusting `success: true`.
