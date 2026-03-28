import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
# Carrega as variáveis de ambiente
load_dotenv()

# Global client variable for connection pooling
# Variável global do cliente para pool de conexões
_client = None

def get_database_connection():
    """
    Establishes and returns a connection to MongoDB Atlas using a singleton pattern.
    Estabelece e retorna uma conexão com o MongoDB Atlas usando o padrão singleton.
    """
    global _client
    
    # Get MongoDB URI from .env
    # Obtém a URI do MongoDB do .env
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME", "consorcio_alecs_db")

    if not mongo_uri:
        print("Error: MONGO_URI not found in .env file.")
        print("Erro: MONGO_URI não encontrada no arquivo .env.")
        return None

    try:
        if _client is None:
            # Initialize the client with certifi for secure Atlas connection
            # Inicializa o cliente com certifi para conexão segura com o Atlas
            _client = MongoClient(
                mongo_uri, 
                serverSelectionTimeoutMS=5000,
                tlsCAFile=certifi.where()
            )
            
            # Test connection
            # Testa a conexão
            _client.server_info() 
        
        return _client[db_name]
    
    except Exception as e:
        print(f"Database connection error: {e}")
        print(f"Erro de conexão com o banco de dados: {e}")
        return None

if __name__ == "__main__":
    # Internal connection test
    # Teste interno de conexão
    print("Testing connection to MongoDB Atlas...")
    print("Testando conexão com o MongoDB Atlas...")
    
    db = get_database_connection()
    if db is not None:
        print("Successfully connected to MongoDB Atlas!")
        print("Conexão com MongoDB Atlas realizada com sucesso!")