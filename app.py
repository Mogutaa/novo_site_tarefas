import streamlit as st
import datetime
import matplotlib.pyplot as plt
import pandas as pd
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import bcrypt
import os

# Carregar variáveis do .env
load_dotenv()

# Recuperar a URI do MongoDB
uri = os.getenv("MONGO_URI")

# Conectar ao MongoDB usando a URI
client = MongoClient(uri)

# Acessar o banco de dados e a coleção
db = client["gerenciamento_tarefas"]  # Nome do banco de dados
usuarios_collection = db["usuarios"]  # Nome da coleção de usuários
tarefas_collection = db["tarefas"]  # Nome da coleção de tarefas

# Dicionário de usuários (usando variáveis de ambiente)
usuarios = {
    "admin": os.getenv("USERS_ADMIN"),
    "alan": os.getenv("USERS_ALAN"),
    "gustavo": os.getenv("USERS_GUSTAVO"),
    "eryck": os.getenv("USERS_ERYCK"),
}

# Função para hash de senha
def hash_senha(senha):
    # Gerar o salt e hash para a senha
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(senha.encode('utf-8'), salt)
    return hashed

# Verificar se já existem usuários no MongoDB

#if usuarios_collection.count_documents({}) == 0:
    #for user, senha in usuarios.items():
        # Criar hash da senha
       #hashed_senha = hash_senha(senha)
        
        # Inserir o usuário no banco de dados
        #usuarios_collection.insert_one({"username": user, "senha": hashed_senha})

    #st.write("Usuários cadastrados com sucesso!")
#else:
    #st.write("Usuários já estão cadastrados no banco de dados.")


# Função para verificar login
def verificar_login(usuario, senha):
    usuario_db = usuarios_collection.find_one({"username": usuario})
    if usuario_db and bcrypt.checkpw(senha.encode('utf-8'), usuario_db["senha"]):
        return True
    return False

# Função para adicionar uma nova tarefa no MongoDB
def adicionar_tarefa_mongodb(tarefa):
    tarefas_collection.insert_one(tarefa)

def logout():
    if 'logado' in st.session_state:
        del st.session_state['logado']
        del st.session_state['usuario']
        st.success("Você foi deslogado com sucesso!")
   

def alterar_status_mongodb(tarefa_id, novo_status, usuario):
    tarefas_collection.update_one(
        {"_id": ObjectId(tarefa_id)},
        {"$set": {"status": novo_status},
         "$push": {"historico": f"{datetime.datetime.now()}: Status alterado para '{novo_status}' por {usuario}."}}  # Adicionando o usuário
    )

# Função para buscar as tarefas do MongoDB
def buscar_tarefas_mongodb():
    tarefas = tarefas_collection.find()  # Retorna todas as tarefas
    return list(tarefas)  # Convertendo o cursor para uma lista

