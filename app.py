import os
import secrets
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rh.db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'muda-isso-depois-por-algo-seguro'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class Contratado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    email = db.Column(db.String(100))
    token =db.Column(db.String(23), unique=True)
    documentos = db.relationship('Documento', backref='contratado')

class Documento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50))
    nome_arquivo = db.Column(db.String(200))
    contratado_id = db.Column(db.Integer, db.ForeignKey('contratado.id'))

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200))
    senha_hash = db.Column(db.String(200))

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

@login_manager.user_loader
def carregar_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))

DOCUMENTOS_OBRIGATORIOS = ['RG', 'CPF', 'Comprovante de residencia', 'Título de Eleitor', 'PIS',
                           'Conta Bancária', 'Reservista']
PASTA_UPLOADS = 'uploads'
os.makedirs(PASTA_UPLOADS, exist_ok=True)

@app.route('/')
def home():
    return render_template ('home.html', nome='Miguel')

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        nome_digitado = request.form.get('nome')
        return f'Você digitou {nome_digitado}'
    return render_template('formulario.html')

@app.route('/sobre')
def sobre():
    return 'sobre'

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        token_gerado = secrets.token_urlsafe(8)

        novo_contratado = Contratado(nome=nome, email=email, token=token_gerado)
        db.session.add(novo_contratado)
        db.session.add(novo_contratado)
        db.session.commit()
        link = f'htpp://127.0.0.1:5000/upload/{novo_contratado.token}'
        return f'Contratado {nome} cadastrado! Link de acesso: {link}'
    return render_template('cadastrar.html')

@app.route('/contratados')
@login_required
def contratados():
    todos = Contratado.query.all()
    return render_template('contratados.html', contratados=todos)

@app.route('/upload_pessoal/<token>', methods=['GET', 'POST'])
def upload_pessoal(token):
    contratado = Contratado.query.filter_by(token=token).first()

    if contratado is None:
        return 'Link inválido ou não encontrado.', 404

    if request.method == 'POST':
        tipo_documento = request.form.get('tipo_documento')
        arquivo = request.files.get('documento')
        nome_seguro = secure_filename(arquivo.filename)
        caminho = os.path.join(PASTA_UPLOADS, nome_seguro)
        arquivo.save(caminho)

        novo_documento = Documento(tipo=tipo_documento, nome_arquivo=nome_seguro, contratado_id=contratado.id)
        db.session.add(novo_documento)
        db.session.commit()

        return f'Documento "{tipo_documento}" enviado com sucesso, {contratado.nome}!'

    return render_template('upload_pessoal.html', contratado=contratado, tipos=DOCUMENTOS_OBRIGATORIOS)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.verificar_senha(senha):
            login_user(usuario)
            return redirect(url_for('contratados'))

        return 'Email ou senha incorreto!'

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
