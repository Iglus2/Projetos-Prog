"""
Aplicativo principal Flask integrado com SQLAlchemy e WTForms.
Define a configuração básica, modelos de banco de dados, formulários e rotas.
"""
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from flask_sqlalchemy import SQLAlchemy

# Inicialização e configuração do aplicativo Flask
app = Flask(__name__)
# A chave secreta é usada para proteger proteger sessões e formulários (CSRF)
app.config['SECRET_KEY'] = 'kfjad fkjasdlkfja;sldkfj39480293afKJ KJD:'
# Configuração do banco de dados SQLite local
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
# Desabilita o rastreamento de modificações para otimizar desempenho
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# Inicialização da extensão SQLAlchemy
db = SQLAlchemy(app)

# ================= MODELOS =================
class Desenvolvedor(db.Model):
    """Modelo representando um Desenvolvedor."""
    id = db.Column(db.Integer,  primary_key=True)
    nome = db.Column(db.String(25), nullable=False)
    # Relação 1-para-N com Task: Um desenvolvedor pode ter várias tarefas
    tarefa = db.relationship('Tarefa', backref='desenvolvedor', lazy=True, cascade='all, delete-orphan')

class Tarefa(db.Model):
    """Modelo representando uma Tarefa atribuída a um Desenvolvedor."""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    prioridade = db.Column(db.Integer, nullable=False)
    prazo = db.Column(db.Date, nullable=False)
    # Chave estrangeira que vincula a tarefa ao ID de um desenvolvedor
    id_desenvolvedor = db.Column(db.Integer, db.ForeignKey('desenvolvedor.id'), nullable=False)

# ================= FORMS =================
class DeveloperForm(FlaskForm):
    """Formulário para cadastrar um novo desenvolvedor."""
    nome = StringField('Nome do Desenvolvedor', validators=[DataRequired(message="O nome é obrigatório.")])
    submit = SubmitField('Cadastrar')

class TarefaForm(FlaskForm):
    """Formulário para criar uma nova tarefa e atribuí-la a um desenvolvedor."""
    id_desenvolvedor = SelectField('Desenvolvedor', coerce=int, validators=[DataRequired(message="Selecione um desenvolvedor.")])
    nome = StringField('Nome da Tarefa', validators=[DataRequired()])
    descricao = TextAreaField('Descrição')
    prioridade = IntegerField('Prioridade (1 a 10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    prazo = DateField('Data de Entrega', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Criar Tarefa')

class TarefaPesquisarForm(FlaskForm):
    data_busca = DateField('Filtrar por Data de Entrega (opcional)', format='%Y-%m-%d', render_kw={"type": "date"})
    submit = SubmitField('Pesquisar')

class TarefaAtualizarForm(FlaskForm):
    id_desenvolvedor = SelectField('Desenvolvedor', coerce=int, validators=[DataRequired()])
    nome = StringField('Nome da Tarefa', validators=[DataRequired()])
    descricao = TextAreaField('Descrição')
    prioridade = IntegerField('Prioridade (1 a 10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    prazo = DateField('Data de Entrega', validators=[DataRequired()], format='%Y-%m-%d', render_kw={"type": "date"})
    submit = SubmitField('Atualizar Tarefa')

# ================= ROTAS =================
@app.route('/')
def index():
    """Rota principal que exibe todos os desenvolvedores e tarefas cadastradas."""
    developers = Desenvolvedor.query.order_by(Desenvolvedor.nome).all()
    tarefas = Tarefa.query.order_by(Tarefa.prazo).all()
    return render_template('index.html', developers=developers, tarefas=tarefas)

@app.route('/cadastrar-desenvolvedor', methods=['GET', 'POST'])
def registrar_desenvolvedor():
    """Rota para acessar o formulário e cadastrar novos desenvolvedores."""
    form = DeveloperForm()
    # Processa o formulário se enviado com método POST e passar nas validações
    if form.validate_on_submit():
        new_dev = Desenvolvedor(nome=form.nome.data)
        db.session.add(new_dev)
        db.session.commit()
        flash('Desenvolvedor cadastrado com sucesso!', 'success')
        return redirect(url_for('registrar_desenvolvedor'))
    return render_template('registrar_desenvolvedor.html', form=form)

@app.route('/criar-tarefa', methods=['GET', 'POST'])
def criar_tarefa():
    """Rota para visualizar o formulário e criar novas tarefas vinculadas aos desenvolvedores."""
    form = TarefaForm()
    # Popula o SelectField de desenvolvedor_id dinamicamente com as opções do banco de dados
    devs = Desenvolvedor.query.all()
    devs_list = []
    for d in devs:
        devs_list.append((d.id, d.nome))
    form.id_desenvolvedor.choices = devs_list

    # Verifica se os dados do formulário são válidos e processa o cadastro
    if form.validate_on_submit():
        nova_tarefa = Tarefa(
            nome=form.nome.data,
            descricao=form.descricao.data,
            prioridade=form.prioridade.data,
            prazo=form.prazo.data,
            id_desenvolvedor=form.id_desenvolvedor.data
        )
        db.session.add(nova_tarefa)
        db.session.commit()
        flash('Tarefa criada com sucesso!', 'success')
        return redirect(url_for('criar_tarefa'))
    return render_template('criar_tarefa.html', form=form)

@app.route('/pesquisar-tarefas', methods=['GET', 'POST'])
def buscar_tarefas():
    form = TarefaPesquisarForm()
    # Por padrão, mostra todas as tarefas ordenadas por data
    tarefas = Tarefa.query.order_by(Tarefa.prazo).all()

    if form.validate_on_submit():
        if form.data_busca.data:
            tarefas = Tarefa.query.filter_by(prazo=form.data_busca.data).order_by(Tarefa.prioridade).all()
        else:
            tarefas = Tarefa.query.order_by(Tarefa.prazo).all()

    return render_template('busca_tarefas.html', form=form, tarefas=tarefas)

@app.route('/editar-tarefa/<int:id_tarefa>/<string:origem>', methods=['GET', 'POST'])
def editar_tarefa(id_tarefa, origem):
    tarefa = Tarefa.query.get_or_404(id_tarefa)
    form = TarefaAtualizarForm(obj=tarefa)  # Pré-preenche o formulário com os dados atuais
    devs = Desenvolvedor.query.all()
    devs_list = []
    for d in devs:
        devs_list.append((d.id, d.nome))
    form.id_desenvolvedor.choices = devs_list
    print(request.url_rule)
    print(form.validate_on_submit())
    print(origem)
    if form.validate_on_submit() and origem != "buscar_tarefas" :
        # Atualiza os campos manualmente para garantir compatibilidade de tipos
        tarefa.nome = form.nome.data
        tarefa.descricao = form.descricao.data
        tarefa.prioridade = form.prioridade.data
        tarefa.prazo = form.prazo.data
        tarefa.id_desenvolvedor = form.id_desenvolvedor.data
        
        db.session.commit()
        flash('Tarefa atualizada com sucesso!', 'success')
        return redirect(url_for('buscar_tarefas'))

    return render_template('editar_tarefa.html', form=form, tarefa=tarefa)

@app.route('/deletar-tarefa/<int:id_tarefa>', methods=['POST'])
def deletar_tarefa(id_tarefa):
    tarefa = Tarefa.query.get_or_404(id_tarefa)
    db.session.delete(tarefa)
    db.session.commit()
    flash('Tarefa deletada com sucesso!', 'success')
    return redirect(url_for('buscar_tarefas'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas na primeira execução
    app.run(debug=True, host='0.0.0.0', port=5000)