# music_protocol.md — adding our own music to the gravship campaign

_Written 2026-08-11. **Revised the same day** after auditing the actually-installed
music mods — the first draft recommended authoring SongDefs, which is the wrong
first move because **RimTunes is already installed and replaces the vanilla music
system entirely.** Every fact below was read from the live def dump
(`DefDump/`, 2026-08-11T16:25Z), the installed mods on disk, or the mods' own
assemblies. Unverified items say so._

Companion docs: `src/Jawa/README.md` (deployment), `REFRESH.md` (staleness),
`skills/rimworld-modding/` (patch authoring and validation).

---

## 0. The short version

**You already own the tool.** `RimTunes` (`depscian.rimtunes`, WS `3399705740`,
load position 286) is *"a powerful, in-game music manager that replaces the vanilla
system. Add your own music, create playlists, and enjoy a dynamic soundtrack that
adapts to in-game events."* Its dynamic mode is **already switched on**
(`enableDMS: True`) and its data folder is **empty** — so it is running the
soundtrack right now with nothing of ours in it.

RimTunes gives us a **tag system** with seven categories, including biome and
weather tags **generated from the loaded defs** — which means our own
`SW_Sandstorm` WeatherDef is automatically a targetable tag, with no XML at all.

**Recommended path: put the music in through RimTunes first.** Author `SongDef`s
only for what we intend to *ship* as a mod. §5 covers that fallback.

---

## 1. The installed music layer — what we actually have

Ten active mods have audio-related names; three genuinely control music.

| Mod | packageId | What it does |
|---|---|---|
| **RimTunes** | `depscian.rimtunes` | **Replaces the vanilla music manager.** Playlists, tags, dynamic selection, custom import. The main event. |
| Linkin Park Party Music + Party Expansion | `sysmy.pelinkinpark`, `sysmy.partyexpansion` | Hooks `MusicManagerPlay` for a party playlist. ~470 MB of apparent commercial tracks — see §6. |
| Dance Party Custom Music | `east.dancepartycustommusic` | Replaces only the lightball dance track; loads clips at runtime from its own `Music/` folder. |
| Ambient Rim | `swablu.ambience` | Ambience, not music — aggregates sustainers into environmental loops. |
| LiquidSFX | `dorbo.watersfx` | Water ambience by proximity. |
| Outer Rim – Core | `neronix17.outerrim.core` | Ship/interior ambience. |
| Biomes! Core (+ Caverns) | `biomesteam.biomescore` | Biome-keyed song hook; ships the `Song_MapRestrictions` extension (§5.2). |
| Romance On The Rim · LEVIATHANS:SANDWORM | — | Event stingers: wedding, boss entrance. |
| Star Wars Themed Sounds · Medieval Melee · Darkest Dungeon · Realistic Human · Tantrum | — | SFX replacers. No music. |

**Two music managers are running at once.** RimTunes replaces the vanilla system;
Party Expansion hooks the same `MusicManagerPlay` singleton. That is a conflict
waiting to happen and a reason to resolve §6 before building anything.

---

## 2. RimTunes — the real mood map

This is the honest answer to "what moods do our mods react to". RimTunes' taxonomy
is far richer than vanilla's, which offers only `tense` plus time-of-day.

