# ==========================================
# run_desktop_app.py - Launcher principale
# ==========================================

import sys
import os
from pathlib import Path

def main():
    """Funzione principale per avviare l'app desktop"""
    
    # Aggiungi il percorso corrente al PYTHONPATH
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Importa dopo aver configurato il path
    from PyQt6.QtWidgets import QApplication
    from main_app import GameWatchMainWindow
    
    # Crea l'applicazione
    app = QApplication(sys.argv)
    app.setApplicationName("Game Watch Bot")
    app.setApplicationVersion("1.0.0")
    
    # Crea e mostra la finestra principale
    main_window = GameWatchMainWindow()
    main_window.show()
    
    # Avvia il loop dell'applicazione
    sys.exit(app.exec())

if __name__ == "__main__":
    main()