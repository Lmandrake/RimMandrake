ColdStorageGateExtension's External gate reads a 'Type:field' setting by reflection and treats an unreadable one as OPEN, so a typo silently leaves a station always on. selftest_coldstorage seal_static_checks now resolves every settingField/chanceSettingField to a public static field in ColdStorage or TheSump source (mutant-proven).
home: NONE
