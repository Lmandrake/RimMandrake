#!/usr/bin/env python3
"""Fast acceptance-driver fault controls; combined selftest_hole_prison also runs production C# cases."""
from selftest_hole_prison import run_driver_checks

run_driver_checks()
print('PASS: pit-prison driver fault controls, fixture declarations and cleanup')
