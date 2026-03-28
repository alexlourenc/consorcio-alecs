import pandas as pd
from datetime import datetime
from database.db_config import get_database_connection

def save_new_spreadsheet(file):
    """
    Reads the uploaded Excel file and saves its data to MongoDB.
    Lê o arquivo Excel enviado e salva seus dados no MongoDB.
    """
    try:
        db = get_database_connection()
        if db is None:
            return False, "Erro de conexão com o banco de dados."

        collection = db['consortium_data']

        # Read Excel file directly from the file stream
        # Lê o arquivo Excel diretamente do fluxo do arquivo
        df = pd.read_excel(file)

        # Standardize column names
        # Padroniza os nomes das colunas
        df.columns = df.columns.str.strip().str.title()

        # Convert DataFrame to a list of dictionaries
        # Converte o DataFrame para uma lista de dicionários
        records = df.to_dict(orient='records')

        if not records:
            return False, "A planilha está vazia."

        # Clear existing data and insert new data
        # Limpa os dados existentes e insere os novos dados
        collection.delete_many({})
        collection.insert_many(records)

        # Log the upload event in a separate collection
        # Registra o evento de upload em uma coleção separada
        log_collection = db['system_logs']
        log_collection.insert_one({
            "action": "upload_excel",
            "timestamp": datetime.now(),
            "records_inserted": len(records)
        })

        return True, f"Planilha processada! {len(records)} registros salvos no banco de dados."

    except Exception as e:
        return False, f"Erro ao processar e salvar arquivo: {str(e)}"

def get_consortium_data():
    """
    Retrieves the consortium data directly from MongoDB.
    Recupera os dados de consórcio diretamente do MongoDB.
    """
    try:
        db = get_database_connection()
        if db is None:
            return None, "Erro de conexão com o banco de dados."

        collection = db['consortium_data']
        
        # Fetch all records, excluding the MongoDB '_id' field
        # Busca todos os registros, excluindo o campo '_id' do MongoDB
        records = list(collection.find({}, {'_id': 0}))
        
        if not records:
            return None, "Nenhum dado encontrado no banco de dados."
            
        df = pd.DataFrame(records)
        return df, "Sucesso"
        
    except Exception as e:
        return None, f"Erro ao recuperar dados: {str(e)}"