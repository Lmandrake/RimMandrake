On Windows, `driverquery /fo csv` (without /v) has no State column: a script that reads State from it sees every driver as not running. Use `driverquery /v /fo csv`.
