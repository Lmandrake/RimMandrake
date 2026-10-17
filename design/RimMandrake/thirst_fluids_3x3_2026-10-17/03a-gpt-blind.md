1. **Three different logistics models**

| Model | Mouths, crops, machines | Trade-offs; when it dominates |
|---|---|---|
| **Portable supplies** | Pawns carry bottles; haulers supply bucket caches and stationary barrels. Growers water patches from buckets; operators fetch complete machine batches. | Visible labor and vulnerable supply lines. Best for small colonies, tribal starts and expeditions; expensive at agricultural scale. |
| **Fixed utilities** | Pipes supply neighborhood bottle-filling taps, sprinklers and machine buffers. Canals serve irrigation. Pawns carry drinking reserves. | Lowest recurring labor; construction, contamination and outages become the challenge. Best for established settlements. |
| **Scheduled service** | Consumers request deliveries below minimum stock. Workers run batched routes: exchange bottles, refill field cisterns, connect hose reels and replenish machine buffers. | Fewer permanent connections, but delivery delays matter. Best for scattered bases, temporary operations and intermittent industrial demand. |

These are alternative defaults; combining them should remain possible.

2. **Concrete rules**

Everything below is a proposed balance default unless already ruled.

**Classify liquids by permitted use, separately from hazards.**

| Class | Rows and behavior |
|---|---|
| Potable | Clean fresh water; individually approved mineral waters. Colour never establishes safety. |
| Treatable, currently non-potable | Contaminated fresh water, salt water, brine, toxic water; boiling/icy water until a defined conditioning process makes them safe. Treatment recipes must specify what they remove. |
| Emergency ingestion | Four slimes; salt water exclusively through its desperation state. |
| Industrial/restricted | Acid water, propane, chemfuel, tar, lava, reaction liquor, astrofuel and blood. Never ordinary thirst targets. Blood’s hemogen use requires a separate rule. |

Track contamination independently: a dirty bottle can spoil otherwise potable water. Unknown liquids default to restricted.

**Gathering:** automatic collection targets potable sources only. Non-potable extraction—including powered pumps—requires a player order specifying liquid, destination and quantity, or an explicitly authorized repeating bill. Machine demand cannot create that permission. Emergency drinking consumes directly; it never silently creates a hauling order.

**Drinking:** prefer carried bottle → nearby filled bottle/refill → bucket → tank tap → barrel. Compare travel costs so a distant bottle cannot defeat urgent local drinking. Bottles hold 1.5 L: two provide an ordinary adult’s daily 3 L; heat may require six.

Buckets remain normal drinking vessels. Tank/barrel drinking gives **−3 mood for six hours**, refreshing without stacking, when no practical bottle option exists. An inaccessible or dirty bottle does not qualify.

**“No potable available”** means no usable amount—suggested minimum 0.25 L—in inventory, reachable permitted containers, functioning taps or directly drinkable terrain. Respect prison boundaries, ownership, forbidden status, danger and actual access. Include immediately available refilling; exclude hoped-for hauling, construction and treatment. Brief reservations trigger waiting/rechecking, not instant slime drinking. Show the blocking reason.

**Slime:** eligible below 10% thirst only after that check fails; recheck before swallowing. Give all kinds **−25 mood for one day** and a distinct **24-hour laxative hediff**: periodic bowel incidents and +50% thirst depletion. Repeated doses refresh duration and increase severity within a cap.

- **Red:** mouth/stomach burns, pain and reduced eating capacity; this follows its fictional burning property, not pH alone.
- **Green:** irritant digestive injury. Organ rotting would extend “rots immersed objects” and needs owner approval.
- **White:** temporary flammable residue, increasing injury if subsequently exposed to fire; swallowing alone never ignites it.
- **Yellow:** additional nausea/vomiting. Literal mucus does not automatically establish infectious disease.

**Salt desperation:** after six continuous hours at empty thirst, no potable access and reachable salt water, enable a custom mental state with a suggested 12-hour mean waiting time. No low-mood requirement. It drinks one 0.5 L dose, then ends with a one-day cooldown. Brief perceived relief lasts one hour without resetting dehydration progression. A dose-based **salt poisoning hediff** progresses through nausea/thirst, impaired consciousness and movement, then seizures/coma/death. Potable hydration and doctor treatment reduce severity; repeated doses worsen it. Brine remains excluded unless explicitly approved.

