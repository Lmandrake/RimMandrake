from pathlib import Path
root=Path.cwd();p=root/'src/RimMandrake/HugeThings/Source/TrunkDoorValidationHooks.cs'
s=p.read_text().replace('using System.Linq;','using System;\nusing System.Collections.Generic;\nusing System.Linq;')
pos=s.rfind('    }\n}')
s=s[:pos]+'''        /// <summary>Ground-only ClearArea integration control on a declared disposable
        /// fixture contact. Refuses unrelated objects and does not advance time.</summary>
        public static string ClearFixtureContact(string args)
        {
            string[] parts = (args ?? "").Split('|');
            if (parts.Length != 3) return "FAIL expected plantID|x,z|mode";
            string[] xy = parts[1].Split(',');
            int x, z;
            GravshipPlacementUtility.ClearMode mode;
            if (xy.Length != 2 || !int.TryParse(xy[0], out x) || !int.TryParse(xy[1], out z)
                || !Enum.TryParse(parts[2], out mode)
                || (mode != GravshipPlacementUtility.ClearMode.NaturalRockOnly
                    && mode != GravshipPlacementUtility.ClearMode.BlockingBuildingsOnly))
                return "FAIL fixture arguments";
            Map map = Find.CurrentMap;
            IntVec3 cell = new IntVec3(x, 0, z);
            if (map == null || x != 175 || z != 111 || !cell.InBounds(map)) return "FAIL outside declared contact";
            Plant plant = map.listerThings.AllThings.OfType<Plant>().FirstOrDefault(p => p.ThingID == parts[0]);
            var mc = map.GetComponent<MapComponent_HugeFootprints>();
            var things = cell.GetThingList(map);
            Building_TrunkBlocker blocker = things.OfType<Building_TrunkBlocker>().SingleOrDefault();
            if (plant == null || plant.Position != new IntVec3(175, 0, 110) || blocker == null
                || mc == null || !mc.HasCutClaim(plant, blocker) || things.Count != 1)
                return "FAIL contact not exclusively owned fixture blocker";
            GravshipPlacementUtility.ClearArea(map, cell, new HashSet<IntVec3> { IntVec3.Zero }, mode);
            return "mode=" + mode + " plantDestroyed=" + plant.Destroyed + " blockerDestroyed=" + blocker.Destroyed;
        }
''' +s[pos:]
p.write_text(s)

p=root/'src/RimMandrake/HugeThings/northstar/trunk_doors_live.py';s=p.read_text()
s=s.replace("self.field(field).lower() == str(value).lower()", "(float(self.field(field)) == float(value) if field == 'plantTrunkScale' else self.field(field).lower() == str(value).lower())")
s=s.replace("self.rec['door_before'], self.rec['bench_before'] = door[0], bench[0]","self.rec['door_before'], self.rec['bench_before'] = door[0], bench[0]\n        self.rec['walls_before'] = self.things('Wall')")
s=s.replace("plant = self.stage_plant(100, 100)","self.rec['failure_stage'] = 'HARNESS_natural_growth'\n        plant = self.stage_plant(100, 100)")
s=s.replace("self.rec['cut_recovered'] = True","require(self.things('Wall') == self.rec['walls_before'], 'growth/cutting changed existing walls')\n        self.rec['cut_recovered'] = True")
s=s.replace("for _ in range(30):\n            self.ticks(100)","for _ in range(80):\n            self.ticks(100)")
s=s.replace("for x in (125, 140, 155, 175):\n            self.stage_plant(x, 100)\n        self.ticks(2000)\n        self.ticks(500)",'''self.call('jawa/build_batch', ops='SteamGeyser:165,101', faction='none')
        geyser = self.things('SteamGeyser', '165,101,2,2')
        require(len(geyser) == 1, 'indestructible fixture absent')
        self.rec['indestructible_def'] = self.call('jawa/get_defs', defs='ThingDef/SteamGeyser', fields='destroyable')
        require(self.rec['indestructible_def']['defs'][0]['fields']['destroyable'] is False, 'indestructible definition differs')
        for x in (125, 140, 155, 165, 175):
            self.stage_plant(x, 100)
        self.stage_plant(175, 110)
        self.rec['control_growth_samples'] = []
        for _ in range(6):
            self.ticks(2000)
            states = [self.sc('DebugPlantState', 'current|%d,%d' % xy) for xy in
                      ((125,100),(140,100),(155,100),(165,100),(175,100),(175,110))]
            self.rec['control_growth_samples'].append(states)
            if all(kv(state).get('oldEnough') == 'True' and int(kv(state).get('claimed', 0)) > 0 for state in states):
                break
        require(all(kv(state).get('oldEnough') == 'True' and int(kv(state).get('claimed', 0)) > 0 for state in states),
                'HARNESS: controls did not naturally grow claimed contacts')
        self.ticks(500)''')
