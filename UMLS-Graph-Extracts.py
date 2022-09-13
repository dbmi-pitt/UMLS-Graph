# UMLS-Graph Extract

# Generates a set of CSV files for ingest into a graph database (neo4j).
# Assumes accessible Oracle database of UMLS Metathesaurus and Semantic Network

# import sys
import numpy as np
import pandas as pd
import cx_Oracle
import sqlalchemy
import argparse


# Parse an argument that identifies the version of the UMLS in Neptune from which to build
# the CSV files.
class RawTextArgumentDefaultsHelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawTextHelpFormatter
):
    pass


parser = argparse.ArgumentParser(
    description='Build .csv files from UMLS tables in Neptune',
    formatter_class=RawTextArgumentDefaultsHelpFormatter)
parser.add_argument("umlsversion", help="version of the UMLS refresh")
args = parser.parse_args()

# Connect to Neptune.
_ = open('conn_string.txt', 'r');
conn_string = _.read().replace('\n', '');
_.close()
engine = sqlalchemy.create_engine(conn_string, arraysize=100000, max_identifier_length=128)
pd.set_option('display.max_colwidth', None)

# Check for a schema that matches the argument.
query = "SELECT username FROM sys.all_users WHERE username='{0}'".format(args.umlsversion)
df = pd.read_sql_query(query, engine)
if df.size == 0:
    raise SystemExit('There is no UMLS schema named' + str(args.umlsversion) + ' in the database.')

# EXPORT TO FILES SELECTED INFORMATION FROM THE UMLS METATHESAURUS AND SEMANTIC NETWORK.
# ------
# TUIs.csv
# Semantic Types from the Semantic Network.

print('TUIs.csv: export started')
query = "SELECT DISTINCT UI, STY_RL, STN_RTN, DEF FROM {0}.SRDEF WHERE RT = 'STY'".format(args.umlsversion)
df = pd.read_sql_query(query, engine)
df.columns = ['TUI:ID', 'name', 'STN', 'DEF']
df.to_csv(path_or_buf='TUIs.csv', header=True, index=False)
print('TUIs.csv: {0} records exported'.format(str(df.size)))

# ------
# TUIrel.csv
query = "WITH Semantics as (SELECT DISTINCT UI from {0}.SRDEF WHERE RT = 'STY') SELECT DISTINCT UI3, UI1 FROM {0}.SRSTRE1 INNER JOIN Semantics ON {0}.SRSTRE1.UI1 = Semantics.UI WHERE UI2 = 'T186'".format(args.umlsversion)
df = pd.read_sql_query(query, engine)
df.columns =[':END_ID', ':START_ID']
df.to_csv(path_or_buf='TUIrel.csv', header=True, index=False)
print('TUIrel.csv: {0} records exported'.format(str(df.size)))

# ------
# CUIs.csv
# Concepts from the Metathesaurus that have preferred terms in English.

print('CUIs.csv: export started')
query = "SELECT DISTINCT CUI from {0}.MRCONSO where {0}.MRCONSO.ISPREF = 'Y' AND {0}.MRCONSO.STT = 'PF' AND " \
        "{0}.MRCONSO.TS = 'P' and {0}.MRCONSO.LAT = 'ENG'".format(args.umlsversion)
df = pd.read_sql_query(query, engine)
df.columns =['CUI:ID']
df.to_csv(path_or_buf='CUIs.csv', header=True, index=False)
print('CUIs.csv: {0} records exported'.format(str(df.size)))

# ------
# CUI-TUIs.csv
# Semantic types (TUI) assigned to each concept (CUI)

print('CUI-TUIs.csv: export started')
query = "SELECT DISTINCT CUI, TUI FROM {0}.MRSTY".format(args.umlsversion)
df = pd.read_sql_query(query, engine)
df.columns =[':START_ID', ':END_ID']
df.to_csv(path_or_buf='CUI-TUIs.csv', header=True, index=False)
print('CUI-TUIs.csv: {0} records exported'.format(str(df.size)))

