# GimmeSomeSlack 0.2.0 in-game visit 2: polish (a record; nobody fixes these)

- Core/CordBuilder.cs: a through-wall cord that runs along a wall turns about 80 degrees into its plate within 0.15 cell; read 'wall' (forced) by the bar (S_V2_DIVE_CORD_TURNS_AT_PLATE).
- Device plugs at heaters and near lamps lie under the machine's art, so no plug shows there; the plug's place is right.
- `proof_all.py --only scenes` alone reads SC_cords_all_slack and SC_no_two_cords_alike UNMEASURED (no strands on an empty map): run it with matrix,core.
