A selftest of a real-data reading must feed the real state file, not a dict made in the test: selftest_conversion_owed passed {mod: Pyrelands} while the real stage.json says mod RimMandrake/Pyrelands, so the Pyrelands 0.2.0 Designer packet silently read 'none' for its owed conversion.
item: RIMMANDRAKE_READ_FIX_AA31225CA5_WITH_FRESH_EYES
home: NONE
