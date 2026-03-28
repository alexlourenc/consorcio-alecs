import bcrypt
from database.db_config import get_database_connection

def create_user(username, password):
    """
    Creates a new admin user with a hashed password in MongoDB.
    Cria um novo usuário administrador com senha criptografada no MongoDB.
    """
    try:
        db = get_database_connection()
        if db is None:
            return False, "Erro de conexão com o banco de dados."
        
        users_collection = db['admin_users']
        
        # Check if user already exists
        # Verifica se o usuário já existe
        if users_collection.find_one({"username": username}):
            return False, "Usuário já existe no sistema."
        
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        users_collection.insert_one({
            "username": username,
            "password_hash": hashed,
            "role": "admin",
            "active": True
        })
        return True, "Usuário criado com sucesso."
    except Exception as e:
        return False, f"Erro ao criar usuário: {str(e)}"

def verify_user(username, password):
    """
    Verifies if the provided username and password match the database.
    Verifica se o usuário e a senha fornecidos correspondem ao banco de dados.
    """
    try:
        db = get_database_connection()
        if db is None:
            return False
            
        users_collection = db['admin_users']
        user = users_collection.find_one({"username": username})
        
        if not user or not user.get("active", True):
            return False
            
        return bcrypt.checkpw(password.encode('utf-8'), user['password_hash'])
    except Exception:
        return False

def get_all_users():
    """
    Retrieves all registered admin users (excluding passwords).
    Recupera todos os usuários administradores cadastrados (excluindo senhas).
    """
    try:
        db = get_database_connection()
        if db is None:
            return []
            
        users_collection = db['admin_users']
        
        # Exclude '_id' and 'password_hash' from the results
        # Exclui '_id' e 'password_hash' dos resultados
        users = list(users_collection.find({}, {"_id": 0, "password_hash": 0}))
        return users
    except Exception:
        return []

def delete_user(username):
    """
    Deletes a user from the database.
    Remove um usuário do banco de dados.
    """
    try:
        db = get_database_connection()
        if db is None:
            return False, "Erro de conexão com o banco de dados."
            
        users_collection = db['admin_users']
        
        # Prevent deleting the last admin user (safety check could be added here)
        # Previne deletar o último usuário admin (checagem de segurança pode ser adicionada aqui)
        
        result = users_collection.delete_one({"username": username})
        
        if result.deleted_count > 0:
            return True, "Usuário removido com sucesso."
        return False, "Usuário não encontrado."
    except Exception as e:
        return False, f"Erro ao remover usuário: {str(e)}"