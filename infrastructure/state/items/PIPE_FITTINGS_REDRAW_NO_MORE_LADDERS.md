# PIPE_FITTINGS_REDRAW_NO_MORE_LADDERS — draft FlowWorks pipe fittings, end caps and pump looks

Owner, by question card 2026-10-22 ~07:46 PDT: "May we draft replacements for FlowWorks pipe art (real 3- and 4-way
fittings, one coupling per joint, a matched end cap per look, three more pump looks)? → Draft all of it".

## Why (joints study, Transient/pile_2026-10-22/joints_study.md; question Q5 in morning_questions.md)
- D9: a pipe T or cross meets under a small token; Modern and Futuristic repeat coupling bands so a run reads as a
  ladder or a cable (`Transient/pile_2026-10-22/joints/sheet_A.jpg`).
- D10: the pump has one picture (the scrap hub) in every look (`joints/sheet_C.jpg`).
- D11: end caps differ: dark knobs in Scrapper/Industrial, tiny ticks in Modern/Futuristic.

## Scope
- Per look (Scrapper, Industrial, Modern, Futuristic — PipeStyles.Looks): a 4-way cross fitting, a 3-way tee fitting,
  one coupling band, one end cap, each drawn in that look's pipe-atlas colours and conformed to the atlas's girth
  (pipe 0.10 cell); plus a composed DRAFT atlas per look (one coupling per joint, real T/cross hubs, matched caps).
- Pump: Industrial, Modern, Futuristic looks of the live 4-port hub (Things/Building/FlowWorks/Machinery/RM_LiquidPump).
- Review sheet built and gated with art_sheet.py; NOT served until the owner can review. Nothing installed.

## Not in scope
- Pump look switching (style defs like the tanks) is C#/def work for after his picks.
- Installing any atlas: only after his picks, through `art.py enact`.

Progress: Transient/pile_2026-10-22/purges_and_pipe_art.md
