A float-times-int in a Ceil can overshoot: 0.3f*100 ceils to 31, moving a 30% floor by one HP. Keep thresholds as whole percents and compare hp*100 > max*pct.
