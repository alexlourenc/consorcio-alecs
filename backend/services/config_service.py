from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
# Carrega variáveis de ambiente
load_dotenv()

# MongoDB Connection
# Conexão com o MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
config_collection = db["system_configs"]

def get_ai_script():
    """Retrieves the current AI instruction script"""
    """Recupera o script de instrução da IA atual"""
    try:
        config = config_collection.find_one({"type": "ai_script"})
        if config:
            return config.get("content")
        return "Você é um assistente especializado em consórcios da ALECS SEGUROS."
    except Exception as e:
        print(f"Erro ao buscar script: {e}")
        return "Erro ao carregar script do banco."

def update_ai_script(new_content):
    """Updates or creates the AI instruction script"""
    """Atualiza ou cria o script de instrução da IA"""
    try:
        config_collection.update_one(
            {"type": "ai_script"},
            {"$set": {"content": new_content}},
            upsert=True
        )
        return True, "Script atualizado com sucesso!"
    except Exception as e:
        print(f"Erro ao salvar no MongoDB: {e}")
        return False, str(e)