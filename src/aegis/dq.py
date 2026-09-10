import hashlib


from warehouse import get_con

VOLUME_FAIL_BELOW = 1
NULL_FAIL_PCT= 20.0
NULL_WARN_PCT= 5.0
FRESHNESS_FAIL_HOURS =72
FRESHNESS_WARN_HOURS =24

def ensure_table(con):
    con.execute("""CREATE TABLE IF NOT EXISTS ops.dq_metrics (
                checked_at TIMESTAMP, 
                layer TEXT, 
                table_name TEXT, 
                metric TEXT, 
                column_name TEXT, 
                value DOUBLE, 
                value_text TEXT, 
                status TEXT)""")





def grade(metric, value):
    if metric == "volume":
        return "fail" if value < VOLUME_FAIL_BELOW else "ok"
    if metric == "null_pct":    
        if value >= NULL_FAIL_PCT:        
            return "fail"
        if value >= NULL_WARN_PCT:
            return "warn"
        return "ok"
    if metric == "freshness_hours": 
        if value >= FRESHNESS_FAIL_HOURS: 
            return "fail"
        if value >= FRESHNESS_WARN_HOURS: 
            return "warn"
        return "ok"
    if metric == "schema_hash":
        return "ok"
    return "ok"

def record(con, layer, table_name, metric, value,status, column_name=None, value_text=None):
    con.execute("""INSERT INTO ops.dq_metrics (checked_at, layer, table_name, metric, column_name, value, value_text, status)
                VALUES (CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?, ?)""",
                (layer, table_name, metric, column_name, value, value_text, status),)
    con.commit()
    shown = value if value_text is None else value_text
    print(f"{layer:>5}.{table_name} {metric:>12} {shown:>10} [{status}]]")


def check_volume(con):
    silver_n = con.execute("SELECT count(*) FROM silver.trips").fetchone()[0]
    record(con, "silver", "trips", "volume", float(silver_n), grade("volume", silver_n))

    gold_n = con.execute("SELECT coalesce(sum(trip_count), 0) FROM gold.trips_hourly").fetchone()[0]
    record(con, "gold", "trips_hourly", "volume", float(gold_n), grade("volume", gold_n))


def check_freshness(con):
    hours = con.execute("Select date_diff('hour',max(ingested_At),now()) FROM silver.trips").fetchone()[0]
    hours  = 0 if hours  is None else float(hours)
    record(con, "silver", "trips", "freshness_hours", float(hours), grade("freshness_hours", hours))


def check_null_pct(con):
    pct = con.execute(""" SELECT 100.0 * count(*) FILTER (WHERE passenger_count IS NULL)
             / nullif(count(*), 0)
        FROM silver.trips""").fetchone()[0]
    pct  = 0.0 if pct  is None else float(pct)
    record(con, "silver", "trips", "null_pct", float(pct), grade("null_pct", pct))


def check_schema_hash(con):
    rows = con.execute(""" SELECT column_name, data_type
                                FROM information_schema.columns
                                WHERE table_schema = 'bronze' AND table_name = 'trips_raw'
                                ORDER BY ordinal_position""").fetchall()
    payload = "|".join(f"{name}:{dtype}" for name, dtype in rows)
    digest = hashlib.md5(payload.encode()).hexdigest()
    record(con, "bronze", "trips_raw", "schema_hash",None, grade("schema_hash", digest),value_text=digest)

def compute():
    con = get_con()
    ensure_table(con)
    check_volume(con)
    check_freshness(con)
    check_null_pct(con)
    check_schema_hash(con)
    print("\nLatest snapshot:")
    print(con.execute("""SELECT checked_at, layer, table_name, metric, column_name, value, value_text, status
            FROM ops.dq_metrics
            ORDER BY checked_at DESC, metric
            LIMIT 20""").fetchdf()
    )
    con.close()

if __name__ == "__main__":
    compute()