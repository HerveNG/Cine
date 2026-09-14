"""Seed the database with demo data for local testing / pilot users.

This seed creates demo USERS and PROJECTS — real usable accounts/data, not
simulated market data. Funding opportunities (Phase 3) are seeded
separately by scripts/seed_funding_opportunities.py, since those are real
curated funds rather than demo data tied to the demo accounts here.

Run with:
    cd backend && source .venv/bin/activate && python scripts/seed.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.project import Project, ProjectStatus, ProjectType  # noqa: E402
from app.models.user import User, UserType  # noqa: E402

DEMO_USERS = [
    dict(
        email="demo.realisatrice@filmfundafrica.dev",
        password="Demo1234!",
        prenom="Amina",
        nom="Traoré",
        pays="Côte d'Ivoire",
        ville="Abidjan",
        profession="Réalisatrice",
        user_type=UserType.DIRECTOR,
    ),
    dict(
        email="demo.producteur@filmfundafrica.dev",
        password="Demo1234!",
        prenom="Jean-Paul",
        nom="Mbarga",
        pays="Cameroun",
        ville="Douala",
        profession="Producteur",
        user_type=UserType.PRODUCER,
    ),
]

DEMO_PROJECTS = [
    dict(
        title="Les Voix du Fleuve",
        project_type=ProjectType.DOCUMENTARY,
        genre="Social",
        country="Cameroun",
        language="Français",
        duration_minutes=52,
        logline="Un portrait des pêcheurs du Wouri face au changement climatique.",
        status=ProjectStatus.DEVELOPMENT,
    ),
    dict(
        title="Marché de Nuit",
        project_type=ProjectType.SHORT_FILM,
        genre="Fiction",
        country="Côte d'Ivoire",
        language="Français",
        duration_minutes=18,
        logline="Une nuit dans un marché d'Abidjan bouleverse la vie de trois inconnus.",
        status=ProjectStatus.WRITING,
    ),
    dict(
        title="Racines",
        project_type=ProjectType.TV_SERIES,
        genre="Drame",
        country="Cameroun",
        language="Français",
        logline="Trois générations d'une même famille racontées en parallèle.",
        status=ProjectStatus.IDEA,
    ),
]


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        created_users = []
        for data in DEMO_USERS:
            existing = db.query(User).filter(User.email == data["email"]).first()
            if existing:
                created_users.append(existing)
                continue
            user = User(
                email=data["email"],
                hashed_password=hash_password(data["password"]),
                prenom=data["prenom"],
                nom=data["nom"],
                pays=data["pays"],
                ville=data["ville"],
                profession=data["profession"],
                user_type=data["user_type"],
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            created_users.append(user)
            print(f"Created demo user: {user.email} / password: {data['password']}")

        owner = created_users[0]
        for data in DEMO_PROJECTS:
            existing = (
                db.query(Project)
                .filter(Project.title == data["title"], Project.user_id == owner.id)
                .first()
            )
            if existing:
                continue
            project = Project(user_id=owner.id, **data)
            db.add(project)
            db.commit()
            print(f"Created demo project: {project.title} (owner: {owner.email})")

        print("\nSeed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
