import requests
import time
import pymysql
import matplotlib.pyplot as plt
import seaborn as sns


# MySQL 配置
mysql_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "wikidata_music",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

# gStore 配置
gstore_url = "http://localhost:9000"
gstore_payload_base = {
    "username": "root",
    "password": "123456",
    "db_name": "wikidata_music",
    "operation": "query",
    "format": "json"
}

# 查询任务列表（SQL/SPARQL 成对）
query_tasks = [
    {
        "id": "Q1",
        "desc": "厂牌 → 艺人",
        "sparql": """
            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
            SELECT ?artist WHERE {
              ?artist wdt:P264 <http://www.wikidata.org/entity/Q21077> .
            }
        """,
        "sql": """
            SELECT a.artist_id, a.artist_name
            FROM artists a
            JOIN artist_label al ON a.artist_id = al.artist_id
            WHERE al.label_id = 'http://www.wikidata.org/entity/Q21077';
        """
    },
    {
        "id": "Q2",
        "desc": "厂牌 → 艺人 → 歌曲",
        "sparql": """
            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
            SELECT ?artist ?work WHERE {
              ?artist wdt:P264 <http://www.wikidata.org/entity/Q21077> .
              ?work wdt:P175 ?artist .
            }
        """,
        "sql": """
            SELECT w.work_id, w.work_name
            FROM labels l
            JOIN artist_label al ON l.label_id = al.label_id
            JOIN artists a ON al.artist_id = a.artist_id
            JOIN artist_work aw ON a.artist_id = aw.artist_id
            JOIN works w ON aw.work_id = w.work_id
            WHERE l.label_id = 'http://www.wikidata.org/entity/Q21077';
        """
    },
    {
        "id": "Q4",
        "desc": "模糊匹配歌曲名包含 love",
        "sparql": """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?work ?label WHERE {
              ?work rdfs:label ?label .
              FILTER CONTAINS(LCASE(?label), "love")
            }
        """,
        "sql": "SELECT work_id, work_name FROM works WHERE LOWER(work_name) LIKE '%love%';"
    },
    {
        "id": "Q5",
        "desc": "统计每个厂牌的艺人数",
        "sparql": """
            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
            SELECT ?label (COUNT(?artist) AS ?count) WHERE {
              ?artist wdt:P264 ?label .
            }
            GROUP BY ?label
        """,
        "sql": """
            SELECT label_id, COUNT(*) as count
            FROM artist_label
            GROUP BY label_id;
        """
    },
]

# 测试执行
def run_tests():
    results = []

    connection = pymysql.connect(**mysql_config)

    for task in query_tasks:
        print(f"\n▶ 任务 {task['id']}：{task['desc']}")

        # gStore 查询
        sparql_payload = gstore_payload_base.copy()
        sparql_payload["sparql"] = task["sparql"]

        try:
            t1 = time.time()
            r = requests.post(gstore_url, json=sparql_payload)
            t2 = time.time()
            sparql_result = r.json()
            gstore_count = len(sparql_result.get("results", {}).get("bindings", []))
            gstore_time = (t2 - t1) * 1000
        except Exception as e:
            print(f"❌ gStore 查询失败：{e}")
            gstore_time = -1
            gstore_count = 0

        # MySQL 查询
        try:
            with connection.cursor() as cursor:
                t3 = time.time()
                cursor.execute(task["sql"])
                mysql_result = cursor.fetchall()
                t4 = time.time()
                mysql_time = (t4 - t3) * 1000
                mysql_count = len(mysql_result)
        except Exception as e:
            print(f"❌ MySQL 查询失败：{e}")
            mysql_time = -1
            mysql_count = 0

        # 打印并记录结果
        print(f"  gStore 时间: {gstore_time:.2f} ms，结果数: {gstore_count}")
        print(f"  MySQL 时间: {mysql_time:.2f} ms，结果数: {mysql_count}")

        results.append({
            "query_id": task["id"],
            "description": task["desc"],
            "gstore_time_ms": gstore_time,
            "mysql_time_ms": mysql_time,
            "gstore_result_count": gstore_count,
            "mysql_result_count": mysql_count
        })

    connection.close()
    return results

# 执行脚本
if __name__ == "__main__":
    data = run_tests()

