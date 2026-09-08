# Rites — validation walk
subject: src/RimUtinni/Rites  (packageId `mandrake.rut.rites`)
deps: mandrake.rut.antiquities (own tier, hard modDependency + loadAfter)
list: minimal+mandrake.rut.antiquities
status-hint: the liturgy research tree — five ResearchProjectDefs chained T0..T4, each tier past the Scrap Shrine gated by a hiddenPrerequisites on an Antiquities stage (visible-locked, not hidden from the tree).

## must be true
- ResearchTabDef `RUT_Rites` exists, label "the rites".
- Five ResearchProjectDefs chained: RUT_Rites_ScrapShrine (baseCost 400, techLevel Neolithic, no prerequisites) → RUT_Rites_ConduitChoir (1200, Industrial, prereq ScrapShrine, hiddenPrereq RUT_Antiq_Language) → RUT_Rites_GodSpeakerArray (2600, Industrial, prereq ConduitChoir, hiddenPrereq RUT_Antiq_Religion) → RUT_Rites_HullLiturgy (4000, Spacer, prereq GodSpeakerArray, hiddenPrereq RUT_Antiq_Culture) → RUT_Rites_GodsSpeakBack (8000, Ultra, prereq HullLiturgy, hiddenPrereq RUT_Antiq_Voice).
- All five sit on tab RUT_Rites.
- A tier whose hiddenPrerequisite stage is unfinished cannot be started (CanStartNow false) even once its ordinary `prerequisites` are complete — but it still renders in the research tree (greyed), never disappears from VisibleResearchProjects.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rut.rites"
2. [D] def read-back: ResearchTabDef RUT_Rites exists; label = "the rites"
3. [D] def read-back: ResearchProjectDef RUT_Rites_ScrapShrine — baseCost=400, techLevel=Neolithic, tab=RUT_Rites, no prerequisites
4. [D] def read-back: ResearchProjectDef RUT_Rites_ConduitChoir — baseCost=1200, techLevel=Industrial, prerequisites=[RUT_Rites_ScrapShrine], hiddenPrerequisites=[RUT_Antiq_Language]
5. [D] def read-back: ResearchProjectDef RUT_Rites_GodsSpeakBack — baseCost=8000, techLevel=Ultra, prerequisites=[RUT_Rites_HullLiturgy], hiddenPrerequisites=[RUT_Antiq_Voice]
6. [B] jawa/research_availability {project: "RUT_Rites_ConduitChoir"} before RUT_Antiq_Language finishes → prerequisitesCompleted true (ScrapShrine done) but canStartNow false, unfinished list names RUT_Antiq_Language
7. [B] jawa/research_finish_project {project: "RUT_Antiq_Language"} then jawa/research_availability {project: "RUT_Rites_ConduitChoir"} → canStartNow now true
X. [S] (human pass) confirm a locked-but-visible rite renders greyed in the research tree UI rather than vanishing
