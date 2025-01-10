import streamlit as st
import datetime
import matplotlib.pyplot as plt
import pandas as pd
from pymongo import MongoClient
from bson import ObjectId

# Definir a URI de conexão
uri = "mongodb+srv://tarefasinteli:DaXD3KyyMvHbq-y@cluster0.b0h4u.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Conectar ao MongoDB usando a URI
client = MongoClient(uri)

# Acessar o banco de dados e a coleção
db = client["gerenciamento_tarefas"]  # Nome do banco de dados
tarefas_collection = db["tarefas"]  # Nome da coleção de tarefas

# Dicionário de usuários (para exemplo simples)
usuarios = {
    "admin": "1234",
    "alan": "senha123",
    "gustavo": "senha123",
    "eryck": "senha123",
}

# Função para verificar login
def verificar_login(usuario, senha):
    if usuario in usuarios and usuarios[usuario] == senha:
        return True
    return False

# Função para adicionar uma nova tarefa no MongoDB
def adicionar_tarefa_mongodb(tarefa):
    tarefas_collection.insert_one(tarefa)

# Função para buscar as tarefas do MongoDB
def buscar_tarefas_mongodb():
    tarefas = tarefas_collection.find()  # Retorna todas as tarefas
    return list(tarefas)  # Convertendo o cursor para uma lista

# Função para tela de login
def tela_login():
    st.title("Login")
    
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        if verificar_login(usuario, senha):
            st.success(f"Login realizado com sucesso! Bem-vindo, {usuario}.")
            st.session_state['logado'] = True
            st.session_state['usuario'] = usuario
        else:
            st.error("Usuário ou senha incorretos!")

# Função para adicionar uma nova tarefa com formulário
def adicionar_tarefa():
    st.subheader("Adicionar Nova Tarefa")
    
    with st.form(key="tarefa_form"):
        titulo = st.text_input("Título da Tarefa")
        descricao = st.text_area("Descrição da Tarefa")
        prazo = st.date_input("Prazo para Conclusão", min_value=datetime.date.today())
        destinatario = st.selectbox("Destinatário", list(usuarios.keys()))
        
        submit_button = st.form_submit_button("Salvar Tarefa")
        
        if submit_button:
            if not titulo or not descricao:
                st.warning("Título e descrição são obrigatórios!")
            else:
                prazo_formatado = prazo.strftime('%d/%m/%Y')
                data_atual = datetime.date.today().strftime('%d/%m/%Y')
                nova_tarefa = {
                    "titulo": titulo,
                    "descricao": descricao,
                    "adicionada_em": data_atual,
                    "prazo": prazo.strftime('%Y-%m-%d'),
                    "prazo_exibicao": prazo_formatado,
                    "criador": st.session_state['usuario'],
                    "destinatario": destinatario,
                    "status": "Não iniciada",
                    "historico": [f"{datetime.datetime.now()}: Criada por {st.session_state['usuario']}."] 
                }
                # Salvar no MongoDB
                adicionar_tarefa_mongodb(nova_tarefa)
                st.success(f"Tarefa '{titulo}' adicionada com sucesso!")

