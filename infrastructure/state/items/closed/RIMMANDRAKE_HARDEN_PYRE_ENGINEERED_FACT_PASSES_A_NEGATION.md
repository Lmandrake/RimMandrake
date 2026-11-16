## spec
Problem against the test (Pyrelands 0.1.0, bars biome_text_says_engineered and inv_art_and_text; blind challenge cycle 2,
miss_of 1). T_DEFS_OFFLINE's fact was re.search(r"\bengineered\b", desc): the planted description "never genetically engineered"
(fault D_BIOME_TEXT_NEGATED_KEEPS_PHRASE) stayed green, and the word without "genetically" would too. The leaf says the
savanna WAS genetically engineered. Fixed in the test: the phrase "genetically engineered" with no negation earlier in its
clause; two mutants added.

## verify
python3 design/concepts/Pyrelands/version/blind_challenge/cycle_2/lane2/catch_check.py D_BIOME_TEXT_NEGATED_KEEPS_PHRASE src/RimMandrake/Pyrelands/selftest_pyrelands_defs_offline.py exits 0.

## criteria
Acceptance test: that catch_check run, 1 pass (rc 1 on the parent 85c4d61bee, watched; rc 0 on b7b77c929e), and T_DEFS_OFFLINE
PASS with 18 of 18 mutants red.

## refs
file: src/RimMandrake/Pyrelands/selftest_pyrelands_defs_offline.py
