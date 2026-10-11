#!/usr/bin/env python3
"""make_sheet.py: the owner-walk decisions sheet for Gimme Some Slack + FlowWorks (BENCH, 2026-10-11).

    python3 Transient/owner_walk_gss_flowworks_2026-10-11/make_sheet.py            # writes the sheet; decisions only if absent

Owner, 2026-10-11: *"The priority then is to build the human-review sheets for me to walk through them and provide
feedback."* The pictures are the live game (the two review maps, as savegames) and the two gated art sheets; this sheet
is where he records a ruling per thing he must judge. No row is pre-filled as his choice: every row starts on 'later' (Not seen yet), and an agent's
default is written in the row text as "shipped default (an agent's guess)", never as his choice.

Re-running the SHEET is safe. The decisions file is written only when absent (the sidecar owns it after that).
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STEM = "gss_flowworks_owner_walk_2026-10-11"
SHEET = os.path.join(HERE, STEM + ".html")
DEC = os.path.join(HERE, STEM + ".decisions.json")
TEMPLATE = os.path.expanduser("~/.claude/skills/review-sheets/assets/sheet_template.html")
WIN = r"\\wsl.localhost\Ubuntu\home\mandrake\rm\bench\Transient\owner_walk_gss_flowworks_2026-10-11" + "\\"
ART_GSS = "http://localhost:37077/?t=dyGFKcrW-cA5RiNafIt2jQ"   # served by serve_gated.py; log beside the art sheet
ART_FW = "http://localhost:35251/?t=v8JfcEldGTX-ks3enLvX1A"
WALK = r"\\wsl.localhost\Ubuntu\home\mandrake\rm\bench\design\validation_walks\RimMandrake\owner_walk_gss_flowworks_2026-10-11.md"

GUESS = {"default": "an agent's guess"}
HOLD = {"status": "PLACEHOLDER: builder still working"}
JOINT = {"needs": "you present (flight)"}

# (id, group, label, what to look at and what the call means, where, extra meta, contested)
G1 = "GSS 1 · cords on the floor"
G2 = "GSS 2 · overhead lines"
G3 = "GSS 3 · the four looks"
G4 = "GSS 4 · open calls and guessed defaults"
G5 = "GSS 5 · Mod Settings"
G6 = "GSS 6 · the whole mod"
F1 = "FlowWorks 1 · your five visual rules"
F2 = "FlowWorks 2 · your 2026-10-06 notes, as changed"
F3 = "FlowWorks 3 · pits, ladders, spikes, covers"
F4 = "FlowWorks 4 · hoses"
F5 = "FlowWorks 5 · rigid universal pipe (NEW)"
F6 = "FlowWorks 6 · liquids: how they behave"
F7 = "FlowWorks 7 · the whole mod"
F8 = "FlowWorks 8 · Mod Settings"

ROWS = [
    # ── GSS 1
    ("gss_cord_invisible", G1, "Conduit is invisible; only loose cords show",
     "No vanilla conduit pipe anywhere on a run, only the cords. Your 'Jawa should celebrate that'.", "GSS map 1-4", {}, False),
    ("gss_cord_slack", G1, "Cords lie in big slack loops",
     "Each cord much longer than the straight line, broad loops and excursions, piling against walls. Never taut.",
     "GSS map 1-4, 19", {}, False),
    ("gss_cord_wall", G1, "Cord ends at a wall's face ('it's in there')",
     "Where conduit enters a wall or rock, the cord stops at the face with a grommet or stub; never drawn over the wall.",
     "GSS map 13", {}, False),
    ("gss_cord_dive", G1, "A cord that cannot route dives through the wall",
     "When no walkable path exists, the cord goes into the wall and comes back out on the far side. Judge the look.",
     "GSS map 13, 20", {}, False),
    ("gss_cord_tangle", G1, "A dense conduit field reads as one tangled heap",
     "Nine or more conduit cells together become one swirl of wires and power strips, not tidy lines.",
     "GSS map 19 (electric room)", {}, False),
    ("gss_cord_pile", G1, "Junction piles and Modern power-strip piles",
     "One flowing cable through a junction, no orphan strips lying loose. (Hose crossings are in FlowWorks 4.)",
     "GSS map 5, 19", {}, False),
    ("gss_cord_break", G1, "A cut line: live end and dead end differ",
     "At a cut, the end still on power sparks; the dead end lies limp. Must read at normal zoom.",
     "GSS map 1-4 (each has a cut), 14", {}, False),
    # ── GSS 2
    ("gss_span_above", G2, "Overhead spans draw above everything",
     "Spans between masts sit above pawns, buildings and laid hoses, never under them.", "GSS map 6, 26", {}, False),
    ("gss_span_down", G2, "A cut or fallen span lies on the ground",
     "Destroy a mast or cut a span: the wire drops and lies as a fallen cord.", "GSS map 14", {}, False),
    ("gss_tap", G2, "Power tap clamp: look and what it does",
     "A clamp on someone else's line steals 500 W. The theft numbers you confirmed today are not asked again.",
     "GSS map 15", {}, False),
    ("gss_fallen_shock", G2, "A live fallen wire: shock, knockback, fire",
     "Shipped: throws a flesh pawn back 2 cells, knocks out about 2 game hours, can ignite chemfuel or oil. Numbers are guesses.",
     "GSS map 14, then Mod Settings > Overhead lines", GUESS, False),
    ("gss_drip_loops", G2, "Drip loops under the insulators ship OFF",
     "Built, but OFF because it changes spans you already reviewed. Approve = keep OFF; Change = ship ON.",
     "GSS map 6, keeper save with drip loops ON", GUESS, True),
    ("gss_gravship", G2, "Wires survive a gravship launch and landing",
     "Two masts linked on the ship land with the span still drawn and on one power net. Flight only with you there.",
     "joint flight session", JOINT, False),
    # ── GSS 3
    ("gss_look_scrapper", G3, "Scrapper look (default): scrap cable, crude masts",
     "Floor cords, masts, lamp masts, wall brackets, tap clamp, switch and lamp in the Scrapper family.",
     "GSS map 1, 6; art sheet", {}, False),
    ("gss_look_industrial", G3, "Industrial look", "The same set in the Industrial family.", "GSS map 2, 6", {}, False),
    ("gss_look_modern", G3, "Modern look: coloured extension cords, power strips, black lines",
     "The same set in the Modern family.", "GSS map 3, 6", {}, False),
    ("gss_look_modern_colours", G3, "Modern colours: a different colour per run by default",
     "Shipped default is Mixed (one colour per run). The other choice is one colour everywhere. Approve = keep Mixed.",
     "GSS map 5", GUESS, False),
    ("gss_look_futuristic", G3, "Futuristic look: sleek grey cable, teal accents, steel poles",
     "The same set in the Futuristic family.", "GSS map 4, 6", {}, False),
    ("gss_looks_distinct", G3, "The four looks are told apart at a glance",
     "Side by side, nobody mistakes one family for another.", "GSS map 6, 11", {}, False),
    ("gss_one_run_one_look", G3, "One connected run draws in one look",
     "A merge takes the bigger run's look, a split keeps it, and a restyle repaints one run only.", "GSS map 7-10", {}, False),
    ("gss_look_names", G3, "The names: Scrapper, Industrial, Modern, Futuristic",
     "Older docs said Star Wars: Jawa / Star Wars / Extension cord / Cybertek. The build menu now uses these four.",
     "build button > Choose style", {}, False),
    ("gss_default_look", G3, "New games start on Scrapper",
     "The default look for new games and for unstyled conduit. Approve = keep Scrapper.", "Mod Settings > Cables",
     GUESS, False),
    # ── GSS 4
    ("gss_dead_ends", G4, "Unfinished runs: every live dead end sparks",
     "Shipped: every live end sparks. Other choice: a deliberate end wears a taped cap. That is not built and needs art. Approve = keep sparking.",
     "GSS map 1-4", GUESS, True),
    ("gss_charms", G4, "Hanging charms on spans (an old boot, a droid part)",
     "In the design but not built, and they need new art. Approve = build them; Change = drop the idea.",
     "nothing to see yet", {}, True),
    ("gss_decoration", G4, "Phase 3 decoration: snow fade on cords, trunk wraps",
     "Optional in the design, not built, needs art. Approve = build; Change = drop.", "nothing to see yet", {}, True),
    ("gss_art_missing_label", G4, "The style picker says '(art not installed yet)'",
     "A look whose cord art is missing shows that tag and cannot be picked. Is that the right way to show it?",
     "Mod Settings > Cables", {}, False),
    # ── GSS 5
    ("gss_set_cables", G5, "Mod Settings: Cables tab",
     "Default look, Modern colour, slack, loop budget, cords per connection, messiness, sparks, sway, which conduit becomes cords. Is the screen superb?",
     "Mod Settings > Gimme Some Slack > Cables", {}, False),
    ("gss_set_overhead", G5, "Mod Settings: Overhead lines tab",
     "Longest span 20, sag 6%, wires per span 3, sway, explosions cut, taps and theft, gravship, fallen-wire shock, alerts, drip loops.",
     "Mod Settings > Gimme Some Slack > Overhead lines", {}, False),

    # ── FlowWorks 1
    ("fw_vp1_depth", F1, "Rule 1: deep cuts get tall wall faces like a wall seen from above",
     "Faces D1 0.10, D2 0.18, D3 0.30, D4 0.50 cells. D3 was set to a vanilla wall's face height, which is a guess.",
     "FW map block V", GUESS, False),
    ("fw_vp2_material", F1, "Rule 2: walls look like dirt or stone, by the ground beside them",
     "The face takes the neighbouring ground's look, not the rock under the soil. That choice is a guess.",
     "FW map block V", GUESS, False),
    ("fw_vp3_water", F1, "Rule 3: water moves (ripples, V-wakes)",
     "Animated ripples and wakes. There is no flow direction in the ripples (the engine keeps none).", "FW map block V",
     {}, False),
    ("fw_vp4_tar", F1, "Rule 4: tar reads as black liquid, not burnt ground",
     "Now opaque dark grey on stone and dirt alike, never blue, never see-through.", "FW map block V", {}, False),
    ("fw_vp5_scorch", F1, "Rule 5: a burned pit is an empty pit, scorched",
     "Ash floor, sooted faces, blast marks and blackened patches. Scorch fades over 20 days (3x faster in rain); 20 is a guess.",
     "FW map block V", GUESS, False),
    # ── FlowWorks 2
    ("fw_lr_keep_oil_slime", F2, "Dirty oil and slime in a pit (you called them EXCELLENT)",
     "Kept unchanged. Approve if they still look the way you approved them.", "FW map block V", {}, False),
    ("fw_lr_labels", F2, "Names say depth, like riverbanks",
     "'shallow / chest-deep / deep / very deep <liquid>'; dry cuts 'shallow pit / pit / deep pit / very deep pit'.",
     "FW map: hover any cut", {}, False),
    ("fw_lr_more_fluids", F2, "More liquids online: blood, chemfuel, astrofuel, white and red slime",
     "Each can fill a cut and has its own look. The fuels can detonate; blood does not burn.", "FW map block V", {},
     False),
    ("fw_lr_bubbles", F2, "Acid eerie yellow-green and bubbling; slime light bubbles; boiling heavy",
     "Bubble flecks per liquid. Mod Settings has an on/off switch and a density slider.", "FW map block V", {}, False),
    ("fw_lr_propane", F2, "Propane is a medium-pale grey", "Only the colour changed; its transparency is unchanged.",
     "FW map block V", {}, False),
    ("fw_lr_see_through", F2, "Pit floor and walls show through clear liquid",
     "Water shows the floor most, acid and fuels less, tar, oil, slime and blood not at all.", "FW map block V", {},
     False),
    ("fw_lr_pit_walk", F2, "In a pit: walk at normal speed; only climbing is slow; falling is fast",
     "Feel row: draft a pawn into a pit and walk him around.", "FW map 17, 26", {}, False),
    # ── FlowWorks 3
    ("fw_wall_faces_keep", F3, "Wall faces, spikes and ladder art: keep?",
     "The drawn faces of a dug cut, the spikes on a pit floor, and the ladder.", "FW map V, 24, 26; art sheet", {},
     False),
    ("fw_ladder_states", F3, "Raised vs lowered ladder",
     "A raised ladder beside the rim reads different from a lowered one.", "FW map 26; art sheet", {}, False),
    ("fw_lip_window", F3, "A pit occupant shows through a 1-cell window in the near lip",
     "The near bank hides most of a sunk pawn; a 1-cell window keeps him visible at every depth. The window is a guess.",
     "FW map 17, 27", GUESS, False),
    ("fw_cover", F3, "A covered pit looks like plain ground; a faint seam at max zoom",
     "The three covers (woven scrap, plank lattice, reinforced frame). Anything falling through breaks the cover.",
     "FW map 22, 23; art sheet", {}, False),
    ("fw_pit_mood", F3, "A kind colonist feels bad seeing a prisoner exposed in a pit",
     "-3 mood for a compassionate colonist; a psychopath does not care. Cruel at the right strength?", "FW map 28",
     GUESS, False),
    ("fw_sluice_gate", F3, "Sluice gate and grate door: open vs shut readable",
     "Visible without clicking.", "FW map 29; art sheet", {}, False),
    # ── FlowWorks 4
    ("fw_hose_thick", F4, "A hose is much thicker and stiffer than a power cord",
     "Like a fire hose; it turns in wide bends.", "GSS map 16, 17", {}, False),
    ("fw_hose_plump", F4, "Plump while flowing, flat when not",
     "Round and full while liquid moves, flat when idle. Only a powered pump plumps it.", "GSS map 16", {}, False),
    ("fw_hose_brass", F4, "Hose joints look like brass screwed together", "Where one length meets the next.",
     "GSS map 16, 21", {}, False),
    ("fw_reel_nozzle", F4, "The hose leaves the reel from its brass outlet nozzle",
     "The 2x2 reel's hose attaches at the nozzle, not the middle.", "GSS map 11, 30", {}, False),
    ("fw_reel_laid_wound", F4, "A reel with its hose out looks different from a wound reel", "", "GSS map 30, 31", {},
     False),
    ("fw_relay", F4, "Relay reels: a hose ending on the next reel reads as coupled",
     "The way to go past 30 cells.", "GSS map 29", {}, False),
    ("fw_reel_looks", F4, "Reel and hose in the four looks; 'Choose style' on a selected reel", "",
     "GSS map 11", {}, False),
    ("fw_hose_tint", F4, "A charged hose shows the colour of the liquid in it", "", "GSS map 32, 33", {}, False),
    ("fw_hose_words", F4, "Your hose words, in your own wording",
     "The walk's hose paragraph (brass joints, nozzle, deflated unless pumping) was relayed by an agent. Put your own wording in the note.",
     "note only", {}, False),
    ("fw_tank_feeds_hose", F4, "A tank passes liquid into a hose screwed into it, no pump",
     "Your ruling 9 today. Feel row: see the far tank fill.", "walk scene W5", {}, False),
    ("fw_hose_off_drains", F4, "A hose switched off drains out of its open ends",
     "Your ruling 2 today. Being built now; the scene is staged once the builder lands.", "walk scene W4", HOLD,
     False),
    # ── FlowWorks 5
    ("fw_pipe_scrapper", F5, "Rigid pipe: Scrapper look",
     "New art from the Dubs Bad Hygiene / Chemfuel Expanded study. Today the pipe borrows vanilla conduit art.",
     "walk scene W3; art sheet row RM_UniversalPipe", HOLD, False),
    ("fw_pipe_industrial", F5, "Rigid pipe: Industrial look", "", "walk scene W3", HOLD, False),
    ("fw_pipe_modern", F5, "Rigid pipe: Modern look", "", "walk scene W3", HOLD, False),
    ("fw_pipe_futuristic", F5, "Rigid pipe: Futuristic look", "", "walk scene W3", HOLD, False),
    ("fw_pipe_style_ui", F5, "Pipe looks are picked the same way as the wire looks",
     "The same build-button style menu and 'Choose style' as the cords and reels.", "walk scene W3", HOLD, False),
    ("fw_pipe_interop", F5, "Pipe plugs cleanly into other pipe networks",
     "Carries any liquid. A tank never joins two pipe runs into one.", "walk scene W3", HOLD, False),
    # ── FlowWorks 6
    ("fw_intake_pump", F6, "Filling storage needs a pump; draining it does not",
     "Your ruling 3: all storage sits 'above' the world's liquid.", "walk scene W5", {}, False),
    ("fw_pitch", F6, "Tar and pitch stay thick, slow and gooey; never set solid",
     "Your ruling 6. Feel row: watch a tar front lag a water front.", "FW map 10", {}, False),
    ("fw_containers", F6, "Bottles, buckets, barrels take their material's colour",
     "Stone reads as glass; metal and wood refuse acid, plasteel holds it.", "FW map 30; art sheet", {}, False),
    ("fw_unproven_off", F6, "'Unproven mechanics' ship OFF: liquid corrosion, liquid ignition",
     "Both are off by default until proven. Approve = keep off.", "Mod Settings > FlowWorks", GUESS, False),
    ("fw_river_steam", F6, "River steam on Pyrelands: shape and motion vs the reference photo",
     "Needs a Pyrelands map (walk scene W7). Other biomes' rivers stay silent.", "walk scene W7", {}, False),
    ("fw_flyer_river", F6, "A flyer over a river is never moved by the current",
     "Flight only with you there.", "joint flight session", JOINT, False),
    # ── FlowWorks 7
    ("fw_accept", F7, "FlowWorks as a whole: accepted?",
     "After walking the map: do you accept the mod's look and feel for shipping?", "FW map, all", {}, False),
    ("fw_ship_gaps", F7, "Close or park each remaining ship gap",
     "Items FLOWWORKS_NORTHSTAR_SHIP_1 / TRIAL_1 list the gaps. Name any to park in the note.", "note only", {}, False),
    ("gss_accept", G6, "Gimme Some Slack as a whole: accepted?",
     "After walking the map: do you accept the mod's look and feel for shipping?", "GSS map, all", {}, False),
]

FW_SETTINGS = [
    ("excavation", "Excavation and flow", "dig to depth, pulse speed, flow per pulse, largest network, moving seams"),
    ("unproven", "Unproven mechanics (OFF by default)", "liquid corrosion, liquid ignition"),
    ("stock", "Stock, recession and drainage", "fill-in, ponds that run dry, source budget, drainage"),
    ("heat", "Hot and icy liquid", "heat push and its strength"),
    ("fire", "Burning liquid", "canal fire, burn days, fire-front speed, how far fire reaches into a source"),
    ("pits", "Pits, ladders and shooting", "capture, covers, own faction, ladders, spikes, the lip window"),
    ("containers", "Bottles, buckets, barrels", "fill, use, wash; dirty stage"),
    ("tank", "The liquid tank", "tank loop, capacity, pump"),
    ("drill", "Drilling and tapping", "drilling on/off, yield, units per cycle"),
    ("shores", "Typed bodies of water", "liquid shores on new maps (labelled as worldgen-affecting)"),
    ("finds", "Finds while digging", "finds, local only, chance, budget, first-find letter"),
    ("swales", "Swales", "swales on/off and rate"),
    ("rivers", "Rivers", "current, fords, surge, wash-off, weir, levee, silt trap, ferry, drift, steam"),
    ("machinery", "Liquid machinery", "universal pipes, stills, found works, converter throughput"),
    ("tanker", "Tankers", "cargo tank settings"),
    ("sluice", "Sluice gates", "time to open and shut after cranking"),
    ("blood", "Blood draw", "blood draw settings"),
    ("kits", "Liquid kits", "baths, reactions, hot floods; reaction pace, scald strength"),
    ("quarry", "Rivers carry minerals", "river stock, sluice yield, panning yield"),
    ("hoses", "Hoses and pipes", "plump amount, flat/plump transition, collapse delay, default look"),
]
for key, title, what in FW_SETTINGS:
    ROWS.append(("fw_set_" + key, F8, "Mod Settings: " + title, what + ". Clear, grouped, sensible defaults: superb?",
                 "Mod Settings > FlowWorks > " + title, {}, False))
ROWS.append(("fw_set_whole", F8, "FlowWorks settings screen as a whole",
             "20 sections in one long scrolling page with search and per-section reset. Is that the right shape?",
             "Mod Settings > FlowWorks", {}, False))


def items():
    out = []
    for rid, grp, label, effect, where, meta, contested in ROWS:
        m = {"where": where}
        m.update(meta)
        it = {"id": rid, "group": grp, "label": label, "effect": effect or label, "meta": m,
              "prefill": "later", "trueSize": {"none": "a ruling row: the picture is the live game or the art sheet"}}
        if contested:
            it["contested"] = True
        out.append(it)
    return out


def config(n):
    brief = f"""
