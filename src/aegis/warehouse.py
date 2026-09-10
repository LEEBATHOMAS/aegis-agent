import duckdb

from config import DATA_DIR, DUCKDB_PATH, TLC_URL


def get_con():
    """Open the embedded warehouse and ensure schemas exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DUCKDB_PATH))
    con.execute("INSTALL httpfs; LOAD httpfs;")
    for schema in ("bronze", "silver", "gold", "ops"):
        con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")
    return con


def build_bronze(months):
    """Land raw taxi parquet, unchanged, into bronze."""
    con = get_con()
    urls = [TLC_URL.format(month=m) for m in months]
    con.execute("DROP TABLE IF EXISTS bronze.trips_raw;")
    con.execute(
        "CREATE TABLE bronze.trips_raw AS "
        "SELECT * FROM read_parquet(?, union_by_name=true)",
        [urls],
    )
    n = con.execute("SELECT count(*) FROM bronze.trips_raw").fetchone()[0]
    print(f"bronze.trips_raw: {n:,} rows")


def build_silver():
    """Clean, validate, and write the trusted layer."""
    con = get_con()
    con.execute("DROP TABLE IF EXISTS silver.trips;")
    con.execute("""
        CREATE TABLE silver.trips AS
        SELECT
            row_number() OVER ()               AS trip_id,
            tpep_pickup_datetime               AS pickup_ts,
            tpep_dropoff_datetime              AS dropoff_ts,
            passenger_count,
            trip_distance,
            fare_amount,
            total_amount,
            PULocationID                       AS pu_location_id,
            DOLocationID                       AS do_location_id,
            now()                              AS ingested_at
        FROM bronze.trips_raw
        WHERE tpep_pickup_datetime IS NOT NULL
          AND fare_amount   >= 0
          AND trip_distance >= 0;
    """)
    n = con.execute("SELECT count(*) FROM silver.trips").fetchone()[0]
    print(f"silver.trips: {n:,} rows")


def build_gold():
    """Hourly mart a dashboard would read."""
    con = get_con()
    con.execute("DROP TABLE IF EXISTS gold.trips_hourly;")
    con.execute("""
        CREATE TABLE gold.trips_hourly AS
        SELECT
            date_trunc('hour', pickup_ts)                         AS pickup_hour,
            count(*)                                              AS trip_count,
            round(avg(fare_amount), 2)                            AS avg_fare,
            round(sum(total_amount), 2)                           AS total_revenue,
            count(*) FILTER (WHERE passenger_count IS NULL)       AS null_passenger_ct
        FROM silver.trips
        GROUP BY 1
        ORDER BY 1;
    """)
    n = con.execute("SELECT count(*) FROM gold.trips_hourly").fetchone()[0]
    print(f"gold.trips_hourly: {n:,} hourly buckets")


if __name__ == "__main__":
    build_bronze(["2024-01"])
    build_silver()
    build_gold()
