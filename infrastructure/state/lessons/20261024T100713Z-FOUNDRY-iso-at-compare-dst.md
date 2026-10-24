ISO-8601 'at' strings carrying a local offset (now().astimezone()) do not sort as text across a DST change: 01:10-08:00 is AFTER 01:50-07:00 but sorts before it. Compare parsed UTC instants (art_eval runner._instant, 23f5b40cc0).
home: NONE
