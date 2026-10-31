# Calls agents made without you: the ones you might overturn

Audit of the four digests, 28 to 31 October, 1,337 calls. Six are worth a look. Nothing was changed by this audit. Every call below was checked against its full record, not its digest line.

To overturn any of them, say so in a line, such as "put the herd back on me". A seat records your words and undoes it.

## Calls you might want to overturn

**1. Nine creatures you kept were redrawn, and you were never shown.**
- **Decided:** the art pipeline replaced kept pictures of Ullai, Emberscythe, Barbslinger, Suush, Bileworm, Crystal Mit, Furnace Beast, Truffle Mole and Fire Wasp, 23 pictures in all, between 23 and 28 October. All nine are still in the game.
- **Why reverse:** you allowed this with "Yes, but show me after". None of the 29 shadow sheets still on disk flags these swaps. A bug hides the flag when a redraw is accepted. It was filed on 26 October and is still unbuilt (SHADOW_KEPT_SWAP_ENFORCE_FLAG_ON_ACCEPT). Only Coolant Eel was flagged to you.
- **To reverse:** a revert command is on file for each creature. Ask for a sheet of old beside new, and name any to restore.

**2. Four looks you owned now go to an agent judge.**
- **Decided:** on 29 October these four were lowered from your live look to an agent's check: the boar's bright square in the pit, the Bleed Well switch, the hose reel link, and the reel nozzle. You see them on your next walk as feedback, not as a gate.
- **Why reverse:** the delegation policy says those live-look criteria are yours by definition, and that loosening a bar stays with you. You reported or decided these yourself.
- **To reverse:** put the look back as yours. All four are built and waiting, so nothing is lost.

**3. Your herd arbitration and creature walk were handed to agents.**
- **Decided:** on 8 October you said "ticket an item for me to go in and arbitrate the rest" (45 unclear creatures), and asked for a walk through the custom creatures. On 29 October a triage first confirmed the arbitration as yours. Forty minutes later the Conductor moved both to a judge, with provisional group sizes.
- **Why reverse:** you asked to do this yourself, and it was reversed in one night. Items: CANON_HERD_LORE_ARBITRATION_1, BIOME_GROUP_SIZE_WALK_1.
- **To reverse:** return both to you. Neither has started.

**4. The Chill surface sitting no longer needs you.**
- **Decided:** your September card made this "its own sitting with the owner". An agent now picks the guardian's place and adds shore ecology, with one optional card (CHILL_SURFACE_SITTING_1).
- **Why reverse:** you chose a joint sitting, and this is a world-shaping choice.
- **To reverse:** return it to you. It has not started.

**5. Nightside Ice's new life gets a judge instead of your ruling.**
- **Decided:** the finish line said it "carries the owner's keep/cut/change ruling". It now says a judge's verdict, listed in your digest, and your sheet sitting is gone. Four new organisms: saallen, oolm, neshkoll and the ice-kept dead (NIGHTSIDE_ICE_NEW_LIFE_1).
- **Why reverse:** agents rewrote a line that named you, and the build follows the judge.
- **To reverse:** restore the old line. Not built yet.

**6. A fourth redraw round for the Modern pipes went ahead (weakest of the six).**
- **Decided:** the question "allow round 4?" was addressed to you. It was ruled a cost and scope call, because the defects left are fit, not style (MODERN_FIT_REDRAW_ROUND_FOUR_PENDING).
- **Why reverse:** the policy sends anything still failing after three rounds to your sheet. You may want to see it first.
- **To reverse:** stop it and send the three-round results to your sheet. Not started.

## Everything else, one line per class

- **Art:** judges ruled on 606 pictures (347 redo, 161 accept, 36 sent up, the rest held or other), and 116 installs went in. Beyond the nine above, none is listed here. I checked kept-art replacements, not the taste of each verdict.
- **Design:** routine numbers, lore and layout, most from the 29 October queue triage you ordered. Those not listed above stay within policy.
- **Scope and technical:** closures, reroutes and fixes. No drop removed something you asked for.
- **Leftovers:** 43 saves, 22 settings backups and one old clone, 15.8 GB. All 66 archives exist, each with proof, so all of it can be restored.
- **Bridge use while you were idle:** hose, levelling and pit test runs, all after the required 20 idle minutes, and none flying.
- **Unclassified:** mostly bug, test and tooling work whose reason named no policy class. Nothing cannot be undone.
- **Repeated reversals:** only item 3. A few files were installed, reverted and reinstalled within 16 minutes, ending where they began.

## Counts by class (measured from the digests)

| Class | 28 Oct | 29 Oct | 30 Oct | 31 Oct | Total lines | Without repeats |
|---|---|---|---|---|---:|---:|
| Art | 772 | 23 | 0 | 0 | 795 | 788 |
| Unclassified | 217 | 8 | 0 | 9 | 234 | 230 |
| Design | 109 | 35 | 1 | 1 | 146 | 135 |
| Leftovers | 67 | 0 | 0 | 0 | 67 | 67 |
| Bridge idle | 57 | 5 | 4 | 0 | 66 | 66 |
| Technical | 2 | 27 | 0 | 0 | 29 | 29 |
| Scope | 7 | 9 | 0 | 1 | 17 | 17 |
| Cosmetic | 1 | 4 | 0 | 0 | 5 | 5 |
| **Total** | **1,232** | **111** | **5** | **11** | **1,359** | **1,337** |

Only commit lines repeat: the 22 in the 28 October digest appear again in the 29 October one. The other records do not overlap.

## The nine bridge acts on 30 October with no class

Automated arena trial runs. They took the bridge between 16:31 and 18:01 UTC, when it was free or already ours, for pilots L8 and L9 of the trio arm. They were logged as "bridge free", a wording the digest does not count as a class. None involved flying.

## What this audit could not see

- **Missing from the digests:** 20 calls from the 29 October triage (14 drops, 3 reassigns, 2 supersedes, 1 close). Their reason starts differently, so the digest skips them. I read them. The herd reversal in item 3 begins there.
- **After the digests:** the twelve questions cleared today are listed at the end of `D:\Luke\dev\RimMandrake\Transient\owner_pile_2026-10-31.md`. I did not audit them.
- **Not proven:** that no bridge take overrode a hold you had set. Deleted sheets could also have carried the flag in item 1, though the code bug makes that unlikely.
