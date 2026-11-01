Selftests that plant process-wide fixtures cannot be mutation-tested in parallel: each blinds the others, so failures read as kills. Serial or nothing.