**Hardy exemptions:** Ascetic is the strongest trait fit. Tough is an optional flavor exemption; its vanilla effect concerns damage. Iron-willed and Steadfast concern break thresholds. These are proposed extensions, not existing drinking effects. [Trait reference](https://rimworldwiki.com/wiki/Traits)

Robust digestion optionally exempts bottle etiquette; Strong stomach prevents food poisoning, not the mandatory slime laxative or chemical injury. Pigskins carry both genes; use active genes rather than xenotype labels. [Gene reference](https://rimworldwiki.com/wiki/Genes), [Pigskins](https://rimworldwiki.com/wiki/Pigskins)

Tox immunity can block toxic buildup; antitoxic lungs cannot protect against ingestion. Neither establishes salt, acid or slime immunity. [Resistance reference](https://rimworldwiki.com/wiki/Genes)

Map “wild” to actual wild humans, including Run wild until tamed. Tribal factions, Neanderthals, Dirtmoles and low technology do not inherently mean uncivilized. Offer an explicit ideology/precept exemption. [Run wild reference](https://rimworldwiki.com/wiki/Mental_break)

3. **Traffic and edge cases**

- **Batch work:** refill below 25%, target 90%; combine bottle washing/refilling and nearby deliveries. Reserve liters and interaction slots, not whole reservoirs. Failed jobs release reservations and back off.
- **Storage:** empty → filled → dirty after emptying → washed/clean-empty. Washing consumes water and work. Block dirty refilling by default. Reject mixed liquids unless an explicit recipe exists; retain hazardous residues.
- **Bulk:** a water-filled barrel weighs roughly 208 kg before its container. Keep it stationary unless supported transport exists. Buckets serve local transfers; hoses serve sustained bulk transfers. Reels need reachable connection points, occupied hose routes and interruption cleanup.
- **Crops:** start at 0.25 L/growing cell/day, with two-day soil storage and rain replenishment. Dry soil halves growth rather than instantly killing crops. Water patches, never individual plants. Hydroponics uses basin buffers.
- **Machines:** reserve a complete recipe’s liters before starting; consume once at a defined commitment point. Separate potable and industrial networks. Protect drinking/medical reserves before irrigation and industry; include washing and firefighting in demand accounting.
- **Prisoners:** cell-accessible supplies; wardens deliver. Locked external tanks do not count. **Guests:** explicit guest access and consumption budgets. **Hostiles:** use accessible supplies without receiving colony logistics jobs.
- **Downed/babies:** patient/childcare hydration jobs. Mobile children self-drink; hazardous hauling requires age/capability limits. Drafted pawns need carried reserves and warnings.
- **Animals:** preserve pond/river-only drinking. Detect dry pens and frozen access. Caravans need explicit natural-water stop accounting or portable-water exceptions; never silently waive thirst.
- **Frozen/orbital maps:** unavailable sources count unavailable. Use vanilla ambient temperature only; no separate liquid heat simulation. Define conditioning/freezing transitions explicitly.
- **Dubs:** relinquish FlowWorks thirst, drinking AI and desperation triggers. Supply integration must feed Dubs’ systems without duplicate consumption or health effects.

Every feature gets a Mod Settings toggle, with numerical controls where relevant. Disabling features must clean up jobs/hediffs safely; require an explicit choice for stranded liquid.

4. **Owner decisions**

Decide mineral-water safety; direct terrain drinking and its mood effect; emergency forbidden-area overrides; animal caravan/frozen-water handling; green-slime organ damage; blood/hemogen behavior; crop-water severity; and special hydration rules for ghouls, deathrest and other suspended states.

5. **My pick**

Use **fixed utilities with scheduled service at disconnected endpoints**. Bottles handle personal mobility, buckets handle startup and outages, stationary barrels provide buffers, and pipes/hoses absorb agricultural and industrial volume. Scarcity then creates meaningful infrastructure decisions without making every liter a separate pawn trip.