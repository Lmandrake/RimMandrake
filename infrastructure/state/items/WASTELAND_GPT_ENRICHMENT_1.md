# WASTELAND_GPT_ENRICHMENT_1 — four GPT-suggested enrichments the owner picked

Source: a GPT enrichment consult (codex exec, gpt-5.6-sol xhigh, 2026-09-30) on the Wasteland. The
owner picked these four by question card. He declined all four knowledge and gods ideas (*"None of these
thanks."*: Waste Stratigraphy, Unburied Ledger, Crime Strata, Rootglass Vaults); Glass Choir and the
Jawa auctions were not picked either. Builds on `WASTELAND_RULED_CONTENT_1` and
`WASTELAND_MECHANICS_BUILD_1`, and must stay inside what the Wasteland sitting ruled.

## spec

1. **Named storms.** These give the two already-ruled storms their identities; the pass extends their
   WeatherDefs and does not add new storms.
   - **Deadlight Halo** arrives quietly: shadows double, instrument clicks accelerate, and a sickly
     light rims every pawn.
   - **Cinderwire Storm** is terminator-only. It begins with crawling static, levitating scraps and a
     deep electrical whine before its EMP, plasma and burial effects begin.

   Build: sky colours, overlays, motes and SoundDefs, plus a small C# phase controller that gives
   readable warnings, then hands off to the existing storm mechanics. **Model: sonnet.**
2. **Middenshell Procession.** Hours before arrival, the crust trembles and loose metal points toward
   one map edge. The 20-cell Middenshell (owner-ruled width; keep it, or report an engine ceiling)
   crosses on a slow, readable route. It grinds buildings and leaves hot footprints, shell flakes and
   minor bezoars. Waste stockpiles can divert it. If it exits, its trail and edge scar remain. Build: a
   large C# extension to TitanicCreatures' route and destruction wake, plus an XML incident, sounds,
   and footprint filth or terrain. **Model: opus.**
3. **Sealed Cask Bay.** A ship-bound bay accepts dangerous waste casks and clearly shows seal
   integrity, internal heat, stored dose and launch safety. Powered seals contain pollution. Processor
   animals can convert selected cargo into bricks or bezoars. Compound damage risks a visible leak.
   Build: XML building and cask defs, plus a medium C# containment comp tied to gravship membership and
   launch validation; use Harmony only if launch checks have no extension point. Settings cover
   capacity, leak severity and processing rate. **Model: opus.** ⚠️ This is a WASTE-cask bay. It is
   separate from `WARCASKET_CASK_BAY_AND_SARCOPHAGI_1` (the warcasket suit bay); give the two
   distinct defNames and labels.
4. **Rite of Tipping.** A Junker-supervised waste convoy offers silver and access rights if the colony
   licenses a marked dumping pad. Wildsteam may ask for evidence, and Deepwater may finance proper
   containment. Accepted casks remain physical objects that can leak, feed processors, enter the Cask
   Bay, or be illegally reburied. Build: QuestScriptDefs, an IncidentDef, cask items and faction
   rewards, plus a small C# dump-pad comp. **Model: sonnet.**

Each ships a Mod Settings toggle and tuning.

## criteria

- Each of the four is quicktest-proven.
- The Procession leaves a visible trail.
- A cask leak is visible and never silent.
