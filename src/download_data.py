import os
import requests
import pandas as pd
import logging
from urllib.parse import urlsplit

from src.config import *

# Optional: install tqdm if not already installed
from tqdm import tqdm

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

RAW_CONTINUOUS_PM25_DIR = 'raw_pm25_data'

def ensure_directory_exists(path):
    os.makedirs(path, exist_ok=True)

def download_file(url, directory, fname=''):
    """
    Download a file from a given URL and save it to a directory.
    - input:
        - url (str): The URL to download from.
        - directory (str): Directory path to save the file.
        - fname (str): Optional custom file name.
    """
    file_name = fname if fname else url.split('%2F')[-1]
    file_path = os.path.join(directory, file_name)
    
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/113.0.0.0 Safari/537.36'
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        with open(file_path, 'wb') as f:
            f.write(response.content)
        logger.info(f"Downloaded: {file_name}")
    except requests.RequestException as e:
        logger.error(f"Failed to download {url}: {e}")

def download_station_file():
    """
    Download and save NAPS stations information.
    """
    url_df = pd.read_csv(str(DATA_URLS_FILE))
    station_df = url_df[url_df['type'] == 'meta'].copy()
    ensure_directory_exists(str(RAW_META_DIR))

    for _, row in tqdm(station_df.iterrows(), total=len(station_df), desc="Downloading files"):
        download_file(row['url'], str(RAW_META_DIR))


def download_integrated_pm25():
    """
    Download and save NAPS Integrated data for PM2.5.
    """
    url_df = pd.read_csv(str(DATA_URLS_FILE))
    integrated_df = url_df[(url_df['type'] == 'integrated') & (url_df['description'] == 'PM2.5')].copy()
    
    ensure_directory_exists(str(RAW_INTEGRATED_DATA_DIR))

    for _, row in tqdm(integrated_df.iterrows(), total=len(integrated_df), desc="Downloading files"):
        download_file(row['url'], str(RAW_INTEGRATED_DATA_DIR))


def download_continuous_dataset():
    """
    Download and save continuous PM2.5 speciation data.
    """
    url_df = pd.read_csv(DATA_URLS_FILE)
    continuous_df = url_df[url_df['type'] == 'continuous'].copy()
    ensure_directory_exists(RAW_CONTINUOUS_PM25_DIR)

    for _, row in tqdm(continuous_df.iterrows(), total=len(continuous_df), desc="Downloading files"):
        download_file(row['url'], RAW_CONTINUOUS_PM25_DIR)