# Função para gerenciar tarefas com filtros e remoção
def gerenciar_tarefas():
    st.subheader("Gerenciar Tarefas")
    
    tarefas = buscar_tarefas_mongodb()  # Recuperando as tarefas do MongoDB
    
    if len(tarefas) == 0:
        st.info("Nenhuma tarefa cadastrada.")
        return
    
    # Filtros
    filtro_data_inicial = st.date_input("Filtrar por Data de Início", value=datetime.date.today())
    filtro_data_final = st.date_input("Filtrar por Data Final", value=datetime.date.today())
    filtro_criador = st.multiselect("Filtrar por Criador", ["Todos"] + list(set([t["criador"] for t in tarefas])))
    filtro_destinatario = st.multiselect("Filtrar por Destinatário", ["Todos"] + list(set([t["destinatario"] for t in tarefas])))
    filtro_status = st.multiselect("Filtrar por Status", ["Todos", "Não iniciada", "Em andamento", "Concluída"])

    # Aplicando os filtros
    tarefas_filtradas = tarefas
    
    if filtro_criador != ["Todos"]:
        tarefas_filtradas = [t for t in tarefas_filtradas if t["criador"] in filtro_criador]
    
    if filtro_destinatario != ["Todos"]:
        tarefas_filtradas = [t for t in tarefas_filtradas if t["destinatario"] in filtro_destinatario]
    
    if filtro_status != ["Todos"]:
        tarefas_filtradas = [t for t in tarefas_filtradas if t["status"] in filtro_status]
    
    if filtro_data_inicial:
        tarefas_filtradas = [t for t in tarefas_filtradas if datetime.datetime.strptime(t["adicionada_em"], "%d/%m/%Y").date() >= filtro_data_inicial]
    
    if filtro_data_final:
        tarefas_filtradas = [t for t in tarefas_filtradas if datetime.datetime.strptime(t["adicionada_em"], "%d/%m/%Y").date() <= filtro_data_final]

    # Exibindo as tarefas filtradas com estilo de card
    for i, tarefa in enumerate(tarefas_filtradas):
        st.markdown(
            f"""
            <div style="border: 2px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 20px; background-color: #f9f9f9;">
                <h3 style="color: #333;">{tarefa['titulo']}</h3>
                <p><b>Descrição:</b> {tarefa['descricao']}</p>
                <p><b>Adicionada em:</b> {tarefa['adicionada_em']}</p>
                <p><b>Prazo:</b> {tarefa['prazo_exibicao']}</p>
                <p><b><span style="color: #2e8b57;">Criado por:</span></b> <b>{tarefa['criador']}</b></p>
                <p><b><span style="color: #1e90ff;">Destinatário:</span></b> <b>{tarefa['destinatario']}</b></p>
                <p>
                    <b>Status:</b>
                    <span style="color: {'red' if tarefa['status'] == 'Não iniciada' else 'orange' if tarefa['status'] == 'Em andamento' else 'green'};">
                    {'🔴 Não Iniciada' if tarefa['status'] == 'Não iniciada' else '🟠 Em Andamento' if tarefa['status'] == 'Em andamento' else '🟢 Concluída'}</span>
                </p>
                <p><b>Histórico:</b></p>
                <ul style="padding-left: 20px;">
                    {"".join([f"<li>{evento}</li>" for evento in tarefa['historico']])}
                </ul>
                <div style="display: flex; justify-content: space-between;">
                    <button style="padding: 5px 10px; background-color: #4CAF50; color: white; border: none; border-radius: 5px;" onclick="alterar_status()">Alterar Status</button>
                    <button style="padding: 5px 10px; background-color: #f44336; color: white; border: none; border-radius: 5px;" onclick="remover_tarefa()">🗑️ Remover Tarefa</button>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Função para gráficos de progresso das tarefas
def graficos_progresso():
    st.subheader("Gráficos de Progresso das Tarefas")
    
    # Preparar dados para gráficos
    df = pd.DataFrame(buscar_tarefas_mongodb())  # Atualizar com as tarefas do MongoDB

    # Gráfico de status das tarefas por criador
    tarefas_por_status = df.groupby(["criador", "status"]).size().unstack().fillna(0)
    ax = tarefas_por_status.plot(kind='bar', stacked=True, figsize=(6, 3), color=["red", "orange", "green"])  # Tamanho ajustado
    ax.set_title("Status das Tarefas por Criador", fontsize=12)  # Fonte ajustada
    ax.set_ylabel("Quantidade de Tarefas", fontsize=8)  # Fonte ajustada
    
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', 
                    (p.get_x() + p.get_width() / 2, p.get_height()), 
                    ha='center', va='center', 
                    fontsize=8, color='white')
    
    st.pyplot(ax.figure)
    st.write(f"Total de tarefas: {df.shape[0]}")

# Função de Overview
def tela_overview():
    st.title("Visão Geral das Tarefas")
    
    
    # Buscar tarefas do MongoDB
    tarefas = buscar_tarefas_mongodb()

    # Verificar se existem tarefas
    if not tarefas:
        st.info("Nenhuma tarefa cadastrada no momento.")
        return

    # Normalizar os dados para garantir que todas as tarefas têm o campo 'status'
    for tarefa in tarefas:
        if "status" not in tarefa:
            tarefa["status"] = "Não especificado"  # Valor padrão

    # Criar DataFrame a partir das tarefas
    tarefas_df = pd.DataFrame(tarefas)

    # Verificar se o DataFrame tem a coluna 'status'
    if "status" not in tarefas_df.columns:
        st.warning("As tarefas não possuem o campo 'status'.")
        return

    # Contando as tarefas por status
    tarefas_por_status = tarefas_df["status"].value_counts()

    # Dividindo a tela em duas colunas
    col1, col2 = st.columns(2)

    # Card com o total de tarefas (Coluna 1)
    with col1:
        st.markdown(
            f"""
            <div style="border: 2px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 20px; background-color: #f9f9f9; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);">
                <h3 style="color: #333; font-size: 20px; font-weight: bold;">Total de Tarefas</h3>
                <p style="font-size: 18px; color: #555;"><b>{len(tarefas_df)}</b> tarefas cadastradas</p>
            </div>
            """, unsafe_allow_html=True)

    # Card com tarefas concluídas (Coluna 1)
    with col1:
        st.markdown(
            f"""
            <div style="border: 2px solid #4CAF50; border-radius: 10px; padding: 15px; margin-bottom: 20px; background-color: #e8f5e9; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);">
                <h3 style="color: #388E3C; font-size: 20px; font-weight: bold;">Tarefas Concluídas</h3>
                <p style="font-size: 18px; color: #388E3C;"><b>{tarefas_por_status.get('Concluída', 0)}</b> tarefas concluídas</p>
            </div>
            """, unsafe_allow_html=True)

    # Card com tarefas em andamento (Coluna 2)
    with col2:
        st.markdown(
            f"""
            <div style="border: 2px solid #FF9800; border-radius: 10px; padding: 15px; margin-bottom: 20px; background-color: #fff3e0; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);">
                <h3 style="color: #F57C00; font-size: 20px; font-weight: bold;">Tarefas em Andamento</h3>
                <p style="font-size: 18px; color: #F57C00;"><b>{tarefas_por_status.get('Em andamento', 0)}</b> tarefas em andamento</p>
            </div>
            """, unsafe_allow_html=True)

    # Card com tarefas não iniciadas (Coluna 2)
    with col2:
        st.markdown(
            f"""
            <div style="border: 2px solid #f44336; border-radius: 10px; padding: 15px; margin-bottom: 20px; background-color: #ffebee; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);">
                <h3 style="color: #D32F2F; font-size: 20px; font-weight: bold;">Tarefas Não Iniciadas</h3>
                <p style="font-size: 18px; color: #D32F2F;"><b>{tarefas_por_status.get('Não iniciada', 0)}</b> tarefas não iniciadas</p>
            </div>
            """, unsafe_allow_html=True)

    # Gráfico de status das tarefas
    st.subheader("Gráfico de Status das Tarefas")
    cores = ['#D32F2F', '#F57C00', '#388E3C']  # Vermelho, Laranja, Verde
    fig, ax = plt.subplots()
    tarefas_por_status.plot(kind="pie", autopct='%1.1f%%', colors=cores, ax=ax)
    ax.set_ylabel("")
    plt.title("Distribuição das Tarefas por Status")
    st.pyplot(fig)

# Função principal
def main():
    if 'logado' not in st.session_state or not st.session_state['logado']:
        tela_login()
    else:
        st.sidebar.title("Menu")
        opcao = st.sidebar.selectbox("Selecione uma opção", ["Visão Geral", "Adicionar Tarefa", "Gerenciar Tarefas", "Gráficos de Progresso"])
        
        if opcao == "Visão Geral":
            tela_overview()
        elif opcao == "Adicionar Tarefa":
            adicionar_tarefa()
        elif opcao == "Gerenciar Tarefas":
            gerenciar_tarefas()
        elif opcao == "Gráficos de Progresso":
            graficos_progresso()

# Chama a função principal
if __name__ == "__main__":
    main()
