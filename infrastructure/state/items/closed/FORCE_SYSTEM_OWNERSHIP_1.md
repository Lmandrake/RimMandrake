# FORCE_SYSTEM_OWNERSHIP_1 — own the Force: our own DLL, design sitting first

Owner ruled 2026-08-30 ("Weapons wave + Force C#"): full ownership of
lee.theforce.lightsaber.

## spec
Sequence: (1) BENCH design sitting with the owner seeded by
design/Jawa/force_users_build_spec.md — what the Force system SHOULD be here
(owning, not cloning); (2) behavioral inventory — DONE 2026-08-30:
design/Jawa/force_system_inventory.md (89d88150): ~1/3 pure XML re-authors
free; ~2/3 C#-bound (~90 types: lightsaber damage/parry Harmony, duel/lord
state machine, blade/holster rendering, crafting dialogs); jecstools NOT
referenced (resolved); 9 weapon defNames scribed in the frozen world save —
defName preservation applies; (3) DLL spec + FOUNDRY build items, Droidworks
pattern; (4) art rides the weapons-wave tooling.

## verify
Design sitting produces a ruled spec; each build item carries its own proof;
final: lightsaber combat observed on a quicktest under OUR DLL with the
upstream mod retired from a test list.

## criteria
- [ ] OPEN QUESTION for the owner: general Force POWERS (telekinesis,
      lightning, XP) are NOT in this mod — they live in a sibling,
      lee.theforce.standalone, referenced only via MayRequire. Is that sibling
      active/wanted, and does Force ownership cover it too?
- [ ] Design sitting held; spec ruled
- [ ] Build items filed and closed
- [ ] Upstream retirement proven on a test list
