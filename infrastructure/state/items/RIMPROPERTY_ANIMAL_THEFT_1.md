# RIMPROPERTY_ANIMAL_THEFT_1

## Spec
Owner, 2026-09-08 (verbatim on the consolidation sitting): "Some droid
loaders have this property. Also add that some agile pets may be trained
to steal as do some wild animals."

Lands in RimProperty (post-consolidation merge of Property + SalvageClaim
+ TheftHauler). Three pieces: (1) droid loader types carry the
theft-hauler extension via MayRequire patch (Muckraker already does);
(2) a trainable "steal" ability for agile pets (trainability gate TBD);
(3) wild-animal theft behavior for suitable species. Gate all of it on
the Property fabric's TakingEvent so claims resolve correctly.

## Verify
Quicktest: a trained pet and a wild animal each take an item; Property
records the taking; droid loader can uninstall a building via the verb.

## Criteria
Feature works on minimal list; no theft possible for species without the
mark; TakingEvents fire for every route.
