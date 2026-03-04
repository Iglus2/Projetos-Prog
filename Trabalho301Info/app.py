from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    titulo_site = "Aula de Flask - 3º Ano"
    return render_template("index.html", titulo= titulo_site)


@app.route("/sobre")
def sobre():
    nomes = "Kaigal!" 
    return render_template("sobre.html", nome = nomes)


if __name__ == "__main__":
    app.run(debug=True)
