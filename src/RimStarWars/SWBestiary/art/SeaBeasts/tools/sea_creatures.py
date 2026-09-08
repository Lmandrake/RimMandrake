#!/usr/bin/env python3
"""The 18 sea beasts as an art table: slug, approved mockup, canvas, treatment.

Names/bodySize come from design/Jawa/worldbuilding/sea_beasts_roster.md (RULED,
owner 2026-08-31 + the 2026-09-02 renames); drawSize from
design/Jawa/worldbuilding/sea_beasts_def_spec.md section 5. Nothing here is
invented: `treat` describes the mockup the owner KEPT, which is the approved
concept and must not be reinterpreted.

canvas = next power of two at or above drawSize x 128 (owner's 2026-08-23
ruling), CAPPED AT 1024: the image model returns ~1.5 Mpx natively, so a 2048
canvas would be an upscale of art that does not contain 2048px of detail.
The three colossi therefore ship at 85-96 px/cell rather than 128.
"""

MOCKUPS = "/mnt/d/Luke/dev/Rimworld/src/RimStarWars/SeaBeasts/art/mockups"
FINAL = "/mnt/d/Luke/dev/Rimworld/src/RimStarWars/SeaBeasts/art/final"
RAW = "/mnt/d/Luke/dev/Rimworld/Transient/sea_raw"


def canvas_for(draw_size: float) -> int:
    # Floor 256: the skill's own table allows 128 OR 256 at drawSize 1.0, and
    # the source art is ~1500px, so 256 costs nothing that isn't already paid
    # for and keeps the small fish from going blocky when a player zooms.
    want = draw_size * 128.0
    n = 256
    while n < want and n < 1024:
        n *= 2
    return n


