from app.models import Product
from sqlmodel import Session, create_engine, select

db_con = "postgresql://postgres:khansa1086@localhost:5432/ecommerce_app"
engine = create_engine(db_con)

DEFAULT_VALUES = {
    "category": "unstitched",
    "style": "casual",
    "fabric_type": "printed",
    "pieces": "2piece",
}

def fill_empty_fields():
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
        updated = 0
        for product in products:
            changed = False
            if not product.category:
                product.category = DEFAULT_VALUES["category"]
                changed = True
            if not product.style:
                product.style = DEFAULT_VALUES["style"]
                changed = True
            if not product.fabric_type:
                product.fabric_type = DEFAULT_VALUES["fabric_type"]
                changed = True
            if not product.pieces:
                product.pieces = DEFAULT_VALUES["pieces"]
                changed = True
            if changed:
                session.add(product)
                updated += 1
        session.commit()
        print(f"Done! Updated {updated} products.")

if __name__ == "__main__":
    fill_empty_fields()
