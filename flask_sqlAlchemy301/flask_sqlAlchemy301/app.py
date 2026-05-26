from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DateField, SubmitField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Length
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kfjad fkjasdlkfja;sldkfj39480293afKJ KJD:'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Desenvolvedor.query.get(int(user_id))


class Desenvolvedor(db.Model, UserMixin):
    """Modelo representando um Desenvolvedor."""
    id = db.Column(db.Integer,  primary_key=True)
    nome = db.Column(db.String(25), nullable=False, unique=True)
    senha = db.Column(db.String(128), nullable=False) # Novo campo de senha
    tarefa = db.relationship('Tarefa', backref='desenvolvedor', lazy=True, cascade='all, delete-orphan')


class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    prioridade = db.Column(db.Integer, nullable=False)
    prazo = db.Column(db.Date, nullable=False)
    id_desenvolvedor = db.Column(db.Integer, db.ForeignKey('desenvolvedor.id'), nullable=False)


class LoginForm(FlaskForm):
    nome = StringField('Usuário', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class DeveloperForm(FlaskForm):
    """Formulário para cadastrar um novo desenvolvedor com senha."""
    nome = StringField('Nome do Desenvolvedor', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Cadastrar')

class TarefaForm(FlaskForm):
    """Formulário para criar uma nova tarefa e atribuí-la a um desenvolvedor."""
    nome = StringField('Nome da Tarefa', validators=[DataRequired()])
    descricao = TextAreaField('Descrição')
    prioridade = IntegerField('Prioridade (1 a 10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    prazo = DateField('Data de Entrega', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Criar Tarefa')

class TarefaPesquisarForm(FlaskForm):
    data_busca = DateField('Filtrar por Data de Entrega (opcional)', format='%Y-%m-%d', render_kw={"type": "date"})
    submit = SubmitField('Pesquisar')

class TarefaAtualizarForm(FlaskForm):
    nome = StringField('Nome da Tarefa', validators=[DataRequired()])
    descricao = TextAreaField('Descrição')
    prioridade = IntegerField('Prioridade (1 a 10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    prazo = DateField('Data de Entrega', validators=[DataRequired()], format='%Y-%m-%d', render_kw={"type": "date"})
    submit = SubmitField('Atualizar Tarefa')

@app.route('/')
def index():
    """Rota principal que exibe todos os desenvolvedores e tarefas cadastradas."""
    developers = Desenvolvedor.query.order_by(Desenvolvedor.nome).all()
    tarefas = Tarefa.query.order_by(Tarefa.prazo).all()
    return render_template('index.html', developers=developers, tarefas=tarefas)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Desenvolvedor.query.filter_by(nome=form.nome.data).first()
        if user and check_password_hash(user.senha, form.senha.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/cadastrar-desenvolvedor', methods=['GET', 'POST'])
def registrar_desenvolvedor():
    form = DeveloperForm()
    if form.validate_on_submit():
        hash_senha = generate_password_hash(form.senha.data)
        new_dev = Desenvolvedor(nome=form.nome.data, senha=hash_senha)
        db.session.add(new_dev)
        db.session.commit()
        flash('Desenvolvedor cadastrado!', 'success')
        return redirect(url_for('login'))
    return render_template('registrar_desenvolvedor.html', form=form)

@app.route('/criar-tarefa', methods=['GET', 'POST'])
@login_required
def criar_tarefa():
    form = TarefaForm()

    if form.validate_on_submit():
        nova_tarefa = Tarefa(
            nome=form.nome.data,
            descricao=form.descricao.data,
            prioridade=form.prioridade.data,
            prazo=form.prazo.data,
            id_desenvolvedor=current_user.id 
        )
        db.session.add(nova_tarefa)
        db.session.commit()
        flash('Tarefa criada com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('criar_tarefa.html', form=form)

@app.route('/buscar-tarefas', methods=['GET', 'POST'])
@login_required
def buscar_tarefas():
    form = TarefaPesquisarForm()
    tarefas = Tarefa.query.filter_by(id_desenvolvedor=current_user.id).order_by(Tarefa.prazo).all()
    if form.validate_on_submit() and form.data_busca.data:
        tarefas = Tarefa.query.filter_by(id_desenvolvedor=current_user.id, prazo=form.data_busca.data).order_by(Tarefa.prazo).all()
    return render_template('busca_tarefas.html', form=form, tarefas=tarefas)

@app.route('/editar-tarefa/<int:id_tarefa>/<string:origem>', methods=['GET', 'POST'])
@login_required
def editar_tarefa(id_tarefa, origem):
    tarefa = Tarefa.query.get_or_404(id_tarefa)
    
    if tarefa.id_desenvolvedor != current_user.id:
        flash('Você só pode editar suas próprias tarefas!', 'danger')
        return redirect(url_for('buscar_tarefas'))

    form = TarefaAtualizarForm(obj=tarefa)
    if form.validate_on_submit():
        tarefa.nome = form.nome.data
        tarefa.descricao = form.descricao.data
        tarefa.prioridade = form.prioridade.data
        tarefa.prazo = form.prazo.data
        db.session.commit()
        flash('Tarefa atualizada com sucesso!', 'success')
        return redirect(url_for('buscar_tarefas'))
    return render_template('editar_tarefa.html', form=form, tarefa=tarefa)

@app.route('/deletar-tarefa/<int:id_tarefa>', methods=['POST'])
@login_required
def deletar_tarefa(id_tarefa):
    tarefa = Tarefa.query.get_or_404(id_tarefa)
    

    if tarefa.id_desenvolvedor != current_user.id:
        flash('Você só pode deletar suas próprias tarefas!', 'danger')
        return redirect(url_for('buscar_tarefas'))

    db.session.delete(tarefa)
    db.session.commit()
    flash('Tarefa deletada com sucesso!', 'success')
    return redirect(url_for('buscar_tarefas'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True, host='0.0.0.0', port=5000)
