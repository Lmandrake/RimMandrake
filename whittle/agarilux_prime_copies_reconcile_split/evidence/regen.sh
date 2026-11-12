set -u
# Regenerates every evidence file in this folder from the current tree (run from anywhere).
cd /home/mandrake/rm/scratch/BENCH/claude-archmagi-offline2
W=whittle/agarilux_prime_copies_reconcile_split; E=$W/evidence
RW="/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld"
DEFS=(--defs src --defs "$RW/Data" --defs "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100" --defs "$RW/Mods" --mods-config infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml)
python3 $E/resolve_agarilux_prime.py > $E/resolved_texpath_after.txt 2>&1; echo "resolve $?"
python3 $E/search_losing_path.py > $E/search_after.txt 2>&1; echo "search $?"
(python3 src/RimMandrake/Utils/art/art.py status Things/Plants/AB_AgariluxPrime; python3 src/RimMandrake/Utils/art/art.py status RotSpecies/AgariluxPrime; python3 src/RimMandrake/Utils/art/art.py status RM_AgariluxPrime) > $E/art_ledger_status_after.txt 2>&1; echo "status $?"
python3 skills/rimworld-modding/scripts/validate_patch.py src/RimMandrake/TheRot/Patches/RotSpecies_NamesAndSizes.xml src/RimMandrake/TheRot/Patches/RotGiants_HugeFootprint.xml src/RimUtinni/UtinniPatches/Patches/PlantTolerances_Ashkarr.xml "${DEFS[@]}" > $E/validate_patch.txt 2>&1; echo "vpatch $?"
python3 skills/rimworld-modding/scripts/validate_patch.py src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_TheRot_DonorPorts.xml "${DEFS[@]}" > $E/validate_def.txt 2>&1; echo "vdef $?"
python3 src/RimMandrake/Utils/run_selftests.py --workers 2 --only src/RimMandrake/Utils/art/selftest_alpha_plants_renders.py src/RimMandrake/HugeThings/selftest_hugethings_footprint.py src/RimMandrake/Utils/selftest_hugethings_lint.py > $E/selftests.txt 2>&1; echo "selftests $?"
python3 src/RimMandrake/Utils/art/selftest_alpha_plants_renders.py > $E/selftest_alpha_plants_renders.txt 2>&1; echo "alpha $?"
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod UtinniPatches > $E/deploy_plan_UtinniPatches.txt 2>&1; echo "dpU $?"
python3 src/RimMandrake/Utils/deploy_custom_mods.py --compose biomes > $E/deploy_plan_biomes.txt 2>&1; echo "dpB $?"
python3 src/RimMandrake/Utils/unproven_adjudicate.py --check > /dev/null 2>&1 || true
python3 src/RimMandrake/Utils/art/unproven_adjudicate.py --check > $E/unproven_adjudicate_check.txt 2>&1; echo "unproven $?"
python3 src/RimMandrake/Utils/art/bulk_accept_renders.py plan --out /tmp/agp_bulk_plan.json > /tmp/agp_bulk_plan.log 2>&1; echo "bulk $?"
python3 $E/broaden_checks.py > $E/broaden_checks.txt 2>&1; echo "broaden $?"
python3 whittle/agarilux_prime_copies_reconcile_split/evidence/bulk_plan_summary.py > whittle/agarilux_prime_copies_reconcile_split/evidence/bulk_accept_plan_agarilux.txt 2>&1; echo "bulksum $?"
(cd src/RimMandrake/Utils/art && python3 - <<'PY') > $E/sheet_resolution_after.txt 2>&1; echo "sheetres $?"
import subject as S
w = S.World()
t = sorted(w.tex_by_def.get('RM_AgariluxPrime', ()))
print("subject.World().tex_by_def['RM_AgariluxPrime'] (the src texPath art_sheet prefers over the dump):", t)
print("subject.World().def_by_tex['Things/Plants/AB_AgariluxPrime']:", sorted(w.def_by_tex.get('Things/Plants/AB_AgariluxPrime', ())) or 'none')
print("live dump texPath (2026-11-02 full-list load): RotSpecies/AgariluxPrime")
print("=> art_sheet.subject_row's src override now agrees with the dump; its IN GAME column is the drawn v3 (sha 85779af9...)" if t == ['RotSpecies/AgariluxPrime'] else "=> MISMATCH")
PY
python3 $E/judgement_record.py > $E/judgement_record.txt 2>&1; echo "judg $?"
bash $E/resolved_before.sh > $E/resolved_texpath_before.txt 2>&1; echo "before $?"
python3 $E/three_copies.py $E/three_copies_before.png; echo "png $?"
echo ALLDONE
