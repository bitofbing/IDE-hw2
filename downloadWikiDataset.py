from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS

# 设置 SPARQL 查询服务（Wikidata）
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)

# 查询语句
query = """
SELECT ?label ?labelLabel ?artist ?artistLabel ?work ?workLabel
WHERE {
  ?work wdt:P175 ?artist .        # 作品由艺术家创作
  ?artist wdt:P264 ?label .       # 艺术家签约于唱片公司

  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
LIMIT 10000
"""
sparql.setQuery(query)

# 执行查询
results = sparql.query().convert()

# 提取数据
data = []
for result in results["results"]["bindings"]:
    data.append({
        "label": result["label"]["value"],
        "labelLabel": result.get("labelLabel", {}).get("value", ""),
        "artist": result["artist"]["value"],
        "artistLabel": result.get("artistLabel", {}).get("value", ""),
        "work": result["work"]["value"],
        "workLabel": result.get("workLabel", {}).get("value", "")
    })

# 保存为 CSV (MySQL-friendly)
df = pd.DataFrame(data)
df.to_csv("wikidata_music.csv", index=False)
print("✔ 导出为 CSV：wikidata_music.csv")

# 构建 RDF 图用于 gStore（N-Triples）
# 构建 RDF 图用于 gStore（N-Triples）
g = Graph()
for row in data:
    label_uri = URIRef(row["label"])
    artist_uri = URIRef(row["artist"])
    work_uri = URIRef(row["work"])

    g.add((artist_uri, URIRef("http://www.wikidata.org/prop/direct/P264"), label_uri))
    g.add((work_uri, URIRef("http://www.wikidata.org/prop/direct/P175"), artist_uri))

    # 添加标签（加上语言标记 "@en"）
    if row["labelLabel"]:
        g.add((label_uri, RDFS.label, Literal(row["labelLabel"], lang="en")))
    if row["artistLabel"]:
        g.add((artist_uri, RDFS.label, Literal(row["artistLabel"], lang="en")))
    if row["workLabel"]:
        g.add((work_uri, RDFS.label, Literal(row["workLabel"], lang="en")))

# 保存为 .nt 文件（gStore导入格式）
g.serialize(destination="wikidata_music.nt", format="nt")
print("✔ 导出为 N-Triples：wikidata_music.nt")