# slug -> (mockup stem, drawSize, treatment sentence)
CREATURES = {
    "OpeeSeaKiller": ("opee_opt1", 2.25,
        "a brown-and-olive armoured angler-crab: heavy spiny carapace with a "
        "sawtooth dorsal ridge, enormous round maw ringed with cream needle "
        "teeth, two pale bulb lure stalks on curling antennae above the jaw, "
        "rows of small hooked crab legs beneath, broad fan tail, mottled "
        "warm brown shell with a hard black outline"),
    "CrimsonOpee": ("opee_opt2", 2.48,
        "a rust-red barnacled angler-crab: ridged orange-red plate carapace "
        "with a sawtooth dorsal ridge, huge hinged maw of cream needle teeth "
        "with a long wet pink adhesive tongue extended, three pale bulb lure "
        "stalks on curling antennae, many hooked crab legs, spiked fan tail, "
        "warm rust and coral palette with a hard black outline"),
    "ShaleGorger": ("opee_opt3", 2.69,
        "a slate-grey armoured benthic gorger: smooth layered volcanic-rock "
        "plates in overlapping bands like a giant woodlouse, a wide "
        "tooth-ringed maw of pale needle teeth at the blunt front, one pale "
        "blind white eye, short stubby legs tucked beneath, no lure stalks, "
        "charcoal and gunmetal palette with a pale grey underbelly and a hard "
        "black outline"),
    "ColoClawFish": ("colo_opt1", 3.29,
        "a pale cave eel: long ribbon body of white and lavender segments, "
        "flat spade-shaped head, a fan of fine whisker barbels around the "
        "jaws, huge fanged mouth, two clawed pectoral limbs at the shoulders, "
        "trailing violet tail fin, ghost-white with cool violet shading and a "
        "hard black outline"),
    "AbyssalColo": ("colo_opt2", 3.60,
        "a deep-trench eel: grey-green sinuous ribbon body with rows of "
        "glowing cyan spots along both flanks, wide flattened arrow head, "
        "unhinged fanged jaw, glowing teal barbels streaming back, hooked "
        "pectoral claws, teal-edged fins, cold grey-green palette with "
        "luminous teal accents and a hard black outline"),
    "ThornbackColo": ("colo_opt3", 3.06,
        "a spined shallows eel: bone-white and deep purple, hatchet-shaped "
        "armoured skull plate, cavernous fang-lined mouth, pale glowing lure "
        "whiskers, a ridge of dark thorny spines running the length of the "
        "muscular serpent body, ragged violet fins, bone and aubergine "
        "palette with a hard black outline"),
    "SandoAquaMonster": ("sando_opt1", 7.11,
        "a grey-blue swimming leviathan: muscular four-limbed body, broad "
        "feline-reptilian skull with a fanged maw, webbed clawed paws, a "
        "ridge of spine fins down the back, long finned tail, slate grey-blue "
        "hide with a pale underbelly and a hard black outline"),
    "ElderSando": ("sando_opt2", 8.50,
        "a scarred bull leviathan: storm-grey weathered hide crusted with "
        "pale barnacles and old wound scars, heavy ape-like forelimbs with "
        "webbed claws, broad blunt skull with rows of teeth, ridged spine "
        "plates, long finned serpent tail, drab brown-grey palette with a "
        "hard black outline"),
    "StormSando": ("sando_opt3", 6.58,
        "a pelagic leviathan: deep slate-blue hide with bright cyan "
        "bioluminescent striping along the flanks, four webbed fin-limbs, a "
        "ridge of tall spine fins, big-cat skull with jaws open, long finned "
        "tail, navy and cyan palette with a hard black outline"),
    "Mee": ("grazer_opt1", 1.00,
        "a small silver-blue shoal fish: rounded deep body, one large dark "
        "eye, delicate translucent pale-blue fins, a single line of glowing "
        "white-cyan photophore dots along the flank, cool silver palette with "
        "a hard black outline"),
    "Faa": ("grazer_opt2", 1.00,
        "a small gold-olive shoal fish: teardrop body of iridescent "
        "green-gold scales, amber fan tail and spined dorsal fin, small "
        "mouth, a single glowing cyan photophore stripe along the flank, warm "
        "gold palette with a hard black outline"),
    "Laa": ("grazer_opt3", 1.20,
        "a big ornate disc-shaped reef fish: flat circular angelfish body, "
        "pale violet with darker banding, ringed blue eye-spot markings, long "
        "trailing filament streamer fins, lilac and cream palette with a hard "
        "black outline"),
    "Yobshrimp": ("swarm_opt1", 1.00,
        "a pale isopod scavenger: bone-white segmented chitin plates in "
        "overlapping bands, many small pale legs, long feathery antennae "
        "sweeping forward, small dark eyes, fanned tail plate, cream and "
        "bone palette with a hard black outline"),
    "SiltLamprey": ("swarm_opt2", 1.00,
        "a black round-mawed eel: slick glossy dark body tapering to a long "
        "ribbon tail, a circular rasping sucker mouth ringed with pale teeth "
        "held open, milky blind eyes, faint blue-grey sheen on the flanks, "
        "near-black palette with a hard black outline"),
    "RustNipper": ("swarm_opt3", 1.00,
        "a rust-red spiny crab: low angular armoured body of jagged "
        "rust-and-black chitin, long spiky legs, raised barbed claws, a "
        "cluster of glowing red eyes, oxide-red palette with a hard black "
        "outline"),
    "Reefback": ("colossus_opt1", 10.70,
        "a colossal grey-blue filter-feeder: long whale-like body, the back "
        "encrusted with a garden of coral fans, kelp fronds and pale growths, "
        "many long paired fins, a broad passive straining mouth, tiny distant "
        "eyes, mottled slate-blue hide with dusty coral pinks and a hard "
        "black outline"),
    "Starmaw": ("colossus_opt2", 11.40,
        "a colossal deep-blue filter-feeder: broad whale-shark body, a vast "
        "pale cathedral mouth held open, flanks scattered with white-cyan "
        "glowing dots in constellation patterns, wide manta-like pectoral "
        "fins, navy hide with luminous star-speckle and a hard black outline"),
    "Lanternwhale": ("colossus_opt3", 12.00,
        "a colossal moss-shrouded filter-feeder: broad ridged olive-green "
        "plated body draped in hanging moss and weed, immense gill curtains, "
        "chains of glowing blue lantern tendrils hanging beneath the jaw, "
        "tall ridged dorsal crest, moss-green and gold palette with luminous "
        "blue lanterns and a hard black outline"),
}

ORDER = list(CREATURES)

STYLE = ("Flat cel shading, clean readable shapes, hard dark outline, muted "
         "painterly palette, one single creature centred with generous empty "
         "margin on every side, the whole animal fully inside the frame, no "
         "ground, no shadow, no water, no bubbles, no text, no watermark, no "
         "border, and a GENUINELY TRANSPARENT background - output a real alpha "
         "channel, no backdrop of any colour")

