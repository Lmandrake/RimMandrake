## finding (GPT full-file review consult-20261103-012453-2258476, during CRACKEDLANDS_THREE_HEIGHT_FLORA_1)
`RM_MapComponent_RecedeAftermath` keeps ONE deadline for the irqit cohort (`cohortDieTick`) and ONE for floodline
salvage (`salvageExpireTick`), but both lists accumulate across floods. Each new recede overwrites the deadline, so an
earlier batch lives as long as floods keep coming (or dies early when decay settings drop).
## fix
A deadline per cohort batch / salvage claim, scribed; expire only entries past their own deadline; migrate old saves
from the saved aggregate deadlines. Offline: a kernel test over overlapping floods.
