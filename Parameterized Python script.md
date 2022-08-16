# Parameterized Python script

**UMLS-Graph-Extracts.py** is a Python version of the **UMLS-Graph-Extracts.ipynb** Jupyter notebook.

Like the notebook, the script assumes:

1. An Oracle database that contains tables that correspond to the RRF files that are extracted from UMLS via the MetamorphoSys application. 
2. A text file named conn-string.txt that contains a connect string for the Oracle database.

Differences between the notebook and the script:

1. The script takes as an argument a string that corresponds to the descriptor for a biannual UMLS refresh (e.g., UMLS2022AB). The script confirms that the database contains a schema with a name that matches the argument string.
2. The script exports the CSV files to the application folder.
3. The script writes status updates to the screen before and after each individual export.
4. The script's SQL queries are parameterized to use the argument.