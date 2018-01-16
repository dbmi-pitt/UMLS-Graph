# UMLS-Graph
UMLS Graph database for semantic queries.

This project loads, deploys, and queries neo4j graph database and docker container directly from the UMLS distribution files.
It uses the conceptual model pictured here: ![Alt text](UMLS-Graph-Model.jpg?raw=true "Title")
The starting point of this repository is the UMLS active subset distribution loaded into Oracle.
The ending point of this repository (what it functionally creates) is a live neo4j database of the UMLS active subset English Terms, Codes, Concepts, Semantic Types, Definitions and NDC codes linked to RXNorm according to the conceptual model pictured, and deployed in a docker container on Amazon Web Services.
