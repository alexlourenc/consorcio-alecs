import streamlit as st
import requests
import os
import pandas as pd
from dotenv import load_dotenv

# ---
# ADMIN DASHBOARD | PAINEL ADMINISTRATIVO INTEGRADO
# ---

# Load environment variables
# Carrega variáveis de ambiente
load_dotenv()

st.set_page_config(
    page_title="Admin - CONSORCIO-ALECS",
    page_icon="🔐",
    layout="wide"
)

# Environment variables and API setup
# Variáveis de ambiente e configuração da API
API_TOKEN = os.getenv("INTERNAL_API_TOKEN", "alecs_secure_token_2026_xyz")
HEADERS = {"X-Alecs-Token": API_TOKEN}
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5001/api/v1")

def show_script_editor():
    """
    Interface to customize the AI System Prompt.
    Interface para customizar o System Prompt da IA.
    """
    st.subheader("📝 Customização do Agente IA")
    st.info("Defina as regras e o passo a passo de 7 pontos que a IA deve seguir.")

    # Fetch current script from API
    # Busca o script atual via API
    if "current_script" not in st.session_state:
        try:
            response = requests.get(f"{BACKEND_URL}/admin/config/script", headers=HEADERS)
            if response.status_code == 200:
                st.session_state.current_script = response.json().get("script", "")
            else:
                st.session_state.current_script = ""
        except Exception as e:
            st.error(f"Erro ao buscar script: {e}")
            st.session_state.current_script = ""

    # Text area for editing
    # Área de texto para edição
    new_script = st.text_area(
        "Script de Instruções (System Prompt):",
        value=st.session_state.get("current_script", ""),
        height=400,
        help="Insira aqui o roteiro de atendimento da ALECS SEGUROS."
    )

    if st.button("Salvar Novo Script", use_container_width=True):
        with st.spinner("Atualizando cérebro da IA no MongoDB..."):
            try:
                res = requests.post(
                    f"{BACKEND_URL}/admin/config/script",
                    json={"script": new_script},
                    headers=HEADERS
                )
                if res.status_code == 200:
                    st.success("✅ Script atualizado! A IA já está operando com as novas regras.")
                    st.session_state.current_script = new_script
                else:
                    st.error(f"❌ Erro ao salvar no banco: {res.status_code}")
            except Exception as e:
                st.error(f"❌ Falha de conexão com o Backend: {e}")

def login_section():
    """
    Handles the admin authentication UI using the database.
    Gerencia a interface de autenticação do administrador usando o banco de dados.
    """
    st.title("🔐 Acesso Restrito")
    st.markdown("Por favor, insira suas credenciais para acessar o painel administrativo.")
    
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar", use_container_width=True)
        
        if submit:
            if username and password:
                try:
                    res = requests.post(
                        f"{BACKEND_URL}/admin/login",
                        json={"username": username, "password": password},
                        headers=HEADERS
                    )
                    if res.status_code == 200:
                        st.session_state['admin_logged_in'] = True
                        st.session_state['current_user'] = username
                        st.rerun()
                    else:
                        st.error("Usuário ou senha inválidos.")
                except Exception as e:
                    st.error(f"Erro de conexão com o servidor: {e}")
            else:
                st.error("Informe usuário e senha.")

def admin_dashboard():
    """
    Main admin dashboard layout with 3 tabs.
    Layout principal do painel administrativo com 3 abas.
    """
    st.title("⚙️ Painel de Administração - CONSORCIO-ALECS")
    
    col_header, col_logout = st.columns([8, 1])
    with col_header:
        st.write(f"Bem-vindo, **{st.session_state.get('current_user', 'Admin')}**!")
    with col_logout:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state['admin_logged_in'] = False
            st.session_state['current_user'] = None
            st.rerun()

    st.markdown("---")

    # Added the third tab here for IA Configuration
    # Adicionada a terceira aba aqui para Configuração IA
    tab1, tab2, tab3 = st.tabs(["📊 Base de Dados", "🤖 Configuração IA", "👥 Gestão de Usuários"])

    # TAB 1: DATABASE (Original logic maintained)
    with tab1:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Upload de Base de Dados")
            st.info("Upload da planilha Excel. Os dados antigos serão substituídos.")
            uploaded_file = st.file_uploader("Selecione o arquivo Excel", type=['xlsx', 'xls', 'csv'])
            if uploaded_file and st.button("Processar e Salvar no Banco", use_container_width=True):
                with st.spinner("Processando..."):
                    try:
                        files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        res = requests.post(f"{BACKEND_URL}/admin/upload-excel", files=files, headers=HEADERS)
                        if res.status_code == 200:
                            st.success(res.json().get("message", "Sucesso!"))
                        else:
                            st.error(f"Erro no servidor: {res.status_code}")
                    except Exception as e:
                        st.error(f"Falha de comunicação: {e}")

        with col2:
            st.subheader("Visualização dos Dados (MongoDB)")
            if st.button("🔄 Atualizar Tabela", use_container_width=True):
                st.rerun()
            try:
                res = requests.get(f"{BACKEND_URL}/admin/data", headers=HEADERS)
                if res.status_code == 200:
                    data_response = res.json()
                    if data_response.get("success") and data_response.get("data"):
                        df = pd.DataFrame(data_response["data"])
                        st.dataframe(df, use_container_width=True, height=400)
                        st.caption(f"Total de registros: {len(df)}")
            except Exception as e:
                st.error(f"Erro ao carregar banco: {e}")

    # TAB 2: AI CONFIGURATION (New logic)
    with tab2:
        show_script_editor()

    # TAB 3: USER MANAGEMENT (Original logic maintained)
    with tab3:
        col_add, col_list = st.columns([1, 2])
        with col_add:
            st.subheader("Novo Usuário")
            with st.form("new_user_form", clear_on_submit=True):
                new_user = st.text_input("Nome de Usuário")
                new_pass = st.text_input("Senha", type="password")
                if st.form_submit_button("Criar Usuário"):
                    if new_user and new_pass:
                        res = requests.post(f"{BACKEND_URL}/admin/users", json={"username": new_user, "password": new_pass}, headers=HEADERS)
                        if res.status_code == 201:
                            st.success("Usuário criado!")
                            st.rerun()
                        else:
                            st.error(res.json().get("error", "Erro ao criar."))

        with col_list:
            st.subheader("Usuários Cadastrados")
            if st.button("🔄 Atualizar Lista", use_container_width=True):
                st.rerun()
            try:
                res = requests.get(f"{BACKEND_URL}/admin/users", headers=HEADERS)
                if res.status_code == 200:
                    users = res.json().get("users", [])
                    for u in users:
                        with st.container():
                            uc1, uc2 = st.columns([4, 1])
                            uc1.write(f"👤 **{u['username']}** - {'🟢 Ativo' if u.get('active') else '🔴 Inativo'}")
                            if u['username'] != st.session_state.get('current_user'):
                                if uc2.button("🗑️", key=f"del_{u['username']}"):
                                    requests.delete(f"{BACKEND_URL}/admin/users/{u['username']}", headers=HEADERS)
                                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao listar usuários: {e}")

if __name__ == "__main__":
    if 'admin_logged_in' not in st.session_state:
        st.session_state['admin_logged_in'] = False

    if not st.session_state['admin_logged_in']:
        login_section()
    else:
        admin_dashboard()