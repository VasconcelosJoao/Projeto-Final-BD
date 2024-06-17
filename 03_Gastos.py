import requests
import mysql.connector

# Conectando ao banco de dados
with mysql.connector.connect(
    database="TFBD",
    user="root",
    password="unbMySQL#21",
    host="localhost",
    port="3306"
) as conn:
    with conn.cursor() as cur:
        # Criando a tabela gastos se ela não existir
        cur.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_deputado INT,
                data DATE,
                valor FLOAT,
                tipoDespesa VARCHAR(255),
                codDocumento INT,
                partido VARCHAR(50),
                FOREIGN KEY (id_deputado) REFERENCES deputados(id),
                FOREIGN KEY (partido) REFERENCES partidos(sigla)
            )
        """)
        conn.commit()  # Confirmar a transação após a criação da tabela

        # Selecionando todos os IDs de deputados e seus partidos
        cur.execute("SELECT id, partido FROM deputados")
        deputados = cur.fetchall()
        # Para cada deputado
        for deputado in deputados:
            id_deputado = deputado[0]
            partido = deputado[1]  # Buscando o partido do deputado
            pagina = 1
            while True:
                # Fazendo a requisição para a API
                url = f'https://dadosabertos.camara.leg.br/api/v2/deputados/{id_deputado}/despesas'
                params = {'ano': '2023', 'pagina': pagina,
                          'itens': 100, 'ordenarPor': 'dataDocumento'}
                response = requests.get(url, params=params)
                data = response.json()
                # Se não houver mais dados, sair do loop
                if not data['dados']:
                    break

                # Para cada gasto do deputado
                for gasto in data['dados']:
                    cur.execute("""
                        INSERT INTO gastos (id_deputado, data, valor, tipoDespesa, codDocumento, partido) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (id_deputado, gasto['dataDocumento'], gasto['valorLiquido'], gasto['tipoDespesa'], gasto['codDocumento'], partido))
                    conn.commit()  # Confirmar a transação após cada inserção

                # Ir para a próxima página
                pagina += 1
        # Fechando o cursor e a conexão
        cur.close()
        conn.close()