import pytest
import os
import csv
from writer import add_root_product, get_root_product, _ensure_csv_exists, CSV_FILE
# Nota: Substitua 'your_module' pelo nome real do seu arquivo Python (ex: 'main')
# Você pode precisar copiar as funções auxiliares (_ensure_csv_exists, ROOT, CSV_FILE)
# para este arquivo de teste se elas não forem exportadas diretamente.

# inicio do teste

# --- Estratégia de Fixture com tmp_path ---
# O pytest fornece a fixture 'tmp_path' para lidar com arquivos temporários.

# 1. FIXTURE para Redefinir as Variáveis de Caminho e o Estado
@pytest.fixture(autouse=True)
def setup_csv_environment(tmp_path, monkeypatch):
    """
    Cria um ambiente limpo para cada teste:
    1. Redefine ROOT e CSV_FILE para um diretório temporário único.
    2. Garante que as funções usem o novo caminho.
    3. Limpa o ambiente após o teste (feito automaticamente por tmp_path).
    """
    # Define o novo caminho ROOT e CSV_FILE dentro do diretório temporário
    NEW_ROOT = tmp_path / "test_csv_data"
    NEW_CSV_FILE = NEW_ROOT / "DataBaseARQ.csv"
    
    # Faz o 'monkeypatch' para que as funções do módulo testado usem os novos caminhos
    # Isso assume que as variáveis ROOT e CSV_FILE são globais no seu módulo original
    monkeypatch.setattr('writer.ROOT', str(NEW_ROOT))
    monkeypatch.setattr('writer.CSV_FILE', str(NEW_CSV_FILE))
    
    # Garante que o diretório temporário exista e que o CSV seja criado
    os.makedirs(NEW_ROOT, exist_ok=True)
    
    # Chama a função auxiliar para garantir o arquivo CSV com cabeçalho
    # usando o novo caminho definido pelo monkeypatch.
    _ensure_csv_exists()

    # Retorna o caminho do CSV, caso algum teste precise acessá-lo diretamente
    return NEW_CSV_FILE

# 2. FIXTURE para Adicionar Dados Iniciais
@pytest.fixture
def initial_products(setup_csv_environment):
    """Adiciona os produtos iniciais necessários para os testes GET."""
    # Como setup_csv_environment garante que o CSV está limpo, podemos adicionar
    # os dados sem nos preocuparmos com duplicação (o add_root_product fará isso).
    
    add_root_product(id="001", nome="Apple", price=0.80, quantity="unit")
    add_root_product(id="025", nome="Orange", price=1.50, quantity="bag")
    add_root_product(id="026", nome="Grape", price=5.00, quantity="kilo")
    # Este produto é o alvo primário de muitos testes
    add_root_product(id="031", nome="Watermelon", price=10.00, quantity="unit")

# --------------------------------------------------------------------------
# ## Testes para add_root_product (Função de Adição)
# --------------------------------------------------------------------------

def test_add_novo_produto_com_sucesso(setup_csv_environment):
    """Verifica se um novo produto é adicionado corretamente e se está no CSV."""
    
    # Tenta adicionar o produto
    resposta = add_root_product(id="030", nome="Banana", price=1.20, quantity="15")
    assert "adicionado com sucesso" in resposta
    
    # Verifica se ele realmente existe no arquivo CSV
    # Reutilizamos get_root_product para verificar a adição
    produto_buscado = get_root_product(id="030")
    assert "ID: 030" in produto_buscado
    assert "Name: Banana" in produto_buscado

def test_add_produto_com_id_duplicado(initial_products):
    """Verifica se a adição falha ao tentar usar um ID que já existe ('031')."""
    # Tenta adicionar um produto com ID 031, mas nome diferente
    resposta = add_root_product(id="031", nome="Strawberry", price=2.50, quantity="box")
    assert "Erro: Produto com ID '031' já existente!" in resposta

def test_add_produto_com_nome_duplicado(initial_products):
    """Verifica se a adição falha ao tentar usar um Nome que já existe ('Apple')."""
    # Tenta adicionar um produto com Nome 'Apple', mas ID diferente
    resposta = add_root_product(id="050", nome="Apple", price=0.50, quantity="unit")
    assert "Erro: Produto com nome 'Apple' já existente!" in resposta

def test_add_tentativa_de_adicionar_duas_vezes(setup_csv_environment):
    """Verifica a sequência de sucesso e falha por duplicação."""
    add_root_product(id="100", nome="Pera", price=1.00, quantity="unit")
    resposta_duplicada = add_root_product(id="100", nome="Pera", price=1.00, quantity="unit")
    
    assert "Erro: Produto com ID '100' já existente!" in resposta_duplicada

# --------------------------------------------------------------------------
# ## Testes para get_root_product (Função de Busca)
# --------------------------------------------------------------------------

def test_get_busca_por_id_existente(initial_products):
    """Verifica a busca por ID ('031' - Watermelon)."""
    produto = get_root_product(id="031")
    assert "ID: 031 | Name: Watermelon | Price: 10.00 | Quantity: unit" in produto

def test_get_busca_por_nome_existente(initial_products):
    """Verifica a busca por Nome ('Apple')."""
    produto = get_root_product(name="Apple")
    assert "ID: 001 | Name: Apple | Price: 0.80 | Quantity: unit" in produto

def test_get_busca_por_preco_existente(initial_products):
    """Verifica a busca por Preço (5.00 - Grape)."""
    produto = get_root_product(price=5.00)
    assert "ID: 026 | Name: Grape | Price: 5.00 | Quantity: kilo" in produto

def test_get_busca_por_quantidade_comum_retorna_multiplos(initial_products):
    """Verifica a busca por Quantity ('unit'), que deve retornar Apple e Watermelon."""
    produto = get_root_product(quantity="unit")
    # Note que a função retorna os dois produtos que têm 'unit'
    assert "ID: 001 | Name: Apple" in produto
    assert "ID: 031 | Name: Watermelon" in produto
    # Verifica se há mais de uma linha de produto no retorno
    assert produto.count('\n') >= 2

def test_get_busca_sem_correspondencia(initial_products):
    """Verifica o comportamento ao buscar um produto inexistente (ID='999')."""
    produto = get_root_product(id="999")
    assert produto.strip() == "Produto não encontrado"

def test_get_busca_com_varios_criterios_or(initial_products):
    """Verifica a busca com múltiplos critérios (lógica OR)."""
    # Busca por ID='999' (não existe) OU Name='Orange' (existe)
    produto = get_root_product(id="999", name="Orange")
    assert "ID: 025 | Name: Orange" in produto
    assert "Produto não encontrado" not in produto

# --------------------------------------------------------------------------
# Fim dos testes