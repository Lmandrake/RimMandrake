
## spec

Owner answered 'Queue all' on a question card 2026-10-08 (decision taken by question card) for the remaining work of `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md`. Row X-13 there is the spec:

| X-13 | **A tow line on the ship.** The tether that pulls creatures can hook wrecks, carcasses or a downed beast and drag them home. It pairs with KeelHoist's vertical cargo lift. | CB-9 | M–L | med (save-key migration) | CreatureBehaviors, TheSump, KeelHoist | `IRM_TetherPullHost` has 2 hosts, both pawn-only |
| CB-9 | A salvage winch. The tether line can hook heavy objects as well as creatures (wreck chunks, carcasses, a downed beast) and drag them home to a capstan or the ship. | Generalise RM_CompTetherPull's target from Pawn to Thing, plus a host that only reels objects; research-gated. | M–L | med (save-key migration on `target`) | CreatureBehaviors, TheSump (RM_CapstanTurret), KeelHoist, salvage mods | `IRM_TetherPullHost` has 2 hosts (TractionLance, `TheSump/Source/RM_CapstanTurret.cs`), all with `Pawn target`; no drag/tow mechanic in src (`grep` for drag/tow/winch: only KeelHoist, which is vertical); no item names a tow or salvage winch |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.