# ------
# CUI-CUIs.csv
# Relationships between concepts that are:
# a. not self-relationships
# b. not sibling relationships
# c. active (not suppressed)

print('CUI-CUIs.csv: export started')
query = "WITH SABlist as (SELECT DISTINCT SAB from {0}.MRCONSO where {0}.MRCONSO.LAT = 'ENG') SELECT DISTINCT CUI2, " \
        "CUI1, NVL(RELA, REL), {0}.MRREL.SAB from {0}.MRREL inner join SABlist on {0}.MRREL.SAB = SABlist.SAB where " \
        "{0}.MRREL.SUPPRESS <> 'O' and CUI1 <> CUI2 and REL <> 'SIB'".format(args.umlsversion)
df = pd.read_sql_query(query, engine)
df.columns =[':START_ID', ':END_ID', ':TYPE', 'SAB']
df.to_csv(path_or_buf='CUI-CUIs.csv', header=True, index=False)
print('CUI-CUIs.csv: {0} records exported'.format(str(df.size)))

# ------
# CODEs.csv
# Source codes (from source vocabularies) for concepts.

print('CODEs.csv: export started')
query = "With CUIlist as (SELECT DISTINCT CUI from {0}.MRCONSO where {0}.MRCONSO.ISPREF = 'Y' AND {0}.MRCONSO.STT = " \
        "'PF' AND {0}.MRCONSO.TS = 'P' and {0}.MRCONSO.LAT = 'ENG') SELECT DISTINCT ({0}.MRCONSO.SAB||' '||" \
        "{0}.MRCONSO.CODE), {0}.MRCONSO.SAB, {0}.MRCONSO.CODE from {0}.MRCONSO inner join CUIlist on {0}.MRCONSO.CUI = " \
        "CUIlist.CUI where {0}.MRCONSO.LAT = 'ENG' and SUPPRESS <> 'O'".format(args.umlsversion)
df = pd.read_sql_query(query, engine)
df.columns =['CodeID:ID', 'SAB', 'CODE']
df.to_csv(path_or_buf='CODEs.csv', header=True, index=False)
print('CODES.csv: {0} records exported'.format(str(df.size)))

# ------
# CUI-CODEs.csv
# Map CUIs to source codes.
print('CUI-CODEs.csv: export started')
query = "SELECT DISTINCT CUI, (SAB||' '||CODE) FROM {0}.MRCONSO WHERE LAT = 'ENG' AND SUPPRESS <> 'O'".format(args.umlsversion)
df = pd.read_sql_query(query, engine)
df.columns =[':START_ID', ':END_ID']
df.to_csv(path_or_buf='UMLS-Graph-Extracts/CUI-CODEs.csv', header=True, index=False)
print('CUI-CODEs.csv: {0} records exported'.format(str(df.size)))

# Keep a copy for use by NDCs later
CUI_CODEs = df.copy()

# ------
# SUIs.csv
# Unique string terms for concepts.
print('SUIs.csv: export started')
query = "SELECT DISTINCT {0}.MRCONSO.SUI, {0}.MRCONSO.STR FROM {0}.MRCONSO WHERE {0}.MRCONSO.LAT = 'ENG'".format(args.umlsversion)
df = pd.read_sql_query(query, engine)
df.columns =['SUI:ID', 'name']
df.to_csv(path_or_buf='SUIs.csv', header=True, index=False)
print('SUIs.csv: {0} records exported'.format(str(df.size)))

# ------
# CODE-SUIs.csv
# Map strings (SUIs) to concept codes.

print('CODE-SUIs.csv: export started')
query = "SELECT DISTINCT SUI, (SAB||' '||CODE), TTY, CUI FROM {0}.MRCONSO WHERE LAT = 'ENG' AND SUPPRESS <> 'O'".format(args.umlsversion)
df = pd.read_sql_query(query, engine)
df.columns =[':END_ID', ':START_ID', ':TYPE', 'CUI']
df.to_csv(path_or_buf='CODE-SUIs.csv', header=True, index=False)
print('CODE-SUIs.csv: {0} records exported'.format(str(df.size)))

