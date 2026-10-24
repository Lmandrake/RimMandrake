# WORLD_REMAKE_AUDIT_DEPENDENCY_CLOSURE_FIRST

Source: Transient/gpt_review_world_remake_plan_2026-10-19.txt (section 3). GPT opinion. Hard rules: OFFLINE ONLY, no worldgen of any kind, no test redraft or alternate planet. GPT's Option D (decouple dev from canonical replacement) changes the owner's plan and is on GPT_CONFLICTS_FOR_OWNER_DIGEST, not acted on here.

## spec
GPT quotes:
- "'Remove 124' is not dependency-safe. 'Nothing of ours hard-depends' excludes retained third-party dependants. Custom Quest Framework supports retained Dungeon Pack; VFE Props supports retained Gerrymon's Dungeon; Apparel Accessories supports retained More Utility Packs; Minerals Framework supports retained Minerals Sparkle (01 sections 5,10). Compute the removal set's dependency closure first."
- "The proposed drops include Alien Worlds, My Little Planet, Sensible Factions and Deep Orbit. Yet the documented preset procedure depends on Alien Worlds, and 02 section 2 explicitly assumes Deep Orbit remains at generation."
- "04's inactive-mod cut includes Pyrinth, required for Wave 1. Its Warscar cut includes WARSCAR_SHEET_DONOR_PORT_1, classified prerequisite in 03."
- "Settlements also regress: 121 CSV entries versus 96 canonical NPC settlements."

Build: script (offline, reads About.xml/loadAfter/dependency + Patches) that takes the 124-mod removal set and outputs the closure: retained mods that depend on/support a removed one, worldgen prerequisites inside the set, and conflicts with Wave 1 and the 04 cuts. Output to /mnt/d/ClaudeWork/rimmandrake/ and a short table for the plan owner.

## verify
- Output lists at least the four named retained dependants (sanity probe: if it does not find them the script is blind).
- Alien Worlds and Deep Orbit flagged as worldgen prerequisites; Pyrinth and WARSCAR_SHEET_DONOR_PORT_1 flagged as conflicts.
- Settlement 121 vs 96 discrepancy listed as an exporter-scope note.
- No game launched, no world generated.
