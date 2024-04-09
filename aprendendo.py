import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name("token.json", SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET = CLIENT.open("Acomp").sheet1  # Altere para o nome da sua planilha

CORRETORES = ["DOUGLAS", "CHRIS", "FABIO", "GABRIELA", "JOSUE", "MAYSA", "MICHELLE", "LEONARDO", "TAYNAH", "TIAGO", "WANDERSON", "WELLINGTON"]
STATUS = ["AGENDAMENTO", "REAGENDAMENTO", "VISITA", "PROPOSTA", "EM RESERVA", "VENDA", "FINALIZADOS"]
MOMENTOLEAD = ["REAGENDAMENTO", "SEM INTERAÇÃO", "ENVIO DE DOC", "EM PROCESSO", "DESISTENCIA", "PROPOSTA", "APROVADO", "CONDICIONADO", "REPROVADO", "COND PENDENTE", "RESTRIÇÃO CAD", "PENDENTE"]

def cadastrar_lead():
    st.title("Cadastro de Novo Lead")
    
    session_state = st.session_state.get("cadastro_lead", {"lead": "", "lead_name": "", "corretor_sb": CORRETORES[0], 
                                                           "status_sb": STATUS[1], "momentolead_sb": MOMENTOLEAD[0], 
                                                           "obs": ""})
    
    with st.form(key="Cadastro"):
        data_cad = st.date_input(label="Data")
        session_state["lead"] = st.text_input(label="Digite o nº do Lead", value=session_state["lead"])
        session_state["lead_name"] = st.text_input(label="Digite o nome do Cliente", value=session_state["lead_name"])
        session_state["corretor_sb"] = st.selectbox("Corretor", options=CORRETORES, index=CORRETORES.index(session_state["corretor_sb"]))
        session_state["status_sb"] = st.selectbox("Status", options=STATUS, index=STATUS.index(session_state["status_sb"]))
        session_state["momentolead_sb"] = st.selectbox("Momento do Lead", options=MOMENTOLEAD, index=MOMENTOLEAD.index(session_state["momentolead_sb"]))
        session_state["obs"] = st.text_area(label="Observação", value=session_state["obs"])

        st.markdown("**required**")

        submit_button = st.form_submit_button(label="Cadastrar")

        if submit_button:
            if not session_state["lead"] or not session_state["lead_name"]:
                st.warning("Preencha todos os campos para cadastrar.")
                st.stop()
            else:
                data_cad_str = datetime.strftime(data_cad, "%d/%m/%Y")
                # Adicionar novo lead
                new_row = [data_cad_str, session_state["lead"], session_state["lead_name"], session_state["corretor_sb"], 
                           session_state["status_sb"], session_state["momentolead_sb"], session_state["obs"]]
                SHEET.append_row(new_row)
                st.success(f"Lead {session_state['lead']} cadastrado com sucesso!")
                # Limpar os campos do formulário de cadastro após a inclusão
                session_state["lead"] = ""
                session_state["lead_name"] = ""
                session_state["corretor_sb"] = CORRETORES[0]
                session_state["status_sb"] = STATUS[1]
                session_state["momentolead_sb"] = MOMENTOLEAD[0]
                session_state["obs"] = ""

def editar_lead():
    st.title("Edição de Lead")
    lead_id = st.text_input(label="Digite o número do Lead que deseja editar")

    session_state_edit = st.session_state.get("editar_lead", {"searching": True, "lead_index": None})

    if st.button("Buscar") or session_state_edit["searching"]:
        if lead_id:
            lead_index = df.index[df['Lead'] == lead_id].tolist()
            if lead_index:
                session_state_edit["searching"] = False
                session_state_edit["lead_index"] = lead_index[0]
            else:
                st.warning(f"Lead {lead_id} não encontrado na planilha.")
                return
    # Restante do código...

def filtrar_lead():
    st.title("Filtragem de Leads")
    corretor_filtro = st.selectbox("Filtrar por Corretor", options=["Todos"] + CORRETORES)
    status_filtro = st.selectbox("Filtrar por Status", options=["Todos"] + STATUS)
    if st.button("Aplicar Filtro"):
        filtered_df = df.copy()
        if corretor_filtro != "Todos":
            filtered_df = filtered_df[filtered_df['Corretor'] == corretor_filtro]
        if status_filtro != "Todos":
            filtered_df = filtered_df[filtered_df['Status'] == status_filtro]

        st.write(filtered_df)

def visualizar_lead():
    st.title("Visualização de Leads")
    st.write(df)

def main():
    st.sidebar.title("Menu")
    menu_selection = st.sidebar.radio("Selecione uma opção", ["Cadastrar Novo Lead", "Editar Lead", "Filtrar Lead", "Visualizar Lead"])

    if menu_selection == "Cadastrar Novo Lead":
        cadastrar_lead()
    elif menu_selection == "Editar Lead":
        editar_lead()
    elif menu_selection == "Filtrar Lead":
        filtrar_lead()
    elif menu_selection == "Visualizar Lead":
        visualizar_lead()

if __name__ == "__main__":
    main()
