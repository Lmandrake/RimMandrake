# AGENT_OPS_state.md — where OPS is

## 🔴 PRE-BOOT WRAP 2026-08-13 ~23:2x — this section supersedes everything below

**Game was DOWN this whole session.** Bridge never taken, nothing left on any map.
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
- **Gravship radius unresolved** — Bigger Gravships set to 34 in
  `Config/Mod_3522759531_GravshipSizeSettings.xml` but bakes radii at **startup**.
  If this session's defs carry the ~25.9 defaults, **a ship built now will not lift
  and nothing logs why.** BRIDGE owes the `get_def GravFieldExtender` call.
  **Do not build a ship until settled.**
