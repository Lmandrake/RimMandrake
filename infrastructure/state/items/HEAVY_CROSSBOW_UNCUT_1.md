## spec
🔴 **OWNER, 2026-08-22: *"Agreed on the BS_ items."*** `VFEM_Bow_HeavyCrossbow` (Big and
Small - Races) is the **sole surviving carrier** of `BS_CrossbowTag`, and three
combatPower-120 kinds name it: `BS_CrossbowDvergr`, `BS_Crossbowman`,
`BS_DvergrTraditionalist`.

Their two other tags cannot save them: `VFEM2_Arbalest` needs *VFE Medieval 2* and
`DankPyon_Arbalest` its own mod, and **neither is installed** — measured, both defNames are
absent from the capture. All three kinds were arriving bare-handed.

## verify
- the live Cherry Picker config reads **1342** `<li>`, down from 1343
- `VFEM_Bow_HeavyCrossbow` does not appear in it
- the `deployed/config/v1_freeze/` mirror is byte-identical to the live file
- on the NEXT dump, `BS_CrossbowTag` has 1 carrier and the three kinds leave the
  `weapon_tag_audit` disarmed list

## criteria
CHECK, next load: spawn `BS_Crossbowman` 5 times; all 5 hold a heavy crossbow.
