# FOG_REVIEW_SITTING_WITH_OWNER_1 — turn the fog off with him watching, tonight

Owner, 2026-09-02: *"I can't look at the fog, I'm remote right now, but we can do that
tonight. Good find. File a ticket about doing this with me live."*

## spec

**The find this exists to act on: CAI is not the fog.** He proposed dropping CAI 5000
for review passes. CAI 5000 (`krkr.rule56`, position 11 of 593) has its own fog **already
switched off** — `Mod_3673768803_CombatAIMod.xml` reads `FogOfWar_Enabled.15 = False`
and `FogOfWar_DisableOnPlayerMap.15 = True`. The fog comes from a *second* mod sitting
immediately after it at position 12: **`Mlie.NWNRealFogOfWar`** — "(NWN) Real Fog of War
(Continued)", workshop `3391128917`. CAI's own About.xml says the two are compatible
*provided CAI's fog is off*, which is exactly the configuration we are in.

⇒ Dropping CAI would cost the whole combat AI and remove no fog at all.

**⚠️ THE SWITCH IS NOT AN ENABLE/DISABLE FIELD.** Measured 2026-09-02 by decompiling
`3391128917\1.6\Assemblies\rimworld-mod-real-fow.dll` (ilspycmd): `RfowSettings` has **no
global on/off** — its 27 settings are all tuning (view ranges, `fogAlpha`, `fogFadeSpeed`,
`mapRevealAtStart`, hearing, audio muffling). The earlier line here claiming an
enable/disable field was an inference from a strings dump, and it was wrong.

**The switch that actually exists is `onlyOutsideColony`** — labelled *"Only show fog on
non-colony maps"* (`Languages/English/Keyed/Preference.xml`). It is a complete off switch
for colony maps, on BOTH halves of the mod, which is why it is the right one:
- `SectionLayerFoVLayer.Visible` returns false → the fog overlay is not drawn.
- `MapComponentSeenFog.IsShown` returns **true unconditionally** on a player-home map →
  `CompHideFromPlayer.hasPartShownToPlayer()` always passes, so nothing is hidden.
  `FoWThingUtils.FowIsVisible` short-circuits the same way.

✅ **MEASURED: it is LIVE, no restart.** Closing the settings window calls
`ModSettings.ExposeData` → `applySettings()` → `mapDrawer.RegenerateEverythingNow()` on
every map (`RfowSettings.cs:357-373, 408`). So this never becomes a profile, and the
`CHERRYPICKER_TWO_PROFILES_1` pairing is not needed for it.

⚠️ **One residue to watch when he looks.** The mesh regeneration redraws the fog; it does
not itself walk things back out of `CompHiddenable.Hidden`. A non-player thing already
hidden un-hides on its next `UpdateVisibility` (position change or force check), so a
few may linger invisible until something nudges them. If that shows, a save/load of the
map settles it — it is not the toggle failing.

**What to do, with him at the bench:** Options → Mod settings → *(NWN) Real Fog of War
(Continued)* → tick **"Only show fog on non-colony maps"** → close the window. Then he
looks. The question is only ever answerable by his eye: *is a review pass legible now?*

**No `Mod_3391128917_*.xml` exists**, so the mod has never been opened and is running its
shipped defaults — fog on. Closing the settings window once will create that file.

## verify
He looks at a map with the toggle off and says whether it is reviewable. Nothing else
settles it; a screenshot of fog is still fog.

## criteria
A review pass can be run on a map he can actually see, without giving up CAI's combat
AI, and we know whether the toggle costs a restart.
