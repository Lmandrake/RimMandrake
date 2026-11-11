# Actual call trace

Search across FlowWorks found no ToggleRails symbol. The current public setter is SetRailings.

RailingGizmo captures want = !r.railings when creating a Command_Toggle. Its toggleAction calls the bridge component's SetRailings(r,want); the same captured request is safe when invoked again by multi-selection. SetRailings early-returns when r.railings already equals on, otherwise updates the record and visits every lane and index 1..LastDeck.

The on arm calls PlaceRailing for a walkable deck or an existing built railing; the off arm calls RemoveRailing unconditionally. PlaceRailing is also called by Notify_DeckBuilt when the owning record requests railings. RailedAt delegates to actual BuiltAt<Building_SuspensionRailing>; it is also read by the fall and jump protections, which are not changed. RemoveRailing enumerates a copy: rail blueprints/frames are cancelled; built rails vanish under god mode or receive a Deconstruct designation in player mode, only if one is absent.

Old PlaceRailing returned at the existing-railing check. New branch visits actual Building_SuspensionRailing objects in that cell, deletes only DesignationOn(existing,Deconstruct), then returns before all placement paths. Missing railing def still returns immediately. Blueprint/frame duplicate guard, RailingStuffFor, style application and actual god/player placement remain byte-for-byte unchanged. All unrelated designations and things remain untouched.

Raised-leaf admission uses RailedAt OR DeckAt, rather than replacing DeckAt with StructuralDeckAt: it reaches existing railings on a raised leaf without enabling new plans on empty raised cells. Actual Building_SpanDeck.Decked is !collapsed && Spawned && !Raised, read by RM_SpanUtility.DeckAt in the same source file.

Existing ProofRails forced god mode and therefore could not reproduce queued Deconstruct. Its optional third field ;player now temporarily disables god mode for the actual SetRailings call and restores the prior mode in the existing finally. Two-field callers retain god behavior and the old output shape. ProofSpan independently reads the record's railings flag. Live identity/designation readers are existing bridge tools; no new companion API was invented.

Unchanged idempotence means an already-stuck old save with railings=true is not automatically healed by repeating true; an off/on cycle is required. This repair targets the explicitly frozen off/back-on scenario. Cancellation also applies to a manually queued Deconstruct on that railing; there is no designation provenance distinction. Notify_DeckBuilt now shares that cancellation when a railing already exists.
