replay_watch.told() and relentless.py call incident.signal with a hardcoded {'incident':{'enabled':True}}, bypassing dispatcher_schedule.json's switch ('Off: nothing rings'). replay_watch now reads the schedule (wave 81); relentless.py writes its own told.jsonl and was not changed.
home: NONE
