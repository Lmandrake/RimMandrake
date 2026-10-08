cd /home/mandrake/rm/foundry
for m in WreckedMachines Droidworks FallLineArrivals UnfinishedLine; do
  python.exe -u Transient/acc_biomes/run_live_suite.py $m > Transient/acc_green/h_$m.txt 2>&1
  echo done_$m >> Transient/acc_green/h_progress.txt
done
python.exe -u Transient/acc_biomes/run_live_suite.py LuminousPigment --chains=00_log_baseline,defs_load,settings_apply > Transient/acc_green/h_LuminousPigment.txt 2>&1
echo done_LP >> Transient/acc_green/h_progress.txt
