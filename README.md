# UMLS-Graph
UMLS Graph database for semantic queries.

This project extracts from UMLS Metathesauras and Semantic Network files in Oracle, transforms, loads, deploys, and queries the resulting neo4j knowledge graph.
It uses the conceptual model pictured here:

![Alt text](UMLS-Graph-Model.jpg?raw=true "Title")

The starting point of this repository is the UMLS active subset distribution loaded into Oracle.
The ending point of this repository (what it functionally creates) is a live neo4j database of the UMLS active subset English Terms, Codes (including NDC Codes as an SAB called NDC), Concepts, Semantic Types, and Definitions according to the conceptual model pictured, and deployed in a docker container on Amazon Web Services with a UI at Guesdt.com.

## CSV-Extracts
CSV-Extracts.md contains descriptions of and the SQL to generate each of the CSV files from UMLS active subset in Oracle. This file also contains the neo4j database import load script which reads the CSV files and loads them into neo4j. Note this has only been tested on the community edition running from neo4j's unix tar distribution on Mac OSX. A roughly equivalent but better Jupyter Notebook for the SQL extracts is also in this repository (not including the neo4j loads or index calls).

## Graph-Query-Examples
Graph-Query-Examples.md contains example useful Cypher queries for the complete UMLS-Graph database running in neo4j. NEEDS UPDATE.

## Graph-Deploy-AWS
Graph-Deploy-AWS.md contains implementation instructions to build a Docker version of UMLS-Graph on an AWS EC2 instance (minimum 4 GB memory recommended).

## UI Javascript code
Guesdt-X.X.X.html is the UI code deployed at guesdt.com after login.
