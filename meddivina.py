import streamlit as st
import pyodbc
import time
import math
import pandas as pd
import pyodbc    
import datetime
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

menu = st.sidebar.selectbox(
    "O que você precisa fazer?",
    ("Bem-vindo", "Resumo", "Validades", "Estoque", "Faltas")
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

# *LOGIN
elif menu == "Resumo":
    logar, cadastrar = st.tabs(["Login", "Cadastro"])
    with logar:
        st.subheader("Quem está aí?")
        email_logar = st.text_input("Insira seu email para fazer login")
        login_btn = st.button("Entrar", type="primary")

        st.divider()

        if login_btn:
            try:
                conn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};Server=medddatabase.c5slvt4ub1v5.us-east-2.rds.amazonaws.com;Database=medD;UID=meddadmin;PWD=vinivods045031;")
                cursor = conn.cursor()

                try:
                    cursor.execute('SELECT Nome, Sobrenome FROM Cadastro WHERE Email = ?', email_logar)
                    se_cadastro_existe = cursor.fetchone()

                    if se_cadastro_existe:
                        nome_entrar = se_cadastro_existe[0]
                        sobrenome_entrar = se_cadastro_existe[1]

                        st.markdown(f"Olá, {nome_entrar} {sobrenome_entrar}!")

                        try:
                            #consulta resumo validades
                            cursor.execute(f'SELECT COUNT(v.Medicamento) AS Qtt, c.Farmacia FROM Validades v JOIN Cadastro c ON v.Email = c.Email WHERE v.Data_vencimento <= DATEADD(DAY, 30, GETDATE()) AND v.Email = ? GROUP BY c.Farmacia', email_logar)
                            resultado_validade_cadastro = cursor.fetchone()

                            if resultado_validade_cadastro is not None:
                                quantidade_vencendo = resultado_validade_cadastro[0]
                                farmacia_vencendo = resultado_validade_cadastro[1]

                                st.info(f":warning: **Atenção:** Você tem **{quantidade_vencendo}** medicamentos vencendo em até **30 dias** na farmácia {farmacia_vencendo}.")
                            else:
                                st.info(f":thumbsup: Tudo tranquilo por aqui. Você **não** tem medicamentos vencendo em até **30 dias**.")

                            st.divider()

                            #consulta resumo faltas
                            cursor.execute('SELECT cf.Medicamento, COUNT(cf.Medicamento) AS QttFaltas, cf.Tasy FROM ControleFaltas cf LEFT JOIN Cadastro c ON cf.Farmacia = c.Farmacia WHERE cf.Data_falta <= DATEADD(DAY, 30, GETDATE()) AND c.Email = ? GROUP BY cf.Medicamento, cf.Tasy, c.Farmacia', email_logar)
                            resultado_resumo_faltas = cursor.fetchall()

                            if resultado_resumo_faltas:
                                st.info("Há faltas adicionadas nos últimos **30 dias** para os seguintes medicamentos:")
                                for medicamento, qtd_faltas, tasy_controle in resultado_resumo_faltas:
                                    st.info(f"- **{qtd_faltas}** faltas de **{medicamento}({tasy_controle})**")
                            
                            else:
                                st.info("Você não teve faltas adicionadas nos últimos 30 dias.")

                        except Exception as e:
                            print(f"Erro: {e}")
                    
                    else:
                        st.write("Acho que não te conheço. Que tal criar seu cadastro rapidinho?")
                
                except Exception as e:
                    print(f"Erro: {e}")

            except pyodbc.Error as e:
                print(f"Erro na conexão: {e}")
                st.toast("Sem conexão. Entre em contato.")
    
    with cadastrar:
        with st.container():
            st.subheader("Me conte sobre você")
            nome_cadastro = st.text_input("Qual é o seu nome?")
            sobrenome_cadastro = st.text_input("Qual é seu sobrenome?")
            email_cadastro = st.text_input("E o seu email?")
            farmacia_cadastro = st.radio("Qual é a sua farmácia?", ["Emergência", "Central", "CAF", "Endovascular", "Centro Obstétrico", "Bloco Cirúrgico"], index=None)
            enviar_cadastro = st.button("Fazer cadastro", type="primary")

            if enviar_cadastro:
                if nome_cadastro == '' or sobrenome_cadastro == '' or email_cadastro == '' or farmacia_cadastro == '':
                    st.error("Por favor, preencha todas as informações")
                else:
                    try:
                        conn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};Server=medddatabase.c5slvt4ub1v5.us-east-2.rds.amazonaws.com;Database=medD;UID=meddadmin;PWD=vinivods045031;")
                        cursor = conn.cursor()

                        try:
                            cursor.execute('INSERT INTO Cadastro (Nome, Sobrenome, Email, Farmacia) VALUES (?, ?, ?, ?)', nome_cadastro, sobrenome_cadastro, email_cadastro, farmacia_cadastro)

                            time.sleep(.1)
                            st.toast("Salvando informações...")
                            time.sleep(1)
                            st.toast("Cadastro criado com sucesso!")

                            conn.commit()
                        
                        except Exception as e:
                            print(f"Erro: {e}")
                            time.sleep(.1)
                            st.toast("Salvando informações...")
                            time.sleep(1)
                            st.toast("Não foi possível fazer o cadastro.")

                        finally:
                            cursor.close()
                            conn.close()
                    
                    except pyodbc.Error as e:
                        print(f"Erro na conexão: {e}")
                        st.toast("Sem conexão. Entre em contato.")

