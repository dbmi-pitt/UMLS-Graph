# UMLS-Graph
UMLS Graph database for semantic queries.

This project loads, deploys, and queries neo4j graph database and docker container directly from the UMLS distribution files.
It uses the conceptual model pictured here: ![Alt text](UMLS-Graph-Model.jpg?raw=true "Title")
The starting point of this repository is the UMLS active subset distribution loaded into Oracle.
The ending point of this repository (what it functionally creates) is a live neo4j database of the UMLS active subset English Terms, Codes, Concepts, Semantic Types, Definitions and NDC codes linked to RXNorm according to the conceptual model pictured, and deployed in a docker container on Amazon Web Services.

## CSV-Extracts
CSV-Extracts.md contains descriptions of and the SQL to generate each of the CSV files from UMLS active subset in Oracle. This file also contains the neo4j database import load script which reads the CSV files and loads them into neo4j. Note this has only been tested on the community edition running from neo4j's unix tar distribution on Mac OSX.

## Graph-Query-Examples
Graph-Query-Examples.md contains example useful Cypher queries for the complete UMLS-Graph database running in neo4j.

## Graph-Deploy-AWS
Graph-Deploy-AWS.md contains implementation instructions to build a Docker version of UMLS-Graph on an AWS EC2 instance (minimum 4 GB memory recommended).
