DRY WALK plan: disposable, a rehearsal of the shape.

Structure: one order Gizmo on a commandable creature; a per-pawn order record, saved; a JobDriver for digging that reuses the Shovels rule's check.
Reuse: Shovels (its tool check, not a copy); vanilla Mine designation only for the cell's state, never for job pickup, since pickup is the work-toggle the concept rejects.
Order: dig_order_probe first; one_creature_digs; refused_at_click; no_bare_paws; resumes_same_order; no_work_toggle; order_cost; first_walk.
Risks: a Gizmo on an animal outside player control may not draw; interrupted-job resume collides with vanilla's job queue; how a creature holds a shovel (a stat, an inventory item) is unsettled.
Three designs: a queued order on the pawn (chosen); a one-pawn-reserved designation; a work type with a whitelist. The third is the rejected one.
The agent picks: one tamed animal for the first spike, the waiver leaves it to the agent.