# *VALIDADES
elif menu == "Validades":
    with st.container():
        st.title("Adicionar validades")
        email = st.text_input("Insira seu email")

        st.subheader("Dados do medicamento")
        tasy = st.number_input("Insira o Tasy", value=0)
        medicamento = st.text_input("Insira o nome do medicamento")
        lote = st.text_input("Insira o lote do medicamento")
        quantidade_validade = st.number_input("Insira a quantidade para este lote", value=0)

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
                    cursor.execute("INSERT INTO Validades (Tasy, Medicamento, Lote, Quantidade, Data_vencimento, Email) VALUES (?, ?, ?, ?, ?, ?)", tasy, medicamento, lote, quantidade_validade, data_vencimento, email)

                    time.sleep(.1)
                    st.toast("Adicionando...")
                    time.sleep(1)
                    st.toast("Adicionado com sucesso!")

                    conn.commit()

                except Exception as e:
                    print(f"Erro: {e}")
                    time.sleep(.1)
                    st.toast("Adicionando...")
                    time.sleep(1)
                    st.toast("Validade já adicionada para este email.")

                finally:
                    cursor.close()
                    conn.close()

            except pyodbc.Error as e:
                print(f"Erro na conexão: {e}")
                st.toast("Sem conexão. Entre em contato.")

        botao_adicionar = st.button("Adicionar", type="primary")
        if botao_adicionar:
            if email == '' or tasy == '' or medicamento == '' or lote == '' or data_vencimento == '' or tasy == 0 or quantidade_validade == 0:
                st.error("Por favor, preencha todas as informações")
            else:
                add()

    st.divider()

