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

## done 2026-09-20 — the art was already rendered, and he approved it on sight

No regeneration was needed. Three facings had been rendered **2026-09-19** under
`ROT_FLORA_FAUNA_VERDICTS_1` as `rot_mycoidcolossus_v2_{south,east,north}` at
2048x2048, all `status: ok`, and never wired to anything. They match his brief —
six-legged, purple hide, a grove of glowing lilac caps on the back — and they obey
the 2026-09-15 facing convention: south is the front with the head to camera, north
is the rear with no face, east is a clean profile. Owner, on the contact sheet:
*"That's a cool mycoid. I like it."*

Shipped at **1024x1024** from the 2048 masters:

- the sub-visible export halo (alpha 1-16, ~80,000 px per facing) was zeroed first —
  measured fringe 2.15% / 2.13% / 2.09% → 0.83% / 0.87% / 0.92%;
- downscaled with **premultiplied** alpha, so the cutout carries no dark halo;
- 1024 is a deliberate call, not a shortfall. At the ruled drawSize the 128 px/cell
  target lands past what the generator fills with real detail, so this ships at
  ~85 px/cell — the same call the sea-beast colossi shipped at.
- three distinct sha256s, so no facing is a copy of another.

Deployed and `VERIFIED in sync`. The override sits at index **608** in the live
`ModsConfig.xml` against `sarg.alphaanimals` at **409**, so it wins same-path
resolution.

⚠️ The three `rut_mycoidcolossus_v1_*` jobs I queued before finding the existing
renders were pulled; one (`_east`) was already running and its output is discarded.

## flagged for him, deliberately not fixed

🔴 **North draws about half again as tall as the other two facings.** MEASURED on the
shipped files: north's subject is 922x981 (aspect 0.94) against south 983x656 and
east 1003x671 (aspect ~1.50). RimWorld scales every facing into the same drawSize
box, so the creature will appear to change size as it turns — the same defect he
named on Anooba (*"North is HUGE compared to east"*). Recomposing north changes the
art, which is his call, so it stands as it is.

## not owed here

**Size 12 belongs to `ROT_SIZE_REJUDGE_APPLY_1`**, which applies all 11 re-judged Rot
sizes as one wave. 🔴 The live `bodyGraphicData.drawSize` is **4** — set 12 against 4,
not against the 15 in `df261b2bc`. ⚠️ Two owner notes disagree on the number: the Rot
verdict sheet said *"15 wide"* (which is what the art was drawn to) and the size
re-judge sheet said *"Size 12"*. The later note wins unless he says otherwise.

## the bigger question — needs the owner

⚠️ **One of 152 bulk-installed PNGs is provably mis-routed. The other 151 are
unverified.** A mis-route is only detectable by LOOKING: the art is valid, gate-passed
and correctly named — it is simply on the wrong creature.

🔑 A contact sheet of every stem from `cea007c3a` beside its creature's label would
find the rest in one pass. Not built — the owner has just finished one review sheet
and should choose whether to spend another sitting on this.
