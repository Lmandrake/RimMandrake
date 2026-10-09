NEW mechanism never observed: none new; it re-measures a fixed fail (A1 stands failed on the ledger).

Re-check of LEANINGSCRUB_WEEPER_VINE_1.A1 (FAIL in sitting 2: pools refused natural terrain). Fixed by removing placementMask from RM_VenomPool and RM_ThornLitter (cd03da899, on origin/main); sitting 2 saw 8 pools from a weeper after redeploy but recorded it only run-level.

## criteria
- [ ] A1: RM_FourFormsProof weeper|on sheds RM_VenomPool on natural ground; weeper|off sheds none.

## verify
`jawa/static_call` RM_FourFormsProof.ProofForm `weeper|on` then `weeper|off` on a quicktest map; record against LEANINGSCRUB_WEEPER_VINE_1.A1 (and A3 fade if a long run is cheap).
