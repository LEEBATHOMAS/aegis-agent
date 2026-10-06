# Runbook: Volume drop in silver or gold

## Symptoms of a volume drop
A volume drop shows up in ops.dq_metrics as metric volume much lower than usual for
silver.trips, or gold.trips_hourly hours with very low or zero trip_count. Normal
volume for one month of yellow taxi data is about 2.9 million trips.

## How to confirm a volume drop
Compare row counts in bronze.trips_raw and silver.trips. If bronze is also low, data
never arrived from the source. If bronze is normal but silver is low, the silver
contract is rejecting more rows than usual, for example many negative fares.

## What to do about a volume drop
If the source is missing data, check whether the NYC TLC file was complete and re-run
build_bronze. If the silver contract is rejecting rows, inspect the rejected rows in
bronze before changing any rules. Never relax the contract just to make the count
look normal.