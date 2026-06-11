import os
from urllib.parse import quote

from flask import Flask, render_template, redirect, url_for, session, request
from PIL import Image, ImageDraw, ImageFont

from database import criar_tabelas, get_connection
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template

app = Flask(__name__)

PAGINAS = [
    {"nome": "Início", "rota": "index"},
    {"nome": "Loja", "rota": "loja"},
    {"nome": "Banho e Tosa", "rota": "banho_tosa"},
    {"nome": "Contato", "rota": "contato"},
]


def pagina_atual(nome_rota):
    rotas = [p["rota"] for p in PAGINAS]
    indice = rotas.index(nome_rota)

    anterior = PAGINAS[indice - 1] if indice > 0 else None
    proxima = PAGINAS[indice + 1] if indice < len(PAGINAS) - 1 else None

    return {
        "paginas": PAGINAS,
        "atual": nome_rota,
        "anterior": anterior,
        "proxima": proxima
    }


@app.route("/")
def index():
    return render_template("index.html", nav=pagina_atual("index"))


@app.route("/loja")
def loja():
    produtos = [
        {"nome": "Ração Premium", "preco": 89.90},
        {"nome": "Coleira", "preco": 29.90},
        {"nome": "Shampoo Pet", "preco": 19.90},
    ]
    return render_template("loja.html", produtos=produtos, nav=pagina_atual("loja"))


@app.route("/banho-tosa")
def banho_tosa():
    return render_template("banho_tosa.html", nav=pagina_atual("banho_tosa"))


@app.route("/contato")
def contato():
    return render_template("contato.html", nav=pagina_atual("contato"))


if __name__ == "__main__":
    app.run(debug=True)
app = Flask(__name__)

# ✅ CORREÇÃO 1: SECRET_KEY sem fallback fraco.
# Se a variável não estiver definida, a aplicação não sobe em produção.
_secret_key = os.getenv("SECRET_KEY")
if not _secret_key:
    raise RuntimeError(
        "SECRET_KEY não definida. "
        "Defina a variável de ambiente SECRET_KEY antes de iniciar o servidor."
    )
app.secret_key = _secret_key

WHATSAPP_NUMBER = "5541998309920"

PASTA_ORIGINAIS = "static/images/produtos/originais"
PASTA_PROCESSADOS = "static/images/produtos_processados"

# ✅ CORREÇÃO 3 (parte 1): Pasta base resolvida em caminho absoluto
# para comparação segura contra path traversal.
PASTA_ORIGINAIS_ABS = os.path.realpath(PASTA_ORIGINAIS)

os.makedirs(PASTA_PROCESSADOS, exist_ok=True)

criar_tabelas()


def dict_factory(cursor, row):
    return {col[0]: row[index] for index, col in enumerate(cursor.description)}


def formatar_preco(valor):
    return f"R$ {valor:.2f}".replace(".", ",")


def gerar_imagem_produto(imagem_original, nome, preco):
    if not imagem_original:
        return "produto.png"

    # ✅ CORREÇÃO 3: Proteção contra Path Traversal.
    # Resolve o caminho real e verifica se está dentro da pasta permitida.
    caminho_origem = os.path.realpath(
        os.path.join(PASTA_ORIGINAIS, imagem_original)
    )

    if not caminho_origem.startswith(PASTA_ORIGINAIS_ABS + os.sep):
        print(f"[SEGURANÇA] Tentativa de path traversal bloqueada: {imagem_original}")
        return "produto.png"

    if not os.path.exists(caminho_origem):
        return imagem_original

    nome_base, _ = os.path.splitext(imagem_original)
    nome_final = f"{nome_base}_preco.png"
    caminho_final = os.path.join(PASTA_PROCESSADOS, nome_final)

    if os.path.exists(caminho_final):
        return nome_final

    try:
        img = Image.open(caminho_origem).convert("RGBA")
        draw = ImageDraw.Draw(img)

        try:
            fonte = ImageFont.truetype("arial.ttf", 32)
        except OSError:
            fonte = ImageFont.load_default()

        draw.rectangle(
            (0, img.height - 110, img.width, img.height),
            fill=(0, 0, 0, 180)
        )

        draw.text((20, img.height - 100), nome, fill="white", font=fonte)
        draw.text((20, img.height - 55), formatar_preco(preco), fill="#2ecc71", font=fonte)

        img.save(caminho_final)
        return nome_final

    except Exception as erro:
        print(f"Erro ao gerar imagem do produto: {erro}")
        return imagem_original


