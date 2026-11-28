A sheet generator seeds a row's 'picks' and migration turns a prefill decision into a 'migrated' slot pick, so DV.slot_picks() returns agent guesses as well as his clicks. Code that records an owner ruling from slot_picks must take only a non-migrated slot record (state pick, its own at) — the same test the sheet's SLX.state uses — or it writes agent guesses as his keeps.
item: RIMMANDRAKE_READ_ART_CANON_BUNDLE_FIXES_WITH_FRESH_EYES
home: src/RimMandrake/Utils/art/decisions_v2.py
