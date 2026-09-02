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

**What to do, with him at the bench:**
- NWN exposes its own toggle in the mod-settings window (its DLL carries `RfowSettings`
  with an enable/disable field and a `DoSettingsWindowContents`). **No
  `Mod_3391128917_*.xml` exists**, so the mod has never been opened and is running its
  shipped default — for a fog mod, fog-on.
- ⚠️ UNMEASURED: whether the toggle takes effect live or needs a restart. The field
  reads like a per-frame render check rather than a Harmony install gate, which usually
  means live — but that is an inference, not a reading. Budget for a restart.
- He looks. The question is only ever answerable by his eye: *is a review pass legible
  now?*

**If it is live**, this is free and the answer is a settings toggle flipped per pass. **If
it needs a restart**, it becomes a profile the way the Cherry Picker cut list did
(`CHERRYPICKER_TWO_PROFILES_1`) — and the two should then be flipped together, since a
review pass wants both no fog and no cuts.

## verify
He looks at a map with the toggle off and says whether it is reviewable. Nothing else
settles it; a screenshot of fog is still fog.

## criteria
A review pass can be run on a map he can actually see, without giving up CAI's combat
AI, and we know whether the toggle costs a restart.
