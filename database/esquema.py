"""
Definição do esquema do banco de dados.

Este módulo contém a definição do esquema do banco de dados utilizado pelo SQL Agent.
"""

# Esquema do banco de dados para o contexto do modelo
ESQUEMA_BD = """
CREATE TABLE clientes (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  saldo DECIMAL(10, 2) NOT NULL
);

CREATE TABLE produtos (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  preco DECIMAL(10, 2) NOT NULL,
  categoria VARCHAR(255) NOT NULL
);

CREATE TABLE transacoes (
  id SERIAL PRIMARY KEY,
  cliente_id INTEGER REFERENCES clientes(id),
  produto_id INTEGER REFERENCES produtos(id),
  data_compra TIMESTAMP NOT NULL,
  quantidade INTEGER NOT NULL,
  valor_total DECIMAL(10, 2) NOT NULL
);
"""

# SQL para criar as tabelas no banco de dados
SQL_CRIAR_TABELAS = [
    """
    CREATE TABLE IF NOT EXISTS clientes (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        saldo DECIMAL(10, 2) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS produtos (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(255) NOT NULL,
        preco DECIMAL(10, 2) NOT NULL,
        categoria VARCHAR(255) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS transacoes (
        id SERIAL PRIMARY KEY,
        cliente_id INTEGER REFERENCES clientes(id),
        produto_id INTEGER REFERENCES produtos(id),
        data_compra TIMESTAMP NOT NULL,
        quantidade INTEGER NOT NULL,
        valor_total DECIMAL(10, 2) NOT NULL
    )
    """
]

# SQL para inserir dados de exemplo
SQL_INSERIR_CLIENTES = """
INSERT INTO clientes (nome, email, saldo)
VALUES 
    ('Ana Silva', 'ana.silva@email.com', 5000.00),
    ('Bruno Costa', 'bruno.costa@email.com', 3500.00),
    ('Carla Oliveira', 'carla.oliveira@email.com', 2000.00),
    ('Daniel Santos', 'daniel.santos@email.com', 7500.00),
    ('Elena Martins', 'elena.martins@email.com', 1200.00)
ON CONFLICT (email) DO NOTHING
"""

SQL_INSERIR_PRODUTOS = """
INSERT INTO produtos (nome, preco, categoria)
VALUES 
    ('Notebook Dell XPS', 4999.99, 'Eletrônicos'),
    ('Smartphone Samsung Galaxy', 2499.99, 'Eletrônicos'),
    ('Monitor LG 27"', 1299.99, 'Eletrônicos'),
    ('Teclado Mecânico', 349.99, 'Periféricos'),
    ('Mouse Gamer', 199.99, 'Periféricos'),
    ('Headset Wireless', 599.99, 'Áudio'),
    ('Tablet iPad', 3499.99, 'Eletrônicos'),
    ('Notebook Lenovo ThinkPad', 5499.99, 'Eletrônicos'),
    ('Smartphone iPhone', 4999.99, 'Eletrônicos')
"""

SQL_INSERIR_TRANSACOES = """
INSERT INTO transacoes (cliente_id, produto_id, data_compra, quantidade, valor_total)
VALUES 
    (1, 1, '2023-10-15 10:30:00', 1, 4999.99),
    (1, 4, '2023-10-16 14:20:00', 1, 349.99),
    (2, 2, '2023-10-10 09:15:00', 1, 2499.99),
    (3, 5, '2023-10-12 16:45:00', 2, 399.98),
    (4, 1, '2023-10-05 11:30:00', 1, 4999.99),
    (4, 3, '2023-10-05 11:35:00', 2, 2599.98),
    (4, 6, '2023-10-06 15:20:00', 1, 599.99),
    (5, 5, '2023-10-18 13:10:00', 1, 199.99),
    (2, 8, '2023-10-20 10:00:00', 1, 5499.99),
    (3, 7, '2023-10-22 14:30:00', 1, 3499.99)
"""