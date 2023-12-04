import streamlit as st
import pyodbc
import time
import math

menu = st.sidebar.selectbox(
    "O que você precisa fazer?",
    ("Bem-vindo", "Validades", "Estoque", "Faltas")
)

if menu == "Bem-vindo":
    with st.container():
        st.markdown("<h1 style='text-align: center; font-family: Repo'>Seja muito bem-vindo(a) à med<span style='color: green'>D</span></h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-bottom: 3%; font-family:Repo'>Descubra o melhor jeito de administrar suas validades, encontrar seu estoque ideal e controlar suas faltas de medicamentos.</h3>", unsafe_allow_html=True)

        st.markdown("<h4 style='text-align: center; font-family: Repo'>Validades</h4>", unsafe_allow_html=True)
        st.markdown("<h5 style='text-align: center; margin: 0 0 2% 0'; font-family: Repo>Cadastre as validades dos medicamentos que você quer acompanhar. <br>Quando um medicamento for vencer, você receberá um lembrete em seu email.</h5>", unsafe_allow_html=True)

        st.markdown("<h4 style='text-align: center; font-family: Repo'>Estoque</h4>", unsafe_allow_html=True)
        st.markdown("<h5 style='text-align: center; margin: 0 0 2% 0; font-family: Repo'>Informe a quantidade de dispensações de um medicamento nos últimos três meses e descubra o estoque padrão ideal para sua farmácia.</h5>", unsafe_allow_html=True)

        st.markdown("<h4 style='text-align: center; font-family: Repo'>Faltas</h4>", unsafe_allow_html=True)
        st.markdown("<h5 style='text-align: center; margin: 0 0 2% 0; font-family: Repo'>Adicione diariamente as faltas de medicamento e receba alertas sobre faltas em excesso.</h5>", unsafe_allow_html=True)


elif menu == "Validades":
    st.title("Adicionar validades")
    email = st.text_input("Insira seu email")
    st.caption("Você receberá lembretes neste :green[email].")

    st.subheader("Dados do medicamento")
    tasy = st.number_input("Insira o Tasy", value=0)
    medicamento = st.text_input("Insira o nome do medicamento")
    lote = st.text_input("Insira o lote do medicamento")

    st.subheader("Data de vencimento")
    
    data_vencimento = st.date_input("Insira a data de vencimento", format="DD/MM/YYYY")

    def add():

        # Estabeleça a conexão
        try:
            # Substitua com suas próprias credenciais e informações do banco de dados
            server = 'medddatabase.c5slvt4ub1v5.us-east-2.rds.amazonaws.com'
            database = 'medD'
            username = 'meddadmin'
            password = 'vinivods045031'
            driver = '{ODBC Driver 17 for SQL Server}'  # Ou o driver que você está usando

            # Crie a string de conexão
            connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

            # Conecte ao banco de dados
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()

            # # Execute a consulta
            try:
                cursor.execute("INSERT INTO Validades (Lote, Tasy, Medicamento, Data_vencimento, Email) VALUES (?, ?, ?, ?, ?)", lote, tasy, medicamento, data_vencimento, email)

                time.sleep(.5)
                st.toast("Adicionado com sucesso!")

                conn.commit()
                print("Tudo certo.")

            except Exception as e:
                print(f"Erro: {e}")

            finally:
                cursor.close()
                conn.close()

        except pyodbc.Error as e:
            print(f"Erro na conexão: {e}")

    st.button("Adicionar", type="primary", on_click=add)

    # DESCOBRIR VALIDADES ADICIONADAS
    st.divider()

    with st.container():
        st.title("Retornar validades")
        st.subheader("Insira o lote para pesquisar a validade")
        lote_pesquisar = st.text_input("Lote")

        botao_pesquisar = st.button("Pesquisar", type="primary")

        if botao_pesquisar:
            user = 'meddadmin'
            password = 'vinivods045031'
            host = 'medddatabase.c5slvt4ub1v5.us-east-2.rds.amazonaws.com'
            database = 'medD'

            conn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};Server=medddatabase.c5slvt4ub1v5.us-east-2.rds.amazonaws.com;Database=medD;UID=meddadmin;PWD=vinivods045031;")
            
            cursor = conn.cursor()

            result_proxy = cursor.execute("SELECT Lote, Tasy, Medicamento, CONVERT(varchar, Data_vencimento, 103) AS DataFormatada FROM Validades WHERE Lote = ?", lote_pesquisar)

            resultado = result_proxy.fetchone()

            if resultado:
                lote_retorno = resultado[0]
                tasy_retorno = resultado[1]
                medicamento_retorno = resultado[2]
                data_retorno = resultado[3]

                st.subheader(f"{medicamento_retorno} - {tasy_retorno}, lote {lote_retorno}, irá vencer no dia {data_retorno}.")

            else:
                st.write("Nenhuma informação para este lote.")

            cursor.close()
            conn.close()
        
    st.divider()

    with st.container():
        st.title("Excluir validade adicionada")
        st.subheader("Exclua uma validade")

        lote_excluir = st.text_input("Informe o lote do medicamento que você quer excluir")
        botao_excluir = st.button("Excluir", type="primary")

        if botao_excluir:
            conn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};Server=medddatabase.c5slvt4ub1v5.us-east-2.rds.amazonaws.com;Database=medD;UID=meddadmin;PWD=vinivods045031;")
            
            cursor = conn.cursor()

            # cursor.execute("DELETE FROM Validades WHERE Lote = ?", lote_excluir)
            cursor.execute("DELETE FROM Validades WHERE Lote = ?", lote_excluir)
            cursor.commit()

            time.sleep(.5)
            st.toast("Validade excluída!")

            cursor.close()
            conn.close()

