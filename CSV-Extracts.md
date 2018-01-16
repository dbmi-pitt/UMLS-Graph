# UMLS-Graph

SCRIPTS TO EXTRACT FROM NEPTUNE UMLS Relational and LOAD to UMLS Graph (using neo4j-community-3.3.1-unix.tar) - JCS Nov 30, 2017 - Dec 7, 2017

## V2: Dec 16, 2017 - V2 Used the principle of creating a concise database that accounts for TTY.
"SELECT DISTINCT" was used liberally (even where it was not needed, because of unique IDs in UMLS). For convenience, we allow to relationships fail on import, if the connecting nodes don't exist, due to leveraging the --ignore-missing-nodes flag.

### Extract TUI-nodes and save as TUIs.csv (with header):
```SQL
SELECT DISTINCT UI as "TUI:ID", STY_RL as "name", STN_RTN as "STN", DEF from UMLS.SRDEF where RT = 'STY';
```

### Extract TUI-relationships (only ISA_STY among TUI-nodes which is TUI: T186) and save as TUIrel.csv (with header):
```SQL
WITH Semantics as (SELECT DISTINCT UI from UMLS.SRDEF WHERE RT = 'STY') SELECT DISTINCT UI3 as ":END_ID", UI1 as ":START_ID" FROM UMLS.SRSTRE1 INNER JOIN Semantics ON UMLS.SRSTRE1.UI1 = Semantics.UI WHERE UI2 = 'T186';
```

### Extract Concept-nodes as CUIs.csv (with header):
Notes: this would select unique CUIs even without distinct because there is only one English Preferred Term (but DISTINCT is used as "assurance for future versions of UMLS having integrity"). Surprisingly, some English Preferred Terms are listed in Obsolete AUIs, so SUPPRESS <> 'O' is not used here. This query is then used by other queries that generate Nodes (Codes, Terms, Definitions) to limit those queries to result in nodes that are connected to these concepts (via AUIs).
```SQL
SELECT DISTINCT CUI as "CUI:ID" from UMLS.MRCONSO where UMLS.MRCONSO.ISPREF = 'Y' AND UMLS.MRCONSO.STT = 'PF' AND UMLS.MRCONSO.TS = 'P' and UMLS.MRCONSO.LAT = 'ENG';
```

### Extract TUI-relationships of CUIs as CUI-TUIs.csv (with header):
```SQL
SELECT DISTINCT CUI AS ":START_ID", TUI AS ":END_ID" from UMLS.MRSTY;
```

### Extract Relationships among CUIs as CUI-CUIs.csv (with header) and limit to ENGlish: 
```SQL
WITH SABlist as (SELECT DISTINCT SAB from UMLS.MRCONSO where UMLS.MRCONSO.LAT = 'ENG') SELECT DISTINCT CUI2 AS ":START_ID", CUI1 AS ":END_ID", (RELA||' '||REL) as ":TYPE", UMLS.MRREL.SAB, RELA, REL from UMLS.MRREL inner join SABlist on UMLS.MRREL.SAB = SABlist.SAB where UMLS.MRREL.SUPPRESS <> 'O' and CUI1 <> CUI2 and REL <> 'SIB';
```

### Extract Code-nodes and save as CODEs.csv (with header):
```SQL
With CUIlist as (SELECT DISTINCT CUI from UMLS.MRCONSO where UMLS.MRCONSO.ISPREF = 'Y' AND UMLS.MRCONSO.STT = 'PF' AND UMLS.MRCONSO.TS = 'P' and UMLS.MRCONSO.LAT = 'ENG') SELECT DISTINCT (UMLS.MRCONSO.SAB||' '||UMLS.MRCONSO.CODE) as "CodeID:ID", UMLS.MRCONSO.SAB, UMLS.MRCONSO.CODE from UMLS.MRCONSO inner join CUIlist on UMLS.MRCONSO.CUI = CUIlist.CUI where UMLS.MRCONSO.LAT = 'ENG' and SUPPRESS <> 'O' and UMLS.MRCONSO.CODE <> 'NOCODE';
```

