from wtforms.validators import DataRequired
from wtforms import PasswordField, StringField, SubmitField
from flask_wtf import FlaskForm

app = Flask(__name__)

app.config["SECRET_KEY"] = "1234"

lista_logins = []


class EfetuarLogin(FlaskForm):
    nome = StringField(
        "Nome:", validators=DataRequired(message="É obrigatório colocar o nome!")
    )
    senha = PasswordField(
        "Senha: ", validators=DataRequired(message="É obrigatório colocar uma senha!")
    )
    submit = SubmitField("Concluir login")


@app.route("/", methods=["GET", "POST"])
def login():
    formulario = EfetuarLogin()

    if formulario.validate_on_submit():
        novo_login = {"nome": formulario.nome.data, "senha": formulario.senha.data}
        cookies = request.cookies.get("lista_logins")

        if cookies:
            lsta_logins = json.loads(cookies)
            lsta_logins.append(
                {"nome": formulario.nome.data, "senha": formulario.senha.data}
            )
        else:
            lsta_logins = [
                {"nome": formulario.nome.data, "senha": formulario.senha.data}
            ]

        resposta = make_response(redirect(url_for("login")))
        resposta.set_cookie("lista_logins", json.dumps(lsta_logins, max_age=4000))

        lista_logins.append(
            {"nome": formulario.nome.data, "senha": formulario.senha.data}
        )

        return resposta

    return render_template("index.html", form=formulario)
