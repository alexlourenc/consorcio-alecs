import pandas as pd
import os

# ---
# CONSORTIUM DATABASE GENERATOR | GERADOR DE BASE DE DADOS DE CONSÓRCIO
# ---

def create_initial_excel():
    """
    Creates a professional Excel file with consortium quotes for testing.
    Cria um arquivo Excel profissional com cotas de consórcio para teste.
    """
    data = {
        'ID': [1, 2, 3, 4, 5, 6, 7, 8],
        'Administradora': ['Porto Seguro', 'Porto Seguro', 'Itaú', 'Itaú', 'Caixa', 'Caixa', 'HSBC', 'HSBC'],
        'Segmento': ['Imóvel', 'Imóvel', 'Automóvel', 'Automóvel', 'Pesados', 'Pesados', 'Imóvel', 'Automóvel'],
        'Credito': [200000, 500000, 50000, 80000, 300000, 450000, 250000, 60000],
        'Parcela': [1150.00, 2850.00, 650.00, 980.00, 1950.00, 2700.00, 1400.00, 750.00],
        'Prazo_Meses': [200, 180, 60, 72, 120, 120, 180, 60],
        'Taxa_Adm': [15, 12, 14, 13, 16, 15, 14, 15]
    }

    df = pd.DataFrame(data)
    
    # Path inside the project | Caminho dentro do projeto
    folder = os.path.join(os.getcwd(), '..', '..', 'data')
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    file_path = os.path.join(folder, 'base_consorcios.xlsx')
    
    # Save to Excel | Salva para Excel
    df.to_excel(file_path, index=False)
    print(f"[CONSORCIO-ALECS] Arquivo criado com sucesso em: {file_path}")

if __name__ == "__main__":
    create_initial_excel()