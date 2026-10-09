# Belt strays 2026-10-09

1. SHIPVERMIN_FREE_TIER_BEASTS_1.md: matched ledger item (validated, owed A3 L2 / A4 L4), no secrets. LANDED 26194e0aa.
2. SacredGraffiti.dll.srchash: NOT landed. Its "# dll:" line is 9053ec87..., but the DLL on origin/main (and in the tree, identical) hashes 483cd99e... so the stamp does not describe the committed DLL. Origin has no srchash for SacredGraffiti (dll_source_stamp does not check it). Needs a real rebuild via winbuild.py (DLL + srchash as a pair), not a lone stamp.
3. Cauldron DLL pair: source hashes in srchash are identical to origin; only the "# dll:" line and DLL bytes changed (same size 76288), i.e. nondeterministic rebuild. dll_source_stamp check: MATCH on origin. Left uncommitted.
4. Peer files untouched.
