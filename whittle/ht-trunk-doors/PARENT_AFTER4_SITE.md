# After4 site refusal — bounded setup repair

After4 startup was clean (zero exceptions/config/parse errors) following Steam validation; no causal repair claim. The functional script loaded/snapshotted the disposable site, then correctly refused clearing because three existing player Baseliner colonists fall in the broad96x30 bounding rectangle. Restoration succeeded with no errors; driver stopped/released.

Parent extracted only baseline IDs/positions/type into parent_admin/after4-existing-pawns.json from the raw calls. This is a SITE/HARNESS layout issue, not observed trunk behavior.

A small option is to clear only the disjoint workshop/control plots, with a per-plot empty-pawn check, while retaining the broad rectangle for baseline/restoration accounting. Workshop and control roots are far apart; the currently fixed gravship contact can stay175,111 if its plot is safe. Preserve untouched existing Things outside owned plots. Existing disposable player colonists can be temporarily isolated by drafting after the scene-begin snapshot if needed, recording their prior state and proving exact restoration afterward. Do not kill baseline pawns or let them wander into the work fixture. No need for an unrelated C# coordinate redesign if the existing geometry can be staged safely.

Use your source/site evidence for the smallest sound repair. Keep the occupied-workshop/natural growth/unforced real cutting and restoration bars unchanged, and retain this nonpass. Ask for a parent commit if any production script/source changes; C# rebuild only if actual runtime inputs change.
