import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name("token.json", SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET = CLIENT.open("Acomp").sheet1  # Altere para o nome da sua planilha

# Fetch all values from the sheet
values = SHEET.get_all_values()

# Convert to DataFrame
df = pd.DataFrame(values[1:], columns=values[0])

CORRETORES = ["DOUGLAS", "CHRIS", "FABIO", "GABRIELA", "JOSUE", "MAYSA", "MICHELLE", "LEONARDO", "TAYNAH", "TIAGO", "WANDERSON", "WELLINGTON"]
STATUS = ["AGENDAMENTO", "REAGENDAMENTO", "VISITA", "PROPOSTA", "EM RESERVA", "VENDA", "FINALIZADOS"]
MOMENTOLEAD = ["REAGENDAMENTO", "SEM INTERAÇÃO", "ENVIO DE DOC", "EM PROCESSO", "DESISTENCIA", "PROPOSTA", "APROVADO", "CONDICIONADO", "REPROVADO", "COND PENDENTE", "RESTRIÇÃO CAD", "PENDENTE"]

def cadastrar_lead():
    st.title("Cadastro de Novo Lead")
    with st.form(key="Cadastro"):
        data_cad = st.date_input(label="Data")
        lead = st.text_input(label="Digite o nº do Lead")
        lead_name = st.text_input(label="Digite o nome do Cliente")
        corretor_sb = st.selectbox("Corretor",options=CORRETORES,index=None)
        status_sb = st.selectbox("Status",options=STATUS,index=1)
        momentolead_sb = st.selectbox("Momento do Lead",options=MOMENTOLEAD, index=None)
        obs = st.text_area(label="Observação")

        st.markdown("**required**")

        submit_button = st.form_submit_button(label="Cadastrar")

        if submit_button:
            if not lead or not lead_name:
                st.warning("Preencha todos os campos para cadastrar.")
                st.stop()
            else:
                # Check if lead already exists
                if lead in df['Lead'].values:
                    corretor = df.loc[df['Lead'] == lead, 'Corretor'].values[0]
                    st.warning(f"O lead {lead} já existe e está cadastrado com o corretor {corretor}")
                    st.write("Peça para o administrador mudar o lead para você fazer as atualizações")
                    st.stop()
                else:
                    data_cad_str = datetime.strftime(data_cad, "%d/%m/%Y")
                    # Add new lead
                    new_row = [data_cad_str, lead, lead_name, corretor_sb, status_sb, momentolead_sb, obs]
                    SHEET.append_row(new_row)
                    st.success(f"Lead {lead} cadastrado com sucesso!")


# EDITAR LEAD
def editar_lead():
    st.title("Edição de Lead")
    lead_id = st.text_input(label="Digite o número do Lead que deseja editar")

    # Recuperar o estado da sessão ou inicializá-lo
    session_state = st.session_state.get("lead_editing", {"searching": True, "lead_index": None})

    if st.button("Buscar") or session_state["searching"]:
        if lead_id:
            lead_index = df.index[df['Lead'] == lead_id].tolist()
            if lead_index:
                session_state["searching"] = False
                session_state["lead_index"] = lead_index[0]
            else:
                st.warning(f"Lead {lead_id} não encontrado na planilha.")
                return  # Retorna aqui para evitar a execução adicional da função

    if not session_state["searching"]:
        lead_index = session_state["lead_index"]
        if lead_index is not None and lead_index >= 0 and lead_index < len(df):
            # Buscar dados atualizados da planilha
            data_cad_str = df.at[lead_index, 'Data']
            try:
                data_cad = datetime.strptime(data_cad_str, "%d/%m/%Y")
            except ValueError:
                st.error("Formato de data inválido na planilha. Certifique-se de que a data esteja no formato DD/MM/AAAA.")
                st.stop()

            lead_name = df.at[lead_index, 'NomeCliente']
            corretor_sb = df.at[lead_index, 'Corretor']
            status_sb = df.at[lead_index, 'Status']
            momentolead_sb = df.at[lead_index, 'MomentoLead']
            obs = df.at[lead_index, 'Observação']

            st.markdown("**required**")

            with st.form(key="editar_lead_form"):
                # Exibe os campos de edição com os dados atualizados da planilha
                data_cad = st.date_input(label="Data", value=data_cad)
                lead_name = st.text_input(label="Nome do Cliente", value=lead_name)
                corretor_sb = st.selectbox("Corretor", options=CORRETORES, index=CORRETORES.index(corretor_sb) if corretor_sb in CORRETORES else 0)
                status_sb = st.selectbox("Status", options=STATUS, index=STATUS.index(status_sb) if status_sb in STATUS else 0)
                momentolead_sb = st.selectbox("Momento do Lead", options=MOMENTOLEAD, index=MOMENTOLEAD.index(momentolead_sb) if momentolead_sb in MOMENTOLEAD else 0)
                obs = st.text_area(label="Observação", value=obs)

                if st.form_submit_button(label="Salvar"):
                    # Update lead
                    SHEET.update_cell(lead_index + 1, 4, lead_name)
                    SHEET.update_cell(lead_index + 1, 5, corretor_sb)
                    SHEET.update_cell(lead_index + 1 6, status_sb)
                    SHEET.update_cell(lead_index + 1, 7, momentolead_sb)
                    SHEET.update_cell(lead_index + 1, 8, obs)
                    st.success(f"Lead {lead_id} atualizado com sucesso.")
                    # Limpar os campos do formulário após a atualização
                    session_state["searching"] = True
                    session_state["lead_index"] = None
                    st.rerun()
        else:
            st.warning("Índice de lead inválido.")
            return

    # Salva o estado da sessão
    st.session_state["lead_editing"] = session_state

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

