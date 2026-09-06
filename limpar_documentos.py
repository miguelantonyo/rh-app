from app import app, db, Documento

with app.app_context():
    Documento.query.delete()
    db.session.commit()
    print('Todos os documentos foram removidos.')