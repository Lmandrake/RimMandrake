# EXPECTED_FAILURES_next_load.md — the three assemblies, written BEFORE the load

**Written 2026-08-13 by OPS, game DOWN. For: the NEXT cold load** (the first load
after the three-assemblies batch, i.e. the one that follows the 2026-08-13 10:05
companion deploy). Queue item **O5**, ruled LIVE by the owner.

**Why this file exists.** The owner granted the three-assemblies waiver
(`TODO.md` §7, "the waiver STANDS. Batch it.") on one mandatory condition: *write
the three expected-failure signatures down before launching.* A signature invented
after reading the log is not evidence, it is a story that fits. This is that
document. **Do not edit the signatures below after the log exists** — append
results underneath instead.

⚠️ **A clean log proves NOTHING here.** Two of the three assemblies emit zero
bytes to `Player.log` in any state. For those, the positive sighting is the whole
test.

---

## The three, and their deploy state (all verified on disk 2026-08-13, game down)

| # | assembly | deployed to | size | mtime | state |
|---|---|---|---|---|---|
| A1 | `JawaBench.BridgeTools` | `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\JawaBench.BridgeTools.dll` | 154,112 B | 2026-08-13 10:05 | byte-identical to repo artifact |
| A2 | `JawaIonWeapons` | `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\JawaIonWeapons\Assemblies\JawaIonWeapons.dll` | 5,120 B | 2026-08-12 21:53 | md5 `b72cade88872860ab36206c1e01cccae`, identical to repo |
| A3 | `OuterRimGalacticEmpire` | `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2919248699\1.6\Assemblies\OuterRimGalacticEmpire.dll` | 10,752 B | 2026-08-12 16:06 | Workshop, **1.6 folder** — matches the 10,752 B recorded in `TODO.md:216` |

**All three are already on disk. None needs a shutdown window.** The 1.4 and 1.5
copies of A3 are 10,240 B; only the 1.6 one is 10,752 B, so 1.6 is what loads.

