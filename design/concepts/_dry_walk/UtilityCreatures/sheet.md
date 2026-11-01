DRY WALK: not a concept he has seen. A second model stood in for him. Every answer below except `his words` is the stand-in's. Nothing here is on the ledger as his.

# Utility Creatures (rehearsal, item UTILITY_CREATURES_DESIGN_DIG_THIS_PIT_BOY)

## his words
"So let's make shovels and shovel creatures. Kinda begs a new mod doesn't it? Utility creatures. Creatures with commands like "dig this pit" or "cut that tree." File that idea for v2 for now. It's a good one." (ledger OWNER, tsn 1792940188649007959, 2026-10-25)

## root (stand-in, not his)
- `rs1`: you order one chosen creature to dig one chosen pit, and that creature does it
- `rs2`: an order that cannot be carried out is refused at the click, with the reason
- `rc1`: no order is forgotten half-way

## does
- [leaf:one_creature_digs] One chosen creature digs the one cell the player ordered
- [leaf:refused_at_click] With no shovel in reach the order is refused at the click, with the reason on screen
- [leaf:resumes_same_order] An interrupted creature goes back and finishes the same order by itself
- [leaf:order_cost] The order loop stays cheap
- [floor:save_compat] Adds to an existing save
- [floor:log] Clean log
- [floor:mod_settings] On/off per major feature

## does not
- [leaf:no_work_toggle] It is not a work priority: nothing digs without an order
- [leaf:no_bare_paws] A creature never digs without a shovel: the Shovels rule holds
- [floor:worldgen] Nothing at world generation
- [waived:w1] Which kinds of creature take commands in the first version

## waived
- w1: droids or animals for the first version (stand-in, round 1)

## open
- how a creature comes to accept commands: training, or by kind. Not asked: two rounds spent. Not core to the first order, so it does not block

## delegated
- none: the stand-in delegated nothing, so the agent picks one creature for the first spike in plan.md, and says so

## pruning
- one_creature_digs: "dig this pit"
- refused_at_click: stand-in round 2 ask 1, Yes. HIS WORDS DO NOT COVER THIS: he must answer it
- resumes_same_order: stand-in round 2 ask 3, Yes. HIS WORDS DO NOT COVER THIS: he must answer it
- order_cost: the agent's line, kept to exercise a constraint leaf. He may well prune it
- no_work_toggle: "Creatures with commands"
- no_bare_paws: "shovels and shovel creatures"
- first_walk: the walk leaf every mod has
