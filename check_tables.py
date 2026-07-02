# check_tables.py
from sqlalchemy import create_engine, inspect
from app.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

tables = inspector.get_table_names()
print("Tables in database:")
for table in sorted(tables):
    print(f"  - {table}")