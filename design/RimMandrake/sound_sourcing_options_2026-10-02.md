# Sound sourcing options (SOUND_SOURCING_ROUTE_1) — 2026-10-02

**Ruled 2026-10-03 (owner, typed): vanilla sounds ship as final for now, no retuning; sound work has not
started.** No audio item is stalled on sourcing (`SOUND_SOURCING_ROUTE_1` dropped; `infrastructure/agents/FOUNDRY.md`
"Audio"). The research below is for when sound work begins.

Research for the question **where do our sounds come from?**
The mods are meant for free Steam Workshop release, so every route is judged on whether we may
**redistribute the clip as a loose `.ogg` inside a public mod**, not merely "use it in a project".

## 1. The need (counted from the items)

| Item | Sounds owed | Kinds | Today |
|---|---|---|---|
| `CAULDRON_ENRICHMENT_AUDIO_1` (+ `CAULDRON_MECHANICS_BUILD_1` part 1) | ~25 clips per the spec's own count (`cauldron_enrichment_audio_visuals_spec_2026-10-02.md` §4): bellow x3, vexxiss vox ~8, metal chop x6, felled x2, vapour hiss x6; then the Engine Underfoot floor + groans (~1 loop + ~6) | creature calls, one-shots, positional hisses, one ambient loop | vexxiss silent; harvest on vanilla `Recipe_Smith` |
| `CRACKEDLANDS_FIVE_BEATS_AUDIO_1` | 6 SoundDefs (`RM_CanyonBeat_SlotWind`, `_PanTick`, `RM_CanyonChime_Far/_Mid/_Near`, `RM_CanyonFlood_Roar`) + the tarruq call | wind loop, ticks, tuned chimes (3–4 tones), a roar sustainer, a long low creature call | vanilla clips retinted by pitch |
| `FORGE_VOICES_AUDIO_1` | 8 (turbine throb loop, vent cough, boiling-rain hiss loop, basalt tick, glass singing, cracking pulse, phase stinger, nodule click) + optional tower harmonics | loops + one-shots, industrial/geologic | vanilla clips retinted; 4 also fail `selftest_sound_paths.py` (packed in `resources.assets`) |
| `FEVERWOOD_CROWN_SOUND_HEAT_1` | 1 sustained bed (`RM_FeverWood_CrownHum`) | ambient loop | **spec already sanctions shipped Core/DLC clips**; owned audio is a later swap |
| `ABYSS_SOUNDSCAPE_BUILD_1` | 4 families: gust impact, gill-fan rustle, grain ticks, dying-lamp clatter (~12–16 clips at 3–4 variants) | sparse one-shots over silence | nothing built |
| Rust Cathedral (`RUT_HumLayers.xml`, `RUSTCATHEDRAL_BASE_FINISH_BUILD_1`, `RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1`) | 3 hum layers (`RUT_HumLayerDrone/Tense/Alarm`), `RM_LineCycleRoll`, `RM_BorehulkGrind` + its grinding horn | drones/tonal beds, a travelling rumble, machine moans | 3 placeholder hum clips |

**Total: roughly 75–90 clips across ~35 SoundDefs.** By kind: about **15 creature vocalisations**
(vexxiss, tarruq), **8–10 ambient loops/drones**, **50–60 short one-shots** (impacts, hisses, ticks,
chops, clicks). All mono `.ogg`, 44.1 kHz, mostly under 4 s; loops 10–30 s seamless. Every item binds
code to **defNames only**, so any route swaps `grains` in place without code changes.

Two constraints the specs already set:
- An `RM_` (free tier) mod may not depend on `src/RimStarWars/` clip libraries (SWBestiary, Armoury).
- The Cauldron bans steam/geyser sounds; the Forge wants them. Source per-biome, not one shared pool.

## 2. What the machine has (measured 2026-10-02)