# Função para tela de login
def tela_login():
    # Estilização geral
    st.markdown(
        """
        <style>
        body {
            margin: 0;
            padding: 0;
        }
        .main-title {
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            color: #4CAF50;
            margin-top: 10px;
            margin-bottom: 20px;
        }
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            transition: 0.3s;
        }
        .stButton > button:hover {
            background-color: #45a049;
        }
        .stTextInput > div {
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 5px;
            background-color: #f9f9f9;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        }
        .login-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            max-width: 400px;
            margin: auto;
            padding: 20px;
            border: 2px solid #ddd;
            border-radius: 10px;
            background-color: #ffffff;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Título principal do site
    st.markdown('<h1 class="main-title">Site de Tarefas - Inteligência Logística</h1>', unsafe_allow_html=True)

    # Layout centralizado do formulário de login
    #st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="stTitle">🔒 Login</h2>', unsafe_allow_html=True)
    
    # Campos de entrada
    usuario = st.text_input("Usuário", key="login_usuario")
    senha = st.text_input("Senha", type="password", key="login_senha")
    
    # Botão de login
    if st.button("Entrar"):
        if verificar_login(usuario, senha):
            st.success(f"Login realizado com sucesso! Bem-vindo, {usuario}.")
            st.session_state['logado'] = True
            st.session_state['usuario'] = usuario
        else:
            st.error("Usuário ou senha incorretos!")
    
    st.markdown('</div>', unsafe_allow_html=True)




def remover_tarefa_mongodb(tarefa_id):
    """Remove uma tarefa do MongoDB."""
    tarefas_collection.delete_one({"_id": ObjectId(tarefa_id)})
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
    for tarefa in tarefas_filtradas:
        # Corrigir a formatação da descrição e do histórico
        descricao_formatada = tarefa['descricao'].replace('\n', '<br>')
        
        # Formatando o histórico com a tag <ul> corretamente
        historico_formatado = ""
        for evento in tarefa.get('historico', []):
            historico_formatado += f"<li>{evento.replace('\n', '<br>')}</li>"

        st.markdown(
            f"""
            <div style="border: 2px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 20px; background-color: #f9f9f9; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);">
                <h3 style="color: #333; font-size: 20px; margin-bottom: 10px;">{tarefa['titulo']}</h3>
                <p><b>Descrição:</b> {descricao_formatada}</p>
                <p><b>Adicionada em:</b> {tarefa['adicionada_em']}</p>
                <p><b>Prazo:</b> {tarefa['prazo_exibicao']}</p>
                <p><b>Criado por:</b> {tarefa['criador']}</p>
                <p><b>Destinatário:</b> {tarefa['destinatario']}</p>
                <p><b>Status Atual:</b> 
                    <span style="color: {'red' if tarefa['status'] == 'Não iniciada' else 'orange' if tarefa['status'] == 'Em andamento' else 'green'};">
                    {'🔴 Não Iniciada' if tarefa['status'] == 'Não iniciada' else '🟠 Em Andamento' if tarefa['status'] == 'Em andamento' else '🟢 Concluída'}</span>
                </p>
                <p><b>Histórico:</b></p>
                <ul style="padding-left: 20px; list-style: disc;">
                    {historico_formatado}
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # Controles para ações
        col1, col2 = st.columns([3, 1])  # Ajustar layout
        with col1:
            novo_status = st.selectbox(
                f"Alterar status de '{tarefa['titulo']}'",
                ["Não iniciada", "Em andamento", "Concluída"],
                index=["Não iniciada", "Em andamento", "Concluída"].index(tarefa["status"])
            )
            if st.button(f"Salvar Alteração ({tarefa['titulo']})"):
                alterar_status_mongodb(tarefa['_id'], novo_status, st.session_state['usuario'])  # Passando o usuário
                st.success(f"Status da tarefa '{tarefa['titulo']}' alterado para '{novo_status}'.")
                

        with col2:
            if st.button(f"Remover Tarefa ({tarefa['titulo']})"):
                remover_tarefa_mongodb(tarefa['_id'])
                st.warning(f"Tarefa '{tarefa['titulo']}' removida com sucesso.")


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
    st.title("📊 Visão Geral das Tarefas")

    # Descrição explicativa abaixo da visão geral
    st.markdown(
    f"""
    ## Bem-vindo {st.session_state['usuario']} à Visão Geral das Tarefas! 🎉

    Aqui você pode visualizar o status de todas as tarefas em andamento 🛠️, 
    concluídas ✅ ou ainda não iniciadas ⏳. Utilize as opções para alterar o status 
    das tarefas conforme o andamento do seu trabalho. Além disso, você pode 
    acompanhar o progresso do time através de gráficos 📊 e cartões interativos 📅.

    Abaixo, você encontrará um resumo geral e gráficos sobre as tarefas do sistema. 
    Com eles, você pode ter uma visão rápida do desempenho da equipe 💪 e do andamento 
    dos projetos. Clique nas tarefas para ver mais detalhes 👇 e atualizar seu status.
    """
)

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
                <h3 style="color: #388E3C; font-size: 20px; font-weight: bold;">Tarefas Concluídas ✅</h3>
                <p style="font-size: 18px; color: #388E3C;"><b>{tarefas_por_status.get('Concluída', 0)}</b> tarefas concluídas</p>
            </div>
            """, unsafe_allow_html=True)

    # Card com tarefas em andamento (Coluna 2)
    with col2:
        st.markdown(
            f"""
            <div style="border: 2px solid #FF9800; border-radius: 10px; padding: 15px; margin-bottom: 20px; background-color: #fff3e0; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);">
                <h3 style="color: #F57C00; font-size: 20px; font-weight: bold;">Tarefas em Andamento 🛠️</h3>
                <p style="font-size: 18px; color: #F57C00;"><b>{tarefas_por_status.get('Em andamento', 0)}</b> tarefas em andamento</p>
            </div>
            """, unsafe_allow_html=True)

    # Card com tarefas não iniciadas (Coluna 2)
    with col2:
        st.markdown(
            f"""
            <div style="border: 2px solid #f44336; border-radius: 10px; padding: 15px; margin-bottom: 20px; background-color: #ffebee; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);">
                <h3 style="color: #D32F2F; font-size: 20px; font-weight: bold;">Tarefas Não Iniciadas ⏳</h3>
                <p style="font-size: 18px; color: #D32F2F;"><b>{tarefas_por_status.get('Não iniciada', 0)}</b> tarefas não iniciadas</p>
            </div>
            """, unsafe_allow_html=True)

    # Gráfico de status das tarefas
    st.subheader("📊 Gráfico de Status das Tarefas")
    cores = ['#D32F2F', '#F57C00', '#388E3C']  # Vermelho, Laranja, Verde
    fig, ax = plt.subplots()
    tarefas_por_status.plot(kind="bar", color=cores, ax=ax)

    # Adicionando os números no topo de cada barra
    for p in ax.patches:
        ax.annotate(f'{p.get_height()}', 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    xytext=(0, 5), 
                    textcoords='offset points', 
                    ha='center', 
                    va='bottom', 
                    fontsize=12, color='black')

    ax.set_ylabel("Número de Tarefas")
    ax.set_xlabel("Status das Tarefas")
    ax.set_title("Distribuição das Tarefas por Status")
    st.pyplot(fig)

    # Exibir lista de tarefas com expander para mostrar detalhes
    st.subheader("✅ Detalhes das Tarefas")
    for tarefa in tarefas:
        if tarefa['status'] != 'Concluída':  # Filtrando tarefas concluídas
            with st.expander(f"{tarefa['titulo']} - Status: {tarefa['status']}"):
                with st.container():
                    # Exibir detalhes da tarefa
                    st.write(f"**Descrição:** {tarefa['descricao']}")
                    st.write(f"**Responsável:** {tarefa['destinatario']}")
                    st.write(f"**Data de Criação:** {tarefa['adicionada_em']}")
                    st.write(f"**Prazo (previsto):** {tarefa['prazo_exibicao']}")
                    st.write(f"**Histórico:**")
                    for evento in tarefa.get('historico', []):
                        st.write(f"- {evento}")

                    # Checkboxes para alternar entre os status
                    status_atual = tarefa['status']
                    if status_atual == "Não iniciada":
                        if st.checkbox(f"Marcar como Em andamento", key=f"checkbox_iniciada_{tarefa['_id']}"):
                            novo_status = "Em andamento"
                            alterar_status_mongodb(tarefa['_id'], novo_status, st.session_state['usuario'])
                            st.success(f"Tarefa '{tarefa['titulo']}' foi marcada como Em andamento.")
                    elif status_atual == "Em andamento":
                        if st.checkbox(f"Marcar como Concluída", key=f"checkbox_em_andamento_{tarefa['_id']}"):
                            novo_status = "Concluída"
                            alterar_status_mongodb(tarefa['_id'], novo_status, st.session_state['usuario'])
                            st.success(f"Tarefa '{tarefa['titulo']}' foi marcada como Concluída.")
                    elif status_atual == "Concluída":
                        if st.checkbox(f"Reiniciar tarefa", key=f"checkbox_concluida_{tarefa['_id']}"):
                            novo_status = "Não iniciada"
                            alterar_status_mongodb(tarefa['_id'], novo_status, st.session_state['usuario'])
                            st.success(f"Tarefa '{tarefa['titulo']}' foi marcada como Não iniciada.")



# Função principal
def main():
    if 'logado' not in st.session_state or not st.session_state['logado']:
        tela_login()
    else:
        st.sidebar.title("Menu")
        opcao = st.sidebar.selectbox("Selecione uma opção", ["Visão Geral", "Adicionar Tarefa", "Gerenciar Tarefas", "Gráficos de Progresso", "Sair"])
        
        if opcao == "Visão Geral":
            tela_overview()
        elif opcao == "Adicionar Tarefa":
            adicionar_tarefa()
        elif opcao == "Gerenciar Tarefas":
            gerenciar_tarefas()
        elif opcao == "Gráficos de Progresso":
            graficos_progresso()
        elif opcao == "Gráficos de Progresso":
            logout()

# Chama a função principal
if __name__ == "__main__":
    main()
