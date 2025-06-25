import re
import pandas as pd

def drop_vflag_cols(df):
    """Drop columns ending with '-VFlag'."""
    return df.drop(columns=df.filter(regex=r'-VFlag$').columns)

_RENAME_MAP = {
    'NAPS Site ID': 'site_id',
    'Sampling Date': 'sampling_date',
    'Sampling Type': 'sampling_type',
    'Sample Type': 'sampling_type',
}

def rename_cols(df, mapping=_RENAME_MAP):
    """Rename key metadata columns for clarity."""
    return df.rename(columns=mapping)

def normalize_analyte_names(df):
    """
    Simplify analyte column names:
    - Keep only the abbreviation inside parentheses
    - Leave columns like 'Levoglucosan' or 'X-MDL' unchanged
    """
    rename_map = {}
    for col in df.columns:
        if col.endswith('-MDL'):
            continue
        match = re.search(r'\(([^)]+)\)', col)
        rename_map[col] = match.group(1).strip() if match else col
    return df.rename(columns=rename_map)

def convert_micro_to_nano(df):
    """
    Convert units from µg/m³ to ng/m³,
    preserving -999 values as-is.
    - input: df: DataFrame
    - output: A DataFrame with converted units
    """
    df_converted = df.copy()
    for col in df.columns:
        if df[col].dtype.kind in 'fi':  # numeric column
            # Convert values that are not -999
            df_converted[col] = df[col].apply(
                lambda x: x * 1000 if x != -999 else x
            )

    return df_converted
