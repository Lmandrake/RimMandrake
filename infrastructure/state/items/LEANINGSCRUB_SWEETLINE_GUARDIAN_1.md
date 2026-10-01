# LEANINGSCRUB_SWEETLINE_GUARDIAN_1 — the resident guardian a named sweetline tree wakes

From `LEANINGSCRUB_GPT_ENRICHMENT_1` part 3: "harming it wakes a resident guardian (dormant pawn or
incident) — guardian creature still to design." `arid_shrubland.md` §4 records it as a candidate
that was never ruled: *"unique animals that dwell near the trees and defend them from human-sized
things"*.

The hook is ready. `RM_CompSweetlineStation` (`src/RimMandrake/LeaningScrub/Source/RM_SweetlineStation.cs`)
already sees every damaging hit in `PostPostApplyDamage` and records it in the tree's history.
Waking a guardian adds one call there.

## open questions (owner, then design)

1. **What is the guardian?** A new creature (needs a roster row, a canon/IP tier ruling and art), or
   an existing Scrub species in a guardian role?
2. **Dormant pawn or incident?** Either one sleeps at the tree from mapgen and wakes on harm, or it
   arrives by incident when the tree is harmed.
3. **What counts as harm?** Any damage, or only felling or harvest-cutting?

## criteria

- Ruled by the owner, then built and gated by the existing "Named sweetline trees" Mod Setting.
