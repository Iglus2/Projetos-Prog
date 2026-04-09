from wtforms.validators import DataRequired
from wtforms import PasswordField, StringField, SubmitField
from flask_wtf import FlaskForm
from flask import Flask, json, make_response, render_template, redirect, url_for, request


app = Flask(__name__)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

app.config["SECRET_KEY"] = "1234"

lista_tarefas = []
lista_finalizada = []


class AdicionarTarefa(FlaskForm):
    nome = StringField(
        "Nome:", validators=DataRequired(message="É obrigatório colocar um nome!")
    )
    descricao = PasswordField(
        "Descricao: ", validators=DataRequired(message="É obrigatório colocar uma descricao!")
    )
    submit = SubmitField("Concluir Tarefa")


@app.route("/", methods=["GET", "POST"])
def Taf():
    formulario = AdicionarTarefa()

    if formulario.validate_on_submit():
        nova_tarefa = {"nome": formulario.nome.data, "descricao": formulario.descricao.data}
        cookies = request.cookies.get("lista_tarefas")

        if cookies:
            lsta_tarefas = json.loads(cookies)
            lsta_tarefas.append(
                {"nome": formulario.nome.data, "descricao": formulario.descricao.data}
            )
        else:
            lsta_tarefas = [
                {"nome": formulario.nome.data, "descricao": formulario.descricao.data}
            ]

        resposta = make_response(redirect(url_for("login")))
        resposta.set_cookie("lista_tarefas", json.dumps(lsta_tarefas, max_age=4000))

        lista_tarefas.append(
            {"nome": formulario.nome.data, "descricao": formulario.descricao.data}
        )

        return resposta

    return render_template("index.html", form=formulario)

@app.route("/", methods=["GET", "POST"])
    