<p><b>What this is.</b> Every look and feel in <b>Gimme Some Slack</b> and <b>FlowWorks</b> that only your eyes can
settle: {n} rows. The machine-checkable rows (61 FlowWorks state rows PASSed today) are not here. Rows are grouped by mod; GSS first.</p>
<p><b>Where the pictures are.</b> Not in this page. You asked to see FlowWorks in the game, so each row names a
<b>map station</b> on one of the two review maps (keeper savegames: <code>RM_gss_review_owner_walk</code> and
<code>RM_fw_review_owner_walk</code>), a <b>walk scene</b> W1-W8, or a Mod Settings section. Sprites at true size,
beside a human, are on the two art sheets: <a href="{ART_GSS}" target="_blank">Gimme Some Slack art</a> (4 sprites) and <a href="{ART_FW}" target="_blank">FlowWorks art</a> (47 rows).<br>
Scene list: <code>{WALK}</code></p>
<p><b>Nothing is pre-filled as your choice.</b> Every row starts on <b>Not seen yet</b>, our marking, never an approval. Where we shipped a default that was an agent's guess, the
row says so (tag <i>default: an agent's guess</i>), and <b>Approve</b> keeps it. <b>Change</b> means it is wrong; say how in the note.
<b>Not seen yet</b> parks a row you could not judge. Rows tagged <i>PLACEHOLDER</i> wait for the rigid pipe art and the
hose-off drain, which are being built now. Rows tagged <i>contested</i> are open choices, either answer defensible.</p>
<p>Keys: <kbd>1</kbd> approve · <kbd>2</kbd> change · <kbd>3</kbd> not seen yet · <kbd>n</kbd> note. Saves to the file as you go.</p>
"""
    return {
        "sheetId": STEM,
        "title": "Gimme Some Slack + FlowWorks: your walk",
        "subtitle": "looks and feel only your eyes can settle · 2026-10-11",
        "briefHtml": brief,
        "criterion": "Ordered by mod and by the order you meet things on the walk. No ranking: every row is a yes/no on your taste.",
        "invented": [
            "Which rows are yours: we kept a look bar only where the ledger owes an owner look or the bar is a taste call, and left out the bars a state read or a frame check already settles.",
            "The station numbers point at the existing review maps (GSS 33 stations, FlowWorks block V + 52 stations). The hose stations are still on the GSS map.",
            "Power-theft numbers (2 goodwill/day, 12 cells) are left out: you confirmed them today.",
            "'Not seen yet' is our option, so a parked row is not read as a rejection.",
        ],
        "posture": {"mode": "whitelist",
                    "explain": "Only rows you mark Approve count as signed off. Change and Not seen yet both stay open."},
        "options": [
            {"key": "approve", "label": "Approve", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "change", "label": "Change (say how)", "hotkey": "2", "color": "#e06c6c", "counts": "out"},
            {"key": "later", "label": "Not seen yet", "hotkey": "3", "color": "#98a2b3"},
        ],
        "groupLabel": "group",
        "media": False,
        "trueSize": "optional",
        "decisionsFile": STEM + ".decisions.json",
        "decisionsPath": WIN + STEM + ".decisions.json",
        "sheetPath": WIN + STEM + ".html",
    }


def main():
    its = items()
    ids = [i["id"] for i in its]
    assert len(ids) == len(set(ids)), "duplicate row id"
    html = open(TEMPLATE, encoding="utf-8").read()
    a = html.index('<script id="CONFIG" type="application/json">')
    b = html.index("</script>", a)
    html = html[:a] + '<script id="CONFIG" type="application/json">\n' + json.dumps(config(len(its)), indent=1) + "\n" + html[b:]
    a = html.index('<script id="ITEMS" type="application/json">')
    b = html.index("</script>", a)
    html = html[:a] + '<script id="ITEMS" type="application/json">\n' + json.dumps(its, indent=1) + "\n" + html[b:]
    open(SHEET, "w", encoding="utf-8").write(html)
    import subprocess   # the non-art declaration lives in the HTML, so every rebuild re-adds it
    subprocess.run([sys.executable, os.path.join(HERE, "..", "..", "src", "RimMandrake", "Utils", "art", "nonart_sheet.py"),
                    "declare", SHEET], check=True)
    if not os.path.exists(DEC):
        doc = {"sheetId": STEM, "posture": "whitelist",
               "reviewStatus": {"state": "prefill", "by": None, "at": None,
                                "evidence": "generated by make_sheet.py; every row pre-marked later (Not seen yet) by the agent; nobody has ruled"},
               "decisions": {i: {"decision": "later", "note": "", "prefill": "later"} for i in ids}}
        json.dump(doc, open(DEC, "w"), indent=1)
        print("wrote", DEC)
    print("wrote", SHEET, len(its), "rows;",
          {g: sum(1 for i in its if i["group"].startswith(g)) for g in ("GSS", "FlowWorks")})


if __name__ == "__main__":
    sys.exit(main())