**Log path for every grep below:**
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log`

```bash
LOG="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
```

---

# A1 — `JawaBench.BridgeTools` (BRIDGE's companion, 17 tools)

**What it is.** Not a RimWorld mod — it ships no `About.xml` and RimWorld's mod
loader never sees it. `RimBridgeServer` scans the game-root `BridgeTools\` folder
late in startup and registers the `[Tool("jawa/...")]`-attributed static methods
off `JawaBench.BridgeTools.JawaBenchTerrainTools`. One source file, 2,415 lines,
zero Harmony, zero `Log.*`, zero `throw`.

**17 tools, VERIFIED by scanning the deployed DLL's string heaps:**

```
jawa/damage        jawa/destroy_batch  jawa/drain_log      jawa/fire_incident
jawa/get_def       jawa/get_roof_batch jawa/get_terrain_batch
jawa/list_factions jawa/list_pawns     jawa/refresh_rect   jawa/send_letter
jawa/set_plants    jawa/set_roof_batch jawa/set_terrain    jawa/set_terrain_batch
jawa/spawn_batch   jawa/spawn_pawn
```

## ✅ EXPECTED SUCCESS — the positive sighting (do this FIRST)

**Nothing in `Player.log` proves A1 works.** The census is the test:

```bash
python.exe src/RimMandrake/bridgetools/prove_new_tools.py
```

Read line 0, the deploy census. **The number to see is 17.**

| census reads | meaning |
|---|---|
| **17** | ✅ the 2026-08-13 10:05 `--gm` build is live. A1 PASSES. |
| 16 | pre-`list_factions` build — deploy did not take |
| 14 | pre-roof build |
| 7 | the old seven, i.e. a stale companion the deploy could not overwrite |
| 0 | RimBridgeServer never loaded the bundle at all |

🔴 **PRE-EMPT THIS FALSE ALARM.** `prove_new_tools.py:79-85` `ALL_TOOLS` lists only
**16** entries — it predates `jawa/list_factions`. So on a *correct* deploy the
script prints a **FAIL**: `all 16 companion tools registered   17 of 16`. **That
FAIL is the pass.** 17-of-16 = healthy. Do not "fix" the deploy on the strength of
it, and do not fix the script during the load — note it and move on.

Second, cheaper positive: `rimbridge/get_bridge_status` → `companions.diagnostics`
carries `companionCount` / `companionWarningCount` / `companionErrorCount`.
Want `companionErrorCount = 0` and a non-zero `companionCount`.

## ❌ EXPECTED FAILURE SIGNATURES

**A1 is the one of the three that CAN fail loudly** — the host reports on the
companion's behalf. All strings below are **VERIFIED** in the `#US` heap of
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3727949765\1.6\Assemblies\RimBridgeServer.dll`.
`{0}` etc. are .NET format placeholders — grep the literal prefix, not the braces.

| signature (VERIFIED) | means |
|---|---|
| `[RimBridge] Failed to load companion assembly '` | the DLL is corrupt or targets the wrong framework |
| `[RimBridge] Failed to scan companion assembly '` | loaded but reflection over it threw |
| `[RimBridge] Loader exception while scanning companion assembly '` | a referenced type is missing — usually an SDK mismatch |
| `[RimBridge] Failed to inspect companion tool type '` | `JawaBenchTerrainTools` found, attribute read failed |
| `[RimBridge] Failed to prepare companion tool type '` | tool methods found, instantiation failed |
| `[RimBridge] Skipping companion tool type '` | type rejected — the follow-on fragment is `' has instance tool methods but no public parameterless constructor.` |
| `[RimBridge] Could not resolve global BridgeTools folder: ` | the game-root `BridgeTools\` folder was not found at all |
| `[RimBridge] Failed to register annotated extension provider '` | registration itself failed |
| `[RimBridge] Ignoring companion-local SDK copy '` | a stray `RimBridgeServer.Sdk.dll` shipped beside ours. Follow-on: `'. Companion tools must bind to the SDK shipped by RimBridgeServer.` |
| `Companion references RimBridgeServer.Sdk ` | SDK version drift. Follow-on fragments: `, but the running host provides ` and `. Rebuild/redeploy the companion and restart RimWorld if tool calls fail.` |
| `[RimBridge] STARTUP_INIT_FAILURE: ` | the bridge itself did not come up — A1 is untestable, not failed |
| `[RimBridge] Failed to start server: ` | same; nothing bridge-side is measurable this load |

**One-shot grep — paste this:**

```bash
grep -nE "\[RimBridge\] (Failed to (load|scan|inspect|prepare|register)|Loader exception|Skipping companion|Could not resolve global BridgeTools|Ignoring companion-local SDK|STARTUP_INIT_FAILURE|Failed to start server)|Companion references RimBridgeServer\.Sdk" "$LOG"
```

**Want: zero lines.** Then confirm the bridge came up at all:

```bash
grep -nE "\[RimBridge\] (GABP server running standalone|Startup conditions satisfied|STARTUP_TIMING phase=tools\.register-extensions)" "$LOG"
```
*(All three were present in the 2026-08-13 07:55 baseline log, lines 5794/5805/5811.)*

## Silent-failure mode

🔴 **YES — the commonest A1 failure is silent.** Windows keeps the companion
memory-mapped for the life of the process, so a deploy attempted while the game
runs *cannot* write the file and **nothing anywhere says so**. The host then loads
the OLD companion cleanly, logs nothing, and every `[RimBridge]` line above stays
absent. **This is why the census, not the log, is the A1 gate.** The deploy at
10:05 was in a shutdown window and byte-verified, so this should not bite — but
17-vs-16-vs-7 is what settles it.

Also silent by design: every in-tool error is a JSON `{success:false, message:...}`
payload, never a log line. A tool that *runs* and refuses tells you in the reply.

---

# A2 — `JawaIonWeapons` (OPS's ion rebuild)

