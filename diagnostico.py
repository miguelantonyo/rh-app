import os
from app import app, db
from sqlalchemy import inspect

print("Pasta atual:", os.getcwd())
print("Pasta tem permissão de escrita?", os.access(os.getcwd(), os.W_OK))

with app.app_context():
    print("URL do banco (via engine):", db.engine.url)
    db.create_all()
    inspetor = inspect(db.engine)
    print("Tabelas criadas:", inspetor.get_table_names())

print("Arquivos na pasta atual:", os.listdir('.'))