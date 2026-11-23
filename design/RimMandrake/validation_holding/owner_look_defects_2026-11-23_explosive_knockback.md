# Owner look, Explosive Knockback, 2026-11-23 about 12:30 PM PST (informal, no bar decided)

Save `EK_VISIT4_WALK_20261123` on ArchBig, full list, paused. Station list: `D:\ClaudeWork\rimmandrake\showings\EK_VISIT4_LOOK_20261123\stations.md`.

His words, whole:

> For the Explosive Knockback, on station 8, I see the gun lockers. They are showing their weapons on the screen. Terrible behavior for a locker... and I note you ruled to keep the guns safe within the locker [confirm this]. If so, we should patch them to not show their contents for consistency with our rule that if you can see it, it goes flying. Station ten generated Tox Gas... might not be explosive/flammable gas if that's what you were hoping for. Pit covers definitely broken (if they were there before, can't tell) Colonists are IN the pit, correctly. [I must say these are hard tests to evaluate given I can't see their initial states. It might be useful to replicate their frozen initial states beside them so I can see before / after when I review.] Station 14 says goods were knocked around, but I see lots of items still on shelves, I can't evaluate if that's ok or not without initial state. Ok, done with informal walkthrough. I don't think I was too helpful here, but thanks for the opportunity. Release walkthrough.

What he saw, one line each:
- Station 8: the gun lockers draw their weapons on screen. His rule of 2026-11-12 is "Anything that draws its contents is open". The test `sc_closed_containers` treats the weapons lockers as closed.
- Station 10: the cloud is tox gas. The scene may not have used a flammable gas.
- Stations 10 and 14: the pit covers are broken and the colonists are in the pit, which is correct. He cannot tell what was there before.
- Station 14: the sign says goods were knocked around; many items are still on shelves. He cannot judge it without the start state.
- Every station: an aftermath with no start state beside it is hard to judge. He asks for a frozen copy of the start state beside each station.