**What it is.** One class, `JawaIonWeapons.DamageWorker_IonBuildup`, wired in
purely from XML — `Defs/DamageDefs_JawaIon.xml:60`
`<workerClass>JawaIonWeapons.DamageWorker_IonBuildup</workerClass>`. **No Harmony
at all**; the assembly references only `mscorlib` and `Assembly-CSharp`. It exists
because `additionalHediffs` is only read by `DamageWorker_AddInjury.ApplyDamageToPart`,
which a `StunBase`-derived def never reaches — so the XML block was inert and the
worker hand-applies it.

**The rebuild being tested is the guard fix.** `Source/DamageWorker_IonBuildup.cs:92`:

```csharp
if (pawn.RaceProps == null || pawn.RaceProps.IsMechanoid)
```

`IsMechanoid` is the *post-fix* guard (`CLOSED.md:37`, W8). The old wrong version
was `!pawn.RaceProps.IsFlesh`, which `Jawa_Doctrine/Patches/DroidsAreMachines.xml`
(`isOrganic:false`) silently inverted. **VERIFIED in the deployed IL**: `Apply`
IL_0033 is `callvirt RaceProperties::get_IsMechanoid`, and `get_IsFlesh` appears
nowhere in the DLL.

Defs it owns: `JawaIon_Damage` (DamageDef), `JawaIon_Stun` (HediffDef),
`JawaIon_Bullet` + `JawaIon_Blaster` (ThingDefs), `JawaIon_Weaponry` (ResearchProjectDef).

## ✅ EXPECTED SUCCESS — the positive sighting

**This is the live check already queued as `NEXT_RELOAD.md` §"Live checks" row 1
(Ion vs a KotOR droid). It is the ONLY thing that proves A2.**

```
jawa/spawn_pawn  kindDef=KotORDroidBad_KM1MD  faction=hostile
jawa/damage      JawaIon_Damage, repeatedly   (W8 needed 14 applications — `amount` is a request, not a delivery)
jawa/list_pawns  -> read the droid back
```

| must see | value |
|---|---|
| `JawaIon_Stun` hediff **present** on the droid | severity climbing past 0.35 → 0.65 → 0.9 |
| at severity ≥ 0.9 | `downed: true` |
| the pawn | **still exists** — not a corpse, not destroyed |

⚠️ Severity stuck at **0.0** = the guard is wrongly blocking it. That is the exact
failure the rebuild was meant to fix.

⚠️ `ABF_FleshType_Synstruct_Base` is a **third** flesh def, never tested, and it
ships `CorpsesMechanoid`. If the downed KotOR chassis resolves as a *corpse*
rather than a capturable pawn, the capture-and-upgrade loop is dead while every
static check still looks green. Watch for a corpse.

**Offline confirmation, cheap, do it while the game loads:** the def dump must show

```
JawaIon_Damage.workerClass == JawaIonWeapons.DamageWorker_IonBuildup
```

## ❌ EXPECTED FAILURE SIGNATURES

🔴 **The assembly contains ZERO strings.** VERIFIED at the binary level: the DLL's
`#US` (user-string) heap is **4 bytes, all `0x00`** — the assembly has no user
strings whatsoever, so it is incapable of logging anything. `About.xml:15` states
this deliberately: *"It contains no Log calls, so it is SILENT whether it works or
not — a clean log is not evidence about it either way."*

Every signature below therefore comes from **RimWorld's own** error shapes, not
from the mod. Marked accordingly.

