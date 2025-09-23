from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Service, Product, Reservable, ReservableService, SchedulePolicy, AvailabilityPolicy
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})
SessionLocal = sessionmaker(bind=engine)

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Servicios
    services = [
        Service(name="Masaje Sueco Anti Estrés"),
        Service(name="Masaje de Pareja"),
        Service(name="Masaje Descontracturante"),
        Service(name="Peeling Quimico")
    ]
    db.add_all(services)
    db.commit()

    # Productos
    products = [
        Product(name="Té verde", price=20.0),
        Product(name="Cafe Americano", price=20.0),
        Product(name="Vainilla", price=40.0)
    ]
    db.add_all(products)
    db.commit()

    # Reservables
    reservables = [
        Reservable(name="Fanny Cervantes"),
        Reservable(name="Paty"),
        Reservable(name="Cosmetologa Sofia")
    ]
    db.add_all(reservables)
    db.commit()

    # Relaciones ReservableService
    fanny = db.query(Reservable).filter_by(name="Fanny Cervantes").first()
    sofia = db.query(Reservable).filter_by(name="Cosmetologa Sofia").first()
    masaje_sueco = db.query(Service).filter_by(name="Masaje Sueco Anti Estrés").first()
    masaje_descontracturante = db.query(Service).filter_by(name="Masaje Descontracturante").first()
    peeling = db.query(Service).filter_by(name="Peeling Quimico").first()

    rs1 = ReservableService(reservable_id=fanny.id, service_id=masaje_sueco.id)
    rs2 = ReservableService(reservable_id=fanny.id, service_id=masaje_descontracturante.id)
    rs3 = ReservableService(reservable_id=sofia.id, service_id=peeling.id)
    db.add_all([rs1, rs2, rs3])
    db.commit()

    # SchedulePolicies (ejemplo para Fanny - Masaje de Pareja)
    masaje_pareja = db.query(Service).filter_by(name="Masaje de Pareja").first()
    sp1 = SchedulePolicy(reservable_id=fanny.id, service_id=masaje_pareja.id, rrule="FREQ=WEEKLY;BYDAY=MO,TU,WE;BYHOUR=9,10,11,12")
    sp2 = SchedulePolicy(reservable_id=fanny.id, service_id=masaje_pareja.id, rrule="FREQ=WEEKLY;BYDAY=FR,SA;BYHOUR=15,16,17,18")
    db.add_all([sp1, sp2])
    db.commit()

    # AvailabilityPolicies (ejemplo para Masaje de Pareja)
    ap1 = AvailabilityPolicy(service_id=masaje_pareja.id, rrule="FREQ=WEEKLY;BYDAY=SU;BYHOUR=9,10,11,12,13,14")
    db.add(ap1)
    db.commit()

    db.close()

if __name__ == "__main__":
    seed()