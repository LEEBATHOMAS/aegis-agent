from warehouse import get_con

from mcp.server.mcpserver import MCPServer


mcp = MCPServer("aegis")

MAX_ROWS = 50
BLOCKED = ("insert", "update", "delete","drop","truncate","alter","create","copy","replace")

get_lineage = {}

def _rows(cursor):
    columns = [c[0] for c in cursor.description]
    out = []
    for row in cursor.fetchall():
        out.append({
            col: val if isinstance(val, (int,float,str,bool)) or val is None else str(val)
            for col,val in zip(columns,row) 

        })
    return out


@mcp.tool()
def get_dq_metrics(limit: int =20) -> dict:
    """Limit data-quality checks from ops.dq_metrics: volume, freshness_hours,
    null_pct and schema_hash, each with status ok/warn/null. NEwest first.
    Call this first when investigating a data incident"""

    conn = get_con()
    try:
        cur = conn.execute(
            """
            Select checked_at,layer,table_name,metric,column_name,value,value_text,status
            from ops.dq_metrics
            order by checked_at desc
            LIMIT ?
            """,
            [limit],

        )
        return {"rows": _rows(cur)}

    finally:
        conn.close()



@mcp.tool()
def run_sql(query:str) -> dict:
    """Run a read only SQL query against the duckDB warehouse.
    Only Select ot WITH queries are allowed. Results are capped at 50 rows.
    Tables: bronze.trips_raw, silver.trips, gold.trips_hourly, ops.dq_metrics"""

    q = query.strip().rstrip(";").lower()

    if not q.startswith(("select","with")):
        return {"error": "Only Select or WITH queries are allowed"}
    if any (word in q.split() for word in BLOCKED):
        return {"error":"Query contains blocked keywords was rejected"}

    conn = get_con()
    try:
        cur = conn.execute(f"SELECT * FROM ({q})as t LIMIT {MAX_ROWS}")
        return {"rows": _rows(cur)}

    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

LINEAGE = {
    "gold.trips_hourly": {
            "built_from": ["silver.trips"],
            "job":"warehouse.build_gold",
            "logic":"Hourly aggregate: trip count, avg fare, total revenue, null passenger count"
             
    },

    "silver.trips": {
        "built_from": ["bronze.trips_raw"],
        "job":"warehouse.build_silver",
        "logic":"Rename columns, add trip_id and ingested_at",
        "contract":[
                   "drops rows with nullpickup time",
                   "drops rows with fare_amount < 0",
                   "drops rows with trip_distance < 0",
                   "keeps rows with null passenger_count",
                   
                   ],
    },
    "bronze.trips_raw": {
        "built_from": ["NYC TLC yellow taxi parquet files"],
        "job":"warehouse.build_bronze",
        "logic":"Raw parquet files from NYC TLC",
        
    },
}

@mcp.tool()
def get_lineage(table:str="") -> dict:
    """Show where a table's data comes from and which rules were applied.
    Pass a table like 'silver.trips' or leave empty for the full pipeline.
    User this to walk upstream from a falling table to its source.
    """

    if not table:
        return {"lineage": LINEAGE}
    if table not in LINEAGE:
        return {"error": f"Unknown table: '{table}'. Known {', '.join(LINEAGE)}"}
    return {"lineage": LINEAGE[table]}


PIPELINE_RUNS = [
    {"job": "warehouse.build_bronze", "status": "success", "finished_at": "2026-09-16 20:03:40"},
    {"job": "warehouse.build_silver", "status": "success", "finished_at": "2026-09-16 20:03:55"},
    {"job": "warehouse.build_gold", "status": "success", "finished_at": "2026-09-16 20:04:00"},
    {"job": "upstream_vendor_feed", "status": "success", "finished_at": "2026-09-16 20:05:10",
     "note": "Vendor deployed new app version; passenger count field became optional."},
    {"job": "warehouse.build_silver", "status": "success", "finished_at": "2026-09-16 20:05:20"},
    {"job": "warehouse.build_gold", "status": "success", "finished_at": "2026-09-16 20:05:30"},
]


@mcp.tool()
def get_pipeline_runs(limit: int =10) -> dict:
    """Recent pipeline runs, newest first. Use this to check whether
    something changed before it went bad.

    """
    runs = sorted(PIPELINE_RUNS, key=lambda x: x["finished_at"], reverse=True)
    return {"runs": runs[:limit]}


if __name__ =="__main__":
    mcp.run()
