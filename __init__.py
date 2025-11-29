
ROOT = ".\\processamento_dados_CSV"

def get_root_product(
        id: str | None = None,
        name: str | None = None,
        price: float | None = None,
        quantity: str | None = None
    ):
    with open(f"{ROOT}\\DataBaseARQ.csv", "r") as file:
        data = file.readlines()
        products = zip([line.strip().split(",") for line in data[1:]])
        for product in products:
            prod_id, prod_name, prod_price, prod_quantity = product[0]
            if (id is not None and prod_id == id) or \
               (name is not None and prod_name == name) or \
               (price is not None and float(prod_price) == price) or \
                (quantity is not None and prod_quantity == quantity):
                return {
                    "id": prod_id,
                    "name": prod_name,
                    "price": float(prod_price),
                    "quantity": prod_quantity
                }

if __name__ == "__main__":
    produto = get_root_product(id="025")
    print(produto)
    produto = get_root_product(name="apple")
    print(produto)
    produto = get_root_product(price=1999.99)
    print(produto)
    produto = get_root_product(quantity="10")
    print(produto)