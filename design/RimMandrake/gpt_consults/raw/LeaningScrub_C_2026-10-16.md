SUBJECT: LeaningScrub (RimWorld 1.6 mod, C# + XML defs). Slice: LeaningScrub_C.

1. **Three admitted venomvine forms are missing from the natural roster**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/LeaningScrub/Defs/BiomeDefs/RM_LeaningScrub_Biome.xml:218–220`, end of `wildPlants`:

   ```xml
   <RM_SleeperVenomvine>0.01</RM_SleeperVenomvine>
   <RM_Salvessa>0.22</RM_Salvessa>
   </wildPlants>
   ```

   `RM_StranglerVenomvine`, `RM_WeeperVenomvine`, and `RM_LureVenomvine` all have complete definitions, including wild-cluster tuning, but **none appears anywhere in this biome’s `wildPlants`**. Of the four forms introduced together in `RM_VenomvineFourForms.xml`, only Sleeper is wired into the roster. Ordinary biome plant selection therefore cannot select the other three.

   **Repro:**
   1. Parse the supplied biome XML.
   2. Enumerate the element names under `BiomeDef/wildPlants`.
   3. Check membership for Strangler, Weeper, Lure, and Sleeper.
   4. The first three fail; Sleeper passes. Repeat against the resolved biome in-game to detect any compensation by other patches.

   **Confidence:** high for the missing roster entries. This does not establish that omitted C# or other patches never spawn them.

2. **Salvessa assigns `sowTags` twice**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_Salvessa.xml:30` and `:42–43`, `RM_Salvessa/plant`:

   ```xml
   <sowTags Inherit="False" />
   <sowTags>
     <li>Ground</li>
   ```

   These are two sibling declarations of the same field. The inheritance-reset directive belongs on the populated declaration. As written, this is a duplicate-field XML configuration error, rather than a single explicit replacement of the inherited list. It also violates the supplied validation walk’s clean-load requirement.

   **Repro:**
   1. Load the mod with developer logging enabled.
   2. Inspect startup XML diagnostics for duplicate `sowTags` in Salvessa.
   3. Independently, parse the supplied file and count `ThingDef[defName="RM_Salvessa"]/plant/sowTags`; the count is **2**.
   4. Inspect the resolved sow tags before trusting either this plant or reskins inheriting from it.

   **Confidence:** high for the duplicate declaration; medium for the precise diagnostic and surviving value without running the 1.6 loader. I am not claiming sowing necessarily fails.

## Outside this slice

The following are concrete inspection targets, **not established runtime findings**:

- **Weeper explicitly carries the contact-poison configuration despite promising harmless passage.**  
  `src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_VenomvineFourForms.xml:112–114`:

  ```xml
  <li Class="RimMandrake.EnvironmentalHazards.CompProperties_ContactVenom">
    <damageDef>RM_VenomvineScratch</damageDef>
    <damageAmount>3</damageAmount>
  ```

  Its description says, “It is not dangerous to pass.” Test a healthy, unprotected adult walking through a mature Weeper and remaining for at least 2,500 ticks. **Confidence: medium:** the contradictory configuration is visible, but whether the shared contact implementation exempts this form requires its omitted source.

- **Dripping’s ordinary harvest designation needs checking.**  
  `src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_LeaningScrubVenomvineForms.xml:52–54`:

  ```xml
  <harvestedThingDef>RM_RawVenom</harvestedThingDef>
  <harvestYield>3</harvestYield>
  <harvestWork>250</harvestWork>
  ```

  The definition supplies no `harvestTag`. Inspect its resolved `plant.harvestTag`, then attempt an ordinary Harvest designation on a mature stand. **Confidence: medium:** a missing effective tag would obstruct the standard harvest path, but the parent definition and startup mutation code are absent.

- **Whipfuzz declares a harvest without naming a product.**  
  `src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_LeaningScrubFuzzFlora.xml:55–57`:

  ```xml
  <harvestTag>Standard</harvestTag>
  <harvestYield>1</harvestYield>
  <harvestWork>30</harvestWork>
  ```

  Inspect the resolved `plant.harvestedThingDef` and try harvesting a mature Whipfuzz. **Confidence: medium:** the local declaration has no product; the unseen parent could supply one.

There are no C# implementations in this slice. Save round trips, stale references, tick scheduling, settings cleanup, Harmony ordering, and component lifetime cannot be responsibly diagnosed from these XML declarations or the validation document.