# NEXT_RELOAD.md — the shared queue for the next game load

_A cold load costs **~23–30 minutes**. It is the scarcest resource in this project.
This file exists so that a load is never spent on one question._

**Any thread may append here.** Before launching, work the pre-flight list — every
item on it is offline and free, and each one is a way a load gets wasted. After
the load, harvest the whole log, tick items off, and clear the file.

Last updated 2026-08-11 · state verified against `ModsConfig.xml` (written 19:56)
and `Player.log` (19:01).

---

## ⚠️ Pre-flight — fix these BEFORE launching (all offline, all free)

**1. Confirm the Linkin Park removal after the game has fully exited.**
As of the last check both were still listed in `activeMods` and still on disk —
but ⚠️ **that proves nothing while RimWorld is running.** The game holds its mod
list in memory and rewrites `ModsConfig.xml` on exit, and Steam will not remove an
unsubscribed mod's folder while the game has it open. The user has removed and
unsubscribed both; re-check only after a clean exit.

| packageId | position | on disk |
|---|---|---|
| `sysmy.partyexpansion` | 258 | 6.4 MB |
| `sysmy.pelinkinpark` | 456 | 237 MB |

They hook `MusicManagerPlay`, the same singleton **RimTunes replaces**. If they
are still present, two music managers are fighting and any Tag Editor work done in
that state may not reflect how the game behaves once they're gone — so verify
post-exit before the tagging session, not during.

**2. Our mods are no longer loading last.** A re-sort scattered them:

| mod | position (of 573) |
|---|---|
| `mandrake.jawa.patches` | **190** |
| `mandrake.rimdefdump` | 290 |
| `mandrake.jawavoice` | 454 |
| `mandrake.jawaionweapons` | 553 |

`jawa.patches` at 190 means **~383 mods load after it** and are free to redefine
the defs it patches. The biome-duplicate fix, the weather attach and the new
Wookiee swap all assume last position. Move it to the bottom, or we risk
re-debugging solved problems.

**3. Deploy pending patches.** ✅ Done 2026-08-11 19:0x — armoury + doctrine
patches regenerated, validated (0 errors) and deployed after the session that
found the `Inherit="False"` bug. Re-check anyway if anyone has edited since;
`WookieeHead_Upgrade.xml` was already in place:
```bash
python Utils/deploy_custom_mods.py            # plan — read the output
python Utils/deploy_custom_mods.py --apply
```
Watch for `-` lines (present in game, absent from repo) — that means another
thread hand-edited the deployed copy; `--pull` it back first.

**4. `dump_request.txt` is still armed** with `all`. Every load costs an extra
27 s and rewrites 1.3 GB. Delete it unless you want a fresh dump — and you
probably do, see item 6.

**5. Timestamps disagree — expected while the game runs.** `Player.log` 19:01 vs
`ModsConfig.xml` 19:56 means a re-sort happened after the load, so **the running
game does not match the file**. This is the normal signature of a live session,
not evidence of a problem. Re-read both after exit before concluding anything
about the mod list.

**6. The live dump is stale.** Captured 16:25 with 556 mods; `ModsConfig` now
lists 573. Thirteen mods added (`deon.rimtek.*`, `jecrell.doorsexpanded`,
`lumi.*`, `dubwise.dubsrimkit`, `clown.dedicatedturrets`, `arcjc007.lasercannon`,
`zal.moreutilitypacks`, `vesper.egihologramsandprojectors`,
`mlie.betterprojectileorigin`, `jellypowered.survivaltools`), one removed
(`automatic.gunplay`). Also: **RimTalk is still fully disabled (0 active)** — if
that is still the bisect state, this dump would be a *debug* capture. Per
`REFRESH.md`, don't regenerate the armoury patches from it.

---

## ⚔️ Armoury round 2 — verify the melee fixes (added 2026-08-11, post-test)

Round 1 ran live at 13:57 and **found real bugs**. All are fixed, validated and
deployed; every number below is a decisive pass/fail. Full account in
`skills/rimworld-modding/references/traps.md`.

**What round 1 proved.** A patch aimed at `Force_LightsaberBase` applied cleanly
and was then *discarded*: KotOR Weapons injects `<tools Inherit="False">` onto 8
of the 15 sabers. So the 7 sabers nobody uses got retuned and the 8 with crystal
slots — the ones a player actually carries — kept their stock values. Confirmed
in-game: Protosaber read 0.14% AP, Dual-bladed read 31%.

| check | expect | why it matters |
|---|---|---|
| **Curved lightsaber** AP | **0%** exactly, at any quality | the 8 injected sabers are now targeted by defName |
| **Protosaber** AP | **0%** — not 0.14% | the hilt tool is patched now too; it was deriving AP from its own power |
| **Curved** melee damage | edge/tip **88**, hilt **34** | was stuck at 26/10 |
| **Broadsaber** edge | **120** (top of band) | the band's ceiling should be reachable |
| **Any Yautja blade** AP | **60%** | these had **zero** operations before — the 0.60 tier has never existed in-game |
| **"Echani Foil"** AP | **133%**, not 0% | it is a *vibro-sword*; the old name-matcher gave it lightsaber AP while tripling its damage |
| **Megafauna "claw saber"** AP | back to its own **~24–28%** | it is a beast's claw and had been zeroed |
| **Droid factory** | absent from build menu | ✅ already confirmed; the dead `menuHidden` op is removed, so its XML error should be gone from the log too |

**The decisive one is a lightsaber against powered armour.** AP 0 vs Sharp 1.40
should deflect almost everything. That is Law 3 (mass defeats lightsabers) and it
is the single design claim most likely to be wrong.