### Extract CODE-relationships of CUIs and save as CUI-CODEs.csv (with header):
```SQL
SELECT DISTINCT CUI as ":START_ID", (SAB||' '||CODE) as ":END_ID", TTY as ":TYPE" from UMLS.MRCONSO where LAT = 'ENG' and SUPPRESS <> 'O' and CODE <> 'NOCODE';
```

### Extract Term-nodes and save as SUIs.csv (with header):
Again SUPPRESS is not used here but ENG language is - there are orphaned Terms because CUIs rather than CODEs are used to subselect here in order to include Preferred terms that have suppressed codes or no codes (e.g. orphaned Terms will include those that are not Preferred and therefore don't connect to CUIs directly in the graph, even though they share an AUI with an included CUI, but also that have suppressed or no code, so they also don't connect with a CODE directly in the graph) - SO, rather than account for such complexity with concatenated and then distincted queries, this query just takes a broader approach by only limiting to graph-included CUIs, not limiting to graph-included CODEs OR Preferred Terms, with the resulting benefit of reducing the number of Terms somewhat at extraction, but also still having some orphan Terms - one should run a Cypher script to eliminate the orphans later - e.g. those with no relations - AFTER LOADING, NOT NOW, DO MATCH (n:Term) WHERE size((n)--())=0 DELETE (n) - e.g. in the V1 graph of 2017AB, MATCH (n:Term) WHERE size((n)--())=0 RETURN count(n) was 46070 before they were deleted:
```SQL
With CUIlist as (SELECT DISTINCT CUI from UMLS.MRCONSO where UMLS.MRCONSO.ISPREF = 'Y' AND UMLS.MRCONSO.STT = 'PF' AND UMLS.MRCONSO.TS = 'P' and UMLS.MRCONSO.LAT = 'ENG') SELECT DISTINCT UMLS.MRCONSO.SUI as "SUI:ID", UMLS.MRCONSO.STR as "name" FROM UMLS.MRCONSO inner join CUIlist on UMLS.MRCONSO.CUI = CUIlist.CUI where UMLS.MRCONSO.LAT = 'ENG';
```

### Extract Term-relationships of Codes and save as CODE-SUIs.csv (with header):
```SQL
SELECT DISTINCT SUI as ":END_ID", (SAB||' '||CODE) as ":START_ID", TTY as ":TYPE" from UMLS.MRCONSO where LAT = 'ENG' and SUPPRESS <> 'O' and CODE <> 'NOCODE';
```

### Extract Preferred Term-relationship of Concepts and save as CUI-SUIs.csv (with header):
```SQL
SELECT DISTINCT CUI as ":START_ID", SUI as ":END_ID" from UMLS.MRCONSO where UMLS.MRCONSO.ISPREF = 'Y' AND UMLS.MRCONSO.STT = 'PF' AND UMLS.MRCONSO.TS = 'P' and UMLS.MRCONSO.LAT = 'ENG';
```

### Extract Definition-nodes and save as DEFs.csv (with header) - BACKLOG: should limit to ENGlish like did with CUI-CUIs:
```SQL
With CUIlist as (SELECT DISTINCT CUI from UMLS.MRCONSO where UMLS.MRCONSO.ISPREF = 'Y' AND UMLS.MRCONSO.STT = 'PF' AND UMLS.MRCONSO.TS = 'P' and UMLS.MRCONSO.LAT = 'ENG') SELECT DISTINCT UMLS.MRDEF.ATUI as "ATUI:ID", UMLS.MRDEF.SAB, UMLS.MRDEF.DEF FROM UMLS.MRDEF inner join CUIlist on UMLS.MRDEF.CUI = CUIlist.CUI where SUPPRESS <> 'O';
```
### Extract DEF-relationships and save as DEFrel.csv (with header):
```SQL
SELECT DISTINCT ATUI as ":END_ID", CUI as ":START_ID" from UMLS.MRDEF where SUPPRESS <> 'O';
```

