A claude -p result's top-level usage is the main thread only; modelUsage is the whole process with subagents (the Slack Fable run: usage < modelUsage). weighted_v1 read usage, so it undercounted every run with subagents; weighted_v2 reads modelUsage first. Designer runs read ~10% dearer in v2 for this reason (whole/v1 0.882 vs pure repricing 0.810).
item: RIMMANDRAKE_WEIGH_TOKENS_BY_MODEL_OPUS_INPUT_UNIT
home: NONE
