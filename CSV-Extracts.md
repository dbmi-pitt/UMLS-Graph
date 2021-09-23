# UMLS-Graph

SCRIPTS TO EXTRACT FROM NEPTUNE UMLS Relational and LOAD to UMLS Graph - JCS Nov 30, 2017 - Dec 09, 2020

V6: Sept 23, 2021 - the precise queries here are not all valid/updated, but they are valid in the related Jupyter Notebook in this repository - specifically the current documentation here has NDC codes as a distinct item, whereas they are true Codes in the proper Notebook. This is why the "neo4j/import" command no longer refers to NDC-related csv files and why the NDC-related constraints and indexes have been removed here.

V5: Dec 9, 2020 - Updated to neo4j 4.2 with APOC Core (for WHEN clauses in APIs) and UMLS2020AB - removed Term .name_lc to use Neo4j 4.2 Lucene-based search - added back MTH NOCODE - removed the use of combined relationships of REL plus RELA and just use the most specific - changed schema to remove TTY between CUI and CODE - changed schema to add CUI to Code-Term relations for proper graph navigation in circumstances of ambiguous codes (multi-concept codes).

V4: May 07, 2019 - Updated to neo4j 3.5.5 and UMLS2019AA

V3: Feb 19, 2018 - V3 Updated to neo4j 3.3.3 and added Term .name_lc for case in-sensitive search

V2: Dec 16, 2017 - V2 Used the principle of creating a concise database that accounts for TTY.

### General comment
"SELECT DISTINCT" was used liberally (even where it was not needed, because of unique IDs in UMLS). For convenience, we allow to relationships fail on import, if the connecting nodes don't exist, due to leveraging the --skip-bad-relationships flag.

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

### Extract Relationships among CUIs as CUI-CUIs.csv (with header) and limit to ENGlish and no SIB relationships and no Obsolete: 
```SQL
WITH SABlist as (SELECT DISTINCT SAB from UMLS.MRCONSO where UMLS.MRCONSO.LAT = 'ENG') SELECT DISTINCT CUI2 AS ":START_ID", CUI1 AS ":END_ID", NVL(RELA, REL) as ":TYPE", UMLS.MRREL.SAB from UMLS.MRREL inner join SABlist on UMLS.MRREL.SAB = SABlist.SAB where UMLS.MRREL.SUPPRESS <> 'O' and CUI1 <> CUI2 and REL <> 'SIB';
```

### Extract Code-nodes and save as CODEs.csv (with header):
```SQL
With CUIlist as (SELECT DISTINCT CUI from UMLS.MRCONSO where UMLS.MRCONSO.ISPREF = 'Y' AND UMLS.MRCONSO.STT = 'PF' AND UMLS.MRCONSO.TS = 'P' and UMLS.MRCONSO.LAT = 'ENG') SELECT DISTINCT (UMLS.MRCONSO.SAB||' '||UMLS.MRCONSO.CODE) as "CodeID:ID", UMLS.MRCONSO.SAB, UMLS.MRCONSO.CODE from UMLS.MRCONSO inner join CUIlist on UMLS.MRCONSO.CUI = CUIlist.CUI where UMLS.MRCONSO.LAT = 'ENG' and SUPPRESS <> 'O';
```

### Extract CODE-relationships of CUIs and save as CUI-CODEs.csv (with header):
```SQL
SELECT DISTINCT CUI as ":START_ID", (SAB||' '||CODE) as ":END_ID" from UMLS.MRCONSO where LAT = 'ENG' and SUPPRESS <> 'O';
```

### Extract Term-nodes and save as SUIs.csv (with header):
Again SUPPRESS is not used here but ENG language is - DISTINCT is essential. There are orphaned Terms because the query is not limiting to graph-included CUIs, CODEs OR Preferred Terms. At the end of this guide one runs a Cypher script to eliminate the orphans later.
```SQL
SELECT DISTINCT UMLS.MRCONSO.SUI as "SUI:ID", UMLS.MRCONSO.STR as "name" FROM UMLS.MRCONSO WHERE UMLS.MRCONSO.LAT = 'ENG';
```

### Extract Term-relationships of Codes and save as CODE-SUIs.csv (with header):
```SQL
SELECT DISTINCT SUI as ":END_ID", (SAB||' '||CODE) as ":START_ID", TTY as ":TYPE", CUI as CUI from UMLS.MRCONSO where LAT = 'ENG' and SUPPRESS <> 'O';
```