elif menu == "Estoque":
    st.title("Estoque")
    st.subheader("Adicione a quantidade de saídas dos últimos três meses e descubra seu estoque padrão ideal")
    with st.container():
        antepe = st.number_input("Antepenúltimo mês", value=1)
        penul = st.number_input("Penúltimo mês", value=1)
        ultimo = st.number_input("Último mês", value=1)

        # Cálculo variação
        penul_antepe = round((int(penul) - int(antepe)) / int(antepe) * 100)
        ulti_penul = round((int(ultimo) - int(penul)) / int(penul) * 100)
        media_mes = round((int(antepe) + int(penul) + int(ultimo)) / 3)
        calculo_variacao = int(ulti_penul) + int(penul_antepe)

        # Média por dia dos últimos meses
        dias_antepe = int(antepe) / 30
        dias_penul = int(penul) / 30
        dias_ulti = int(ultimo) / 30
 
        media_todos_meses = (float(dias_antepe) + float(dias_penul) + float(dias_ulti)) / 3
        ideal_um_dia = math.ceil(media_todos_meses)
        ideal_tres_dias = ideal_um_dia * 3
        mais_20_porcento = (ideal_um_dia * 30) * 0.2
        ideal_um_mes = int(ideal_um_dia * 30) + int(mais_20_porcento)

        st.divider()

        st.write(f"O estoque padrão ideal para um dia é: **{ideal_um_dia}**")
        st.write(f"O estoque padrão ideal para três dias é: **{ideal_tres_dias}**")
        st.write(f"O estoque padrão ideal para um mês é: **{ideal_um_mes}***")
        st.caption("*Cálculo padrão ideal + 20%")

        ante_mes, penul_mes, ult_mes = st.columns(3)

        dias_antepe_round = round(dias_antepe)
        dias_penul_round = round(dias_penul)
        dias_ulti_round = round(dias_ulti)

        with ante_mes:
            st.metric(label="Média diária do antepenúltimo mês", value=f"{dias_antepe_round}")
        with penul_mes:
            st.metric(label="Média diária do penúltimo mês", value=f"{dias_penul_round}", delta=f"{penul_antepe}%")
        with ult_mes:
            st.metric(label="Média diária do último mês", value=f"{dias_ulti_round}", delta=f"{ulti_penul}%")

        st.metric(label="Média dos últimos três meses", value=f"{media_mes}", delta=f"{calculo_variacao}%")

        if calculo_variacao >= 100:
            st.write(f":warning: A quantidade de saídas aumentou em :green[{calculo_variacao}%] nos últimos meses. Talvez o estoque precise ser ainda maior do que o recomendado.")
        elif calculo_variacao <= -50:
            st.markdown(f":warning: A quantidade de saídas diminuiu em :red[{calculo_variacao}%] nos últimos meses. Talvez o estoque precise ser ainda menor do que o recomendado.")
        else:
            pass

