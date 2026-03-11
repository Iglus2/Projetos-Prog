from flask import Flask, render_template, request, redirect
from datetime import datetime


# Criando a aplicação Flask
app = Flask(__name__)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

lista_pedidos = []
lista_finalizados = []

# Criando uma ROTA (o endereço do site)
@app.route("/")
def home():
    # Aqui o Python prepara os dados
    titulo_site = "Aula de Flask - 3º Ano"
    
    # O Python "renderiza" (desenha) o HTML e envia as variáveis
    return render_template("index.html", titulo=titulo_site)

@app.route("/contato")
def sobre():
    return render_template("contato.html", titulo="Contato")


@app.route("/receber-pedido", methods=['POST'])
def receber_pedido():
    # O objeto 'request.form' funciona como um dicionário
    # Ele pega os dados pelo 'name' que definimos no HTML
    
    prato_escolhido = request.form.get('nome_do_prato')
    mesa_cliente = request.form.get('numero_mesa')
    
    # Vamos mostrar no terminal do VS Code para o programador ver
    print(f"NOVO PEDIDO! Mesa: {mesa_cliente} | Prato: {prato_escolhido}")
    lista_pedidos.append({"mesa": mesa_cliente, "prato": prato_escolhido})
    # Retorna uma confirmação para o usuário
    return f"""
    <h1>Pedido Recebido! ✅</h1>
    <p>A cozinha está preparando um <strong>{prato_escolhido}</strong> para a mesa <strong>{mesa_cliente}</strong>.</p>
    <a href='/'>Voltar</a>
    """


@app.route("/atualizar-pedido", methods=['POST'])
def atualizar_peditdo():
    # O objeto 'request.form' funciona como um dicionário
    # Ele pega os dados pelo 'name' que definimos no HTML
    
    mesa_cliente = request.form.get('numero_mesa')
    novo_prato_escolhido = request.form.get('nome_do_prato')

    pedidos_da_mesa = []

    for pedido in lista_pedidos:
        if pedido["mesa"] == mesa_cliente:
            pedido["prato"] = novo_prato_escolhido

            pedidos_da_mesa.append(pedidos_recebidos)
    
    if not pedidos_da_mesa:
        print("Não existe")
        return f"""
        <h1>Não tem pedidos</h1>
        """

    else:
        # Vamos mostrar no terminal do VS Code para o programador ver
        print(f"NOVO PEDIDO ATUALIZADO! Mesa: {mesa_cliente} | Prato: {novo_prato_escolhido}")
        # Retorna uma confirmação para o usuário
        return f"""
        <h1>Pedido Atualizado! ✅</h1>
        <p>A cozinha está preparando um <strong>{novo_prato_escolhido}</strong> para a mesa <strong>{mesa_cliente}</strong>.</p>
        <a href='/'>Voltar</a>
        """

@app.route("/pedidos-recebidos")
def pedidos_recebidos():
    existe_pedidos = len(lista_pedidos) > 0
    data = datetime.now()
    return render_template("cozinha.html", pedidos=lista_pedidos, existe_pedidos=existe_pedidos, hoje=data)


@app.route("/finalizar-pedido", methods=['POST'])
def finalizar_pedido():
    numero_pedido = request.form.get('numero_pedido')
    
    if not lista_pedidos:
        return f"""
        <h1>Não tem pedidos</h1>
        """
    
    indice = int(numero_pedido) - 1
    
    if indice >= 0 and indice < len(lista_pedidos):
        pedido_finalizado = lista_pedidos.pop(indice)
        lista_finalizados.append(pedido_finalizado)
        print(f"PEDIDO FINALIZADO! Mesa: {pedido_finalizado['mesa']} | Prato: {pedido_finalizado['prato']}")
        return redirect("/balcao")
    else:
        return f"""
        <h1>Pedido não encontrado</h1>
        """


@app.route("/balcao")
def balcao():
    existe_finalizados = len(lista_finalizados) > 0
    data = datetime.now()
    return render_template("balcao.html", pedidos=lista_finalizados, existe_finalizados=existe_finalizados, hoje=data)

@app.template_filter('datetime_format')
def datetime_format(value, format="%H:%M %d-%m-%y"):
    return value.strftime(format)

# Rodando o servidor
if __name__ == "__main__":
    app.run(debug=True) # debug=True faz o site atualizar sozinho quando salvamos
