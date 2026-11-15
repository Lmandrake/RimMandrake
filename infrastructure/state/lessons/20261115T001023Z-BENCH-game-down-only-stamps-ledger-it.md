./game down only STAMPS the ledger; it does not close RimWorld (measured 2026-11-14: tasklist still showed RimWorldWin64 and modset_builder --apply refused on a live Player.log). Close it with python3 src/RimMandrake/Utils/game_instance.py stop <PID>, then apply the tier and launch with powershell.exe Start-Process 'steam://rungameid/294100'.
item: NONE
