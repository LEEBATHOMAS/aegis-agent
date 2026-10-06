# Runbook: Null spike in a silver column
## Symptoms of a null spike
A null spike shows up in ops.dq_metrics as metric null_pct with status warn or fail
for a column in silver.trips, usually passenger_count. The silver row count (volume)
stays normal. The bronze schema_hash does not change. Normal null_pct for
passenger_count is about 4 to 5 percent.
## How to confirm a null spike
Query silver.trips and group null counts by day of pickup_ts. A real spike starts on a
specific date and stays high after it, instead of being spread evenly. Check
bronze.trips_raw for the same date range. If bronze is also null, the problem came from
upstream, not from the silver transformation.
## Likely causes of a null spike
The most common cause is an upstream vendor change, for example a new app version that
made a field optional. Check get_pipeline_runs for an upstream_vendor_feed run just
before the spike. A less common cause is a bug in build_silver that drops or renames
the column. If the bronze schema_hash changed, suspect a schema change instead.
## What to do about a null spike
Do not delete the affected rows. Silver keeps rows with null passenger_count on
purpose, because the trip itself is still valid and revenue numbers depend on it.
Notify the vendor feed owner, the Integrations team. Add a note to dashboards that
use passenger_count for the affected dates. Only backfill after the vendor sends
corrected data.