### Extract Preferred Term-relationship of Concepts and save as CUI-SUIs.csv (with header):
```SQL
SELECT DISTINCT CUI as ":START_ID", SUI as ":END_ID" from UMLS.MRCONSO where UMLS.MRCONSO.ISPREF = 'Y' AND UMLS.MRCONSO.STT = 'PF' AND UMLS.MRCONSO.TS = 'P' and UMLS.MRCONSO.LAT = 'ENG';
```

### Extract Definition-nodes and save as DEFs.csv (with header) - limit to ENGlish
```SQL
With CUIlist as (SELECT DISTINCT CUI from UMLS.MRCONSO where UMLS.MRCONSO.ISPREF = 'Y' AND UMLS.MRCONSO.STT = 'PF' AND UMLS.MRCONSO.TS = 'P' and UMLS.MRCONSO.LAT = 'ENG') SELECT DISTINCT UMLS.MRDEF.ATUI as "ATUI:ID", UMLS.MRDEF.SAB, UMLS.MRDEF.DEF FROM UMLS.MRDEF inner join CUIlist on UMLS.MRDEF.CUI = CUIlist.CUI where SUPPRESS <> 'O' AND NOT (UMLS.MRDEF.SAB LIKE 'MSH%' AND UMLS.MRDEF.SAB <> 'MSH') AND NOT (UMLS.MRDEF.SAB LIKE 'MDR%' AND UMLS.MRDEF.SAB <> 'MDR');
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
```
edit the neo4j.conf file and add this line:
```dbms.recovery.fail_on_missing_files=false```
```bash
rm -rf data/databases/*
rm -rf data/transactions/*
```

#### Put all csv files into standard neo4j import directory and then load into Neo4j via import tool from standard neo4j directory:
```bash
bin/neo4j-admin import --nodes=Semantic="import/TUIs.csv" --nodes=Concept="import/CUIs.csv" --nodes=Code="import/CODEs.csv" --nodes=Term="import/SUIs.csv" --nodes=Definition="import/DEFs.csv" --relationships=ISA_STY="import/TUIrel.csv" --relationships=STY="import/CUI-TUIs.csv" --relationships="import/CUI-CUIs.csv" --relationships=CODE="import/CUI-CODEs.csv" --relationships="import/CODE-SUIs.csv" --relationships=PREF_TERM="import/CUI-SUIs.csv" --relationships=DEF="import/DEFrel.csv" --skip-bad-relationships --skip-duplicate-nodes
```

#### At this point, after much load feedback a clean load should show something like the following (due to --ignore-missing-nodes there will be a note about bad entries skipped and an import.report but this can be ignored):
IMPORT DONE in 3m 9s 34ms. 
Imported:
  16226447 nodes
  44808023 relationships
  97153835 properties
  
#### Start Neo4j:
```bash
bin/neo4j start
```
### Remove orphan terms (in cypher interface).  Do this before you index the data to avoid indexing orphaned terms ("Deleted 512387 nodes"):
```cypher
MATCH (n:Term) WHERE size((n)--())=0 DELETE (n)
```

#### SET CONSTRAINTS and INDEXES on most things:
```cypher
CREATE CONSTRAINT ON (n:Semantic) ASSERT n.TUI IS UNIQUE;
CREATE CONSTRAINT ON (n:Semantic) ASSERT n.STN IS UNIQUE;
CREATE CONSTRAINT ON (n:Semantic) ASSERT n.DEF IS UNIQUE;
CREATE CONSTRAINT ON (n:Semantic) ASSERT n.name IS UNIQUE;
CREATE CONSTRAINT ON (n:Concept) ASSERT n.CUI IS UNIQUE;
CREATE CONSTRAINT ON (n:Code) ASSERT n.CodeID IS UNIQUE;
CREATE INDEX FOR (n:Code) ON (n.SAB);
CREATE INDEX FOR (n:Code) ON (n.CODE);
CREATE CONSTRAINT ON (n:Term) ASSERT n.SUI IS UNIQUE;
CREATE INDEX FOR (n:Term) ON (n.name);
CREATE CONSTRAINT ON (n:Definition) ASSERT n.ATUI IS UNIQUE;
CREATE INDEX FOR (n:Definition) ON (n.SAB);
CREATE INDEX FOR (n:Definition) ON (n.DEF);
CALL db.index.fulltext.createNodeIndex("Term_name",["Term"],["name"]);
```

#### In the neo4j bolt web interface test the initial import by counting nodes (should return near 15837031):
```cypher
MATCH (n) RETURN count(n)
```
