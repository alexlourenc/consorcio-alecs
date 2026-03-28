import sys
import os
import getpass

# Add the backend directory to sys.path to allow imports
# Adiciona o diretório backend ao sys.path para permitir importações
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from services.user_service import create_user

def main():
    """
    Command line script to create the first admin user securely.
    Script de linha de comando para criar o primeiro usuário administrador com segurança.
    """
    print("--- CONSORCIO-ALECS ---")
    print("Admin Setup / Configuração de Administrador\n")

    username = input("Enter the new admin username / Digite o nome do novo usuário admin: ")
    password = getpass.getpass("Enter the password (hidden) / Digite a senha (oculta): ")
    confirm_password = getpass.getpass("Confirm the password / Confirme a senha: ")

    if password != confirm_password:
        print("\nError: Passwords do not match. / Erro: As senhas não coincidem.")
        return

    print("\nCreating user in MongoDB... / Criando usuário no MongoDB...")
    success, message = create_user(username, password)

    if success:
        print(f"Success! / Sucesso! {message}")
    else:
        print(f"Failed. / Falhou. {message}")

if __name__ == "__main__":
    main()