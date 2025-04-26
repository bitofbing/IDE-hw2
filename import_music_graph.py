import pandas as pd
import pymysql
from sqlalchemy import create_engine

# CSV 文件路径
csv_path = "wikidata_music.csv"
df = pd.read_csv(csv_path)

# 去重拆分三张实体表
labels_df = df[['label', 'labelLabel']].drop_duplicates().rename(columns={"label": "label_id", "labelLabel": "label_name"})
artists_df = df[['artist', 'artistLabel']].drop_duplicates().rename(columns={"artist": "artist_id", "artistLabel": "artist_name"})
works_df = df[['work', 'workLabel']].drop_duplicates().rename(columns={"work": "work_id", "workLabel": "work_name"})

# 构建关系表
artist_label_df = df[['artist', 'label']].drop_duplicates().rename(columns={"artist": "artist_id", "label": "label_id"})
artist_work_df = df[['artist', 'work']].drop_duplicates().rename(columns={"artist": "artist_id", "work": "work_id"})

# 数据库连接参数
host = 'localhost'
user = 'root'
password = 'root'
db_name = 'wikidata_music'
port = 3306

# 创建数据库连接
conn = pymysql.connect(host=host, user=user, password=password, port=port)
cursor = conn.cursor()
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
cursor.close()
conn.commit()
conn.close()

# 用 SQLAlchemy 导入数据
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8mb4")

# 使用 pymysql 执行原生 SQL 建表语句
conn = pymysql.connect(host=host, user=user, password=password, database=db_name, port=port)
cursor = conn.cursor()

create_sqls = [
    '''CREATE TABLE IF NOT EXISTS labels (
        label_id VARCHAR(255) PRIMARY KEY,
        label_name VARCHAR(1024)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;''',

    '''CREATE TABLE IF NOT EXISTS artists (
        artist_id VARCHAR(255) PRIMARY KEY,
        artist_name VARCHAR(1024)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;''',

    '''CREATE TABLE IF NOT EXISTS works (
        work_id VARCHAR(255) PRIMARY KEY,
        work_name VARCHAR(1024)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;''',

    '''CREATE TABLE IF NOT EXISTS artist_label (
        artist_id VARCHAR(255),
        label_id VARCHAR(255),
        PRIMARY KEY (artist_id, label_id),
        FOREIGN KEY (artist_id) REFERENCES artists(artist_id) ON DELETE CASCADE,
        FOREIGN KEY (label_id) REFERENCES labels(label_id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;''',

    '''CREATE TABLE IF NOT EXISTS artist_work (
        artist_id VARCHAR(255),
        work_id VARCHAR(255),
        PRIMARY KEY (artist_id, work_id),
        FOREIGN KEY (artist_id) REFERENCES artists(artist_id) ON DELETE CASCADE,
        FOREIGN KEY (work_id) REFERENCES works(work_id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;'''
]

# 执行建表语句
for sql in create_sqls:
    cursor.execute(sql)

# 提交更改并关闭连接
conn.commit()
cursor.close()
conn.close()

# 插入数据
tables = [
    (labels_df, 'labels'),
    (artists_df, 'artists'),
    (works_df, 'works'),
    (artist_label_df, 'artist_label'),
    (artist_work_df, 'artist_work')
]

# 使用 SQLAlchemy 将数据插入表中
for df, table in tables:
    df.to_sql(table, engine, if_exists='append', index=False, method='multi')

print("数据已成功导入 MySQL，并完成建表。")
