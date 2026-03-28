import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient

# Add current folder to sys.path for Windows imports
# Adiciona a pasta atual ao sys.path para importações no Windows
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import services
# Importação de serviços
from services.excel_service import save_new_spreadsheet, get_consortium_data
from services.data_engine import get_best_consortium
from services.user_service import create_user, verify_user, get_all_users, delete_user

# Load environment variables
# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Professional CORS setup for Streamlit (Port 8501)
# Configuração profissional de CORS para o Streamlit (Porta 8501)
CORS(app)

# Security Token from .env
# Token de Segurança do .env
INTERNAL_TOKEN = os.getenv("INTERNAL_API_TOKEN")

# MongoDB Setup for Configs (AI Prompt)
# Configuração MongoDB para as instruções da IA (System Prompt)
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME", "alecs_consórcio")]
config_collection = db["system_configs"]

# ---
# HELPER FUNCTIONS
# FUNÇÕES AUXILIARES
# ---

def check_token():
    """Security check for internal token / Verificação de segurança do token"""
    token = request.headers.get("X-Alecs-Token")
    return INTERNAL_TOKEN and token == INTERNAL_TOKEN

def get_ai_script():
    """Retrieves script from DB / Recupera script do banco"""
    config = config_collection.find_one({"type": "ai_script"})
    return config.get("content") if config else "Você é um assistente especializado em consórcios da ALECS SEGUROS."

def update_ai_script(new_content):
    """Updates script in DB / Atualiza script no banco"""
    try:
        config_collection.update_one(
            {"type": "ai_script"},
            {"$set": {"content": new_content}},
            upsert=True
        )
        return True, "Script atualizado!"
    except Exception as e:
        return False, str(e)

# ---
# PUBLIC ROUTES
# ROTAS PÚBLICAS
# ---

@app.route('/api/v1/status', methods=['GET'])
def get_status():
    """Health check / Verificação de integridade"""
    return jsonify({"status": "Online", "service": "CONSORCIO-ALECS"}), 200

@app.route('/api/v1/analyze', methods=['POST'])
def analyze_data():
    """
    Analysis engine with OpenAI and History integration.
    Motor de análise com integração OpenAI e histórico.
    """
    if not check_token(): 
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json or {}
    user_message = data.get("message", "")
    chat_history = data.get("history", []) # AJUSTE: Captura o histórico enviado pelo Frontend
    
    # Logic now uses history to maintain context of the 7-step flow
    # Lógica agora usa histórico para manter contexto do fluxo de 7 passos
    answer, raw_data = get_best_consortium(user_message, chat_history)
    
    return jsonify({
        "success": True,
        "response": answer,
        "data": raw_data
    }), 200

# ---
# ADMIN SECURE ROUTES
# ROTAS SEGURAS DE ADMINISTRAÇÃO
# ---

@app.route('/api/v1/admin/login', methods=['POST'])
def admin_login():
    """Validates admin credentials / Valida as credenciais do administrador"""
    if not check_token(): 
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")

    if verify_user(username, password):
        return jsonify({"success": True, "message": "Login successful"}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/v1/admin/users', methods=['GET', 'POST'])
def manage_users():
    """Manages admin users (List and Create) / Gerencia usuários (Lista e Cria)"""
    if not check_token(): 
        return jsonify({"error": "Unauthorized"}), 401
    
    if request.method == 'POST':
        data = request.json or {}
        success, message = create_user(data.get("username"), data.get("password"))
        return jsonify({"message": message}), 201 if success else 400
    
    return jsonify({"success": True, "users": get_all_users()}), 200

@app.route('/api/v1/admin/users/<username>', methods=['DELETE'])
def remove_user(username):
    """Deletes a user by name / Deleta um usuário pelo nome"""
    if not check_token(): 
        return jsonify({"error": "Unauthorized"}), 401
    
    if delete_user(username):
        return jsonify({"success": True, "message": f"Usuário {username} removido"}), 200
    return jsonify({"success": False, "error": "Erro ao remover usuário"}), 400

@app.route('/api/v1/admin/config/script', methods=['GET', 'POST'])
def config_ai_script():
    """Manages AI system prompt / Gerencia o prompt do sistema da IA"""
    if not check_token(): 
        return jsonify({"error": "Unauthorized"}), 401
    
    if request.method == 'POST':
        data = request.json or {}
        success, message = update_ai_script(data.get("script"))
        return jsonify({"success": success, "message": message}), 200 if success else 500
    
    return jsonify({"success": True, "script": get_ai_script()}), 200

@app.route('/api/v1/admin/upload-excel', methods=['POST'])
def admin_upload():
    """Secure upload endpoint / Endpoint de upload seguro"""
    if not check_token(): 
        return jsonify({"error": "Unauthorized"}), 401
    
    if 'file' not in request.files: 
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    success, message = save_new_spreadsheet(file)
    return jsonify({"message": message}), 200 if success else 500

@app.route('/api/v1/admin/data', methods=['GET'])
def get_admin_data():
    """Retrieve data for admin dashboard / Recupera dados para o painel admin"""
    if not check_token(): 
        return jsonify({"error": "Unauthorized"}), 401
        
    df, message = get_consortium_data()
    if df is not None:
        return jsonify({"success": True, "data": df.to_dict(orient='records')}), 200
    return jsonify({"error": message}), 500

if __name__ == '__main__':
    # Running on port 5001 as defined in your setup
    # Rodando na porta 5001 conforme seu setup
    app.run(host='0.0.0.0', port=5001, debug=False)