### Extract RXNORM NDC-nodes and save as NDCs.csv (with header):
Note: This extraction script does not check for the existence of the RXNORM CODE it will relate to (this could leave some "isolated" NDCs because relationships are designed to "silently fail").
```SQL
SELECT DISTINCT ATUI as "ATUI:ID", ATV as "NDC" from UMLS.MRSAT where SAB = 'RXNORM' and ATN = 'NDC' and SUPPRESS <> 'O';
```

### Extract RXNORM NDC-relationships and save as NDCrel.csv (with header):
```SQL
SELECT DISTINCT ATUI as ":END_ID", (SAB||' '||CODE) as ":START_ID" from UMLS.MRSAT where SAB = 'RXNORM' and ATN = 'NDC' and SUPPRESS <> 'O';
```
### Steps to load and verify neo4j database:
#### Delete all Neo4j data (from Neo4j home directory):
```bash
bin/neo4j stop
rm -rf data/*
```

#### Put all csv files into standard neo4j import directory and then load into Neo4j via import tool from standard neo4j directory:
```bash
bin/neo4j-admin import --nodes:Semantic "import/TUIs.csv" --nodes:Concept "import/CUIs.csv" --nodes:Code "import/CODEs.csv" --nodes:Term "import/SUIs.csv" --nodes:Definition "import/DEFs.csv" --nodes:NDC "import/NDCs.csv" --relationships:ISA_STY "import/TUIrel.csv" --relationships:STY "import/CUI-TUIs.csv" --relationships "import/CUI-CUIs.csv" --relationships "import/CUI-CODEs.csv" --relationships "import/CODE-SUIs.csv" --relationships:PREF_TERM "import/CUI-SUIs.csv" --relationships:DEF "import/DEFrel.csv" --relationships:NDC "import/NDCrel.csv" --ignore-missing-nodes
```

#### At this point, after much load feedback a clean load should show something like the following:
IMPORT DONE in 3m 9s 34ms. 
Imported:
  16226447 nodes
  44808023 relationships
  97153835 properties
  
#### Start Neo4j:
```bash
bin/neo4j start
```

#### SET CONSTRAINTS and INDEXES on everything (these were each run as a single line and response confirms success):
```cypher
CREATE CONSTRAINT ON (n:Semantic) ASSERT n.TUI IS UNIQUE
CREATE CONSTRAINT ON (n:Semantic) ASSERT n.STN IS UNIQUE
CREATE CONSTRAINT ON (n:Semantic) ASSERT n.DEF IS UNIQUE
CREATE CONSTRAINT ON (n:Semantic) ASSERT n.name IS UNIQUE
CREATE CONSTRAINT ON (n:Concept) ASSERT n.CUI IS UNIQUE
CREATE CONSTRAINT ON (n:Code) ASSERT n.CodeID IS UNIQUE
CREATE INDEX ON :Code(SAB)
CREATE INDEX ON :Code(CODE)
CREATE CONSTRAINT ON (n:Term) ASSERT n.SUI IS UNIQUE
CREATE CONSTRAINT ON (n:Term) ASSERT n.name IS UNIQUE
CREATE CONSTRAINT ON (n:Definition) ASSERT n.ATUI IS UNIQUE
CREATE INDEX ON :Definition(SAB)
CREATE INDEX ON :Definition(DEF)
CREATE CONSTRAINT ON (n:NDC) ASSERT n.ATUI IS UNIQUE
CREATE CONSTRAINT ON (n:NDC) ASSERT n.NDC IS UNIQUE
```

### Remove orphan terms (again in cypher interface):
```cypher
MATCH (n:Term) WHERE size((n)--())=0 DELETE (n)
```

#### In the neo4j bolt web interface test the initial import by counting nodes (should return near 15837031):
```cypher
MATCH (n) RETURN count(n)
```