| signature | verdict | means |
|---|---|---|
| `Could not find type named JawaIonWeapons.DamageWorker_IonBuildup` | **PREDICTED** (RimWorld def-loader shape) | the DLL did not load, or the type name drifted |
| `Exception loading def from file DamageDefs_JawaIon.xml` | **PREDICTED** (RimWorld shape, confirmed as a real family in `vendor/wisdom/benign_log_errors.md:81`) | the def failed to parse at all |
| `Could not resolve cross-reference: No Verse.HediffDef named JawaIon_Stun found` | **PREDICTED** (shape verified verbatim at `benign_log_errors.md:96`) | the hediff def did not load |
| `Could not resolve cross-reference: No Verse.ThingDef named JawaIon_Bullet found` | **PREDICTED**, same shape | the bullet def did not load |
| `NullReferenceException` in a stack naming `Verse.DamageDef.get_Worker` or `DamageWorker_IonBuildup.Apply` | **PREDICTED**, but the mechanism is **VERIFIED**: `Verse.DamageDef::get_Worker` in the game's own `Assembly-CSharp.dll` is `ldfld workerClass` → `Activator::CreateInstance` → `castclass DamageWorker`, with **no null check**. A null `workerClass` throws on the first shot. | fires on the first ion bolt |

**One-shot grep — paste this:**

```bash
grep -nE "JawaIon|DamageWorker_IonBuildup|jawaionweapons" "$LOG"
```

**Want: exactly one hit** — `  - mandrake.jawaionweapons` in the active-mod list
(that was line 6707 of the 2026-08-13 baseline log). **Any second hit is the
failure.** Then:

```bash
grep -nE "Could not find type named JawaIonWeapons|Exception loading def from file DamageDefs_JawaIon|No Verse\.(HediffDef|ThingDef|DamageDef) named JawaIon" "$LOG"
```

## Silent-failure mode

🔴 **YES, and A2 is the worst of the three.** `Apply` has **four early `return`
paths** — null/dead pawn, mechanoid, null `additionalHediffs`, zero severity — and
**not one of them logs anything**. In that state the ion blaster behaves like a
plain EMP stun gun with no buildup, and `Player.log` is spotless. **This is exactly
the regime the old `!IsFlesh` bug lived in for days.**

**So for A2 the log is not evidence in either direction. The live droid test is
the ONLY gate. If it is not run, A2 is UNVERIFIED — do not record it as passed.**

---

# A3 — `OuterRimGalacticEmpire` (the adopted Empire module)

**What it is.** The smallest of the three and nearly inert: 5 source files, ~200
lines. A `Verse.Mod` subclass (`OuterRimGalacticEmpireMod`), a `ModSettings` with
8 bools, **exactly one Harmony patch** — a `[HarmonyPostfix]` on
`OuterRimCore.OuterRimCoreMod.DoOptionsCategoryContents` that appends to the
settings UI — and one unused custom `PatchOperation`. **No ThingComp, no
IncidentWorker, no GameComponent, no def classes.** Everything the mod actually
ships is XML. The Occupation / Inquisitor / flyover / tax systems named in the
settings strings are commented out in source.

Harmony ID (**VERIFIED** in IL at `.ctor` IL_0091): `Neronix17.OuterRim.GalacticEmpire`.
Built against `Assembly-CSharp 1.6.9293` — a genuine 1.6 build, not a 1.5 carry-over.

⚠️ **Use the Workshop tree, not `vendor/mod_sources/`.** The vendor snapshot ships
1.4/1.5 only, is a different build with a different logging path, and will predict
the wrong log output. It is not what the game loads.

⚠️ **Two hard runtime dependencies are UNDECLARED** — neither is in
`<modDependencies>`, which lists only `Neronix17.OuterRim.Core`:
- **`TabulaRasa`** (ships in `neronix17.toolbox`) — the assembly references it and
  calls `TabulaRasa.SettingsUtil::Note`; `FactionDefs.xml` uses
  `Class="TabulaRasa.PawnGroupMaker_Temperature"` and
  `Class="TabulaRasa.DefModExt_FactionExtension"` with **no `MayRequire`**.
- `OuterRimCore.OuterRimCoreMod.DoOptionsCategoryContents` must still exist for
  `PatchAll` to succeed.

Both are satisfied on this install and in the right load order — `neronix17.toolbox`
at `ModsConfig.xml:518`, `neronix17.outerrim.core` at `:534`,
`neronix17.outerrim.galacticempire` at `:550`. **That is the fragile link if the
Workshop updates anything.**

