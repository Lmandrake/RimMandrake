# Design rows build 2026-10-09

(skeleton; per item below)
- CB-2 HERD_DEFENDS_OWN_YOUNG_1: already built at c46d8afb1 -> reconcile/implemented.
- CB-1 CREATURE_ALARM_ORIGIN_SHARE_1: edited RM_CompReactionSource (+toggle alarmOriginRespondsFirst); build pending.
- CB-4 DUNG_HATCH_WILDLIFE_CAP_1: edited RM_CompDungSeeder (+toggle dungHatchRespectsWildlifeCap); build pending.
- CB-1, CB-4 pushed 6ce1d9009; CB-2 reconciled c46d8afb1.
- TB-3 TWILIGHT_WELL_AVOIDS_CURRENT_1: WellLedger.IsChannelBed asks ChannelCurrent.HasCurrent (toggle). built.
- TB-2 SALT_TRAVELS_WITH_DOOR_1: two-strike prune + minified doors (grace, not literal on-door salt; no toggle). built.
