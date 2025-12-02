import csv
import os

# Define a pasta raiz.
# É uma boa prática verificar se a pasta existe.
ROOT = "processamento_dados_CSV"
CSV_FILE = os.path.join(ROOT, "DataBaseARQ.csv")

# Certifica-se de que o diretório exista
os.makedirs(ROOT, exist_ok=True)

# Função auxiliar para criar o arquivo CSV se não existir, com cabeçalho
def _ensure_csv_exists():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["id", "name", "price", "quantity"])

_ensure_csv_exists()

def get_root_product(
    id: str | None = None,
    name: str | None = None,
    price: float | None = None,
    quantity: str | None = None
) -> str:
    """
    Busca produtos no arquivo CSV com base nos parâmetros fornecidos.
    
    A busca é por correspondência 'OR' (se corresponder a qualquer um dos 
    parâmetros, o produto é retornado).
    """
    list_products = []
    
    try:
        with open(CSV_FILE, "r", newline="") as file:
            # Usa csv.DictReader para ler os dados como dicionários (mais legível)
            reader = csv.DictReader(file)
            
            for row in reader:
                # Converte o preço para float para comparação
                try:
                    prod_price_float = float(row['price'])
                except ValueError:
                    # Ignora linhas com preço inválido
                    continue

                # Lógica de busca: O produto é adicionado se *qualquer* # um dos parâmetros corresponder.
                match = False
                if id is not None and row['id'] == id:
                    match = True
                if name is not None and row['name'] == name:
                    match = True
                if price is not None and prod_price_float == price:
                    match = True
                if quantity is not None and row['quantity'] == quantity:
                    match = True
                
                if match:
                    # Armazena os dados do produto encontrado
                    list_products.append({
                        "id": row['id'],
                        "name": row['name'],
                        "price": prod_price_float,
                        "quantity": row['quantity']
                    })

    except FileNotFoundError:
        return f"Erro: Arquivo '{CSV_FILE}' não encontrado.\n"
    
    # Formata a lista de produtos encontrados
    list_return = [
        f"ID: {prod['id']} | Name: {prod['name']} | Price: {prod['price']:.2f} | Quantity: {prod['quantity']}\n" 
        for prod in list_products
    ]
    
    if not list_return:
        return "Produto não encontrado\n"
        
    return "".join(list_return)

def add_root_product(
    id: str,
    nome: str,
    price: float | str,
    quantity: str
) -> str:
    """
    Adiciona um novo produto ao arquivo CSV, verificando se ID e Nome já existem.
    """
    try:
        # 1. verificar se o DataBaseARQ.csv já existe
        if not os.path.exists(CSV_FILE):
            _ensure_csv_exists()        

        # 2. Verifica duplicatas de ID ou Nome
        with open(CSV_FILE, "r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # adcionar um cabeçalho se o arquivo estiver vazio
                if os.path.getsize(CSV_FILE) == 0:
                    writer = csv.writer(file)
                    writer.writerow(["id", "name", "price", "quantity"])
                # Verifica se o ID ou Nome já existem
                if row['id'] == id:
                    return f"Erro: Produto com ID '{id}' já existente!\n"
                # A verificação de duplicidade deve ser feita apenas 
                # para campos que *devem* ser únicos (ID e Nome são típicos)
                if row['name'] == nome:
                    return f"Erro: Produto com nome '{nome}' já existente!\n"

    except FileNotFoundError:
        # Se o arquivo não existe, a função auxiliar o criará e a próxima 
        # etapa de escrita funcionará
        pass
        
    # 3. Adiciona o novo produto
    try:
        # Abre o arquivo em modo de adição ('a')
        with open(CSV_FILE, "a", newline="") as file:
            # adcionar um cabeçalho se o arquivo estiver vazio
            if os.path.getsize(CSV_FILE) == 0:
                writer = csv.writer(file)
                writer.writerow(["id", "name", "price", "quantity"])
            # Usa csv.writer para garantir que o formato CSV seja correto
            writer = csv.writer(file)
            # Escreve a nova linha com os dados do produto
            writer.writerow([id, nome, float(price), quantity])
            
        return "Produto adicionado com sucesso!\n"
        
    except Exception as e:
        return f"Erro ao adicionar produto: {e}\n"

if __name__ == "__main__":
    # Garante que haja dados iniciais para testar 'get'
    print("testes de add_root_product\n", "=" * 30)
    print(add_root_product(id="001", nome="Apple", price=0.80, quantity="unit"))
    print(add_root_product(id="025", nome="Orange", price=1.50, quantity="bag"))
    print(add_root_product(id="026", nome="Grape", price=5.00, quantity="kilo"))
    print(add_root_product(id="031", nome="Watermelon", price=10.00, quantity="unit"))

    print("Testando get_root_product:\n", "=" * 30)
    
    print("\n--- Busca por ID='031' ---")
    produto = get_root_product(id="031")
    print(produto)
    
    print("\n--- Busca por Name='Apple' ---")
    produto = get_root_product(name="Apple")
    print(produto)
    
    print("\n--- Busca por Price=0.80 ---")
    produto = get_root_product(price=0.80)
    print(produto)
    
    print("\n--- Busca por Quantity='unit' ---")
    produto = get_root_product(quantity="unit")
    print(produto)

    print("\n--- Busca sem correspondência ---")
    produto = get_root_product(id="999")
    print(produto)

    print("=" * 30, "\n")
    print("Testando add_root_product:\n", "=" * 30)
    
    print("\n--- Tentando adicionar novo produto (banana) ---")
    resposta = add_root_product(id="030", nome="Banana", price=1.20, quantity="15")
    print(resposta)
    
    print("\n--- Tentando adicionar produto com ID duplicado (030) ---")
    resposta = add_root_product(id="030", nome="Strawberry", price=2.50, quantity="box")
    print(resposta)
    
    print("\n--- Tentando adicionar produto com Nome duplicado (Apple) ---")
    resposta = add_root_product(id="031", nome="Apple", price=0.50, quantity="unit")
    print(resposta)
    
    print("\n--- Buscando o novo produto adicionado (Banana) ---")
    produto = get_root_product(id="030")
    print(produto)