# ------
# CUI-SUIs.csv
# Obtain relevant CUI-SUI relationships.

print('CUI-SUIs.csv: export started')
query = "SELECT DISTINCT CUI, SUI FROM {0}.MRCONSO WHERE {0}.MRCONSO.ISPREF = 'Y' AND {0}.MRCONSO.STT = 'PF' AND " \
        "{0}.MRCONSO.TS = 'P' and {0}.MRCONSO.LAT = 'ENG'".format(args.umlsversion)
df = pd.read_sql_query(query, engine)
df.columns =[':START_ID', ':END_ID']
df.to_csv(path_or_buf='CUI-SUIs.csv', header=True, index=False)
print('CUI-SUIs.csv: {0} records exported'.format(str(df.size)))

# ------
# DEFs.csv
# Obtain relevant definitions for concepts.
# Special filtering for definitions from the MESH and MEDDRA libraries.

print('DEFs.csv: export started')
query = "With CUIlist as (SELECT DISTINCT CUI from {0}.MRCONSO where {0}.MRCONSO.ISPREF = 'Y' AND {0}.MRCONSO.STT = " \
        "'PF' AND {0}.MRCONSO.TS = 'P' and {0}.MRCONSO.LAT = 'ENG') SELECT DISTINCT {0}.MRDEF.ATUI, {0}.MRDEF.SAB, " \
        "ASCIISTR({0}.MRDEF.DEF) FROM {0}.MRDEF inner join CUIlist on {0}.MRDEF.CUI = CUIlist.CUI where SUPPRESS <> " \
        "'O' AND NOT (SAB LIKE 'MSH%' AND SAB <> 'MSH') AND NOT (SAB LIKE 'MDR%' AND SAB <> 'MDR')".format(args.umlsversion)
df = pd.read_sql_query(query, engine)
df.columns =['ATUI:ID', 'SAB', 'DEF']
df.to_csv(path_or_buf='DEFs.csv', header=True, index=False)
print('DEFs.csv: {0} records exported'.format(str(df.size)))

# ------
# DEFrel.csv
# Map definitions to concepts.

print('DEFrel.csv: export started')
query = "SELECT DISTINCT ATUI, CUI FROM {0}.MRDEF WHERE SUPPRESS <> 'O'".format(args.umlsversion)
df = pd.read_sql_query(query, engine)
df.columns =[':END_ID',':START_ID']
df.to_csv(path_or_buf='DEFrel.csv', header=True, index=False)
print('DEFrel.csv: {0} records exported'.format(str(df.size)))

# ------
# Append NDCs to CODEs.csv and to CUI-CODEs.csv after merge to CUI_CODEs RXNORM CUIs
print('Appending NDC data to CODES.csv: export started')
query = "SELECT DISTINCT ATV, (SAB||' '||CODE) FROM {0}.MRSAT WHERE SAB = 'RXNORM' and ATN = 'NDC' and SUPPRESS <> 'O'".format(args.umlsversion)
df = pd.read_sql_query(query, engine)
df.columns = ['CODE', ':END_ID']
df['SAB'] = 'NDC'
df['CodeID:ID'] = df['SAB'] + " " + df['CODE']
df[['CodeID:ID', 'SAB', 'CODE']].to_csv('CODEs.csv', mode='a', header=False, index=False)
print('CODEs.csv: {0} records appended'.format(str(df.size)))

print('Appending NDC data to CUI-CODES.csv: export started')
df = df.merge(CUI_CODEs, how='inner', on=':END_ID')
df = df[[':START_ID','CodeID:ID']].rename({'CodeID:ID':':END_ID'}, axis=1)
df.to_csv('CUI-CODEs.csv', mode='a', header=False, index=False)
print('CUI-CODEs.csv: {0} records appended'.format(str(df.size)))
print('Exports completed.')
