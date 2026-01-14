from flask import Flask, render_template, request, redirect, url_for, flash
app = Flask(__name__)
app.secret_key = "supersecretkey"

# Lista de produtos
produtos = []

# Rota do admin
@app.route("/admin", methods=["GET", "POST"])
def admin():
    editar_codigo = request.args.get("editar")
    produto_editar = None

    # Se estiver editando
    if editar_codigo:
        produto_editar = next((p for p in produtos if p["codigo"] == editar_codigo), None)

    if request.method == "POST":
        imagem = request.form["imagem"]
        item = request.form["item"].strip()
        categoria = request.form["categoria"].strip()

        try:
            linha = item.split("\n")
            id_desc = linha[0].split("-", 1)
            codigo = id_desc[0].strip()
            descricao = id_desc[1].strip()
            preco_original = float(linha[1].replace(",", ".").strip())
            preco_por = round(preco_original * 2, 2)  # Multiplica por 2
        except:
            flash("Formato do item incorreto. Use: ID - Descrição\\nPreço")
            return redirect(url_for("admin"))

        # Atualizar
        if produto_editar:
            produto_editar["imagem"] = imagem
            produto_editar["descricao"] = descricao
            produto_editar["preco_por"] = preco_por
            produto_editar["categoria"] = categoria
            flash(f"Produto {codigo} atualizado!")
        else:
            # Validação código duplicado
            if any(p["codigo"] == codigo for p in produtos):
                flash("Erro: código já cadastrado!")
            else:
                produtos.append({
                    "codigo": codigo,
                    "descricao": descricao,
                    "preco_por": preco_por,
                    "categoria": categoria,
                    "imagem": imagem
                })
                flash(f"Produto {codigo} cadastrado!")

        return redirect(url_for("admin"))

    return render_template("admin.html", produtos=produtos, produto_editar=produto_editar)


# Deletar produto
@app.route("/deletar/<codigo>")
def deletar(codigo):
    global produtos
    produtos = [p for p in produtos if p["codigo"] != codigo]
    flash(f"Produto {codigo} deletado!")
    return redirect(url_for("admin"))


# Catalogo público
@app.route("/")
def catalogo():
    # Organiza produtos por categorias
    categorias = {}
    for p in produtos:
        categorias.setdefault(p["categoria"], []).append(p)
    return render_template("catalogo.html", categorias=categorias)


if __name__ == "__main__":
    app.run(debug=True)
