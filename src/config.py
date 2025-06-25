from pathlib import Path

RAW_DATA_DIR = Path('../data/raw')
RAW_META_DIR = Path('../data/meta')
RAW_INTEGRATED_DATA_DIR = Path('../data/raw/integrated')

PROCESSED_DATA_DIR = Path('../data/processed/integrated')
PMF_INPUT_DATA_DIR = Path('../data/processed/pmf')

DATA_URLS_FILE = Path('../data/config/data_urls.csv')


available_sheets = {
    2020: ['nt', 'ws', 'ion', 'bbm'],
    2021: ['nt'],
    2022: ['nt'],
    2023: ['nt', 'ws', 'ion', 'bbm'],
}

sheet_key_to_name = {
    'nt': 'Metals_ICPMS (Near-Total)', 
    'ws': 'Metals_ICPMS (Water-Soluble)', 
    'ion': 'Ions-Spec_IC', 
    'bbm': 'Biomass Burning Markers_IC',
}

def get_sheets_for_year(year):
    """Return a list of official Excel sheet names for the given year."""
    keys = available_sheets.get(year, [])
    return {key: sheet_key_to_name[key] for key in keys}
