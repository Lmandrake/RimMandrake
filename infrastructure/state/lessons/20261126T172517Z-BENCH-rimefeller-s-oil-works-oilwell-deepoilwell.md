Rimefeller's oil works (OilWell, DeepOilWell, OilStorage, CrudeCracker, RefineryLoadingBay) inherit designationCategory from abstract parents (BasedRimefellerMom, ChemfuelHopperBase), so a PatchOperationRemove on the child's designationCategory matches nothing. Add an empty <designationCategory/> to the child instead: an empty def node loads as null (Verse.DirectXmlToObject, InnerText.NullOrEmpty sets the field null).
item: OILGAS_BUILDABILITY_EXCISE_FOUND_NOT_FORGED
home: skills/rimworld-modding/references/project-engine-facts.md
