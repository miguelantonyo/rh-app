from app import app, Documento

with app.app_context():
    documentos = Documento.query.all()
    for doc in documentos:
        print(doc.tipo, doc.nome_arquivo, doc.contratado_id)