## ✅ EXPECTED SUCCESS — the positive sighting

🔴 **A3 has a real, verbatim, single-line success marker — the only one of the
three that does.** VERIFIED present at **line 716** of both the current
`Player.log` and the harvested `2026-08-13 07:55` baseline:

```
<color=#00FFFFFF>:: Outer Rim - Galactic Empire :: </color>1.6.9308 ::
```

It is emitted by `Log.Message` at the very top of the mod constructor
(`OuterRimGalacticEmpireMod.cs:36`), **before** `Harmony.PatchAll`. The `1.6.9308`
suffix tracks `AssemblyVersion` and will change if the Workshop item updates.

```bash
grep -n "Outer Rim - Galactic Empire" "$LOG"
```

**Want: exactly one line, and the version to still read `1.6.9308`.**

⚠️ **The banner alone is NOT sufficient.** It prints before `PatchAll`, so it can
appear on a load where the Harmony patch then throws. Pair it with the failure
grep below.

Second positive, defs — these are the sighting targets for "the faction is live":

| def | defName |
|---|---|
| FactionDef | `OuterRim_GalacticEmpire` |
| player FactionDef | `OuterRim_EmpirePlayerFaction` |
| basic member PawnKind | `OuterRim_ImpStormtrooper` |
| leader PawnKind | `OuterRim_ImpStormCommander` |

Live: `jawa/list_factions` must return `OuterRim_GalacticEmpire`, and
`jawa/get_def PawnKindDef OuterRim_ImpStormtrooper` must resolve. That closes
`NEXT_RELOAD.md` "Live checks" row 3 (trooper ladder). The rest of the ladder:
`_Officer`, `OuterRim_ImpStormArty`, `_ImpStormJump`, `_ImpStormIncinerator`,
`_Desert`, `_Snow`, `OuterRim_ImpStormScout`, `OuterRim_ImperialOfficer`,
`OuterRim_ImpISBAgent`.

## ❌ EXPECTED FAILURE SIGNATURES

**The assembly's ENTIRE user-string heap is 18 strings, dumped VERIFIED. Only two
can ever reach the log**, and one of them is dead code. Everything else below is a
RimWorld/Harmony shape.

| signature | verdict | means |
|---|---|---|
| **absence** of `:: Outer Rim - Galactic Empire ::` | **VERIFIED** marker | the mod class never constructed — the hardest failure, and it shows as a missing line, not an error |
| `HarmonyException` naming `Patch_OuterRimCoreMod_Settings` or `DoOptionsCategoryContents` | **PREDICTED** (Harmony shape) | Outer Rim - Core renamed/removed the patch target |
| `ReflectionTypeLoadException` naming `TabulaRasa` | **PREDICTED** (shape verified as a real family at `traps-mods-and-managers.md:60`) | `neronix17.toolbox` disabled or updated — the undeclared dep |
| `Could not find type named TabulaRasa.PawnGroupMaker_Temperature` | **PREDICTED** (RimWorld XML shape) | same cause, seen from `FactionDefs.xml` |
| `Could not find type named TabulaRasa.DefModExt_FactionExtension` | **PREDICTED**, same | same |
| `Could not resolve cross-reference: No Verse.PawnKindDef named OuterRim_ImpStormtrooper found` | **PREDICTED** (shape verbatim at `benign_log_errors.md:96`) | the pawnkind defs did not load; the faction has no members |
| `Configuration error in patch, { settings[i]} is not an existing setting in this mod. This can only check existing boolean settings.` | 🔴 **VERIFIED verbatim** in the `#US` heap, including the author's broken interpolation — the missing `$` means `{ settings[i]}` prints **literally** | dead code. The mod as shipped cannot emit it. If you see it, someone added a `PatchOperation_SettingActive` to the XML. |

**One-shot grep — paste this:**