# *RETORNAR VALIDADES
    with st.container():
        st.title("Retornar validades")
        # st.subheader("Insira seu email para pesquisar")
        email_validade_pesquisar = st.text_input("Insira seu email para pesquisar suas validades")
        intervalo_validades_pesquisar = st.number_input("Insira o intervalo de dias", value=30)

        botao_pesquisar = st.button("Pesquisar", type="primary")

        if botao_pesquisar:
            user = 'meddadmin'
            password = 'vinivods045031'
            host = 'medddatabase.c5slvt4ub1v5.us-east-2.rds.amazonaws.com'
            database = 'medD'

            conn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};Server=medddatabase.c5slvt4ub1v5.us-east-2.rds.amazonaws.com;Database=medD;UID=meddadmin;PWD=vinivods045031;")
            
            cursor = conn.cursor()

            result_proxy = cursor.execute(f"SELECT Tasy, Medicamento, Lote, CONVERT(varchar, Data_vencimento, 103) AS DataFormatada, Quantidade FROM Validades WHERE Email = ? AND Data_vencimento <= DATEADD(DAY, {intervalo_validades_pesquisar}, GETDATE()) ORDER BY Data_vencimento ASC", email_validade_pesquisar)

            resultados = []

            while True:
                resultado = result_proxy.fetchone()
                if resultado is None:
                    break
                resultados.append(resultado)     

            if resultados:
                num_colunas = len(resultados[0])
                resultados = [list(row) for row in resultados]

                df_validades = pd.DataFrame(resultados, columns=['Tasy', 'Medicamento', 'Lote', 'Data de vencimento', 'Quantidade'])

                df_validades['Tasy'] = df_validades['Tasy'].astype(str)

                st.dataframe(df_validades, use_container_width=True)

                def create_pdf(df):
                    # Criação de um arquivo PDF
                    buffer = BytesIO()
                    pdf_canvas = canvas.Canvas(buffer, pagesize=letter)

                    today_str = hoje.strftime("%d/%m/%Y")
                    gerado_em_msg = f"Gerado em {today_str}"
                    pdf_canvas.setFont("Helvetica", 10)
                    pdf_canvas.drawString(50, 780, gerado_em_msg)
                    
                    # Adicionando título
                    pdf_canvas.setFont("Helvetica-Bold", 14)
                    pdf_canvas.drawCentredString(300, 750, "Resumo de Medicamentos")
                    pdf_canvas.setFont("Helvetica", 12)
                    pdf_canvas.drawCentredString(300, 730, f"Medicamentos que vão vencer em até {intervalo_validades_pesquisar} dias")

                    # Reorganizando as colunas no DataFrame
                    df = df[['Medicamento', 'Tasy', 'Data_vencimento', 'Lote', 'Quantidade']]

                    medicamento_width = max(pdf_canvas.stringWidth(str(cell), "Helvetica", 10) for cell in df['Medicamento'])

                    # Adicionando a tabela
                    data = [df.columns.values.astype(str).tolist()] + df.values.tolist()
                    pdf_canvas.setFont("Helvetica", 10)

                    # Ajustando a largura de cada coluna
                    col_widths = [medicamento_width] + [max(pdf_canvas.stringWidth(str(cell), "Helvetica", 10), 50) for cell in data[0][1:]]

                    row_height = 15
                    for i, row in enumerate(data):
                        y = 700 - i * row_height
                        x = (pdf_canvas._pagesize[0] - sum(col_widths) - 10 * (len(col_widths) - 1)) / 2
                        for j, text in enumerate(row):
                            cell_width = col_widths[j] + 10
                            if df.columns[j] == 'Medicamento' and df.columns[j + 1] == 'Data_vencimento':
                                # Adiciona um espaçamento extra entre 'Medicamento' e 'Data_vencimento'
                                cell_width += 20
                            pdf_canvas.drawString(x, y, str(text)[:50])  # Limita o texto a 50 caracteres por célula
                            x += cell_width
                        
                        # Adicionando divider centralizado com cor personalizada
                        divider_color = (0, 0, 0)  # Cor azul para o divider (R, G, B)
                        divider_width_percentage = 80  # Largura percentual do divider

                        pdf_canvas.setLineWidth(1)  # Largura da linha do divider em pontos
                        pdf_canvas.setStrokeColorRGB(*divider_color)
                        
                        divider_width = pdf_canvas._pagesize[0] * (divider_width_percentage / 100)
                        divider_x_start = (pdf_canvas._pagesize[0] - divider_width) / 2
                        divider_x_end = divider_x_start + divider_width
                        divider_y = y - 4  # Posição vertical da linha de divisão

                        pdf_canvas.line(divider_x_start, divider_y, divider_x_end, divider_y)
                        # pdf_canvas.line(0, y - 5, x + sum(col_widths), y - 5)
                    
                    # Salvando o PDF
                    pdf_canvas.save()
                    buffer.seek(0)
                    return buffer.read()
                
                hoje = datetime.date.today()
                today = pd.to_datetime(hoje)
                tres_meses = today + datetime.timedelta(days=intervalo_validades_pesquisar)

                query = f"SELECT Medicamento, CONVERT(varchar, Data_vencimento, 103) AS Data_vencimento, Email, Lote, Tasy, Quantidade FROM Validades WHERE Data_vencimento <= DATEADD(DAY, {intervalo_validades_pesquisar}, GETDATE()) ORDER BY Data_vencimento ASC"
                print(query)
                df = pd.read_sql_query(query, conn)

                create_pdf(df)

                st.download_button("Baixar PDF", data=create_pdf(df), file_name="resumo_medicamentos.pdf", key="download_pdf")

            else:
                st.error("Nenhuma informação para este email.")

            cursor.close()
            conn.close()
        
    st.divider()

