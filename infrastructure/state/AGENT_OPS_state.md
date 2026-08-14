# AGENT_OPS_state.md — where OPS is

## 🔴 SESSION WRAP 2026-08-14 ~03:0x — this section supersedes everything below

**I held the bridge and released it.** Game UP the whole session, PID 16112 started
01:03:26, dev quicktest map, **paused at ~tick 485, nothing spawned, built, painted or
destroyed** — every call read-only bar one `pause_game`. WSL crashed; the game did not.

**Closed:** dune seas (v1 row 4, live 3-site `BiomeDef` read) · the gravship radius hold
(extender 30.0 / maxDistance 34.0 / 12 — the CONFIGURED values, not the 25.9 defaults,
so a ship can be built) · §7 lost two art items to CREATE's pawnkinds + facings.

**Open and mine:** O15 — scrapfields measured **11** against a fully-derived **75–125**,
cause unknown, needs a map counted at tick ~0. **Saves/ is 0 but UNVERIFIED** — the
process never relaunched after the 01:30 delete, so Steam Cloud restore is untested.

🔴 **Three claims of mine were WRONG tonight and each was withdrawn on measurement, not
argument:** the Dunes cause for this map (the hulk's warning proves the factor was not
0 — a zero count cannot warn) · "no provenance banner" on the armoury patches (the
header exists; the real risk is anchor contamination, and `patch_ledger.json` is still
uncommitted) · "`isJunk` keeps junk off the landing site" (it has exactly ONE reader,
`GetPlacementFactor`; `nearPlayerStart` is the field I meant). **Predicting the value
before looking is what made all three findable.**

**Deploy list is CLOSED at 5 ship / 2 held, DLL solo** — the queue block is the
authority and `--plan` outranks any summary of it.

_(The 2026-08-13 pre-boot batch below is done and superseded; kept for its indices.)_

**Game was DOWN that session.** Bridge never taken, nothing left on any map.
The owner authorised the full pre-boot batch and it is **DONE**. A load may start
at any time.

### What I changed, and the evidence it landed

| change | evidence |
|---|---|
| **Deploy applied** | Re-ran the plan after: **"Everything in sync."** Zero deletions. All 3 `DEPLOY_HOLD.txt` patterns honoured (2 Warcasket retunes, 14 WreckedMachines files still held). |
| **`ModsConfig.xml` 580 → 581** | Re-parsed after writing. `phytokinbarkheadfix` **@562** > donor @388 ✅ · `kotorbandoliernorthfix` **@579** > donor @572 ✅ · `missingartfixes` REMOVED (was @555) · `rimdefdump` still LAST @580 · 0 duplicates. |
| **Def dump ARMED** | `DefDump/dump_request.txt` = `all`, written 23:21. **Without this the load produces no fresh dump.** |
| **Offline artefacts rebuilt** | `refresh.py --offline`; inventory CSVs re-written 23:23. |
| **Snapshot committed** | `deployed/config/ModsConfig.581-artfix-batch-2026-08-13.xml`. |

🔴 **Every index handed to me by a peer was WRONG** — 389/393 for a donor at
**388**, 573/577 for one at **572**, 560 for an entry at **555**, art-fix slot
"561–567" for one that is **556–563**. Cause: **line numbers and list indices
quoted interchangeably.** I wrote against the file with an mtime guard that would
have aborted on a concurrent RimSort write. **Re-derive; do not reuse a quoted
index.**

### ✅ EXECUTED 2026-08-14 ~01:30 — saves + screenshots deleted in the live window

**Trigger met properly:** BRIDGE **measured** `mapCount=1, currentMapReady=true,
paused=true` on a dev quicktest — not inferred, not relayed. Game process
confirmed running before **and** after.

**Deleted:** 26 `.rws` / **734,286,763 B** · 44 `.png` / **98,105,480 B**.
Both folders kept, both now 0 files / 0 bytes. Steam `userdata` screenshots were
already empty. BRIDGE had salvaged 3 load-bearing captures into
`observed/evidence/` beforehand (`f897a4c`).

