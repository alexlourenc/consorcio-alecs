import os
import bcrypt
from database.db_config import get_database_connection

def set_admin_password(new_password):
    """
    Hashes and saves the new admin password in MongoDB.
    Gera o hash e salva a nova senha do administrador no MongoDB.
    """
    try:
        db = get_database_connection()
        admin_collection = db['admin_settings']
        
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), salt)
        
        admin_collection.update_one(
            {"setting": "admin_password"},
            {"$set": {"hash": hashed}},
            upsert=True
        )
        return True
    except Exception:
        return False

def verify_admin_password(input_password):
    """
    Verifies if the provided password matches the hash in DB.
    Verifica se a senha fornecida corresponde ao hash no Banco.
    """
    try:
        db = get_database_connection()
        admin_collection = db['admin_settings']
        
        record = admin_collection.find_one({"setting": "admin_password"})
        
        if not record:
            default_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "Alecs2026")
            return input_password == default_password
        
        return bcrypt.checkpw(input_password.encode('utf-8'), record['hash'])
    except Exception:
        return False