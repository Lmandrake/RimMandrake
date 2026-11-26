A paused map switch leaks an OnCamera PerTick sustainer only when its SoundDef's subSounds lack muteWhenPaused: Sample.Volume is 0 while paused for a muted subSound, and the first tick after unpause ends it through the tick gate. Read the SoundDef before adding a MapComponentUpdate end; RM_ForgeVoices and RM_NamedStorms needed no code (selftest_paused_switch_sustainers.py holds both routes).
item: CRACKEDLANDS_FIVE_BEATS_AUDIO_1
home: skills/rimworld-modding/references/project-engine-facts.md
