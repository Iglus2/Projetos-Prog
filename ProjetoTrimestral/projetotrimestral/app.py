from wtforms.validators import DataRequired
from wtforms import StringField, SubmitField, TextAreaField
from flask_wtf import FlaskForm
from flask import (
    Flask,
    json,
    make_response,
    render_template,
    redirect,
    url_for,
    request,
)

app = Flask(__name__)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

app.config["SECRET_KEY"] = "1234"

lista_tarefas = []
lista_finalizada = []


class AdicionarTarefa(FlaskForm):
    nome = StringField(
        "Nome:", validators=[DataRequired(message="É obrigatório colocar um nome!")]
    )
    descricao = TextAreaField(
        "Descrição:",
        validators=[DataRequired(message="É obrigatório colocar uma descrição!")],
    )
    submit = SubmitField("Concluir Tarefa")


@app.route("/", methods=["GET", "POST"])
def Taf():
    formulario = AdicionarTarefa()

    if formulario.validate_on_submit():
        nova_tarefa = {
            "nome": formulario.nome.data,
            "descricao": formulario.descricao.data,
        }

        cookies = request.cookies.get("lista_tarefas")

        if cookies:
            lista = json.loads(cookies)
            lista.append(nova_tarefa)
        else:
            lista = [nova_tarefa]

        resposta = make_response(redirect(url_for("Taf")))
        resposta.set_cookie("lista_tarefas", json.dumps(lista), max_age=4000)

        lista_tarefas.append(nova_tarefa)

        return resposta

    return render_template("index.html", form=formulario, tarefas=lista_tarefas)


@app.route("/atualizar-tarefa", methods=["POST"])
def atualizar_tarefa():
    numero = request.form.get("numero_tarefa")
    nova_desc = request.form.get("nova_descricao")

    tarefas_encontradas = []

    for tarefa in lista_tarefas:
        if str(tarefa["descricao"]) == str(numero):
            tarefa["descricao"] = nova_desc
            tarefas_encontradas.append(tarefa)

    if not tarefas_encontradas:
        return "<h1>Não tem tarefa</h1>"

    return f"""
    <h1>Tarefa Atualizada!</h1>
    <p>Nova descrição: <strong>{nova_desc}</strong></p>
    <a href='/'>Voltar</a>
    """


@app.route("/finalizar-tarefa", methods=["POST"])
def finalizar_tarefa():
    numero = request.form.get("numero_tarefa")

    if not lista_tarefas:
        return "<h1>Não tem tarefas</h1>"

    indice = int(numero) - 1

    if 0 <= indice < len(lista_tarefas):
        tarefa_finalizada = lista_tarefas.pop(indice)
        lista_finalizada.append(tarefa_finalizada)

        print(
            f"Tarefa Finalizada! {tarefa_finalizada['nome']} - {tarefa_finalizada['descricao']}"
        )

        return redirect(url_for("Taf"))

    return "<h1>Tarefa não encontrada</h1>"


if __name__ == "__main__":
    app.run(debug=True)