**Do NOT regenerate the armoury patches from a dump taken with our mods loaded**
unless you have read `Utils/patch_provenance.py`. The generators now route every
anchor through `mods/inventory/patch_ledger.json` and print a provenance banner;
if that banner says values came from `unknown`, stop and bootstrap the ledger
rather than shipping the result.

---

## 🎵 The main event — RimTunes Tag Editor session

RimTunes replaces the vanilla music system, its dynamic mode is already on
(`enableDMS: True`), and `Config/RimTunes/` is **empty** — it is scoring the game
right now with nothing of ours in it. Full context: `runtime/music_protocol.md`.

**Two open questions that static analysis could not answer.** Both change how we
tag everything afterwards, so answer them first:

1. **What are the `Events` tags?** The category exists in the mod's language keys
   but the individual tag names are not in the files or extractable from the
   assembly. Icons include `explosion.png` and `dove.png`. Open the Tag Editor and
   **write down the actual list.**
2. **Do time-range tags mean clock time or position within a song?** The dialog
   subtitle says *"Play only during this part of the song"*; the tag description
   says *"Plays between {range}"*. These contradict.

**Then confirm the generated tags.** The assembly contains `CreateBiomeTags` and
`CreateWeatherTags`, so tags should be built from loaded defs. Verify that
**`SW_Sandstorm` and `SW_DrySandstorm` appear as weather tags** — if they do, we
can score our own weather with no XML at all, which is the single best finding in
the music work.

**Then tag what already exists.** The library holds **102 songs** and RimTunes
auto-discovers mod music. Free, immediate improvement:

- vanilla's 6 desert-appropriate relax tracks → Require the desert biomes
- the ~6 usable `Tense` tracks → Require `Tense`
  (only 11 of 102 are tense, and 5 of those are Caverns tracks locked to the
  fungal forest — so the real combat pool on a desert map is about six. This is
  the thinnest part of the whole soundtrack.)

**Then back it up.** `Config/RimTunes/` and `Config/Mod_3399705740_RimTunesMod.xml`
→ `runtime/backups/`. Hand-made tagging is otherwise unrecoverable, and stale
mod-settings files are a known rot vector (`benign_log_errors.md` §2.4).

---

## 🖼️ Ride-alongs — batch these into the same load

**Wookiee head swap verification.** `WookieeHead_Upgrade.xml` is deployed. Dev-spawn
a `BTD_Wookiee`; the head should be visibly crisper, most obviously in the **east
profile** where the 128px version is worst. `grep Player.log` for
`Failed to find any textures at` and for `OuterRim_WookieeHead`.

**The two AssetBundle mods.** Droid Depot and Galactic Diversity hold ~44
xenotypes of art never audited. We can now read bundles offline
(`Utils/extract_bundle.py`), so **do the offline sweep first** and use the load
only to confirm anything the sweep flags.

**Falleen ridged-spine.** Ships east + north but **no `_south`** for any of its 5
body variants. Check the def before drawing anything — missing vs. mis-pathed have
completely different fixes.

**Facial Animation decision, per race.** FA deletes the vanilla head draw call, so
`forcedHeadTypes` can never render on a pawn FA draws. Look at the Wookiee with FA
active and decide: exclude the race, or author blank heads.

---

## 📋 After the load — harvest everything

Don't check only what you changed. You paid for a full load.

1. `grep -n "static constructor\|TypeInitializationException"` — mods that are
   *dead*, the highest-priority finding in any log.
2. Cross-reference failure count. **Baseline: 28** at the last clean load, all
   known-benign (16 × `Pawn_Melee_Punch_HitBuilding`, 1 × `VWE_Tool_Whip`). A jump
   means one of the 13 new mods brought friends.
3. `Could not load reference to` — **baseline: 0**. Anything here is new stale
   saved data.
4. Update `mods/benign_log_errors.md` with anything new that gets triaged.
5. Append anything that surprised you to
   `skills/rimworld-modding/references/traps.md` — symptom, cause, fix, and
   **"generalises to"**.

---

## Parked — not for this load

- **Broken-infrastructure mod** (repairable workbenches/turrets/engines for the
  ship). Survey what already exists before designing — see
  `image_request/graphics_overhaul_protocol.md` §6.
- **`validate_patch.py` → lxml.** The validator can't evaluate `text()`,
  `contains()` or `starts-with()` and skips those xpaths — precisely the
  interesting ones. `lxml` implements full XPath 1.0 and is already proven to
  handle them correctly. One-line dependency, converts most UNSUPPORTED lines
  into real checks.
- **`validate_patch.py --defnames <file>`.** Validate against a pre-built list of
  every live defName instead of walking the whole `Defs` tree — turns validation
  into a one-second set lookup. The list is already generated locally; only the
  flag is missing. _(Migrated from `HANDOFF_2026-08-10.md` before deleting it,
  2026-08-11 — it was the only home this idea had.)_
- **`check_sprite.py`** — art intake validator (512×512, real alpha, zero
  saturated pixels, value distribution, bounding box, south/north silhouette
  parity). Build it *before* commissioning any art.
- ~~**`git rm mods/modsconfig_audit.md`** and delete `RimWorld\Mods\_to_delete\`.~~
  ✅ **DONE 2026-08-11** (commit `7dd8d7d`, local session). The audit described a
  163-mod stack against today's 570, so every count in it was obsolete;
  `_to_delete\` held one 2-byte test file. All five documents that referenced the
  audit have been updated — and two of them were carrying stale *claims*, not
  just dead links: Vanilla Helixien Gas is now subscribed and ACTIVE (so the
  mandatory infinite-pocket strip is live work, not a future install gate), and
  Way Better Romance is now ON, which resolves the half-assembled-romance-stack
  open item.