# *EXCLUIR VALIDADES
    with st.container():
        st.title("Excluir validade adicionada")
        # st.subheader("Exclua uma validade")

        email_excluir = st.text_input("Informe seu email")

        lote_excluir = st.text_input("Informe o lote do medicamento que você quer excluir")
        botao_excluir = st.button("Excluir", type="primary")

        if botao_excluir:
            conn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};Server=medddatabase.c5slvt4ub1v5.us-east-2.rds.amazonaws.com;Database=medD;UID=meddadmin;PWD=vinivods045031;")
            
            cursor = conn.cursor()

            if lote_excluir == '' or email_excluir == '':
                st.error("Por favor, preencha todas as informações")
            else:
                try:
                    time.sleep(.1)
                    st.toast("Excluindo...")

                    cursor.execute("DELETE FROM Validades WHERE Lote = ? AND Email = ?", lote_excluir, email_excluir)
                    cursor.commit()

                    time.sleep(1)
                    st.toast("Validade excluída!")
                
                except Exception as e:
                    st.toast("Não foi possível excluir esta validade.")

                finally:
                    cursor.close()
                    conn.close()
# *ESTOQUE
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

# *FALTAS
else:
    st.title("Faltas")
    st.subheader("Controle as faltas com o registro de cada ocorrência")

    with st.container():
        tasy_falta = st.number_input("Insira o Tasy do medicamento que faltou", value=1)
        medicamento_falta = st.text_input("Insira o nome do medicamento que faltou")
        quantidade_falta = st.number_input("Insira a quantidade que faltou", value=1)
        data_falta = st.date_input("Insira o dia que este medicamento faltou", format="DD/MM/YYYY")
        farmacia_falta = st.selectbox("Informe em qual farmácia este medicamento faltou", options=['','Emergência','Central', 'CAF', 'Endovascular', 'Centro Obstétrico', 'Bloco Cirúrgico'])



        adicionar_falta = st.button("Adicionar", type="primary")
        if adicionar_falta:
            if tasy_falta == '' or medicamento_falta == '' or quantidade_falta == '' or data_falta == '' or farmacia_falta == '' or quantidade_falta == 0:
                st.error("Por favor, preencha todas as informações")
            else:
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

                        time.sleep(.1)
                        st.toast("Adicionando...")
                        time.sleep(1)
                        st.toast("Falta adicionada com sucesso!")

                        conn.commit()

                    except Exception as e:
                        st.toast("Não foi possível adicionar esta falta. Entre em contato.")

                    finally:
                        cursor.close()
                        conn.close()

                except pyodbc.Error as e:
                    st.toast("Sem conexão. Entre em contato.")
        
    st.divider()

    st.subheader("Pesquise as faltas adicionadas nos últimos dias")

# *PESQUISAR FALTAS
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
