# Next version — switched off

These are the Designer's scope decisions under the cleansing brief. Earlier approvals remain evidence for a future version, not a default-on obligation here. Built code/defs stay resolvable behind their named gates. Ordinary species and their roster placements stay; no feature is retired by this proposal.

### dewsilk
Tamed mirrik's vanilla shearable comp yields two cocoons every six days; tailor recipe spins dewsilk fabric with heat-insulation data. Startup setting removes the shearable comp when off.

Why later: Cocoon-to-cloth manufacturing is an independent export loop; deleting it leaves the native flier, farm, food and land intact. Feed has no cocoon-waste dependency in code. Switch/spec: T1.

### condenser unique
One-per-world spawn latch creates old gorrask on an RM_WeepingStones map's FinalizeInit; saved world flags, season timing and choice letter. Ordinary gorrask remains separate. Initial spawn is local map init, not a world migration event.

Why later: A unique quest-bearing animal is a second system, not ordinary gorrask wildlife or a necessary part of a fish farm. Ordinary RM_Gorrask remains. Switch/spec: T2.

### condenser pool
Seasonal Settled/Waiting/Walking machine grows shallow-water cells, rebuilds truce, letters drying and restores recorded terrain over days on ordinary moves. Protects floors, foundations, edifices and temporary terrain; restores under bridge layers; death/despawn dries immediately and avoids cross-map coordinate restoration.

Why later: Seasonal mobile terrain creation/removal is a second signature. Fixed landmark pools already supply land and the farm. Switch/spec: T3.

### guide
Season-choice Guide sets a reachable site near a random home-area cell (else first colonist), rejection message if no site, then phase machine orders movement. Choice letter removes itself only when action succeeds.

Why later: Guiding a migrating oasis only serves the deferred walking condenser. Switch/spec: T4.

### sell action
Season-choice Sell selects friendly humanlike faction by goodwill, saves buyer and expiry, pays fixed 1500 silver on a surface home map and grants goodwill. This implements a sale action, not fulfilment of the buyer-settlement pool promise or a highest-bidder auction.

Why later: Selling a seasonal destination is a separate faction trade action. The farm and normal caravan trade do not call it. Switch/spec: T5.

### extract plant
Season-choice extraction dries pool, ends moving-oasis world flag, creates/minifies ancient plant, kills crab and letters the loss. No physical surgery job; placement result unchecked; no guilty damage attributed to colony in this action.

Why later: Killing a unique crab to extract portable machinery is a separate salvage choice. It is not required for fish-farming tools. Switch/spec: T6.

### water plant
Portable unpowered rare-ticking building accumulates time, produces RM_CondenserWater flasks with nearby cap and bounds-checked scans; saved accumulator. Flasks are resources; no thirst or ship life-support consumer inferred.

Why later: Portable flask production is its own water-resource loop with no farm feed consumer; do not conflate it with OasisMaker. Switch/spec: T7.

### capture quest
Optional random offer gated on living undowned unclaimed crab on player-home map; deadline to subdue, downed watcher, offstage live transfer to world pawn, ends oasis, rewards/goodwill and sad letter; death/hostility/map loss/timeouts fail.

Why later: An optional collector quest is expressly an extra, even though previously approved and built. Switch/spec: T8.

### keep free quest
Optional 10–15-day survival contract with two hunter raids targeting crab, trophy motive letter, rewards and settlers goodwill; normal water truce reused. Success text promises walking on and farmers sharing water; code does not stage their presence or prove freedom/departure.

Why later: A trophy-hunter defense contract adds raids, faction rewards and freedom adjudication outside the farm chain. Switch/spec: T9.

### quest claim slots
Mutually exclusive accepted quest claim, synchronous rival withdrawal, cleanup/reoffer after failed claim, success settlement; faction slots exclude unusable/self relations and select vanilla fallbacks. Campaign prepends Hutt buyer; settlers/hunters use existing reskins.

Why later: Mutual quest claims and faction slot mappings serve only the deferred contracts; no kept gameplay needs them. Switch/spec: T10.

### sale delivery
Promised buyer-settlement pool/arrival/rights fulfilment is absent from sale implementation; recorded buyer fields alone do not provide it.

Why later: Delivery, rights, refund and failure semantics belong with the deferred sale; a payout field is not delivery. The next-version design default is payment on actual inhabited-site fulfilment, otherwise cancellation. Switch/spec: T22.

### refused toll later
The Refused Toll remains campaign v2, not part of this v1 root or question bank.

Why later: Already deferred by OWNER:1792755168241448197; do not reopen it or modify the no-absentee-toll law. Switch/spec: none: no separate build or switch-off required.

