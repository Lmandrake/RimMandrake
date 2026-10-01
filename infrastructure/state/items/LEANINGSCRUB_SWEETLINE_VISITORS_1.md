# LEANINGSCRUB_SWEETLINE_VISITORS_1 — travellers camp under sweetline trees, pilgrims leave tokens

From `LEANINGSCRUB_GPT_ENRICHMENT_1` part 3: "travellers camp under it, pilgrims leave tokens". The
name, history and wool timer are built in `RM_CompSweetlineStation`
(`src/RimMandrake/LeaningScrub/Source/RM_SweetlineStation.cs`). Its history list is the natural place
to record visits.

This overlaps `LEANINGSCRUB_MECHANICS_BUILD_1` part 8 (inhabited injections: "sweetline pilgrim
camps" appear in the consult's Quincunx). Build it with that scatter set, not as a rival system.

## open questions

1. **Who are the travellers and pilgrims?** Generic `RM_` locals (the free tier), or Jawa/campaign
   dressing that belongs in the Utinni patch layer (Q11a)?
2. **Mapgen or live?** A camp or token scatter placed at generation, or a visitor incident that
   walks in and lingers at a tree?
3. **What is the token?** It needs a new item def and art. No art exists. Check artpipe
   `done/` / `_artsrc/` / `registry.jsonl` before queuing any.

## criteria

- Built, gated under the "Named sweetline trees" setting (or its own), and visits land in the tree's
  history.