```bash
grep -nE "Outer Rim - Galactic Empire|OuterRimGalacticEmpire|Patch_OuterRimCoreMod_Settings|TabulaRasa|OuterRim_GalacticEmpire|OuterRim_ImpStorm" "$LOG"
```

**Want:** the banner line, the `  - Neronix17.OuterRim.GalacticEmpire` mod-list
entry (line 6688 of the baseline), **and nothing else**.

## Silent-failure mode

**Mostly LOUD — A3 is the safest of the three.** The banner is a genuine positive
sighting and both realistic breakages (Harmony target gone, TabulaRasa gone) throw
named exceptions.

**The one silent path** is the *absence* of the banner: if the mod class never
constructs, nothing red is guaranteed, and the only tell is a line that is not
there. That is why the grep above is a **positive** check, not a negative one —
run it looking for a hit, not for silence.

Second silent path, XML-only and outside the assembly: the defs load, the faction
exists, and **it simply never generates a settlement**. `OuterRim_RebelAlliance`
did exactly this (`queue/OPS.md:76`, `:133`) — configured, present, did not
generate. So "the faction resolves" ≠ "the Empire is in the world". Confirm on the
world map, not in the def list.

---

## Attribution at a glance — the property the waiver was granted on

The batch is only affordable because the three fail in **different places**:

| | A1 BridgeTools | A2 JawaIonWeapons | A3 GalacticEmpire |
|---|---|---|---|
| **fails as** | a tool missing from `tools/list` | a droid that stuns but never downs | a missing faction / missing stormtroopers |
| **loud in Player.log?** | **partly** — host-side `[RimBridge] Failed to …` covers type-scan failures | 🔴 **NO — never, in any state.** 0-byte string heap | **mostly yes**, plus a verbatim success banner |
| **own log strings** | 0 | **0** (`#US` heap is 4 bytes, all zero) | 2, one of them dead code |
| **the real gate** | `prove_new_tools.py` census = 17 | the live KotOR droid test | the banner at log line ~716 + the faction on the world map |
| **worst case** | stale DLL loads cleanly, deploy silently never happened | early `return`, gun acts like a plain EMP stunner, log spotless | banner absent — a line that is not there |

**No two of the three can produce the same evidence.** If exactly one gate fails,
attribution is unambiguous.

---

## 5-minute execution order

```bash
LOG="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
```

1. **A3, positive** — `grep -n "Outer Rim - Galactic Empire" "$LOG"`. **Want one
   hit** reading `1.6.9308`. Absence = A3 failed.
2. **A1, negative** — the `[RimBridge]` one-liner. Want **zero** lines. Then the
   three `[RimBridge]` startup lines present.
3. **A2, negative** — `grep -nE "JawaIon|DamageWorker_IonBuildup|jawaionweapons" "$LOG"`.
   Want **exactly one** hit: the mod-list entry.
4. **A3, negative** — the `TabulaRasa` / `Patch_OuterRimCoreMod_Settings` one-liner.
5. **A1, gate** — `python.exe src/RimMandrake/bridgetools/prove_new_tools.py`;
   census must read **17**. It prints this as a FAIL (`17 of 16`) — **that FAIL is
   the pass.**
6. **A2, gate (live, the only proof)** — spawn `KotORDroidBad_KM1MD` hostile, apply
   `JawaIon_Damage` ~14×, confirm `JawaIon_Stun` severity climbs to ≥0.9,
   `downed: true`, **and the pawn still exists** (not a corpse).
7. **A3, gate (live)** — `jawa/list_factions` returns `OuterRim_GalacticEmpire`;
   `OuterRim_ImpStormtrooper` resolves; and a settlement actually exists on the
   world map.

🔴 **Anything unrun stays UNVERIFIED. An unrun check is not a pass, and for A2 a
clean log is not evidence in either direction.**

---

## Results — fill in AFTER the load, do not edit anything above

| assembly | log grep | live gate | verdict |
|---|---|---|---|
| A1 BridgeTools | | | |
| A2 JawaIonWeapons | | | |
| A3 GalacticEmpire | | | |
