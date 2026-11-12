What can stand on a gravship deck is decided by the FOUNDATION: GridsUtility.GetAffordances returns FoundationAt(c).affordances when a foundation is present, and Odyssey Substructure (merged through FloorBase) gives Light, Medium, Heavy, Walkable, Substructure. So floors (Heavy) and ordinary buildings lay on a deck; Bridgeable/GrowSoil/water needs do not; plants root by fertility (0 on a deck); a def with bringAlongOnGravship false stays behind (Gravship.cs). src/RimMandrake/Utils/ship_contributions.py encodes this.
item: BIOME_SHIP_CONTRIBUTIONS_1
home: skills/gravship-layout/SKILL.md
