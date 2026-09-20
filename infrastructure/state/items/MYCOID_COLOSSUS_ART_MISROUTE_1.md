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

1. **Regenerate the art** to the owner's brief: *a huge multi-legged purplish entity
   with glowing mushrooms sprouting from its back*. Three facings, at the same
   texPath `Things/Pawn/Animal/AA_MycoidColossus/AA_MycoidColossus_<facing>.png`.
   **QUEUED 2026-09-20** as `rut_mycoidcolossus_v1_{south,north,east}`, priority 100,
   1024x1024, no reference (this is a restyle, and a `reference=` would trigger
   reskin-validate against the wrong creature).

   🔴 **The art channel is NOT quota-blocked and never was blocked until Monday.**
   MEASURED from the newest manifest (`rut_firehawk_flying_5_south`, completed
   00:12 today): the codex **weekly** meter is at **42%** and resets **2026-09-26**.
   What was actually throttling it is the **5-hour** window at **86%** with the
   daemon `grumpy`, which clears within the 300-minute window — which is why 21
   older jobs are parked at priority 60-70 while these three sit at 100.

   ⚠️ Facings: each of the three carries its OWN surface language per the owner's
   2026-09-15 ruling — south is the front (face toward camera), north is the rear
   (no face, no eyes, the mushroom garden seen from behind), east is a side profile.
   The Rot v2 family's prompts do NOT do this — all three of `rot_agaripawn_v2_*`
   share one identical "Top-down pawn sprite, three facings" prompt, which is the
   exact defect `ARTPIPE_FACING_COHERENCE_1` exists for. Do not copy that family.

**Size 12 is NOT owed here.** His `resize` ruling on this row belongs to
`ROT_SIZE_REJUDGE_APPLY_1`, which applies all 11 re-judged Rot sizes as one wave.
🔴 Whoever applies it: the live `bodyGraphicData.drawSize` is **4** (MEASURED from the
running game's def data), so set 12 against 4 — the 15 in `df261b2bc` is not what the
running game carries. No drawSize patch for `AA_MycoidColossus` exists in `src/` today.

## undeploy — DONE, verified 2026-09-20

The live mod at
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\MycoidColossusArtOverride\`
holds exactly `LICENSE` and `About/About.xml` — no `Textures/` tree, no droid PNGs —
and its `About.xml` is byte-identical to the repo's. The game no longer renders a droid;
the donor's own colossus art wins until the regeneration lands.

## the bigger question — needs the owner

⚠️ **One of 152 bulk-installed PNGs is provably mis-routed. The other 151 are
unverified.** A mis-route is only detectable by LOOKING: the art is valid, gate-passed
and correctly named — it is simply on the wrong creature.

🔑 A contact sheet of every stem from `cea007c3a` beside its creature's label would
find the rest in one pass. Not built — the owner has just finished one review sheet
and should choose whether to spend another sitting on this.
