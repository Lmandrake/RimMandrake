## spec
**A choice only the owner can make.** `XENOTYPE_TOLERANCES_DEPLOY_1` took our six authored
xenotypes as far as vanilla's *realistic* genes go: **−4 … 46 °C** (Wookiee −14 … 46).

**Ash'karr runs −82 … +66 °C, and its habitable p05…p95 is −64 … +57.** So our own species are
still not adapted to most of their own planet. Three ways forward:

| | what it costs |
|---|---|
| **A. Leave it at −4 … 46** | Natives are hardier than offworlders but still need clothes and heat off the temperate band. **Keeps temperature as a real survival pressure.** Costs nothing and is already deployed. |
| **B. `MinTemp_HugeDecrease` (−300 °C)** | One vanilla gene swap ⇒ our species become **effectively immune to cold**. Consistent with *"we aren't trying to model dying in the wrong temperature at this time"*, but it deletes cold as a threat for the player's own colony, permanently. `biostatMet −3`. |
| **C. A custom `GeneDef`** | A band tuned to exactly this planet, at any metabolism cost we choose. ⛔ **A new def is CONTENT, so this is BUILD's to make**, not DECIDE's — it needs an item filed for him. |

🔑 **DECIDE's recommendation: A for now, C if it proves wrong in play.** B is one line and is the
tempting option, but cold immunity cannot be walked back once the campaign is balanced around it,
and the load that would tell us whether A is actually painful has not been run yet. **A is the only
one of the three that keeps the question open.**

⚠️ **This is NOT a blocker.** A is deployed and the game is playable. Nothing waits on this.

## criteria
- [ ] The owner picks A, B or C.
- [ ] If C, an item is filed for BUILD to author the gene.
