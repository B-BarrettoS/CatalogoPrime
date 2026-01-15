from flask import Flask, render_template, request, redirect, url_for, flash, session
import json
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

ADMIN_USER = "admin"
ADMIN_PASS = "JB2026"

ARQUIVO_PRODUTOS = "produtos.json"

# =========================
# Funções de persistência
# =========================
def carregar_produtos():
    if os.path.exists(ARQUIVO_PRODUTOS):
        with open(ARQUIVO_PRODUTOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_produtos(produtos):
    with open(ARQUIVO_PRODUTOS, "w", encoding="utf-8") as f:
        json.dump(produtos, f, ensure_ascii=False, indent=4)

# Carrega ao iniciar
produtos = carregar_produtos()

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
    return redirect(url_for("login"))

# =========================
# Admin
# =========================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("logado"):
        return redirect(url_for("login"))

    editar_codigo = request.args.get("editar")
    produto_editar = next((p for p in produtos if p["codigo"] == editar_codigo), None)

    if request.method == "POST":
        imagem = request.form["imagem"]
        item_texto = request.form["item"].split("\n")

        codigo, descricao = item_texto[0].split(" - ")

        # preço x2 e vírgula brasileira
        preco_por = float(item_texto[1].replace(",", ".")) * 2

        categoria = request.form["categoria"]

        if produto_editar:
            produto_editar.update({
                "codigo": codigo,
                "descricao": descricao,
                "preco_por": preco_por,
                "imagem": imagem,
                "categoria": categoria
            })
            flash("Produto atualizado!")
        else:
            produtos.append({
                "codigo": codigo,
                "descricao": descricao,
                "preco_por": preco_por,
                "imagem": imagem,
                "categoria": categoria
            })
            flash("Produto cadastrado!")

        salvar_produtos(produtos)
        return redirect(url_for("admin"))

    return render_template("admin.html", produtos=produtos, produto_editar=produto_editar)

# =========================
# Deletar
# =========================
@app.route("/deletar/<codigo>")
def deletar(codigo):
    if not session.get("logado"):
        return redirect(url_for("login"))

    global produtos
    produtos = [p for p in produtos if p["codigo"] != codigo]
    salvar_produtos(produtos)
    flash("Produto deletado!")
    return redirect(url_for("admin"))

# =========================
# Catálogo
# =========================
@app.route("/")
def catalogo():
    categorias = {}
    for p in produtos:
        categorias.setdefault(p["categoria"], []).append(p)
    return render_template("catalogo.html", categorias=categorias)

# =========================
# Run
# =========================
if __name__ == "__main__":
    app.run(debug=True)
