from app import app, db, Usuario

with app.app_context():
    novo_usuario = Usuario (email='rh@empresa.com')
    novo_usuario.definir_senha('senha123')

    db.session.add(novo_usuario)
    db.session.commit()

    print('Usuario criado com sucesso')