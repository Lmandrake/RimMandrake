# FORGE_VOICES_AUDIO_1 (2026-10-03)
- "owed now" (VANILLA_PACKED entries for the 4 packed clips) is already done: selftest_sound_paths.py lines 75-78 carry all four.
- All 11 RM_ForgeVoice_*/Dhuvvox* SoundDefs already retint real vanilla clips (pitch/volume/dist); no change made.
- "owed": recorded/sourced clips (throb, cough, hiss, tick, glass, pulse, stinger, click) need a human audio source; cannot be authored here. Replace grains in place, keep defNames. Blocked on owner: audio source.
- Added UI/TickHigh to VANILLA_PACKED in Utils/selftest_sound_paths.py (clip used by RM_DhuvvoxScuttle; was the one failing path).
