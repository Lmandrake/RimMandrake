# JawaIonWeapons — PROVEN WORKING, live, 2026-08-13

**Map: QUICKTEST, not the campaign.** Jungle biome, 250×250, paused throughout
(`ticksGame` 1, TPS 0.0). The campaign save was never opened.

## ✅ The result

**15 points of `JawaIon_Damage` downed a KotOR droid without killing it.**

| | |
|---|---|
| target | `KotORDroidGood_3C` — "3C-T0", id `guy762_DroidRace_3Cseries52567` |
| race | `guy762_DroidRace_3Cseries`, `intelligence: Humanlike`, `fleshType: ABF_FleshType_Synstruct_Base` |
| before | `downed=False stunned=False dead=False` |
| **after 15 dmg** | **`downed=True`, `dead=False`, pawn still on the map** |
| evidence | `observed/evidence/2026-08-13_ion_downs_kotor_droid.png` — droid toppled on its side, alive |

That is the full assertion the queue asked for: **effect applied, pawn downed,
pawn NOT destroyed.** One shot was enough; the 8-shot ladder never got past step 1.

🔴 **Why this test had to exist at all.** `JawaIonWeapons.dll`'s user-string heap
is **4 bytes, all zero** — the assembly cannot emit a log message even in
principle, and `Apply()` has four unlogged early returns. **Today's load harvested
completely green and that was never evidence of anything.** A screenshot is the
only proof this weapon can produce, which is why it is committed beside this file.

## Two false negatives I nearly published, both caught before reporting

**1. `jawa/damage` takes `thingId`, NOT `targetId`.** My first run fired six
"shots" and reported `downed=False` each time. **None of them landed** — the tool
was refusing the whole time. Had I stopped there I would have filed "ion weapon
does nothing" against a weapon that works on the first hit.
⚠️ The refusal is easy to miss: the JSON-RPC envelope reads
`"Status": 2, "Success": true` while the payload reads
`"success": false, "message": "Give either thingId, or both x and z."`
**The envelope describes the CALL; the payload describes the ACTION.** Read the
inner one.

**2. The first spawn "succeeded" then the pawn vanished.** A humanlike pawn with
`faction=none` spawned once, then was gone by +300 ticks. Every later attempt
NRE'd. Do not read the one success as proof the pairing is legal.

## 🔴 Separate real finding: `KotORDroidBad_*` cannot be spawned at all

`KotORDroidBad_KM1MD` **NREs in the pawn generator in every faction tried** —
`none`, `player`, and its own default `guy762_KotORFaction_RogueDroids`:

```
"error": "NullReferenceException", "factionHasIdeo": false
```

The companion's guard also refuses its **own default faction** outright:
> *Refusing to spawn humanlike kind 'KotORDroidBad_KM1MD' into non-humanlike
> faction 'guy762_KotORFaction_RogueDroids'.*

**So this pawnkind is Humanlike while its own default faction is not** — the mod
ships a pairing RimWorld's generator cannot satisfy. `KotORDroidGood_3C` spawns
fine, so it is **not** the whole family.

**Not chased further** — it is a KotOR-mod defect, it did not block the ion test,
and `guy762_KotORFaction_RogueDroids` is a KEEP faction whose raids may hit it.
Worth knowing before a raid from that faction is expected to work.

## Map state left behind

One downed `KotORDroidGood_3C` at **(60,60)**, faction none, alive. Debug log
window **closed by me** (it had auto-opened, full of stale 17:40:17 load lines —
it obscured the first screenshot entirely). Camera left at (60,60). Game still
paused. Nothing else spawned, no terrain written, campaign untouched.

---

# Art-fix visual check — 2026-08-13, same quicktest map

**2 of 8 confirmed rendering. Not 8. Stated as measured.**

| mod | subject | facing | verdict |
|---|---|---|---|
| `gravshipastronautfix` | `VGE_Astronaut` | north | ✅ **real art** — cream helmet, visor slot, lavender shoulders |
| `msedroidfix` | `OuterRim_MSEDroid` | north | ✅ **real art** — black keyline, two tonal bands, panel lines |
| `sauridfrillfix` | `VRESaurids_TownGuard_Saurid` | north | ⬜ captured, not adjudicated |
| `cereanmanefix` | `OuterRim_Cerean` | south | ⬜ captured, not adjudicated |
| `toolbeltfix` · `researchkiteastfix` · `blastdoorframeasyncfix` · `desertvehiclereskin` | — | — | ⬜ **not attempted** |

**What a pass here does and does not mean.** It means a sprite with authored
detail draws at that facing — not RimWorld's blank/`BadTexture` placeholder. It
does **NOT** mean the fix mod supplied it: `GravshipAstronautFix` and
`SauridFrillFix` were shadowed all session by `Jawa_Patches`' md5-identical
copies at the same paths, and **textures bind at startup**, so the pruned game
copy only takes effect next launch. **"The art is right" and "this mod supplied
it" are different claims** and only the second needs a restart.

## 🔴 Two measurement traps that each nearly produced a false verdict

**1. `rootSize 6` renders the entire map FLAT RED.** Reachable only because the
camera-zoom extension was on. My first pass looked like catastrophic texture
corruption across every mod, and it was escalated as such by a peer. It is a
**zoom artifact**: the red frame is bracketed by clean frames 29 s either side
and healed on its own when zoom returned to a legal range.
⭐ **The discriminator is FILE SIZE** — the red frame is **0.49 MB** against
**2.4–3.7 MB** for the clean ones, because flat colour compresses to almost
nothing. A corrupted atlas does not heal in place; a zoom artifact does.

**2. `take_screenshot` names files by SECOND.** Four shots inside one second
overwrote each other down to a single file, and **every call returned
`success: true` with a path**. Space captures ≥1.3 s apart, or verify the paths
differ before believing you have N images.

⚠️ **A pawn moved between shots** — the MSE droid was spawned at (36,210) and
photographed at (32,210). The map is not as static as `TPS 0.0` suggests.
