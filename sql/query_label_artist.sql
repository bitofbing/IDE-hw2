PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?artist ?artistLabel
WHERE {
  ?artist wdt:P264 ?label .                     # 艺术家 → 唱片公司
  ?label rdfs:label "Roadrunner Records"@en .    # 唱片公司英文名匹配

  OPTIONAL {
    ?artist rdfs:label ?artistLabel .
    FILTER(LANGMATCHES(LANG(?artistLabel), "en"))
  }
}
