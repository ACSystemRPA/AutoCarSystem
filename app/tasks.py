import os
import shutil
from datetime import datetime
from flask import current_app

def realizar_backup():
    """
    Script periódico de extração e salvaguarda do sqlite da base de dados.
    Irá criar uma cópia zipada em /backups do autocarsystem.db.
    """
    app = current_app._get_current_object()
    if not app:
        return
        
    try:
        # Aceder ao diretório base onde está a BD
        basedir = os.path.abspath(os.path.join(app.root_path, '..'))
        db_path = os.path.join(basedir, 'autocarsystem.db')
        backup_dir = os.path.join(basedir, 'backups')
        
        # Garante que `backups/` existe
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        data_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        nome_backup = f"autocarsystem_db_backup_{data_str}.db"
        dest_path = os.path.join(backup_dir, nome_backup)
        
        if os.path.exists(db_path):
            shutil.copy2(db_path, dest_path)
            # Registo nos logs de servidor do Flask
            print(f"[Backup Automático] SQLite backup guardado em: {dest_path}")
            
    except Exception as e:
        print(f"[Backup Automático] Falhou a execução: {str(e)}")
