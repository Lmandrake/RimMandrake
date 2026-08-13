# Mr Samuel Streamer — Study Index

_Built 2026-08-01 from the compiled collection index + Fetcher-downloaded lists/configs._

**What's here:** `lists/` = his mod load-orders (in-game `.rml`, RimPy `.xml`, base-game `.rml`); `configs/` = per-mod settings archives (each `Mod_<WorkshopID>_<Name>.xml` = his actual tuning for that mod). `00_MASTER_INDEX.md` = the full 48-collection catalog with Workshop + Drive links.

⭐ = closest to our gravship/Star-Wars/nomad concept.

| # | Collection | Theme | Game ver | Mods | Cfg files | List types |
|---:|---|---|---|---:|---:|---|
| 1 | Mech Hive | Mechanoid hive, build a superweapon | 1.6.4871 rev591 | 370 | — | ingame |
| 2 | Warlock | Medieval dark-cult magic vs early-industrial | 1.6.4871 rev591 | 620 | 81 | ingame |
| 3 | ⭐ Gravtasm | Character-driven Odyssey gravship (debt scenario, Futurama flavor) | 1.6.4633 rev1261 | 587 | 98 | ingame |
| 4 | Backrooms | Kitchen-sink, discarded colonists return | 1.6.4633 rev1261 | 684 | 94 | ingame |
| 5 | Steampunk 2 0 | Dwemer steampunk mountain (Elder Scrolls parody) | 1.6.4633 rev1261 | 516 | 198 | ingame |
| 6 | League of Villains | Wave-based randomized supervillain squad | 1.6.4633 rev1261 | 459 | 85 | ingame |
| 7 | Degeneration | Reversed-tech generations; star erases capability | 1.6.4633 rev1261 | 410 | 76 | ingame |
| 9 | ⭐ Lone Wanderer | Fallout mechanitor RPG nomad across UK/Ireland | 1.6.4633 rev1261 | 423 | 55 | ingame |
| 10 | Nature s Wrath | Total-conversion adventure RPG (multifloor, world-walk, pursuer) | 1.6.4633 rev1261 | 379 | 70 | ingame |
| 11 | 1 6 Adventure Fantasy | Earlier version of Nature's Wrath adventure RPG | 1.6.4566 rev607 | 473 | 136 | ingame |
| 12 | Mafia City | Mafia contraband empire, urban block-by-block | 1.6.4566 rev607 | 329 | 95 | ingame |
| 17 | Catharsis II | Anything-goes excess parody (anime/Space Marines) |  |  | 88 | rimpy |
| 19 | Grey Goo | Grey-goo swarm hardcore survival |  |  | 166 | rimpy |
| 21 | Evolution | Vanilla Insectoids hive vs anti-bug factions | 1.5.4104 rev435 | 284 | 112 | rimpy, basegame |
| 22 | Mystery Co | Character questing + economy story-gates | 1.5.4104 rev435 | 297 | 47 | rimpy, basegame |
| 23 | Twilight | Permanent darkness/cold, 10 humans left | 1.5.4104 rev435 | 250 | 117 | rimpy, basegame |
| 24 | ⭐ Bounty Hunter | Star Wars caravan nomad -> Save Our Ship vessel | 1.5.4104 rev435 | 292 | 145 | rimpy, basegame |
| 26 | 1 6 Foundation Pack | Generic 1.6 QoL/graphics baseline | 1.5.4085 rev545 | 167 | — | rimpy, basegame |
| 27 | Gymbro | Bodybuilding 'Swolly Grail' parody | 1.4.3901 rev238 | 279 | 115 | rimpy, basegame |
| 29 | Bare Essentials Pack | Perf/bugfix/UI-only foundation (WIP) | 1.5.4085 rev545 | 35 | — | rimpy, basegame |
| 31 | War on Christmas | Elves rebel against Santa (1.4) | 1.4.3901 rev238 | 224 | 112 | rimpy, basegame |

## Notes
- **In-game `.rml` lists** carry the exact `<gameVersion>` and full ordered mod-ID list — the most faithful record of what he ran.
- **Config archives** hold one XML per mod, keyed by Steam Workshop ID. This is the hand-tuning that's painful to reproduce through the in-game UI — the main thing worth studying.
- Collections #32–48 (older 1.2–1.4) are concept archives only: Samuel stripped their load orders and saves, so nothing was downloadable. See `00_MASTER_INDEX.md`.
- Starting saves and multi-GB backup folders were intentionally NOT downloaded (you asked for lists + configs). They're linked in the master index if ever wanted.

## ⭐ PARKED — the "dark, low blasting horn" event sound (user loved it, 2026-08-06)

**What / why:** Samuel's CURRENT game (the **Warlock** collection, #2 — user confirmed "it's about a Warlock") uses a mod that replaces RimWorld's traditional event/notification stings with a deep, ominous, low **blasting-horn** sound — "epic," per the user. We want to identify it for our own campaign (would pair beautifully with the dark-biome / cinematic-danger layer).

**Strong lead (found on disk in his Warlock modlist):** **Darkest Dungeon Incident Sounds** — packageId `darkestdungeon.incidentsounds`. Darkest Dungeon's signature audio is exactly that deep low-brass/horn sting on events → best-fit candidate. [Found in `lists/02_Warlock__modlist_ingame.rml`; NOT present in the other collections' lists, which fits "his current game specifically."]

**Fallback candidates (same Warlock list, weaker fit — not event-horn replacers):** `tro.soundscape.enhanced` ("Rimworld: Soundscape Enhanced"), "Mortis Death Sound" (`...`), "Individual Sound Volume" (a mixer, not a sound-set).

**DECISION (user, 2026-08-06): ADOPT — conditional only on "not a disaster."** User: "as long as it's not a disaster, let's add it!" So this is a greenlight, gated solely on the 1.6 / compatibility check below. **Risk read (why this is almost certainly safe):** event-sound mods are typically pure-XML `SoundDef` replacements — no C#, no hard deps, hot-swappable mid-save, trivially removable → "disaster" is very unlikely. The only real gate is 1.6 support (and if the exact mod isn't 1.6, the sound is easy to extract into our own tiny `SoundDef` patch).

**Status:** lead identified + **ADOPT-conditional**; **Fetcher filed `2026-08-06_darkest_dungeon_event_horn_sound.txt`** to confirm the Workshop page/author/packageId, what exactly it replaces, and **1.6 support**. **→ When delivery lands:** (1) confirm 1.6 (or extract the event-horn `SoundDef` into a custom patch); (2) promote into `required_mods.md` as an adopted audio mod; (3) if adopted, verify it doesn't clash with our other sound mods (Realistic Human Sounds, Ambient Rim, Outer Rim Soundtrack).
