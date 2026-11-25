FlowWorks stagers: flowworks_excavation_drive setBodyWaterM (Walk.set_fill, Stage.fill) sets the WHOLE connected dug body to one level, never one square; the shared mock FakeGame writes one square, so a one-square fill of a shared body reads right in --mock and wrong in game. Set the body to the metres you sign, and check the readout against the sign, not 'all squares alike'.
item: RIMMANDRAKE_TRACE_FLOWWORKS_TWO_NOTCH_STRIP_READS_FIVE_THOUSAND_LITRES
home: skills/live-debugging-proof-harness
