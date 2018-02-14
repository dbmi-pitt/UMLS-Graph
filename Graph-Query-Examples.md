# Graph-Query-Examples
## Examples of cypher queries of UMLS-Graph

### Count Nodes:
```cypher
MATCH (n) RETURN count(n)
15837031
```

### Count Directed Relationships:
```cypher
MATCH ()-[r]->() RETURN COUNT(r)
44807143
```

### Get Table of Semantic Network:
```cypher
MATCH (n:Semantic)
RETURN n.TUI, n.name, n.STN, n.DEF
ORDER BY n.STN
LIMIT 200
```

### Visualize 10 nodes:
```cypher
MATCH (n) RETURN n LIMIT 10
```

### UMLS Exact Match Dictionary:
```cypher
MATCH (a:Term)<-[b]-(c:Code)<-[d]-(e:Concept)-[f:DEF]->(g:Definition) 
WHERE a.name = "Breast Cancer" AND Type(b) = Type(d)
WITH e,g MATCH (e:Concept)-[:PREF_TERM]->(t:Term)
RETURN DISTINCT t.name as CUI_PREF_TERM, g.SAB as SAB, g.DEF AS DEF order by SAB
```

### Find Codes from Text Contained in Concept's Terms (Terms from all sources):
```cypher
MATCH (a:Term)<-[b]-(c:Code)<-[d]-(e:Concept)
WHERE a.name CONTAINS "Synercid" AND Type(b) = Type(d)
WITH e MATCH (e:Concept)-[f]->(g:Code), (e:Concept)-[:PREF_TERM]->(t:Term)
RETURN DISTINCT t.name AS CUI_PREF_TERM, g.SAB AS SAB, Type(f) AS TYPE, g.CODE AS CODE, g.CodeID AS SAB_CODE
```

### Find Codes from Text Contained in Related Concept's Terms (and Relations from all sources):
```cypher
MATCH (a:Term)<-[b]-(c:Code)<-[d]-(e:Concept)
WHERE a.name CONTAINS "Synercid" AND Type(b) = Type(d)
WITH e MATCH (e:Concept)-[h]->(i:Concept)-[j]->(k:Code), (e:Concept)-[:PREF_TERM]->(t:Term)
WITH e,h,i,j,k,t MATCH (i:Concept)-[:PREF_TERM]->(u:Term)
RETURN DISTINCT t.name AS CUI1_PREF_TERM, h.SAB AS SAB_REL, Type(h) AS RELATION, u.name AS CUI2_PREF_TERM, Type(j) as TTY, k.SAB as SAB, k.CODE as CODE, k.CodeID as SAB_CODE
```

### Find Codes from Text Contained in Concept's Terms and Report Descendants from all sources:
```cypher
MATCH (a:Term)<-[b]-(c:Code)<-[d]-(e:Concept)
WHERE a.name CONTAINS "Synercid" AND Type(b) = Type(d)
WITH e MATCH (e:Concept)-[:`inverse_isa PAR`|`inverse_isa RB`*1..]->(l:Concept)-[m]-(n:Code), (e:Concept)-[:PREF_TERM]->(t:Term)
WITH e,l,m,n,t MATCH (l:Concept)-[:PREF_TERM]->(v:Term)
RETURN DISTINCT t.name as CUI1_PREF_TERM, "inverse_isa", v.name as CUI2_PREF_TERM, Type(m) as TTY, n.SAB as SAB, n.CODE as CODE, n.CodeID as SAB_CODE
```

### Find RXNORM Code and SNOMEDCT_US Fully Specified Name-Product for an NDC code:
```cypher
MATCH (a:NDC{NDC:'61570026001'})<--(b:Code)<--(:Concept)-[:`inverse_isa PAR`|`inverse_isa RB`*0..5]->(:Concept)-[:`has_active_ingredient RO`]->(:Concept)-[:`inverse_isa PAR`|`inverse_isa RB`*0..5]->(:Concept)-[:FN]->(c:Code{SAB:'SNOMEDCT_US'})-[:FN]->(f:Term) where f.name ends with 'product)' RETURN distinct b.CodeID as RXNORM, c.CodeID as SNOMED, f.name as FN
```

### ICD9CM Paths:
```cypher
MATCH (a:Concept)-[:PT]->(x:Code{SAB:'ICD9CM'})
MATCH p = shortestPath((b:Concept{CUI:'C0178237'})-[:PAR*1..]->(a:Concept))
WHERE NONE (r IN relationships(p) WHERE r.SAB <>'ICD9CM')
UNWIND nodes(p) as n
MATCH (n:Concept)-[:HT]->(y:Code{SAB:'ICD9CM'})
RETURN (collect(y.CODE) + x.CODE) as PATH order by PATH limit 100000
```