**Seven tag categories** (from the mod's own language keys):
`General · Time · Seasons · Biome · Weather · Events · Royalty`

**Fixed tags, with the mod's own descriptions:**

| Tag | Category | Fires when |
|---|---|---|
| `Ambient` | General | "calm, everyday moments" |
| `Peaceful` | General | "peaceful times" |
| `Tense` | General | "tense situations like combat" |
| `Map` | General | "on the world map" |
| `Day` / `Night` | Time | daytime / nighttime |
| `Spring` `Summer` `Fall` `Winter` | Seasons | current season |

**Generated tags** — the important part. The assembly contains `CreateBiomeTags`
and `CreateWeatherTags`, so **biome and weather tags are built from the loaded
defs**. With 561 mods that means every biome in the stack is a tag, and every
WeatherDef is a tag — **including our own `SW_Sandstorm` and `SW_DrySandstorm`.**
We can score our own weather without writing a line of XML.

**Per-tag, per-song state is three-valued** — right-click gives
`Require / Forbid / Default`. So a track can *require* Desert, *forbid* Night, and
stay Default on everything else. That is a real filter, not a checkbox.

**Also present:** `TagWeights` (weighted rather than uniform selection), time-range
tags (`Time Range: {min} - {max}`, "Plays between {range}"), a silence timer
between songs with pause/skip, hotkeys, and a mini-player overlay with a "Dynamic
Music: On/Off" toggle.

⚠️ **Two things I could not determine from static analysis** — both need one
in-game look at the Tag Editor:
1. **What the `Events` tags actually are.** The category exists; the individual tag
   names aren't in the language files or extractable from the assembly. Icons in
   `Textures/UI/Icons/` include `explosion.png` and `dove.png`, which map to
   Tense/Peaceful, so Events may be generated from incidents or game conditions.
2. **Whether time-range tags are in-game time or position within the song.** The
   dialog subtitle says "Play only during this part of the song", which reads like
   song position, but the tag description says "Plays between {range}", which reads
   like clock time. These contradict; check before relying on it.

---

## 3. What's already in the game to evaluate

**102 SongDefs live**, and RimTunes auto-discovers music from other mods
("Mod Integration" is a listed feature), so its library should already contain all
of them plus vanilla's.

| Source | Songs | Tense |
|---|---|---|
| Core | 42 | 5 |
| Biomes! Caverns | 23 | 5 |
| Royalty | 13 | 1 |
| Anomaly | 13 | – |
| Odyssey | 8 | – |
| Ideology · Romance On The Rim · LEVIATHANS:SANDWORM | 3 | – |

**Only 11 of 102 tracks are tense**, and five of those are Caverns tracks locked to
the fungal forest — so on a desert map the real combat pool is about six. **Tense
is the thinnest and highest-impact gap.**

**19 tracks have `commonality: 0`** and never play randomly — the whole Anomaly and
Odyssey catalogue, reachable only through a `MusicSequenceDef`. Worth knowing: the
eight Odyssey orbital tracks will be heard constantly in a gravship campaign.

**Tonally**, vanilla is Americana-frontier: acoustic guitar, harmonica, dust and
warmth. For a Tatooine-flavoured scavenger campaign that is closer to right than
wrong — Star Wars was always a Western. Recommendation is to lean into it and
reserve anything orchestral for rare, high-stakes moments.

**Practical constraint:** Core's music is packed inside `resources.assets.resS`
(254 MB); `Data/Core/` has zero loose audio, so vanilla tracks can't be auditioned
from disk. Mod audio *is* loose — Caverns' 87 mp3s make a good reference for level
and length.

---

## 4. The protocol — RimTunes path (do this first)

**Step 1 — resolve the conflict.** Decide on Linkin Park / Party Expansion (§6)
before tuning anything. Two managers hooking `MusicManagerPlay` will produce
behaviour neither of us can attribute.

**Step 2 — open the Tag Editor and answer §2's two open questions.** Five minutes
in game, and both answers change how we tag everything afterwards. While there,
capture the actual `Events` tag list — that is the missing piece of the mood map.

**Step 3 — tag what's already there before adding anything.** The library already
holds 102 tracks. Tagging vanilla's six desert-appropriate relax tracks to `Desert`
and its five tense tracks to `Tense` + `Require` costs nothing and immediately
improves the score. Do this before sourcing a single new file — it tells us what
the gaps actually sound like.

**Step 4 — add our own audio.** Three import routes: **From Disk** (a folder
browser), **From Library** (already-loaded mod songs), **From URL** (direct links
to audio files only — no streaming pages). Supported formats: **MP3, WAV, OGG.**

Suggested opening set, 12 tracks:

| Slot | Count | Tags |
|---|---|---|
| Desert calm, day | 3 | Require `Desert`/`ExtremeDesert`/`AridShrubland`, Require `Day` |
| Desert calm, night | 2 | same biomes, Require `Night` |
| Sandstorm | 1 | Require `SW_Sandstorm` |
| Tense, desert | 3 | Require `Tense` |
| Gravship / orbit | 3 | see §5.3 — may need the SongDef path |

**Step 5 — back up the config.** RimTunes stores state in
`Config/RimTunes/` (currently empty) and `Config/Mod_3399705740_RimTunesMod.xml`.
Copy both into `deployed/config/` once tagging is done. That work is hand-made and
otherwise unrecoverable — and per `benign_log_errors.md` §2.4, stale mod-settings
files are exactly the kind of thing that rots silently.

---

## 5. The SongDef path — for what we intend to ship

RimTunes state is *ours*, local, and not distributable. Anything we want to ship as
a mod, or that must work without RimTunes, needs real defs.

### 5.1 `SongDef` — the entire authoring surface

Verified against Core's XML and all 102 live defs. These are *all* the fields:

| Field | What it does |
|---|---|
| `clipPath` | Path under the mod's `Sounds/`, **no file extension** |
| `volume` | 0.65–0.7 relax, 1.0 tension in vanilla — the gap is deliberate |
| `tense` | The **only** vanilla mood switch |
| `allowedTimeOfDay` | `Any` / `Day` / `Night` |
| `commonality` | Selection weight. **0 = never picked randomly** |
| `playOnMap` | false = menu/credits only |
| `allowedSeasons`, `minRoyalTitle` | used once each in all of vanilla |
| `modExtensions` | the escape hatch — see 5.2 |

`defName` is optional but **always give ours one** — sequences reference songs by
defName, and an unnamed song can't be patched later.

### 5.2 `Song_MapRestrictions` — biome/weather without RimTunes

**Verified:** class `BiomesCore.DefModExtensions.Song_MapRestrictions`, defined in
**`BiomesTeam.CoreFramework`** (WS `3709492514`), active at position 85.

⚠️ Depend on `biomesteam.coreframework`, **not** `biomesteam.biomescore`. The older
mod also contains the class, but its only 1.6 copy sits in `1.6/Legacy/`, loaded
*only* `IfModNotActive="BiomesTeam.CoreFramework"` — and the framework is active.
Naming the wrong dependency looks right and silently does nothing.

```xml
<modExtensions>
  <li Class="BiomesCore.DefModExtensions.Song_MapRestrictions">
    <biomeDefNameRestrictions>
      <li>Desert</li><li>ExtremeDesert</li><li>AridShrubland</li>
    </biomeDefNameRestrictions>
    <weatherDefNameRestrictions><li>SW_Sandstorm</li></weatherDefNameRestrictions>
  </li>
</modExtensions>
```

Working precedent: `2969748433/1.6/Patches/BiomesCaverns_MusicPatch.xml`.

### 5.3 The 1.6 sequence layer

`MusicSequenceDef` (playlist + fade/loop behaviour) and `MusicTransitionDef` (when
it takes over). **Every transition needs a C# `workerType`**, so a genuinely new
trigger is tier-(c) work. All nine shipped transitions use Ludeon's own workers —
Odyssey's `OrbitalRelax`/`OrbitalCombat` and Anomaly's horror set.

The free lunch: adding songs to `OrbitalRelax` / `OrbitalCombat` gives
**gravship-specific music for zero code**:

```xml
<Operation Class="PatchOperationConditional">
  <xpath>/Defs/MusicSequenceDef[defName="OrbitalRelax"]/songs</xpath>
  <match Class="PatchOperationAdd">
    <xpath>/Defs/MusicSequenceDef[defName="OrbitalRelax"]/songs</xpath>
    <value><li>Jawa_HullSong</li><li>Jawa_SlowDrift</li></value>
  </match>
</Operation>
```

Give sequence-only songs `commonality: 0` so they never leak into the ground
rotation — exactly what Odyssey does with four of its five relax tracks.

### 5.4 Shipping checklist

Separate mod (`src/Jawa/JawaMusic/`, `packageId: mandrake.jawamusic`) — audio
is bulky and rarely changes; mixing it into `Jawa_Patches` makes every patch edit a
huge diff. Declare `BiomesTeam.CoreFramework` in **both** `modDependencies` *and*
`loadAfter` (they are independent). Then:

```bash
python skills/rimworld-modding/scripts/validate_patch.py <patch> --live
python src/RimMandrake/Utils/deploy_custom_mods.py            # plan first
python src/RimMandrake/Utils/deploy_custom_mods.py --apply
```

⚠️ The validator reads `Patches/` only, **never `Defs/`**. Check by hand that every
`clipPath` resolves to a real file with the extension stripped, and that every
defName referenced in a sequence patch exists. A path typo is silent, and silence
in audio is indistinguishable from "the picker chose something else". A small
`check_music.py` that walks `Sounds/` and fails on an unresolved `clipPath` would
close that gap permanently.

---

## 6. The Linkin Park problem

`sysmy.pelinkinpark` (WS 3647834609) ships **~470 MB across 140 .ogg files named
after real Linkin Park songs** — `Crawling.ogg`, `Faint.ogg`,
`Breaking_The_Habit.ogg` — played through a `SingerPlaylist` on a hooked
`MusicManagerPlay` provided by `sysmy.partyexpansion`.

Three separate problems, any one of which justifies removing it:

1. **Almost certainly unlicensed commercial audio** redistributed via the Workshop.
2. **It hooks the same singleton RimTunes replaces.** Two music managers.
3. **It is 47% of all audio in the stack** — 470 MB of ~1 GB.

**Recommendation: disable and unsubscribe both**, unless the party feature is
specifically wanted. If it is, keep `partyexpansion` and drop the track pack.

---

## 7. Sourcing music

Do not embed commercial soundtrack recordings — the project is in git with
publishing ambitions, and §6 is the cautionary example already in the stack. Use
**CC0 / public domain**, **CC-BY with attribution**, or music we generate or
commission. Keep a `CREDITS.md` listing every track, source URL and licence, and
write it as you go.

**Sonic palette**, derived from what the campaign is — hooded scavengers, a
salvaged gravship, a desert world, debt, comedy underneath:

- **Desert calm** — sparse and dry. Solo woodwind or duduk over a low drone, hand
  percussion with space around it, detuned plucked strings. Dust and heat, not
  majesty. Sits naturally beside vanilla's Americana.
- **Sandstorm** — pitched noise. Filtered wind, one sustained tone bending slowly,
  percussion buried and distant. This track should feel *wrong*; the player should
  hear the world turn hostile before reading the alert.
- **Tense / raid** — low ostinato, irregular meter, metallic hits. Resist
  orchestral brass; scrappers being raided isn't heroic. Industrial over symphonic.
- **Gravship / orbit** — cold, wide, slow. Sustained pads, faint mechanical rhythm,
  no percussive pulse. Odyssey's orbital tracks are the reference for restraint.

**Sources:**
[OpenGameArt CC0 music](https://opengameart.org/content/cc0-music-0) ·
[Pixabay CC0](https://pixabay.com/music/search/cc0/) ·
[Free Stock Music CC0](https://www.free-stock-music.com/search.php?cat=&mood=&license=99&bpm=&length=&keyword=)
and its [drone category](https://www.free-stock-music.com/search.php?keyword=drone) ·
[itch.io CC0 collection](https://itch.io/c/7822176/cc0-music) ·
[2026 royalty-free roundup](https://gtstu.com/free-royalty-free-music-indie-games/)

Given the local GPU and Ollama setup, **generating a coherent 12-track set is
viable** and sidesteps licensing entirely — and it is the only way the sandstorm
track gets to be genuinely bespoke, which is the one slot a stock library will
disappoint on. Prefer one source per slot group; twelve tracks from eight artists
sound like a playlist, not a score.

---

## 8. Order of work

1. **Resolve Linkin Park / Party Expansion.** Config-level, no game load needed to
   decide, and it unblocks everything else.
2. **Open the Tag Editor**; answer §2's two open questions and capture the `Events`
   tag list. Five minutes.
3. **Tag the existing 102 tracks.** Free, immediate, and it reveals the real gaps.
4. **Import 12 new tracks via RimTunes** and tag them.
5. **Back up `Config/RimTunes/`** to `deployed/config/`.
6. **Only then** consider the SongDef path, and only for what we intend to ship.

Steps 1–3 need no new audio and no authoring. Step 2 is the only one requiring the
game to be running, and it can ride along with any load already planned — per the
restart economics in `CLAUDE.md`, don't spend a load on it alone.
