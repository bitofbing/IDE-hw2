PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?artist ?artistLabel ?label ?labelLabel ?work ?workLabel
WHERE {
  ?work wdt:P175 ?artist .       # 作品 → 艺术家
  ?artist wdt:P264 ?label .      # 艺术家 → 唱片公司

  OPTIONAL {
    ?artist rdfs:label ?artistLabel .
    FILTER(LANGMATCHES(LANG(?artistLabel), "en"))
  }
  OPTIONAL {
    ?label rdfs:label ?labelLabel .
    FILTER(LANGMATCHES(LANG(?labelLabel), "en"))
  }
  OPTIONAL {
    ?work rdfs:label ?workLabel .
    FILTER(LANGMATCHES(LANG(?workLabel), "en"))
  }
}
LIMIT 5
