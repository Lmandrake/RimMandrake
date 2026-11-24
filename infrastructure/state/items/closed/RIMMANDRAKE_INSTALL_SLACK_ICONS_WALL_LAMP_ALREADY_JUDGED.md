# RIMMANDRAKE_INSTALL_SLACK_ICONS_WALL_LAMP_ALREADY_JUDGED

Gimme Some Slack 0.2.0, the art order for two of its bars: `look_menu_icons` and `wall_lamp_takes_looks`
(`design/concepts/GimmeSomeSlack/record.json`, `version/VERSION.json` field `art_items`).

No art is generated here. The pictures exist: `RIMMANDRAKE_DESIGN_HOME_FOR_VANILLA_ELECTRICAL_ART` rendered and judged them on
2026-11-20 (4 of 4 look icons KEEP, 12 of 12 wall lamp pictures KEEP), and they wait in the art store with their sha and
planned path (`design/specs/2026-11-20-vanilla-electrical-art-home/commissions.md`, verdicts in
`infrastructure/state/delegated/2026-11-20/{VEA_Icons,WallLamp}.json`).

His words: his walk of 2026-11-20 (`D:\ClaudeWork\rimmandrake\conductor\gss_walk_20261120_his_words.md`, message 2):
*"the "change style" really needs some proper icons to represent the different options (true on ALL mods that use our style
switches)"* and *"the Wall Lamp doesn't even have any yet"*.

## spec

Install the 16 kept pictures into Gimme Some Slack through the art ledger's `art install` only (CLAUDE.md §Art):

- the look icons at `src/RimMandrake/GimmeSomeSlack/Textures/RimMandrake/GimmeSomeSlack/UI/Looks/<Look>.png`;
- the wall lamp at `src/RimMandrake/GimmeSomeSlack/Textures/RimMandrake/GimmeSomeSlack/Styles/<Look>/WallLamp_{north,east,south}.png`
  (west mirrors east).

Looks: Scrapper, Industrial, Modern, Futuristic. The code that shows them is the bars' own Stage 3 work (`T_LOOK_ICONS_OFFLINE`,
`T_WALL_LAMP_LOOKS_OFFLINE`). The stub-art census (`T_STUB_ART_CENSUS`) classes every new texture; add the new paths to it in the
same change, or it goes red (commissions.md, "Why nothing is installed").

## criteria

Acceptance test (red today, watched 2026-11-23 2:30 AM PST: `MISSING 16`, exit 1):

    python3 -c "import os,sys;G='src/RimMandrake/GimmeSomeSlack/Textures/RimMandrake/GimmeSomeSlack/';L=['Scrapper','Industrial','Modern','Futuristic'];m=[p for p in [G+'UI/Looks/%s.png'%l for l in L]+[G+'Styles/%s/WallLamp_%s.png'%(l,f) for l in L for f in ('north','east','south')] if not os.path.exists(p)];print('MISSING',len(m));sys.exit(1 if m else 0)"

passes with `MISSING 0` (16 files present), and `python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_stub_art_census.py` still passes.

## verify

Run both commands under ## criteria; cite their output and the `art install` records on the close.