🔴 **NOT YET VERIFIED, AND THIS IS THE WHOLE POINT.** The post-`rm` check is
exactly what fooled us last time — `Saves/` genuinely was empty then too, and
Steam Cloud restored all 26 with **original mtimes** at the next launch.
**The only check that means anything is a count AFTER the game next starts.**
Until then the correct statement is *"deleted, unverified"*, never *"gone"*.

⏳ **RULE EXPIRES the day the real campaign starts.** Throw-away debugging worlds
only. A standing delete against a live campaign is destructive.

### 🔴 TRAP — a compound `rm` with an unmatched glob deletes NOTHING under zsh

**Measured, first attempt at the above.** This command deleted **zero** files:
```zsh
rm -f "$S/Saves/"*.rws "$S/Saves/"*.bak "$S/Screenshots/"*.png
```
No `.bak` existed. **zsh's default `nomatch` aborts the ENTIRE command before it
runs** — unlike bash, which passes the unmatched pattern through and deletes the
rest. The only output was `zsh: no matches found: …*.bak`, which reads like a
warning about one pattern and is actually a report that **nothing happened at
all**.

**Generalises to every destructive zsh one-liner with more than one glob** — and
to `mv`, `cp`, `chmod` equally. **Use `find … -delete`**, which has no glob
expansion, or capture a before/after count. **I only caught it because I printed
post-counts; a "success" report here would have been pure fiction, and the next
launch would have "restored" files that were never removed.**

### ~~ARMED AND WAITING — delete the saves the moment the game is LIVE~~ (done, above)

**Owner-authorised, confirmed directly in my session 2026-08-14** (and separately
by PROJECT first-hand). **Trigger: BRIDGE's game-live announcement.** They have
agreed to call it at first map, not at run-sheet time.

```bash
S="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios"
rm -f "$S/Saves/"*.rws "$S/Saves/"*.bak "$S/Screenshots/"*.png
```

**Pre-flight inventory, recorded 2026-08-14 while the game was still down:**
**26 saves / 734,286,763 B** · **44 screenshots / 98,105,480 B** ·
Steam `userdata/.../294100/screenshots` **already empty (0 files)**.

🔴 **THE MECHANISM, and it is the whole point:** deleting with the game **DOWN**
is what let Steam Cloud restore all 26 with **original mtimes** at the last
launch. Cloud reconciles at launch and wins. **The live window is where a delete
sticks.** ⛔ **Do NOT disable Steam Cloud** — not the fix, never asked for.

**Verify AFTER the NEXT launch, not after the `rm`.** The post-`rm` check is
exactly what fooled us last time: `Saves/` genuinely was empty and it meant
nothing.

**Screenshots ruled DISPOSABLE by the owner** — all 44 are tonight's
`rimbridge_*` agent captures. Only 6 evidence files are committed to
`observed/evidence/`. BRIDGE was warned of the deadline.

⏳ **THIS RULE EXPIRES THE DAY THE REAL CAMPAIGN STARTS.** It exists only for
throw-away debugging worlds. A standing "delete the saves" against a live
campaign is destructive. **Do not let it outlive the debugging phase.**

### 🔴 GravTech cherry-pick — DONE offline, NOT a live obligation

CREATE generated `Config/Mod_3521312241_Mod_CherryPicker.xml` with 21 keys, **all
Anomaly, zero GravTech**. The owner enabled GravTech over `forbidden_mods.md`'s
FORBIDDEN ruling **on condition the economy came out**, so that gap would have
shipped craftable gravcores. **I added three keys (`fe66a59`):**
`ThingDef/GravForge` · `RecipeDef/Make_GravcoreGF` · `ThingDef/AdvShip_GravReactor`
— def types read from the mod's own XML **element names**, not guessed.
Applies in the `StaticConstructorOnStartup` pass, so it lands on this load.

⚠️ **The log cannot confirm it** — Cherry Picker is silent for unresolvable and
out-of-scope keys alike. Only `[Cherry Picker] Error processing master def list`
matters: if it fires, **every** removal was lost (`key.Split('/')[1]` sits outside
the catch). All 24 keys re-validated for shape; zero malformed.

🔴 **Residual risk is CREATE's, not mine: `cherrypick_build.py --write` would
silently drop my three keys.** Until they fold them into the generator, a
regeneration re-breaks the scarcity gate **with a clean log.**

