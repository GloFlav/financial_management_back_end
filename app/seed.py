"""
Lance une seule fois pour initialiser les portefeuilles.
"""
from app.database import SessionLocal, engine
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.database import Base

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(Wallet).count() > 0:
        print("Déjà initialisé.")
        db.close()
        return

    wallets = [
        Wallet(name="Compte bancaire", type="bank",         balance=1_800_000, currency="MGA"),
        Wallet(name="Mvola",           type="mobile_money", balance=10_000,    currency="MGA"),
        Wallet(name="Orange Money",    type="mobile_money", balance=0,         currency="MGA"),
        Wallet(name="Argent liquide",  type="cash",         balance=50_000,    currency="MGA"),
    ]

    db.add_all(wallets)
    db.commit()
    print(f"{len(wallets)} portefeuilles créés.")
    db.close()

if __name__ == "__main__":
    seed()
