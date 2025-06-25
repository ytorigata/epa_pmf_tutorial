from pathlib import Path
import numpy as np
import pandas as pd
from typing import Optional

def export_analytes(df_or_path, dest_dir, prefix=''):
    """
    Split a cleaned input DataFrame or CSV file into individual per-analyte files for EPA PMF input.

    Parameters
    ----------
    df_or_path : DataFrame or str or Path
        Either a cleaned DataFrame or a path to a cleaned CSV file.
    dest_dir : str or Path
        Directory to save individual analyte CSVs.
    prefix : str or None
        Optional prefix for output filenames (e.g., 'nt_', 'ion_').
        If None, no prefix is added.
    """
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Load if a path is given
    if isinstance(df_or_path, (str, Path)):
        input_path = Path(df_or_path)
        df = pd.read_csv(input_path, parse_dates=['sampling_date'], index_col='sampling_date')
        print(f"Loaded: {input_path.name}")
    else:
        df = df_or_path.copy()

    display(df.columns)
    df = df[df['sampling_type'] == 'R']
    
    # Drop metadata columns
    for col in ['site_id', 'sampling_type']:
        if col in df.columns:
            df = df.drop(columns=col)
            
    # Loop through analytes
    analytes = [c for c in df.columns if not c.endswith('-MDL')]
    for analyte in analytes:
        mdl_col = f"{analyte}-MDL"
        if mdl_col not in df.columns:
            continue

        sub_df = df[[analyte, mdl_col]].dropna(how='all')
        if sub_df.empty:
            continue

        sub_df.index.name = 'Date'
        fname = f'{prefix}{analyte}.csv'
        sub_df.to_csv(dest_dir / fname)

    print(f"✔ Exported {len(analytes)} analytes to {dest_dir}")
    

def fill_missing_mdl(df: pd.DataFrame, analyte_cols: Optional[list] = None) -> pd.DataFrame:
    """
    Fill missing MDL values (NaN only) in a DataFrame based on the following logic:
    - If MDL is present, keep it (including -999 values).
    - If MDL is NaN and ≥7 FB/TB blanks are available: MDL = 3 * std(blank_values)
    - Else: MDL = 0.5 * min(positive_values)
    - If no fallback available, leave as NaN.

    Parameters:
    - df: DataFrame with analyte and corresponding '-MDL' columns
    - analyte_cols: Optional list of analytes to process (column names without '-MDL').
                    If None, inferred automatically.

    Returns:
    - Updated DataFrame with missing MDL values filled (except -999)
    """
    df_filled = df.copy()

    if analyte_cols is None:
        analyte_cols = [
            col for col in df_filled.columns
            if not col.endswith('-MDL') and col not in ['sampling_date', 'sampling_type', 'site_id']
        ]

    for analyte in analyte_cols:
        mdl_col = f"{analyte}-MDL"
        if mdl_col not in df_filled.columns:
            continue

        # Identify only true NaN values (do not modify -999)
        mdl_na_mask = df_filled[mdl_col].isna()
        if not mdl_na_mask.any():
            continue

        # Blank values (from field/travel blanks)
        blank_mask = df_filled['sampling_type'].isin(['FB', 'TB'])
        blank_values = df_filled.loc[blank_mask, analyte].replace(-999, np.nan).dropna()

        if len(blank_values) >= 7:
            mdl_value = 3 * blank_values.std()
        else:
            pos_values = df_filled[analyte][df_filled[analyte] > 0]
            mdl_value = 0.5 * pos_values.min() if not pos_values.empty else np.nan

        df_filled.loc[mdl_na_mask, mdl_col] = mdl_value

    return df_filled