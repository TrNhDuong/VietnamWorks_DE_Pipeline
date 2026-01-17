import yaml
import html
import bleach

def load_config_database(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    return config['data']

def load_minio_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    return config['minio']

def load_posgres_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    return config['posgres']

def loader(config_path: str, type: str):
    if type == 'data':
        return load_config_database(config_path=config_path)
    elif type == 'minio':
        return load_minio_config(config_path=config_path)
    elif type == 'posgres':
        return load_posgres_config(config_path=config_path)
    else:
        return None


def clean_html_text(text):
    if not isinstance(text, str):
        return text
    # 1️⃣ Unescape HTML entities
    unescaped = html.unescape(text)
    # 2️⃣ Remove all HTML tags
    clean = bleach.clean(unescaped, tags=[], strip=True)
    # 3️⃣ Strip leading/trailing whitespace
    return clean.strip()


