## Spec row (verbatim, deepfire_luminous_pigment_spec.md §10 step 10)

| # | build | proof |
|---|---|---|
| 10 | Ninefold bridge + deltas; `RM_DeepfireGodExtension`; LightsOut check | quicktest with Ninefold: `GetSatiation` before/after one coat shows +3 on eight gods, +8 on the trio, −3 Ishko. With LightsOut: proxies survive an empty room being "switched off" |

## What already exists to build on

- `NinefoldDeltaBridge.ApplyDelta` ships and is proven working (dish-eaten
  delta, vermilion Ishko penalty — `DEEPFIRE_PAINT_STATUS_CUISINE_1`,
  closed). The remaining §5.2 event rows (first coat, worn coat, sold,
  statue-coat) are one `ApplyDelta` call each from wherever `CompDeepfire`
  raises the event — `CompDeepfire.AddCoat()` (step 5,
  `DEEPFIRE_PAINT_LIVE_VERIFY_1`, closed) is exactly that raise point for the
  coat-applied deltas; sold/statue-coat need their own hook sites (a trade
  postfix, and reading `RM_DeepfireGodExtension.god` off a statue's def when
  `CompDeepfire.AddCoat` fires on it).
- `DeepfireGodExtension` (statue hook, `god` string field) ships, unused
  (`DeepfireGodExtension.cs`) — the Utinni statue mod can already tag idols
  with it; this item is what actually READS the extension and fires the
  delta.

## Build

Wire `ApplyDelta` calls for: first coat applied (+3 eight gods / +8 trio,
from `CompDeepfire.AddCoat` when `coats` goes 0→1), a Deepfire item sold
(trade postfix), a statue coated (read `RM_DeepfireGodExtension.god` off the
target's def when `CompDeepfire.AddCoat` fires on a Thing carrying the
extension, deliver to that specific god only). Then the LightsOut
compatibility check (spec: "proxies survive an empty room being 'switched
off'") — verify `MapComponent_DeepfireLights`'s proxies are not
inadvertently despawned/dimmed by LightsOut's own power-saving mechanism;
if they are, the fix is likely excluding `RM_DeepfireLightProxy` from
whatever LightsOut scans (its `category`/`altitudeLayer` is `Item`, not
`Building` — confirm this already exempts it before assuming a fix is
needed).

## Needs

`bridge` — both Ninefold and LightsOut are soft dependencies needing a live
tier that includes them (see `modset_builder.py` tiers; `deepfire_luminous_pigment_spec.md`
lists both as candidate deps).
