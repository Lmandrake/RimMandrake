## finding
While fixing the IonSlug bug (VERB_MARKERS exclusion, `972798af`), a full in-place
`python3 gen_armour_patch.py` regen against today's live/offline dump changed THREE
guy762_*/KotOR* ops (guy762_RangedDamage_sonic, guy762_MeleeDamage_sonic,
guy762_GrenadeDamage_sonic in Armour_DamageCategories.xml; KotORSlugBolt,
SWProj_TL50slugbolt in Armour_Penetration.xml) from `PatchOperationConditional`
(own-mod attribution, per the deliberate `ARMOURY_RETIRED_GUARD_FIX_1` fix) to
`PatchOperationFindMod` naming "Star Wars KotOR Resources and Materials" (donor
attribution) — unrelated to the fix being made. `declarer()`'s `ds.get()` picks
whichever ONE copy of a co-declared def (ours vs the donor's, per the OWN_NOTE
comment at gen_armour_patch.py:659) the current dump/offline scan surfaces first,
and that pick flipped between whenever these files were last generated and today's
run — same generator, same source, different attribution.

Not fixed this pass: I reverted the unrelated regen output (kept only the
IonSlug removal, hand-edited) rather than risk silently re-introducing
ARMOURY_RETIRED_GUARD_FIX_1 (a FindMod naming a donor mod that later retires
silently no-ops the whole block) on an attribution flip nobody has explained.

## owner decision needed / investigation owed
Read `def_inventory.build()`'s scan order (filesystem enumeration order across
Mods folders is not guaranteed stable) and confirm whether guy762_RangedDamage_sonic
etc. are genuinely co-declared by both `mandrake.rsw.armoury`'s Absorbed_* copy
and the live "Star Wars KotOR Resources and Materials" donor mod right now, or
whether one side dropped out. If both still declare it, `declarer()`/`ds.get()`
needs a deterministic tiebreak (prefer OWN_MODS explicitly) instead of first-seen.

## verify
```
PROVE   two back-to-back gen_armour_patch.py runs (no repo changes between them)
        emit IDENTICAL Conditional-vs-FindMod attribution for every guy762_*/KotOR* op
EXPECT  today: they do NOT (this is the bug); after a tiebreak fix: they do
LIES    a run against a DIFFERENT mod list (minimal vs full) "explaining" the
        flip without fixing the underlying nondeterminism
```