### huldu fat
Rendered huldu fat recipe/item; proposed generic meal-quality improvement is not implemented.

Why later: A second refinement product/quality bonus adds nothing necessary to the farm-to-food choice already served by meat and thoughts. Switch/spec: T11.

### rare loot
Seep-stone and silver special angling rewards.

Why later: A bonus loot lottery is neither ordinary catch life nor the signature husbandry chain. Switch/spec: T21.

### shade study
Dripfringe and shadefern found-tech study hooks injected by EnvironmentalHazards.

Why later: Study-based research progression is an independent interaction. Ordinary plants and geometric shade work without discovering a technology. Preserve the shared engine. Switch/spec: T23.

### recapture ladder
Fin/shield/enclosure/servo-vent settlement progression beyond ordinary roofs; the separate redirected OasisMaker is not commissioned here.

Why later: Active water-budget progression is a second system. Keep ordinary architecture and ruin dressing; redirected OasisMaker is a neighbour, not a new commission. Switch/spec: T24.

### pilgrim routes
Coordinated between-oasis visitor routing, gifts and water-rotation choreography.

Why later: Ordinary wildlife and traders already populate the water; custom visitor schedules/tokens are extras. Switch/spec: T24.

### courtship
Custom fan-dances, romance and bonding events at water.

Why later: Normal reproduction/taming supplies ordinary life; custom ceremonies add a separate interaction. Switch/spec: T24.

### sillik face feeding
Sillik vertical-face movement and shade-only film feeding beyond ordinary animal needs/placement.

Why later: Ground habitat placement and ordinary feeding suffice for this version; vertical climbing/film feeding is an independent behaviour and the source explicitly leaves its shared comp unwired. Switch/spec: T24.

### mirrik swarm
Custom mirrik vermin-breeder swarm/pollination activity.

Why later: A moving flying native remains life without a bespoke population/pollination subsystem. Do not build another breeding engine for flavor. Switch/spec: T24.

### burrak digs
Burrak terrain-changing catch-basins and wells.

Why later: Already later in ruled roster; ordinary animal/wallow fiction does not require generating water. Switch/spec: T24.

### giant geometry
True canyon-sized multi-cell gorrask occupation.

Why later: Already a follow-on; ordinary legendary crab stays and no multi-cell navigation system is commissioned. Switch/spec: T24.

### species catch methods
Separate whistle-call, basket-trap, night-lift and airborne skarrin handling jobs.

Why later: Common thrown-net/catch jobs with species risk complete the signature; separate input verbs would be extras. Flight remains mandatory for any creature still described as flying. Switch/spec: T24.

### cooperative cull
Coordinated multi-handler vhorrin cull.

Why later: A deliberate cull completes recovery without a second actor coordination system; keep the documented small implementation, no waiver re-question. Switch/spec: T24.

### crash year
A fixed year-long stock lockout after overdraw.

Why later: Visible stock loss, breeder reserve and restocking give overdraw a cost; an annual embargo is a separate punishment clock and would obstruct recovery. Switch/spec: T24.

### doubt extensions
Keeper-specific double penalties, colony-wide feast event, named roasts and ideology bless/ban.

Why later: Actual eater/ingredient/trait thoughts fulfil the binding doubt economy; additional social and ideology systems do not. Ideology hook explicitly left to later passes. Switch/spec: T24.

### aeolian chords
Unique array chords, dead-oasis silence signalling and proximity navigation audio.

Why later: Ordinary calls/wind belong to land/life, but authored per-oasis identification audio is an extra; farm warnings use the visible gauge. Switch/spec: T24.

### ssurr aura
A bespoke tame ssurr soothing aura.

Why later: Ordinary taming and reproduction preserve the fan-dancer as life; deleting a soothing aura leaves the farm signature and ordinary native use intact. Its optional shared comp is explicitly unwired. Switch/spec: T24.

# Recommended retirement — owner decision only

- **ivvol effect:** No ivvol-specific escape/emergence benefit; current description's absolute protection and old explicit open question are unresolved.
Recommend retiring the unbuilt absolute vhorrin immunity: it deletes the husbandry consequence and is absent from the pulse inputs. Keep ivvol as a creature and doubtful food; superstition remains attributed as such.

# Existing exclusions stay excluded

Wind-hour and born-and-dying-water were killed by the owner in the 2026-09-24 shine verdicts; neither is deferred here. The four-state vane restoration draft was redirected into the separate OasisMaker, not commissioned again. Fish walk, pilgrim passage, dewsilk casket and lying fish were recorded close misses (OWNER:1790972008544599819), not new pitches. The Refused Toll already belongs to later campaign ritual work (OWNER:1792755168241448197). Worldgen is out of every version.
