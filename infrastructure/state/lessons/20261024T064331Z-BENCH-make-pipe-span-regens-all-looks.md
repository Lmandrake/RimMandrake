make_pipe_span.py regenerates PipeSpan.png for ALL four looks, and LANCZOS resampling drifts the bytes of untouched looks. When one look's atlas changes, restore the other looks' spans (art.py --why) or the commit carries unrelated art churn.
home: src/RimMandrake/FlowWorks/art_source/PipeSpan
