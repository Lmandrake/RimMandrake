# ABYSS_DARK_MUFFLE_ALL_SOUNDS_1 — the Dark swallows EVERY sound, not only the Abyss's own

Split from `ABYSS_SOUNDSCAPE_BUILD_1` (half 2, owner card turn 3 Q3 "both"; review
`design/Jawa/worldbuilding/biomes/blackcrags_bedazzle_review_2026-09-30.md` §11.2 mark 7, ruled §12).

## spike result (recorded in `src/RimMandrake/Abyss/Source/RM_AbyssSoundscape.cs`)

WORKS, per sound, with no global filter: every `Sample` owns its own `AudioSource`, and vanilla's
`SoundParamTarget_PropertyLowPass` attaches an `AudioLowPassFilter` to that source, driven by any
`SoundParamSource` subclass named in XML. `SoundParamSource_RM_DarkMuffle` (the Dark's density at the
camera, times the strength slider) already drives the four gust-soundscape defs' cutoff, 22 kHz clear to
700 Hz in full Dark, toggle `darkMuffleEnabled`.

## spec

Gunshots, footsteps, animal calls and every other sound are still sharp in the Dark. Muffling them needs
a Harmony postfix where a `SampleOneShot`/`SampleSustainer` is created (add or reuse the source's
`AudioLowPassFilter`, set its cutoff from `SoundParamSource_RM_DarkMuffle`, only on an `RM_Abyss` map).
The Abyss assembly carries no Harmony by design, so this also decides whether it takes a Harmony
dependency or the hook lives in an engine mod.

## criteria
- [ ] Every map sound on an Abyss map is low-passed by the Dark's density at the listener, under the same
      `darkMuffleEnabled` setting; nothing changes off the Abyss.
- [ ] Judged with the owner present (sound is never judged solo).

## verify

Offline build + Abyss validation.py; the sound itself is a joint session.
