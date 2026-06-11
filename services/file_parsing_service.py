import pandas as pd
from config import Config
import logging
logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger()

def validate_csv(filename,filepath):
    if filename is None:
        logger.error('Filename not provided')
        raise ValueError('filename must not be None')
    
    if filepath is None:
        logger.error('File path is not provided')
        raise ValueError('filepath must not be None')

    stripped_extension = filename.strip().split('.')
    extension = stripped_extension[1]
    if extension != Config.ALLOWED_EXTENSION:
        logger.warning(f'Given file is not a csv file. Received file_extension:{extension}')
        return None
    df = pd.read_csv(filepath)
    csv_data = df.to_dict(orient='records')

    if not csv_data:
        logger.warning('Csv is empty or data not parsed')
        return None
    
    return csv_data