else:
    st.title("Faltas")
    st.subheader("Controle as faltas com o registro de cada ocorrência.")

    with st.container():
        tasy_falta = st.number_input("Insira o Tasy do medicamento que faltou", value=1)
        medicamento_falta = st.text_input("Insira o nome do medicamento")
        quantidade_falta = st.number_input("Insira a quantidade que faltou", value=1)
        data_falta = st.date_input("Insira o dia que este medicamento faltou", format="DD/MM/YYYY")
        farmacia_falta = st.selectbox("Informe em qual farmácia este medicamento faltou", options=['Emergência','Central', 'Endovascular', 'Centro Obstétrico', 'Bloco Cirúrgico'])

        adicionar_falta = st.button("Adicionar", type="primary")
        if adicionar_falta:
            # Estabeleça a conexão
            try:
                # Substitua com suas próprias credenciais e informações do banco de dados
                server = 'medddatabase.c5slvt4ub1v5.us-east-2.rds.amazonaws.com'
                database = 'medD'
                username = 'meddadmin'
                password = 'vinivods045031'
                driver = '{ODBC Driver 17 for SQL Server}'  # Ou o driver que você está usando

                # Crie a string de conexão
                connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

                # Conecte ao banco de dados
                conn = pyodbc.connect(connection_string)
                cursor = conn.cursor()

                # # Execute a consulta
                try:
                    cursor.execute("INSERT INTO ControleFaltas (Tasy, Medicamento, Quantidade, Farmacia, Data_falta) VALUES (?, ?, ?, ?, ?)", tasy_falta, medicamento_falta, quantidade_falta, farmacia_falta, data_falta)

                    time.sleep(.5)
                    st.toast("Falta adicionada com sucesso!")

                    conn.commit()
                    print("Tudo certo.")

                except Exception as e:
                    print(f"Erro: {e}")

                finally:
                    cursor.close()
                    conn.close()

            except pyodbc.Error as e:
                print(f"Erro na conexão: {e}")
        
    st.divider()

    st.subheader("Pesquise as faltas adicionadas nos últimos dias")

    with st.container():
        tasy_falta_pesquisar = st.number_input("Insira o Tasy do medicamento", value=1)
        farmacia_falta_pesquisar = st.selectbox("Farmácia você quer pesquisar", options=['Emergência','Central', 'Endovascular', 'Centro Obstétrico', 'Bloco Cirúrgico'])
        intervalo = st.number_input("Intervalo de dias", value=30)


        pesquisar_falta = st.button("Pesquisar", type="primary")
        if pesquisar_falta:
            conn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};Server=medddatabase.c5slvt4ub1v5.us-east-2.rds.amazonaws.com;Database=medD;UID=meddadmin;PWD=vinivods045031;")
            cursor = conn.cursor()

            cursor.execute(f"SELECT Medicamento, SUM(Quantidade) AS Quantidade, COUNT(Medicamento) AS FaltasMed FROM ControleFaltas WHERE Tasy = ? AND Farmacia = ? AND Data_falta >= DATEADD(DAY, -{intervalo}, GETDATE()) GROUP BY Medicamento", tasy_falta_pesquisar, farmacia_falta_pesquisar)
            resultado_falta = cursor.fetchone()

            if resultado_falta:
                medicamento_falta_retorno = resultado_falta[0]
                quantidade_falta_retorno = resultado_falta[1]
                vezes_falta = resultado_falta[2]

                st.markdown(f"Nos últimos **{intervalo}** dias, houve **{vezes_falta}** faltas de **{medicamento_falta_retorno}** na **farmácia {farmacia_falta_pesquisar}**, com a quantidade total de **{quantidade_falta_retorno}** unidades ausentes.")

                if vezes_falta >= 3:
                    st.markdown(f":warning: Este medicamento teve três ou mais faltas na **farmácia {farmacia_falta_pesquisar}**, o ideal é checar o estoque físico e virtual e ajustar o estoque padrão.")

            else:
                st.write(f"Não há faltas adicionadas para este Tasy na **farmácia {farmacia_falta_pesquisar}**.")
