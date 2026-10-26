A torn-write fault test that writes n/2 bytes of a batch of equal-length rows tears nothing: with an even row count, half the chunk ends exactly on a newline, so the 'torn tail' test passed without any line ever being torn. Tear inside a line (for example, half of the first line) and mutation-check that the test fails without the repair.
home: NONE
