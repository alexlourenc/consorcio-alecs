import streamlit as st
import requests
import os
import pandas as pd
import urllib.parse # Para codificar a mensagem do WhatsApp
from dotenv import load_dotenv

# ---
# CLIENT CHAT INTERFACE | INTERFACE DE CHAT COM CONVERSÃO WHATSAPP
# ---

load_dotenv()

st.set_page_config(page_title="ALECS SEGUROS - Especialista", page_icon="🤖")

# API Configuration
API_TOKEN = os.getenv("INTERNAL_API_TOKEN")
HEADERS = {"X-Alecs-Token": API_TOKEN}
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5001/api/v1")

st.title("🤖 Assistente de Consórcios ALECS")
st.markdown("---")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "data" in message and message["data"]:
            with st.expander("📊 Ver Opções Detalhadas"):
                st.dataframe(pd.DataFrame(message["data"]), use_container_width=True)

# React to user input
if prompt := st.chat_input("Ex: Qual o melhor plano para um caminhão de 300 mil?"):
    st.chat_message("user").markdown(prompt)
    
    # 1. Prepare history (Last 6 messages)
    history_to_send = [
        {"role": m["role"], "content": m["content"]} 
        for m in st.session_state.messages[-6:]
    ]

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Analisando grupos e calculando estratégias..."):
            try:
                # 2. Call Backend
                response = requests.post(
                    f"{BACKEND_URL}/analyze",
                    json={
                        "message": prompt,
                        "history": history_to_send
                    },
                    headers=HEADERS
                )
                
                if response.status_code == 200:
                    res_json = response.json()
                    answer = res_json.get("response", "Sem resposta.")
                    raw_data = res_json.get("data", [])

                    # Display AI answer
                    st.markdown(answer)
                    
                    # 3. Present data
                    if raw_data:
                        with st.expander("🎯 Grupos Sugeridos para Análise"):
                            st.table(pd.DataFrame(raw_data))

                    # 4. WHATSAPP CONVERSION BUTTON
                    # 4. BOTÃO DE CONVERSÃO WHATSAPP
                    # Detecta se a IA está entregando uma recomendação ou fechando o ciclo
                    keywords = ["estratégia", "recomendação", "escolher", "proposta", "concluir"]
                    if any(key in answer.lower() for key in keywords):
                        # Prepara a mensagem automática para você receber no Zap
                        wa_text = f"Olá Alex! Finalizei minha simulação de consórcio e gostaria de falar com um especialista sobre a proposta: {prompt[:50]}..."
                        wa_encoded = urllib.parse.quote(wa_text)
                        
                        # Coloque seu número com código do país e DDD
                        meu_numero = "5511916008486" 
                        wa_link = f"https://wa.me/{meu_numero}?text={wa_encoded}"
                        
                        st.divider()
                        st.link_button("🚀 Falar com Especialista no WhatsApp", wa_link, use_container_width=True, type="primary")
                    
                    # Save to session
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer, 
                        "data": raw_data
                    })
                else:
                    st.error("Erro na análise do servidor.")
            except Exception as e:
                st.error(f"Falha na comunicação: {e}")