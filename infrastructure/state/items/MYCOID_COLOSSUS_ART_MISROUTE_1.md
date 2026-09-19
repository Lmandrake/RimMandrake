# MYCOID_COLOSSUS_ART_MISROUTE_1

## what happened

`src/RimUtinni/MycoidColossusArtOverride/` shipped a three-facing **droid** render —
rusty bipedal chassis, antenna head, exposed cabling, pincer hands — at
`Things/Pawn/Animal/AA_MycoidColossus/AA_MycoidColossus_<facing>.png`.

That is the live texPath of `AA_MycoidColossus` (label **vorrugath**, Alpha Animals),
MEASURED from the running game's `PawnKindDef.json`. Loose PNGs in a later-loading
mod win same-path resolution, and the mod was deployed, so **the creature rendered
as a droid in game**.

Installed by `cea007c3a` — *"Art-review platform: install every gate-passed render
awaiting verdict (95 stems)"* — a bulk install of **152 PNGs across ~40 ArtOverride
mods**. This stem was routed to the wrong creature.

Caught by the owner on the size re-judge sheet, 2026-09-19, verbatim:

> "What IS this graphic? Is this wired correctly? It's more like something we should
> keep for the Droidworks. Mycoid colossus is supposed to be a huge multi-legged
> purplish entity with glowing mushrooms sprouting from its back. Size 12."

## done

- The droid renders are **kept**, not deleted, at
  `src/RimStarWars/Droidworks/ArtIncoming/` with a README explaining their origin.
  They are wired to nothing.
- The three wrong PNGs are out of the override mod. The mod shell, `About.xml` and
  `LICENSE` stay, so there is no dangling `ModsConfig` entry and the regenerated art
  drops straight back in. `About.xml` says all this at the top.
- With no `Textures/` there, the donor's own colossus art wins again — wrong for the
  campaign, but strictly better than a droid.

## owed

1. 🔴 **Undeploy is NOT done.** The live copy at
   `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\MycoidColossusArtOverride\Textures\...`
   still holds the droid, and `deploy_custom_mods.py` does not auto-delete an
   already-deployed file that stops being shipped. Until it is removed by hand, the
   game still renders a droid. The game was cycling and another window held the
   bridge, so this was deliberately left.
2. **Regenerate the art** to the owner's brief: *a huge multi-legged purplish entity
   with glowing mushrooms sprouting from its back*. Three facings, at the same
   texPath. ⚠️ The art channel is refusing — Codex weekly quota resets **Mon
   2026-09-21 09:32**, which is what failed the other 82 jobs.
3. **Size 12.** His ruling on this row is `resize` with note `Size 12`. The live
   `bodyGraphicData.drawSize` is **4** — note that the earlier 15 from
   `df261b2bc` is NOT what the running game carries, so whoever applies this should
   set 12 against the measured 4, not against 15.

## the bigger question — needs the owner

⚠️ **One of 152 bulk-installed PNGs is provably mis-routed. The other 151 are
unverified.** A mis-route is only detectable by LOOKING: the art is valid, gate-passed
and correctly named — it is simply on the wrong creature.

🔑 A contact sheet of every stem from `cea007c3a` beside its creature's label would
find the rest in one pass. Not built — the owner has just finished one review sheet
and should choose whether to spend another sitting on this.
