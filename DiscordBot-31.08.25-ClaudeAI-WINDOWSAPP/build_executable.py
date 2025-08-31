# ==========================================
# build_executable.py - Script per creare .exe
# ==========================================

"""
Script per creare un eseguibile Windows con PyInstaller

Uso:
1. Installa PyInstaller: pip install pyinstaller
2. Esegui questo script: python build_executable.py
"""

import subprocess
import sys
from pathlib import Path

def build_executable():
    """Crea l'eseguibile Windows"""
    
    # Comandi PyInstaller
    cmd = [
        "pyinstaller",
        "--onedir",  # Crea una cartella con tutti i file
        "--windowed",  # Nasconde la console
        "--name=GameWatchBot",
        "--icon=icon.ico",  # Se hai un'icona
        "--add-data=*.py;.",  # Include tutti i file Python
        "--hidden-import=PyQt6",
        "--hidden-import=aiohttp",
        "--hidden-import=selenium",
        "--hidden-import=beautifulsoup4",
        "run_desktop_app.py"
    ]
    
    try:
        print("🔨 Creazione eseguibile in corso...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Eseguibile creato con successo!")
        print("📁 Puoi trovarlo nella cartella 'dist/GameWatchBot/'")
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore nella creazione dell'eseguibile: {e}")
        print(f"Output: {e.output}")
        return False
    
    return True

if __name__ == "__main__":
    build_executable()