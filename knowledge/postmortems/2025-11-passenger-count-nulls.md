# Postmortem: passenger_count nulls after vendor app release (November 2025)

## Summary of the November 2025 passenger_count incident
On 2025-11-12, null_pct for passenger_count in silver.trips rose from 4 percent to
38 percent and stayed there for six days. Trip volume and revenue were normal.
The data-quality check caught it within one hour.

## Root cause of the November 2025 incident
The taxi vendor released a new driver app version that made passenger count an
optional field. Many drivers skipped it. Our pipeline was working correctly. The
bronze data from the vendor already contained the nulls.

## How the November 2025 incident was resolved
The Integrations team contacted the vendor, who made the field required again in a
follow-up app release on 2025-11-18. We did not delete or impute the null rows.
Dashboards showing average passengers per trip were annotated for 2025-11-12 to
2025-11-18.

## Lessons from the November 2025 incident
Vendor app releases should be announced to the data team in advance. A null spike
with normal volume and an unchanged schema almost always means an upstream data
change, not a pipeline bug.