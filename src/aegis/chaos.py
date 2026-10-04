import sys

from warehouse import get_con, build_bronze, build_silver, build_gold

def null_spike(con):
    before = con.execute("SELECT count(*) FILTER (WHERE passenger_count IS NULL) FROM bronze.trips_raw").fetchone()[0]
    con.execute("""Update bronze.trips_raw set passenger_count = NULL where tpep_pickup_datetime >= TIMESTAMP '2024-01-20'""")

    after = con.execute("SELECT count(*) FILTER (WHERE passenger_count IS NULL) FROM bronze.trips_raw").fetchone()[0]
    print (f"null_spike: bronze null passenger_count {before:,} -> {after:,}")


def volume_drop(con):
    before = con.execute("SELECT count(*) FROM bronze.trips_raw").fetchone()[0]
    con.execute("""Delete from bronze.trips_raw where tpep_pickup_datetime >= TIMESTAMP '2024-01-16'""")

    after = con.execute("SELECT count(*) FROM bronze.trips_raw").fetchone()[0]
    print (f"volume_drop: bronze rows {before:,} -> {after:,}")

SCENARIOS = {
    "null_spike": null_spike,
    "volume_drop": volume_drop,
}

def inject(name):
    if name not in SCENARIOS:
        raise SystemExit(f"Unknown scenario '{name}'. Choose: {', '.join(SCENARIOS)}")
    con = get_con()
    SCENARIOS[name](con)
    print("Revuilding silver and gold from the damaged bronze")

    build_silver()
    build_gold()
    print("Done. Run python src/aegis/dq.py to check the results")


if __name__ == "__main__":
    scenario = sys.argv[1] if len(sys.argv) > 1 else  "null_spike"
    inject(scenario)
