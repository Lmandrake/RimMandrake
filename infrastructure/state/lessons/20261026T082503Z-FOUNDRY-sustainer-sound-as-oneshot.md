A vanilla SoundDef with sustain=True (GeyserSpray) cannot be played with PlayOneShot/PlayOneShotOnCamera: it logs 'Tried to play sustainer SoundDef ... as a one-shot sound' plus 'no on-camera subSounds' and plays nothing. Read the vanilla def's sustain/onCamera before reusing it; for a one-shot, define a new SoundDef on the same clipPath (VENTFLASH_REWIRE_SPRAY_ONESHOT).
home: rimworld-modding
