import datetime
import os
from config import LOG_DIR

def setup_log_directory():
    """Crea el directorio de logs si no existe."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

def log_action(module, action, details):
    """Registra una acción en un archivo de log."""
    setup_log_directory()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file_path = os.path.join(LOG_DIR, f"{datetime.date.today().strftime('%Y-%m-%d')}_system_admin.log")
    
    with open(log_file_path, "a") as f:
        f.write(f"[{timestamp}] [{module}] [{action}] {details}\n")