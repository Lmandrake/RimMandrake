# WORLD_REMAKE_FINAL_STEP_1 — the world gets remade LAST, and that is fine

## the ruling

Owner, 2026-09-20, verbatim:

> *"it is pretty much assured that we will be remaking the world at some point
> once all the biome mods and content donor retirement issues are done. It's
> just very likely and we will handle that when the time comes after
> everything. I mean maybe not but it's ok if we do. We have the worldmap saved
> out and the gravship and the founders. Everything else can be regenerated. So
> don't stress too hard. Let's put that as the very last item to do before the
> official first play session so that you don't get too upset when we can't
> slowly migrate there."*

## what this changes, today

🔑 **A remake is EXPECTED, not a failure.** So stop paying migration tax on the
current world. When a biome mod, a donor retirement, a def rename or a roster
pass would otherwise be shaped around "but the canonical save already has X",
**do the clean thing instead** and let the remake absorb the divergence. The
cost of a careful in-place migration is now a cost we have chosen not to pay.

⛔ This is **not** licence to break the current save casually — it stays the
working article for live tests right up to the remake, and a broken one still
costs a load round. It is licence to stop *designing around* it.

## 🔴 the world gets REPAINTED — owner, 2026-09-20

Verbatim: *"Correct we will repaint the whole world when all the biomes are in.
You don't need to keep rediscovering this."*

🔑 **Biome assignment is redone at the repaint.** The hand-authored geography
survives (see below); which BiomeDef sits on which tile does not have to be
correct today.

⇒ **A biome def with zero tiles is not a defect.** If a biome's content is wired
to a def we own and that def is not painted on the world yet, that is the
expected state until the repaint — `PYRELANDS_WRONG_BIOME_DEF_1` is the worked
example, and it cost a full reconciliation pass to rediscover. Do not "fix" such
a mismatch by repointing content at a donor def; that entrenches the donor and
is backwards from the retirement work.

⇒ **The repaint needs a paint list.** Every owned BiomeDef that must land on the
map belongs in it. Build that list as biomes finish, not at the end.

## carried across the remake — the only three

- **The worldmap** — the hand-authored Ash'karr planet, already saved out.
  🔴 Frozen, hand-made, one world; see CLAUDE.md's no-worldgen ruling. This is
  the thing that must survive, and the only one that cannot be regenerated.
- **The gravship** — exported layout (`ShipLayoutDefV2`; the `gravship-layout`
  skill is the route).
- **The founders** — the hand-edited founding colonists.

Everything else — colony, map state, placed things, stock, research, relations —
**regenerates**. Do not build migration machinery for any of it.

## sequencing

**This is the LAST item before the official first play session.** It runs after,
and only after:

- every biome mod is finished and deployed (the biome wave now in flight), and
- the content donor retirement issues are closed.

⚠️ It therefore must not be claimed early, and nothing may be blocked *on* it.

## spec

Unwritten on purpose — the remake procedure is authored when the gates above are
met, not now. What it will have to cover, at minimum: restoring the saved
worldmap onto a fresh game, re-importing the gravship layout, re-planting the
founders, and a checklist proving the three carried artifacts arrived intact.

## verify

A fresh world exists; the authored Ash'karr map is on it (not a generated one);
the gravship loads; the founders are present and correct. No item anywhere is
still waiting on content from the retired world.

## criteria

The owner sits down to the official first play session on a world that was made
once, deliberately, at the end — with nothing half-migrated behind it.

## Watch out

- 🔴 The worldmap is the single point of failure. Verify the saved-out map is
  loadable **before** the remake is scheduled, not during it.
- The canonical save's mod-list divergence (`CANONICAL_SAVE_MODLIST_DIVERGENCE_1`,
  `CANONICAL_SAVE_SCENARIO_MISMATCH_1`) becomes moot at the remake — check
  whether those items are still worth their remaining effort once this is in
  view, rather than grinding them to completion on a world about to be replaced.
