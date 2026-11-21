## criteria
- A change applied below L2 either records source kinds or the decision to let it stay uncheckable is written in design 4.3 with its reason.
- The share of change records with no source kinds is measured from infrastructure/state/agent_improve/changes/ and stated.

## why
Found building AGENT_IMPROVE_HARDEN_CADENCE_EMPTY_KINDS. Only the L2 gate refuses a change whose cited pieces yield no source kinds (agent_improve.general_gate); at L0 and L1 apply_change still writes such a record. Since that item the cadence reads such a record as unmeasured and never checks it, so its generalization is never measured. Both records on file (rimworld-modding_v1, using-rimflow_v1) have source_kinds []: 2 of 2, a very small sample. task_kind reads only the first parsable item id in a piece's text, so a lesson that names no item yields None. Decide whether the kinds should come from elsewhere (the piece's own item, its lesson's seat work), or whether L1 changes stay uncheckable by design.
