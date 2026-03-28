import sys
import os

# Add the backend directory to sys.path to allow imports
# Adiciona o diretório backend ao sys.path para permitir importações
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from services.user_service import verify_user, get_all_users

def main():
    """
    Script to test database authentication directly.
    Script para testar a autenticação do banco de dados diretamente.
    """
    print("--- CONSORCIO-ALECS DEBUG ---")
    
    # List all users in the database
    # Lista todos os usuários no banco de dados
    users = get_all_users()
    print(f"\nUsers found in MongoDB / Usuários encontrados no MongoDB: {len(users)}")
    for u in users:
        print(f" - {u.get('username')} (Active: {u.get('active')})")

    if not users:
        print("\nNo users found. Please run setup_admin.py first.")
        print("Nenhum usuário encontrado. Por favor, rode o setup_admin.py primeiro.")
        return

    print("\nTest Login / Teste de Login:")
    username = input("Username / Usuário: ")
    password = input("Password / Senha: ")

    # Verify credentials
    # Verifica as credenciais
    is_valid = verify_user(username, password)

    if is_valid:
        print("\n✅ SUCCESS: Username and password match the database!")
        print("✅ SUCESSO: Usuário e senha correspondem ao banco de dados!")
        print("Se isso funcionou, o problema está no Streamlit/Flask (provavelmente o Token ou o Flask precisa ser reiniciado).")
    else:
        print("\n❌ FAILED: Invalid credentials in the database.")
        print("❌ FALHOU: Credenciais inválidas no banco de dados.")
        print("Verifique maiúsculas/minúsculas ou crie o usuário novamente.")

if __name__ == "__main__":
    main()