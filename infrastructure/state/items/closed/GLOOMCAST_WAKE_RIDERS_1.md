# GLOOMCAST_WAKE_RIDERS_1 — which grazers ride the gloomcast's shadow, and what its feeding leaves

Split from `LONGSHADE_GPT_ENRICHMENT_1` §2 ("gloomcast moves shade", owner-picked by card
2026-09-30). The moving shadow itself is built: `RM_Gloomcast` throws real moving shade into the
shade grid (`RM_MovingShadeMath.cs`). Any shade-seeking animal can shelter in it, and an animal
standing in it counts as being in shade. The pirrik ride it again, now that the shadow-follow tree
runs ahead of the shade hop. Two parts of the picked line are unruled content:

> "pirrik and small grazers follow it; footfalls heard before it is seen; dung and feeding scars persist."

## open questions (the owner's)

1. **Which small grazers actively follow it.** Following is opt-in per race
   (`RM_ShadowFollowerExtension`). Without it, a grazer shelters in the shadow only when it happens
   to be near. Name the races (for example sollak, gennok or tebbra, all `RM_LongShade_Fillers.xml`).
2. **Feeding scars.** Dung already persists (`RM_Filth_Gloomcast`, 45–50 days), and filter-feeding
   leaves that same filth. Should the scar be a distinct mark, such as a churned-sand terrain or a
   separate filth with its own art, or is the dung enough?

## criteria

- The owner answers both. Then wire the named followers' extension, and the scar if one is wanted.

## verify
Ruled by card 2026-10-08; built 2026-10-09: `RM_ShadowFollowerExtension` (searchRadius 60, PROVISIONAL) on `RM_Chorn` (ex-sollak), `RM_Gennok`, `RM_Tebbra` in `RM_LongShade_Fillers.xml`. No new scar; dung (`RM_Filth_Gloomcast`) is enough. Toggle: Creature Behaviors "Shadow-following commensals".
- Offline: all three ThingDefs carry the extension (grep `RM_ShadowFollowerExtension` in the Fillers file = 3 + Pirrik).
- Live (owed, needs bridge): a spawned chorn/gennok/tebbra within 60 cells of a gloomcast gets the follow job (job-state read, not a screenshot).
