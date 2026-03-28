import os
from openai import OpenAI
from dotenv import load_dotenv
from services.excel_service import get_consortium_data
from services.config_service import get_ai_script

# Load environment variables
# Carrega variáveis de ambiente
load_dotenv()

def get_best_consortium(user_query, chat_history=None):
    """
    Intelligent engine that reads the System Prompt (7 steps) directly from MongoDB.
    Motor inteligente que lê o System Prompt (7 passos) diretamente do MongoDB.
    """
    if chat_history is None:
        chat_history = []

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Erro: Chave da OpenAI não configurada no .env.", []

    try:
        client = OpenAI(api_key=api_key)
        
        # 1. Fetch data from MongoDB
        # 1. Busca dados de consórcio no MongoDB
        df, _ = get_consortium_data()
        
        # Limitation to 20 rows to avoid Token Limit errors
        # Limitação a 20 linhas para evitar erros de limite de Tokens (Context Window)
        context_data = df.head(20).to_string(index=False) if df is not None else "Sem dados de tabela no momento."

        # 2. Fetch the CUSTOM SCRIPT from MongoDB Admin Config
        # 2. Busca o SCRIPT CUSTOMIZADO das configurações de Admin no MongoDB
        dynamic_system_prompt = get_ai_script()

        # 3. Build the context for OpenAI
        # 3. Monta o contexto para a OpenAI
        full_system_content = f"""
        {dynamic_system_prompt}
        
        ---
        DADOS REAIS DA TABELA PARA CONSULTA (USE APENAS ESTES DADOS):
        {context_data}
        ---
        """

        # Prepare messages starting with the dynamic system prompt
        # Prepara as mensagens começando com o system prompt dinâmico
        messages = [{"role": "system", "content": full_system_content}]
        
        # Append history to maintain the 7-step flow context
        # Adiciona o histórico para manter o contexto do fluxo de 7 passos
        for msg in chat_history:
            messages.append(msg)
            
        messages.append({"role": "user", "content": user_query})

        # 4. Generate response using GPT-4o
        # 4. Gera a resposta usando o GPT-4o
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3 # Precision-focused / Focado em precisão técnica
        )

        answer = response.choices[0].message.content
        
        # Return answer and top 3 candidates for visual presentation
        # Retorna a resposta e os 3 principais candidatos para apresentação visual
        top_candidates = df.head(3).to_dict(orient='records') if df is not None else []
        
        return answer, top_candidates

    except Exception as e:
        print(f"ERRO ENGINE: {e}")
        return f"Ops! Tive um problema técnico ao processar sua solicitação: {str(e)}", []