**A whole sound project already exists and was not cited by any item: `D:\Luke\dev\MandrakeAudio\`**
(founded 2026-09-18, last commit `9db3775`). It is the search result that changes the question: the
routes below are mostly about *finishing* that project's pipeline and pointing it at biomes, not
starting one.

| Asset | State (measured) |
|---|---|
| `D:\Luke\dev\MandrakeAudio\library\sonniss\GDC2024\` | 9 zips, 23.5 GB, **not extracted** (bundle 9 alone lists 90 files and ships `License - GDC Game Audio.pdf`) |
| `D:\Luke\dev\MandrakeAudio\library\kenney\` | 786 files (753 `.ogg`), all 10 Kenney audio packs, CC0 |
| `D:\Luke\dev\MandrakeAudio\research\library_manifest.md` | provenance record for both (source URL, licence quote, date) — the model for a per-clip record |
| `D:\Luke\dev\MandrakeAudio\tools\` | `visualize.py` (waveform/spectrogram/loudness PNG), `droid_voice.py` (parametric synth), `vocal_engine_v2.py`, ogg pipeline normalising to −6 dBFS, audition-page generator |
| `D:\Luke\dev\MandrakeAudio\game-audio-kit\` | HTML listening-booth audition pattern (owner picks per row) |
| venv `~/.venvs/mandrakeaudio` | numpy 2.5, scipy, librosa 1.0, soundfile, matplotlib |
| `ffmpeg` / `ffprobe` | static build in `~/.local/bin` (⚠ segfaults on HTTPS input — curl first, then ffmpeg on local files) |
| `sox`, `oggenc`, SuperCollider | **absent** in WSL. SuperCollider was chosen in MandrakeAudio's design and never installed |
| Windows apps | Audacity 4, Sonic Visualiser installed (`C:\Program Files\`) |
| Stable Audio Open (`D:\Luke\dev\StableAudioOpen\`, venv `~/.venvs/stableaudio`) | torch 2.11+cu128 with sm_120 for the RTX 5080 16 GB; `hf auth whoami` = `lmandrak` (token present). **Gated weights return HTTP 403 with that token** — the model licence has not been accepted on that HF account. No weights on disk, `outputs\` empty: **never run** |
| `codex.exe` (Windows, sandbox-bin) | features list has `image_generation` only; **no audio generation** |
| Gemini CLI | **not installed** |
| `src/RimMandrake/Utils/` | `extract_mlie_sounds.py` (UnityPy donor extraction), `selftest_sound_paths.py` (clipPath guard), `build_jawavoice.py` + `jawavoice/` (Jawa speech, not SFX) |
| `D:\Luke\sounds\` | owner's personal collection, ~10.5k files (inventory in MandrakeAudio `research/local_collection_inventory.md`): commercial music and ripped game audio (AVP, Stargate, Mass Effect …). ⛔ **Reference only — not redistributable** |
| `MandrakeAudio\library\droid_sources\`, `reference\` | copyrighted R2-D2 / film reference clips. ⛔ **Reference only** |

⚠️ Risks to flag, not run: Stable Audio Open inference is local GPU ML. Heavy ML inside this seat's
cgroup has killed the window before (memory note `heavy-ml-in-seat-cgroup-kills-window`), and the
local **image**gen track is PARKED by the owner. Local audio generation is a new local-ML track and
needs his explicit yes, and it must run outside the seat cgroup (its own `systemd-run --user` scope).

## 3. Routes

Licence pages read 2026-10-02. One fact frames all of them: **uploading to Steam Workshop grants Valve
a licence to "use, reproduce, modify, create derivative works from, distribute" the upload, and the
uploader warrants "sufficient rights" to grant it** (Steam Subscriber Agreement,
https://store.steampowered.com/subscriber_agreement/). So the test is not "may we use it in a
project" but "may we hand on those rights". CC0 and our own synthesis pass cleanly. Anything else
needs a reason.

### Route A — Keep vanilla stand-ins (status quo)

- **Cost:** zero. **Effort:** done for Cracked Lands, Forge and Rust Cathedral. Cauldron step 1 is about 1 h.
- **Licence fit:** clean, **as long as we reference and never copy.** A `<clipPath>` naming a Core clip
  ships no audio. The RimWorld EULA (https://rimworldgame.com/eula/) lets us use Ludeon resources "as a
  basis or reference for a Mod" but says *"You're not allowed to rip these resources out and pass them
  around independently"*, and mods may not contain "a substantial part of our … content". ⛔ So never
  extract a packed `resources.assets` clip (the Forge's four) into a mod folder. Reference it, and give
  `selftest_sound_paths.py` its `VANILLA_PACKED` entry.
- **Quality:** low for identity. Pitch-shifted vanilla sounds like vanilla, and a thrumbo under the
  vexxiss will be recognised. It cannot make a tarruq call, tuned chimes, or a Cathedral drone that
  reads as new.
- **Pipeline:** none. It is XML only.

### Route B — Curated royalty-free and CC0 libraries, picked by ear

- **Sources and licences:**
  - **Sonniss GDC 2024 bundle**, **already on disk** (23.5 GB, `D:\Luke\dev\MandrakeAudio\library\sonniss\GDC2024\`).
    The bundled `License - GDC Game Audio.pdf` (read from zip 9) says the licensee "may use and modify
    … for personal and commercial projects without attribution", "may not sell any of the sound effects
    as they come (although … may be sold as incorporated into the licensee project)", and the licence
    has a **NO AI TRAINING OR USAGE** clause. Fit: **good but not CC0.** Shipping a clip inside a mod is
    "incorporated", and the mod is free. The grey edge is Valve's re-licence grant on a loose `.ogg`.
    ⇒ **Ship Sonniss material processed or layered, never byte-identical**, and never feed it to an AI
    model (no Stable Audio audio-to-audio on Sonniss input).
  - **Kenney audio**, **already on disk** (786 files). CC0 1.0 (https://kenney.nl/assets/category:Audio).
    Fit: perfect. Thin on creature and ambient material, strong on impacts, UI and sci-fi blips.
  - **Freesound** (https://freesound.org/help/faq/). Each sound carries CC0, CC BY, CC BY-NC or Sampling+,
    and search can filter by licence. **Use CC0 only**, with CC BY at most, credited in the mod. ⛔ Exclude
    BY-NC and Sampling+. Downloading needs an account, and the API needs a token, so that step is the
    owner's hands once.
  - **OpenGameArt** (https://opengameart.org/content/faq). It mixes CC0, CC-BY, CC-BY-SA, OGA-BY and GPL.
    **Use CC0 only.** CC-BY-SA's share-alike would bind the derived clip and muddle the mod's licence,
    and plain CC-BY forbids DRM platforms (OGA-BY exists to fix that).
- **Cost:** zero money. **Effort:** the real cost is listening. A person picks each clip by ear from
  thousands. Finding one Sonniss clip in 23.5 GB needs extraction plus a searchable index (filenames
  in Sonniss are descriptive, UCS-style).
- **Quality:** high for real-world material: wind, metal, stone, water, steam, machinery, impacts. Weak
  for **invented creatures**, which need processing (Route C) on top.
- **Pipeline:** extract zips → index filenames + loudness/duration (`ffprobe`) → agent shortlists 5–10
  candidates per SoundDef from the brief → MandrakeAudio audition page → owner picks → normalise to
  mono `.ogg` → per-clip provenance row.

### Route C — Procedural synthesis and layering we script ourselves

- **What it is:** clips we author in code. They are either pure synthesis (numpy/scipy, or
  SuperCollider once installed) or **layered and processed** CC0/Sonniss sources: pitch and time
  stretch, convolution with an impulse response, filtering, granular smearing, stacking. This is
  MandrakeAudio's own design direction (`design/utinni_vessel_soundspec.md`: "all free/local"). Its
  first named deliverable was replacing `RUT_HumLayers.xml`'s placeholders.
- **Licence fit:** **the cleanest route.** Pure synthesis is ours outright. Processed CC0 is ours to
  release. Processed Sonniss is "modified and incorporated", which is its licence's intended use.
- **Cost:** zero money. **Effort:** medium to high, front-loaded. Tooling: `ffmpeg` (present), the
  numpy/scipy/librosa venv (present), `sox` (absent, one `apt`/`uv` install) and SuperCollider (absent).
- **Quality by kind:** **excellent for drones, hums, chimes, ticks, hisses, rumbles, wind beds and
  clicks.** That covers the Cathedral hum layers, Cracked Lands chimes and wind, Forge throb, tick and
  glass, the Cauldron hiss and the Abyss ticks. It is about 60–70% of the need. **Weak for creature
  calls** unless built from recorded animal or vocal sources (a pitched-down CC0 elephant, walrus or
  didgeridoo layered under processed breath). Vexxiss and tarruq calls are the hard 15.
- **Pipeline:** one recipe file per SoundDef (YAML: sources with licence ids, filter chain, variants,
  target loudness, loop points) → a deterministic renderer in `D:\Luke\dev\MandrakeAudio\tools\` →
  `ffmpeg -ac 1 -ar 44100 -c:a libvorbis` → copy into the mod's `Sounds/` → `selftest_sound_paths.py`.
  Recipes are committed, `.ogg` output is derived. Re-rendering is free, so tuning after the owner's ear
  costs nothing.

### Route D — Local AI generation: Stable Audio Open 1.0

- **Licence:** Stability AI Community License (https://stability.ai/community-license-agreement). It is
  free for commercial use under USD 1M annual revenue. *"You own any outputs generated from the Models"*.
  Outputs carry no attribution requirement (only Derivative *models* need "Powered by Stability AI").
  You may not use outputs to train a foundation model. Training data was Freesound and FMA under CC0,
  CC BY and CC Sampling+ (model card, https://huggingface.co/stabilityai/stable-audio-open-1.0). Fit:
  **good** for a free mod.
- **Contrast, excluded:** Meta AudioCraft (AudioGen/MusicGen) **weights are CC BY-NC 4.0**
  (https://github.com/facebookresearch/audiocraft/blob/main/LICENSE_weights). Non-commercial weights
  under a Workshop upload, whose Valve grant includes promotion, is a fight not worth having.
- **Cost:** zero money. **The owner's hands, once:** accept the gated licence on Hugging Face for account
  `lmandrak` (measured: the token is present, and the gated file returns **403**). The weights are several
  GB.
- **Risk:** this is **local GPU ML**. Heavy ML in the seat cgroup has killed the window before, and the
  owner PARKED local imagegen. It needs his yes, and must run in its own `systemd-run --user` scope,
  never inside an agent's shell.
- **Quality:** decent for textures and foley (wind, hiss, rumble, crackle, machinery beds), mediocre
  for specific creature calls, and up to 47 s per generation. It is never run here, so this is
  UNMEASURED on our briefs.
- **Pipeline:** prompt per SoundDef from the spec's "brief" column → `generate.py --seed` ×N →
  audition page → pick → trim, loop and normalise (Route C's tail). Seeds plus prompts are the
  provenance.

### Route E — Hosted AI generation: ElevenLabs Sound Effects

- **Licence:** ElevenLabs Terms (https://elevenlabs.io/terms-of-use). *"You retain all rights in and to
  your Output."* But **free-tier use is non-commercial only** (§1(c)), and a paid plan grants commercial
  use. Fit: **good only on a paid plan.** A free Workshop mod is arguably non-commercial, but don't bet
  shipped assets on "arguably".
- **Cost:** Starter plan, which the pricing page (https://elevenlabs.io/pricing) shows at $6 for the
  first month and 30,000 credits. A sound effect is 200 credits per generation, so about **150
  generations a month**. That is roughly two candidates per owed clip in one month. Re-check the
  price at signup.
- **The owner's hands:** an account and payment. This is a purchase, so it is his decision.
- **Quality:** the best of the AI options for **creature vocalisations and specific one-shots**,
  judging by its reputation. That is not measured here. Each output still needs his ear.
- **Pipeline:** the same as D, with an HTTP call in place of local inference. It uses no GPU and puts
  no risk on the seat.

## 4. Recommendation

**Route B + C as the house pipeline, built inside `D:\Luke\dev\MandrakeAudio\` (it already exists for
exactly this), with one AI route admitted only for creature calls.**

1. **Now, at no cost:** keep Route A placeholders where they ship (they already do). Add the Forge's
   `VANILLA_PACKED` entries so the selftest passes.
2. **Build the pipeline once (Route C's recipe renderer + Route B's indexed library):** extract Sonniss
   2024 and index it with Kenney. Render the **Rust Cathedral hum layers first** (MandrakeAudio's own
   named first deliverable, pure synthesis, licence-trivial). Then do Cracked Lands chimes and wind,
   the Forge, and the Abyss and Cauldron hiss and ticks. That is about 60–70% of the ~80 clips, with
   no new money and no new licence surface.
3. **Creature calls (about 15: vexxiss vox and bellow, tarruq):** first try C (processed CC0 animal
   and breath recordings). If his ear rejects that, use D or E per his card answer.
4. **Provenance is part of the deliverable:** each mod with owned audio ships a `Sounds/CREDITS.md`
   (clip → sources → licence → URL). CC0 and Sonniss need no credit, but recording them is how we
   answer a takedown. CC BY sources are credited in the mod description.
5. ⛔ Never ship: a ripped Ludeon clip, anything from `D:\Luke\sounds\`, the droid reference sets,
   AudioCraft output, free-tier ElevenLabs output, or an unprocessed Sonniss file.

This answers the four-option Q1 in the Cauldron spec. It is that spec's option 4 ("build a small sound
pipeline once"), and it turns out to be about half built already.

## 5. Owner question (card-ready)

Header: `Sound source` (12 chars)

**Where should our ~80 owed sounds come from? A sound workshop already exists at
`D:\Luke\dev\MandrakeAudio\` with 23 GB of free-to-use sound libraries downloaded, but nothing has been
made for the biomes yet.**

1. **Build from free libraries plus our own synthesis (Recommended).** We script hums, chimes, ticks,
   hisses and rumbles ourselves, and layer and process royalty-free and public-domain recordings for
   the rest. It costs no money and is the cleanest to publish. It costs your ear on an audition page per
   batch. Creature calls (vexxiss, tarruq) are the weakest part, and may still sound like processed
   real animals.
2. **The same, plus a paid AI sound generator for creature calls** (ElevenLabs, about $6 a month,
   which needs your account and card). Calls come out stranger and more alien, and we own them under a
   paid plan. That is a subscription to manage, and the quality is uneven, so you still judge each one.
3. **The same, plus a free AI generator on this PC for creature calls and textures** (Stable Audio Open).
   It costs no money, but needs you to accept its licence on Hugging Face once. It runs heavy GPU work on
   this machine, which is the kind of local AI work you parked for images.
4. **Keep the retuned vanilla RimWorld sounds for now.** This ships today at zero effort. But the
   biomes sound like RimWorld with a cold, and the Fever Wood silence and the Cathedral hum will not
   feel like new places. We revisit at release.
