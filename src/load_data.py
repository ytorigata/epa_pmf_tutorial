import os
import pandas as pd
from urllib.parse import urlsplit, parse_qs, unquote

from src.config import *

def load_station_data():

    # Load URL
    url_df = pd.read_csv(str(DATA_URLS_FILE))
    station_url = url_df.loc[url_df['description'].str.contains("station", case=False), 'url'].values[0]
    
    # Extract file name from the query parameter
    query = urlsplit(station_url).query
    query_params = parse_qs(query)
    raw_path = query_params.get('path', [''])[0]
    station_filename = os.path.basename(unquote(raw_path))
    
    # Construct full path
    station_file_path = RAW_META_DIR / station_filename

    sheet_name = 'Stations2023'
    
    df = pd.read_excel(
        str(station_file_path), 
        sheet_name=sheet_name, 
        engine='openpyxl',
        header=0,          # use the first row as column names (English header)
        skiprows=[1],      # skip the second row (French header)
    )
    return df


def load_target_sheet(year: int, site_id: int, key: str) -> pd.DataFrame:
    """
    Load one worksheet (identified by *key*: 'nt', 'ws', 'ion', or 'bbm')
    from the Burnaby South file for the given *year*.
    - output: pd.DataFrame
    """
    sheet_map = get_sheets_for_year(year)

    if key == 'pm25':
        sheet_name = 'PM2.5'
    else:
        if key not in sheet_map:
            raise ValueError(f"Sheet key '{key}' not available for {year}")
        sheet_name = sheet_map[key]
    
    file_path = (
        RAW_INTEGRATED_DATA_DIR
        / f"{year}_IntegratedPM2.5-PM2.5Ponctuelles"
        / f"S{site_id}_PM25_{year}_EN.xlsx"
    )

    return pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        engine="openpyxl",
        skiprows=9,   # skip metadata rows
        header=0      # use the 10th row as column names
    )