s=s.replace("[(125, 101), (140, 101), (155, 101)]","[(125, 101), (140, 101), (155, 101), (165, 101)]")
s=s.replace("for x in (125, 140, 155):","for x in (125, 140, 155, 165):")
s=s.replace("require(self.identity(door[0]['id']) == door[0], 'existing building wiped/changed')","require(self.identity(door[0]['id']) == door[0], 'existing building wiped/changed')\n        require(self.identity(geyser[0]['id']) == geyser[0], 'indestructible fixture changed')")
s=s.replace("free_before = self.things",'''clear_plant = self.things(PLANT, '175,110,1,1')
        require(len(clear_plant) == 1 and self.things(BLOCKER, '175,111,1,1'), 'ground ClearArea fixture absent')
        clear_id = clear_plant[0]['id']
        self.rec['ground_clear_negative'] = self.sc('ClearFixtureContact', clear_id+'|175,111|NaturalRockOnly',
                                                   'RimMandrake.HugeThings.TrunkDoorValidationHooks')
        require(self.things(PLANT, '175,110,1,1') and self.things(BLOCKER, '175,111,1,1'), 'NaturalRockOnly cleared giant')
        self.rec['ground_clear_positive'] = self.sc('ClearFixtureContact', clear_id+'|175,111|BlockingBuildingsOnly',
                                                   'RimMandrake.HugeThings.TrunkDoorValidationHooks')
        self.ticks(500)
        require(not self.things(PLANT, '175,110,1,1') and not self.things(BLOCKER, '172,107,7,7'),
                'ground ClearArea left owner or owned blockers')
        free_before = self.things''')
s=s.replace("building=door[0], free_before=free_before", "building=door[0], indestructible=geyser[0], free_before=free_before")
s=s.replace("r.call('jawa/running_mods', assemblyName='RM_HugeThings')","r.call('jawa/running_mods', assembly='RM_HugeThings', details=True)")
s=s.replace("matches = r.rec['running']",'''ids = [x.lower() for x in r.rec['running'].get('packageIds', [])]
        require(len(ids) == len(set(ids)) == 16 and all(x in ids for x in
                ('ludeon.rimworld', 'ludeon.rimworld.royalty', 'ludeon.rimworld.ideology', 'ludeon.rimworld.biotech',
                 'ludeon.rimworld.anomaly', 'ludeon.rimworld.odyssey', 'mandrake.rm.biomes',
                 'mandrake.rm.hugethings', 'mandrake.rm.hugethingstestraces', 'mandrake.rm.flowworks', 'mandrake.rm.patches')),
                'wrong loaded all-five-DLC tier')
        matches = r.rec['running']''')
# Restore process-global settings before loading and advancing restored scene.
start=s.index('        if saved:\n',s.index('    finally:'))
end=s.index("        for pid in r.rec['fixture_ids']:",start)
s=s[:start]+'''        for field, value in r.prior.items():
            try:
                r.setting(field, value)
                require(r.field(field) == value, 'exact setting restoration mismatch '+field)
            except Exception as exc:
                errors.append(repr(exc))
        if r.prior:
            try:
                r.sc('RefreshAllMaps')
            except Exception as exc:
                errors.append(repr(exc))
        if tx:
            try:
                tx.__exit__(None, None, None)
            except Exception as exc:
                errors.append(repr(exc))
        if saved:
            try:
                r.rec['restore_load'] = T.load_site(r.call, 'calm', name=snapshot, check=False, map_controls=('modal_broker',))
                require(r.rec['restore_load']['verified'], 'scene-begin restoration load failed')
                restored = r.sc('Rect', RECT, PROOF)
                restored_pawns = r.pawns()
                restored_extra = r.supplement()
                r.rec['restored'] = dict(rectangle=restored, pawns=restored_pawns, supplement=restored_extra)
                require(restored == baseline and restored_pawns == baseline_pawns
                        and restored_extra == r.rec['baseline']['supplement'], 'restored rectangle/fixtures differ from exact baseline')
                for field, value in r.prior.items():
                    require(r.field(field) == value, 'post-load setting mismatch '+field)
            except Exception as exc:
                errors.append(repr(exc))
''' +s[end:]
# Existing query ignores rect, deliberately filter complete whole-map census.
insert='''    def supplement(self):
        query = self.call('jawa/designate_batch', action='query', limit=10000)
        require(query.get('truncated') is False and query['total'] == query['returned'], 'incomplete designation census')
        rows = [d for d in query['designations'] if 90 <= d['x'] < 186 and 90 <= d['z'] < 120]
        plants = self.things(rect=RECT)
        # Empty target-rectangle plant census is a strong exact growth baseline;
        # refuse a populated plant baseline rather than leave growth unmeasured.
        defs = sorted({t['defName'] for t in plants})
        if defs:
            meta = self.call('jawa/get_defs', defs=';'.join('ThingDef/'+d for d in defs), fields='category')
            require(all(d['fields']['category'] != 'Plant' for d in meta['defs']), 'SITE: baseline rectangle contains plants; growth not covered by Rect hash')
        return dict(designations=sorted(rows, key=lambda d: json.dumps(d, sort_keys=True)), things=plants)

'''
s=s.replace('    def scenario(self, tx):',insert+'    def scenario(self, tx):')
s=s.replace("dict(rectangle=baseline, pawns=baseline_pawns)","dict(rectangle=baseline, pawns=baseline_pawns, supplement=r.supplement())")
p.write_text(s)