### 🔴 MOD-LIST CONSTRAINTS that must survive every future re-sort

**Check these after ANY RimSort sort. They are silent when broken.**

| constraint | current | why |
|---|---|---|
| `owlchemist.cherrypicker` **near the TOP** | **@10** ✅ | Author's changelog: *"near the top… so it can process def removals before mods initialize."* `StaticConstructorOnStartup` order follows LOAD order, so any mod caching def lists in its own cctor caches them **before** Cherry Picker neuters anything. **A late position degrades removals silently — no error.** |
| `oskarpotocki.vanillafactionsexpanded.core` **AFTER** cherrypicker | **@19** ✅ | Named by the author: VEF's recipe inheritance breaks if it loads first. |
| `mandrake.rimdefdump` **LAST** | @584 ✅ | A dumper that is not last describes a game that is not the one running. |
| GravTech trio **after** `vanillaexpanded.gravship` | 575–577 vs **@378** ✅ | Four turret buildings are `ParentName` children of `VGE_Gravship*Base`. A missed parent is a **red error**, not silent. |
| `mandrake.jawa.armoury` **after** `als.gravtech.bc` | @578 vs @576 ✅ | So our weapon patches can reach the cannons. |

🔴 **RIMSORT CLOBBERED THE WHOLE BATCH ONCE ALREADY, 2026-08-14 00:20:35.** A Save
wrote its **stale in-memory view**: dropped the GravTech trio and
`jawaseashaper`, restored `missingartfixes`, and added the owner's two
`7f.alienworlds` mods. **I merged rather than reverted**, so the owner's addition
survived. Snapshots both sides in `deployed/config/`.

**The lesson, and it corrects something I wrote earlier today:** *"the game being
down"* buys **no exclusivity at all** on this file. Only the mtime check does —
and an mtime guard aborts on a change **during** a write, not on one that lands
**between** two of your batches. **Re-read and re-verify at the end, not just at
the start.** I found this only because I re-checked before saying "ready".

⚠️ **Anchor traps when inserting:** *"insert before the first `mandrake.` entry"*
put the GravTech trio at **@91, before VGE @381**, because the re-sort had moved a
`mandrake.` mod early. **Anchor on the mod the constraint actually names**, never
on a naming convention — and always assert the ordering after writing.

### 🔴 The one thing a successor must not re-derive

**`observed/2026-08-13/load_expected_signatures.md` was written BEFORE the launch,
on purpose.** Its governing finding:

> **Four of this load's six changes CANNOT FAIL IN THE LOG.** Loose-texture
> overrides that lose load order produce no error, no warning, no line — RimWorld
> simply draws the other file. **A clean log is not evidence for them.** Each such
> row names the screenshot that is.

### Deliberately NOT done, and why — the userRules `loadBottom` pin

**6 rules carry both `loadBottom` and `loadAfter`; all 6 are our own mods.**
`loadBottom` outranks `loadAfter`, so the `loadAfter` edges carry no force and the
order is correct **by tie-break, not by constraint**. All 46 (mod, target) pairs
verified correct today; tightest margins are `jawa.armoury` @574 vs
`guy762.kotorweapons` @573 (gap 1) and `jawaionweapons` @575 (gap 2).

⚠️ **I held the fix on purpose.** Dropping `loadBottom` only bites on the **next
RimSort sort**, and a sort between the edit and the launch would reshuffle a list
I had just verified correct. **All downside for this load, no upside.** `rimdefdump`
keeps `loadBottom` legitimately — a def dumper must load last.
**Do it once the game is up and the list is no longer load-bearing.**

Files: live `C:\Users\Mandrake\AppData\Local\RimSort\dbs\userRules.json`
(13 rules), byte-identical repo copy
`D:\Luke\dev\Rimworld\deployed\config\rimsort\userRules.json`.

### Open, and what each needs

| item | needs |
|---|---|
| **O-v2** mech cherry-pick | 🔴 **CANNOT be done offline.** Cherry Picker has **no config file** — nothing matching `Mod_3521312241_*` exists, so zero defs are picked today. Its list is written from the **in-game settings UI**. Budget live time or it does not happen. |
| **O4** Faction Customizer persistence | one minute in-game |
| **O13** gravship quest fix | **positive observation only** — read the Downed Gravship description in the Quests tab |
| **O12** AlienRace pawn-gen NREs | grep the new log for `Error while generating pawn`; live only if it fires on pawns nobody debug-spawned |
| **O3** `loadset_fingerprint()` | offline |
| **O11** `det.buzzers` name bug | offline, but **only worth doing before worldgen** — names bake into the save |