def buscar_produtos_por_ids(ids):
    if not ids:
        return []

    # ✅ CORREÇÃO 2: Validação estrita dos IDs antes de montar a query.
    # Garante que todos os elementos são inteiros positivos,
    # eliminando qualquer possibilidade de injeção via sessão manipulada.
    try:
        ids_validados = [int(i) for i in ids]
        if any(i <= 0 for i in ids_validados):
            raise ValueError("ID inválido")
    except (ValueError, TypeError):
        print("[SEGURANÇA] IDs inválidos detectados no carrinho.")
        return []

    placeholders = ",".join(["?"] * len(ids_validados))

    conn = get_connection()
    conn.row_factory = dict_factory

    produtos = conn.execute(
        f"SELECT * FROM produtos WHERE id IN ({placeholders})",
        ids_validados
    ).fetchall()

    conn.close()
    return produtos


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/loja")
def loja():
    conn = get_connection()
    conn.row_factory = dict_factory

    produtos = conn.execute("SELECT * FROM produtos").fetchall()
    conn.close()

    for produto in produtos:
        produto["imagem"] = gerar_imagem_produto(
            produto.get("imagem"),
            produto.get("nome", "Produto"),
            produto.get("preco", 0)
        )

    return render_template("loja.html", produtos=produtos)


@app.route("/adicionar/<int:produto_id>")
def adicionar(produto_id):
    carrinho = session.get("carrinho", {})
    produto_id = str(produto_id)

    carrinho[produto_id] = carrinho.get(produto_id, 0) + 1

    session["carrinho"] = carrinho
    session.modified = True

    return redirect(url_for("carrinho"))


@app.route("/carrinho")
def carrinho():
    carrinho_session = session.get("carrinho", {})

    if not carrinho_session:
        return render_template("carrinho.html", produtos=[], carrinho={})

    ids = [int(produto_id) for produto_id in carrinho_session.keys()]
    produtos = buscar_produtos_por_ids(ids)

    return render_template(
        "carrinho.html",
        produtos=produtos,
        carrinho=carrinho_session
    )


@app.route("/checkout")
def checkout():
    carrinho = session.get("carrinho", {})

    if not carrinho:
        return redirect(url_for("loja"))

    ids = [int(produto_id) for produto_id in carrinho.keys()]
    produtos = buscar_produtos_por_ids(ids)

    if not produtos:
        session.pop("carrinho", None)
        return redirect(url_for("loja"))

    total = sum(
        produto["preco"] * int(carrinho[str(produto["id"])])
        for produto in produtos
    )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO pedidos (total, status, data) VALUES (?, 'novo', datetime('now'))",
        (total,)
    )

    pedido_id = cursor.lastrowid

    for produto in produtos:
        quantidade = int(carrinho[str(produto["id"])])

        cursor.execute(
            """
            INSERT INTO pedido_itens (pedido_id, produto_nome, quantidade, preco)
            VALUES (?, ?, ?, ?)
            """,
            (pedido_id, produto["nome"], quantidade, produto["preco"])
        )

    conn.commit()
    conn.close()

    mensagem = f"🛒 Pedido #{pedido_id}\n\n"

    for produto in produtos:
        quantidade = int(carrinho[str(produto["id"])])
        subtotal = produto["preco"] * quantidade

        mensagem += (
            f"- {produto['nome']} | "
            f"Qtd: {quantidade} | "
            f"{formatar_preco(subtotal)}\n"
        )

    mensagem += f"\nTotal: {formatar_preco(total)}"

    session.pop("carrinho", None)

    whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(mensagem)}"

    return redirect(whatsapp_url)


@app.route("/banho-tosa", methods=["GET", "POST"])
def banho_tosa():
    if request.method == "POST":
        nome_tutor = request.form.get("nome_tutor")
        nome_pet = request.form.get("nome_pet")
        servico = request.form.get("servico")
        data = request.form.get("data")
        hora = request.form.get("hora")

        if not all([nome_tutor, nome_pet, servico, data, hora]):
            return redirect(url_for("banho_tosa"))

        conn = get_connection()

        conn.execute(
            """
            INSERT INTO agendamentos (nome_tutor, nome_pet, servico, data, hora)
            VALUES (?, ?, ?, ?, ?)
            """,
            (nome_tutor, nome_pet, servico, data, hora)
        )

        conn.commit()
        conn.close()

        mensagem = (
            f"Olá! Gostaria de agendar banho e tosa.\n\n"
            f"Tutor: {nome_tutor}\n"
            f"Pet: {nome_pet}\n"
            f"Serviço: {servico}\n"
            f"Data: {data}\n"
            f"Hora: {hora}"
        )

        return redirect(f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(mensagem)}")

    return render_template("banho_tosa.html")


@app.route("/contato")
def contato():
    return render_template("contato.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)