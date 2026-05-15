import os
import json
import pandas as pd
import streamlit as st
import plotly.express as px

# Configuração da página do SIMOC
st.set_page_config(page_title="SIMOC - Monitor de Exfiltração", layout="wide")
st.title("🛡️ SIMOC CyberRange - Análise de Volumetria de Rede")

LOG_FILE = "/var/log/simoc_traffic.log"

# Botão de atualização manual ou loop de auto-refresh
st.sidebar.markdown("### Configurações de Monitoramento")
if st.sidebar.button("Atualizar Dados 🔄"):
    st.rerun()

# Verifica se o arquivo de log existe
if not os.path.exists(LOG_FILE):
    st.info("Aguardando tráfego ser gerado... O arquivo de log ainda não foi populado.")
else:
    # Lê o arquivo de log JSON gerado pelo coletor
    with open(LOG_FILE, "r") as f:
        try:
            data = json.load(f)
            st.sidebar.success(f"Última atualização: {data['timestamp']}")
            st.sidebar.text(f"Host Monitorado: {data['host_origem']}")
            
            # Transforma os dados em um DataFrame do Pandas
            df = pd.DataFrame(data['destinos'])
            
            if not df.empty:
                # Ordena pelos maiores volumes de upload
                df = df.sort_values(by="megabytes", ascending=False)
                
                # Cria duas colunas na tela
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("### Gráfico de Exfiltração por Destino (MB)")
                    # Gera o gráfico de barras dinâmico usando Plotly
                    fig = px.bar(df, x="ip_destino", y="megabytes", 
                                 labels={"ip_destino": "IP de Destino", "megabytes": "Dados Enviados (MB)"},
                                 color="megabytes", color_continuous_scale="Reds")
                    st.plotly_chart(fig, use_container_width=True)
                    
                with col2:
                    st.markdown("### Tabela de Dados Brutos")
                    st.dataframe(df, use_container_width=True)
                    
            else:
                st.warning("Nenhum tráfego externo detectado ainda.")
                
        except json.JSONDecodeError:
            st.error("Erro ao ler o arquivo de log. Aguardando escrita completa.")