ANCHOR = ("Use the creature in the attached image as the exact reference: the "
          "same species, same anatomy, same proportions, same markings and the "
          "same colours. Do not redesign it.")

FACING_PROMPT = {
    "south": (
        "{anchor} Draw that same animal as a RimWorld creature sprite seen "
        "from the FRONT in a tall portrait frame: its head is at the bottom "
        "of the frame facing the viewer head-on, and the body recedes upward "
        "away from the camera in a high three-quarter view so the whole back "
        "and the tail are visible toward the top. The pose is bilaterally "
        "symmetric left to right. It is {treat}. {style}"),
    "north": (
        "{anchor} Draw that same animal as a RimWorld creature sprite seen "
        "from BEHIND in a tall portrait frame: its tail is at the bottom of "
        "the frame nearest the viewer, and the body recedes upward away from "
        "the camera so the whole dorsal surface is visible with the back of "
        "the head at the top, turned away. The face, eyes and mouth are "
        "hidden behind the head; only the back is seen. The pose is "
        "bilaterally symmetric left to right. It is {treat}. {style}"),
}


def prompt_for(slug: str, facing: str) -> str:
    _, _, treat = CREATURES[slug]
    return FACING_PROMPT[facing].format(anchor=ANCHOR, treat=treat, style=STYLE)


# defName suffix is the slug; these are the RULED def names and sizes from
# sea_beasts_def_spec.md section 5, and the ONE visual feature that tells this
# creature apart from its two siblings in the same role. The tell is what an
# in-game check looks FOR - "the sprite appeared" is not an observation.
TELL = {
    "OpeeSeaKiller": ("RSW_OpeeSeaKiller", "opee sea killer", 1.4,
                      "two pale bulb lure stalks over a brown sawtooth carapace"),
    "CrimsonOpee": ("RSW_CrimsonOpee", "crimson opee", 1.7,
                    "the pink adhesive tongue hanging out of a rust-red maw"),
    "ShaleGorger": ("RSW_ShaleGorger", "shale gorger", 2.0,
                    "slate plate bands and NO lure stalks - the pale blind eye"),
    "ColoClawFish": ("RSW_ColoClawFish", "colo claw fish", 3.0,
                     "the fan of white whisker barbels and two clawed forelimbs"),
    "AbyssalColo": ("RSW_AbyssalColo", "abyssal colo", 3.6,
                    "rows of glowing cyan spots down both flanks"),
    "ThornbackColo": ("RSW_ThornbackColo", "thornback colo", 2.6,
                      "the dark thorn ridge along a bone-and-aubergine body"),
    "SandoAquaMonster": ("RSW_SandoAquaMonster", "sando aqua monster", 14.0,
                         "grey-blue lion skull over four webbed clawed limbs"),
    "ElderSando": ("RSW_ElderSando", "elder sando", 20.0,
                   "pale barnacle crusting and scar tissue on a storm-grey hide"),
    "StormSando": ("RSW_StormSando", "storm sando", 12.0,
                   "cyan bioluminescent striping along a navy flank"),
    "Mee": ("RSW_Mee", "mee scalefish", 0.15,
            "one line of white-cyan photophore dots on silver-blue"),
    "Faa": ("RSW_Faa", "faa scalefish", 0.2,
            "the same dot-line, but on gold-olive scales"),
    "Laa": ("RSW_Laa", "laa scalefish", 0.4,
            "ringed blue eye-spots and trailing filament streamers"),
    "Yobshrimp": ("RSW_Yobshrimp", "pale yobshrimp", 0.2,
                  "long feathery antennae on a bone-white banded isopod"),
    "SiltLamprey": ("RSW_SiltLamprey", "silt lamprey", 0.2,
                    "the circular rasping sucker maw held open, no jaw"),
    "RustNipper": ("RSW_RustNipper", "rust nipper", 0.25,
                   "a cluster of glowing red eyes over rust-black spines"),
    "Reefback": ("RSW_Reefback", "reefback", 32.0,
                 "coral fans and kelp growing out of the back"),
    "Starmaw": ("RSW_Starmaw", "starmaw", 36.0,
                "constellation-pattern white dots on a navy flank"),
    "Lanternwhale": ("RSW_Lanternwhale", "lanternwhale", 40.0,
                     "chains of glowing blue lantern tendrils under the jaw"),
}
