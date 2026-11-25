# The pale cloud over the EMP pad (RIMMANDRAKE_EXPLAIN_KNOCKBACK_PALE_CLOUD_OVER_EMP_PAD), ArchSmall, 2026-11-25

Explained as not Explosive Knockback's. Probe `scripts/probe_emp_cloud.py` (EXPLORED), release build ddbf5e27c549, tier
explosiveknockback_visit (25 mods), fresh quicktest maps, a Shell_EMP alone on soil, no other blast on the map:

- Run 11:48 PST (`evidence/emp_cloud_show_on_vs_all_off.jpg`): pad A with every show switch on, pad B 40 cells away with the
  knockback master switch (`enabled`) and all seven show switches off. Both pads are plain soil at tick 0 and both carry the
  same large pale cloud at 100 and 300 ticks. So the cloud is not our show and not a throw of ours; and with no incendiary
  on the map, it is not fire_soil's smoke drifting in.
- Runs 11:44 and 11:46 PST (`evidence/emp_cloud_gas_cleared.jpg`): `jawa/set_gas action=clear` of BlindSmoke, ToxGas,
  RotStink and DeadlifeDust on the pad changed 0 cells each, and the cloud stayed: it is not one of the four vanilla gas grid
  types. No thing on the pad at 300 ticks explains it.
- The 11:46 run also shows a cloud over pad B at its tick 0, before its own EMP: the cloud of pad A's EMP had spread 40 cells.

What is not known: which code draws it (vanilla 1.6's EMP, or another mod on this tier, such as the Vanilla Expanded or
EBSG frameworks). sc_blast_show decides no bar on it: its emp_soil rows read our scars, and those passed.
