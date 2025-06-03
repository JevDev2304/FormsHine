from sqlmodel import create_engine, Session

DATABASE_URL = "postgresql://juan:contraseña123@localhost:5433/hine"

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
