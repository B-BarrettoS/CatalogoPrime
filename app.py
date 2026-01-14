from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "supersecretkey"  # necessário para session e flash

# Usuário/admin fixo
ADMIN_USER = "admin"
ADMIN_PASS = "JB2026"

# Lista de produtos (exemplo)
produtos = [
    {
        "codigo": "0001",
        "descricao": "Anel Prata",
        "preco_por": 150.00,
        "imagem": "https://catalogo.softarte.com.br/imagens/Produtos/0066103.jpg",
        "categoria": "Anel"
    },
    {
        "codigo": "0002",
        "descricao": "Pulseira Prata",
        "preco_por": 200.00,
        "imagem": "https://catalogo.softarte.com.br/imagens/Produtos/0066103.jpg",
        "categoria": "Pulseira"
    }
]

# =========================
# Login / Logout
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        if usuario == ADMIN_USER and senha == ADMIN_PASS:
            session["logado"] = True
            return redirect(url_for("admin"))
        else:
            flash("Usuário ou senha incorretos!")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logado", None)
    flash("Você saiu do admin.")
    return redirect(url_for("login"))

# =========================
# Painel Admin
# =========================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("logado"):
        flash("Faça login para acessar o painel admin.")
        return redirect(url_for("login"))

    editar_codigo = request.args.get("editar")
    produto_editar = next((p for p in produtos if p["codigo"] == editar_codigo), None)

    if request.method == "POST":
        imagem = request.form["imagem"]
        item_texto = request.form["item"].split("\n")
        codigo, descricao = item_texto[0].split(" - ")
        preco_por = float(item_texto[1])
        categoria = request.form["categoria"]

        if produto_editar:
            produto_editar.update({
                "imagem": imagem,
                "codigo": codigo,
                "descricao": descricao,
                "preco_por": preco_por,
                "categoria": categoria
            })
            flash("Produto atualizado com sucesso!")
        else:
            produtos.append({
                "imagem": imagem,
                "codigo": codigo,
                "descricao": descricao,
                "preco_por": preco_por,
                "categoria": categoria
            })
            flash("Produto cadastrado com sucesso!")

        return redirect(url_for("admin"))

    return render_template("admin.html", produtos=produtos, produto_editar=produto_editar)

# =========================
# Deletar produto
# =========================
@app.route("/deletar/<codigo>")
def deletar(codigo):
    if not session.get("logado"):
        flash("Faça login para acessar o painel admin.")
        return redirect(url_for("login"))

    global produtos
    produtos = [p for p in produtos if p["codigo"] != codigo]
    flash("Produto deletado com sucesso!")
    return redirect(url_for("admin"))

# =========================
# Página do catálogo
# =========================
@app.route("/")
def catalogo():
    categorias = {}
    for p in produtos:
        categorias.setdefault(p["categoria"], []).append(p)
    return render_template("catalogo.html", categorias=categorias)

# =========================
# Rodar app
# =========================
if __name__ == "__main__":
    app.run(debug=True)
