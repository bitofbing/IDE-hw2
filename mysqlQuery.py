import pymysql
import time

def get_artists_by_label_name(label_name, connection):
    with connection.cursor() as cursor:
        # 查厂牌 ID
        cursor.execute("SELECT label_id FROM labels WHERE label_name = %s", (label_name,))
        label = cursor.fetchone()
        if not label:
            return set(), f"未找到名为「{label_name}」的厂牌。"

        label_id = label["label_id"]

        # 查该厂牌下的艺人
        query = """
            SELECT artists.artist_name
            FROM artist_label
            JOIN artists ON artist_label.artist_id = artists.artist_id
            WHERE artist_label.label_id = %s
        """
        cursor.execute(query, (label_id,))
        artists = cursor.fetchall()

        # 注意：artists 是一个列表，元素是 {'name': xxx} 的字典
        artist_set = set(a["artist_name"] for a in artists)

        return artist_set, f"厂牌「{label_name}」的艺人共 {len(artist_set)} 位。"

# MySQL 配置
mysql_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "wikidata_music",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

connection = pymysql.connect(**mysql_config)

# 调用方式
t3 = time.time()
artist_set, summary = get_artists_by_label_name("Roadrunner Records", connection)
t4 = time.time()
mysql_time = (t4 - t3) * 1000

print(f"MySQL 查询时间: {mysql_time:.2f} ms")
print(summary)
for artist in sorted(artist_set):
    print(" -", artist)
