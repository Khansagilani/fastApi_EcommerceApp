from sqlmodel import Session, select
from app.db import engine
from app.models import User
from hashing import hash_password


def create_admin():
    name = input("Enter admin name: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")

    with Session(engine) as session:
        existing = session.exec(
            select(User).where(User.email == email)
        ).first()

        if existing:
            print(f"User {email} already exists!")
            return

        admin = User(
            name=name,
            email=email,
            password=hash_password(password),
            is_admin=True
        )
        session.add(admin)
        session.commit()
        print(f"Admin {email} created!")


create_admin()
