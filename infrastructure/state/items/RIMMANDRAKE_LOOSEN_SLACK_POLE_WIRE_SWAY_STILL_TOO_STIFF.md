# RIMMANDRAKE_LOOSEN_SLACK_POLE_WIRE_SWAY_STILL_TOO_STIFF

Gimme Some Slack, **next version** (Polish of a look; not in the 0.1.1 scope he picked by card on 2026-11-20, and he passed 0.1.0
after saying it). Merged by the ticket sweep of 2026-11-22 from `RIMMANDRAKE_CLEAN_SLACK_SWAY_POLE_WIRES_ONLY_NOT_CONDUIT`, whose
code half is done (0a0fd8343b removed ground-cord wind, shader sway and floor ripple; proven live on 1d580847bd2e:
B7_ground_cords_never_sway, R3_sway_proxy, R3b_sway_looks_each_draw PASS; visit 3 of 0.1.1 again PASS).

His words, word for word:
- Card answered 2026-11-16 (6:48 AM PST): *"Oh wow, there's been some confusion. Wires swaying in the wind were supposed to be about power pole wires. Wind wasn't supposed to mess with conduit-based wiring at all, nor about terminal wires in walls extending cable hanging out. Let's clean that up."*
- Typed right after the card, 2026-11-16, about the power-pole wires as they are today: *"They look like they're swaying, though it's not a great effect. They're too stiff."*

## spec

The power-pole wires' wind sway reads as a stiff rod, not a hanging wire. Three candidate motions exist in code (Pendulum, Rope,
Gust; Rope ships), each staged by `validation_aerial.py` R3b. Stage the three on one map, have a judge agent that did not make them
pick against his words above (`design/RimMandrake/art_judge_brief.md`, a delegated call; agents make taste calls), ship the pick,
and show it at his next walk.

## criteria

Acceptance test: none, a look (the judge's pick, then his walk); the state rows R3_sway_proxy and R3b_sway_looks_each_draw must
stay PASS.

## verify

The judge verdict file for the pick, and R3_sway_proxy and R3b_sway_looks_each_draw PASS on the shipped pick; cite both on the close.