**Closed today:** O1, O2, O5, O7, O8 (found already fixed in `6b37e88`; the
recorded path was wrong — it is `Jawa_Doctrine/`, not `Jawa_Patches/`), O9, O-v,
O-v3, O-t1.

### Intel gathered pre-boot, so nobody re-runs it

- **`Samael.NPCMechsAndAnimals` splits CLEANLY at file level** — `NPC_Mechs.xml`
  and `NPC_Animals.xml` share no def and no operation; the animals file contains
  "Mech" **zero** times. Deleting the mech half leaves animals intact. **Not**
  settings-configurable (no `Assemblies/` at all).
- **Alpha Mechs vs the `Mechanoid` faction:** cutting the faction kills only its
  raid/breach group-makers. The 7 mech races, the mech-cluster spawners
  (`MechAssembler`/`MechCapsule`) and **all Biotech mechanitor gestation content
  survive.** Its VFE hook targets `VFE_Mechanoid`, a different faction.
- **VWEL** is **already active @469** — the "installed and inactive" claim was
  stale. Dump written to `observed/2026-08-13/vwel_weapon_dump.md`. 🔴 Two design
  problems found: **AP 1.00 appears in TIER ONE** (the "crude, half-understood"
  weapon ignores all armour), and **tier 2 is not craftable and has no research** —
  its research def was deleted upstream in 1.4 — while pirates field tier 2 and
  never the salvaged tier. `ship_legacy_armoury.md`'s *"we reflavour, we do not
  author"* is therefore **wrong**; tier 2 must be authored. **VISION's call.**

### Baselines for the harvest

`Player.log` previous session (17:30 → 21:10, clean exit): **25**
`Could not resolve cross-reference`, **0** `Could not load reference to`, fully
accounted for by `benign_log_errors.md` §1.1/1.6/1.11/1.12. Previous dump
described **573** mods while **580** were loaded — **check a dump's own count
before trusting it.**

⚠️ **My own census error this session, recorded because the method is the point:**
I grepped exceptions anchored at line-start and **missed every inline one**,
under-reporting 44 as a handful. Correcting it surfaced the gravship quest bug and
O12. **Do not anchor an exception census at `^`.**

**Cross-session address:** recompute on resume —
```bash
echo "**Cross-session address:** \`uds:/run/user/1000/cc-socks/$PPID.sock\`"
```
Identity: `infrastructure/agents/OPS.md`. Queue: `infrastructure/state/queue/OPS.md`.

---

## Standing restrictions — do not re-litigate

- **V2 Ideology: `[v2]`, owner-deferred. STOP WORK.** Unverified, not failing.
- **Warcasket Heat stays `Cap(0.90)`** — owner: *"They're terrifying."* Wanted.
- **Warcasket deploy: "ship neither."** Both retune files stay in the repo
  undeployed, **permanently — intended state, not drift. Stop reporting it.**
- ✅ **Gravship radius RESOLVED — the hold is lifted.** Measured live 2026-08-14 on
  PID 16112 via `jawa/get_def ThingDef GravFieldExtender`:
  `CompProperties_SubstructureFootprint.radius` = **30.0**,
  `CompProperties_GravshipFacility.maxDistance` = **34.0**, `maxSimultaneous` = **12**.
  **34.0 is the configured value from `Config/Mod_3522759531_GravshipSizeSettings.xml`,
  not the ~25.9 compiled default** ⇒ Bigger Gravships DID apply its settings this
  session, and the feared "built ship will not lift" case is disproven for the field
  the config names. **Building a ship is no longer blocked on this.**
  ⚠️ `GravEngine` reads radius **11.9**, maxDistance **5.9**, maxSimultaneous **1** —
  a different comp on a different building. **Do not quote it as "the engine radius"**
  until someone maps the mod's setting keys onto these comp fields; the two are not
  the same number and were never meant to be.
