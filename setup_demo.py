"""
Setup script to create admin user and demo deck.
Run this against the production database.
"""
import os
import sys
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import User, Deck, Word
from app.db.base import get_password_hash

# Get database credentials from AWS Secrets Manager
import boto3

def get_db_credentials():
    """Get database credentials from AWS Secrets Manager."""
    client = boto3.client('secretsmanager', region_name='us-east-1')

    # Get the app secret
    app_secret_response = client.get_secret_value(SecretId='cantonese-word-game-secrets')
    app_secret = json.loads(app_secret_response['SecretString'])

    # Get the RDS secret
    rds_secret_response = client.get_secret_value(SecretId='CantoneseWordGameStackPostg-ho5tqD7nznHr')
    rds_secret = json.loads(rds_secret_response['SecretString'])

    return rds_secret['uri']

def setup_admin_and_demo_deck():
    """Create admin user and demo deck."""
    # Get database URL
    database_url = get_db_credentials()

    # Create engine
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Check if admin exists
        admin = db.query(User).filter(User.username == "admin").first()

        if not admin:
            print("Creating admin user...")
            admin = User(
                username="admin",
                password_hash=get_password_hash("cantonese"),
                role="admin"
            )
            db.add(admin)
            db.commit()
            print(f"✅ Admin user created (username: admin, password: cantonese)")
        else:
            print("ℹ️  Admin user already exists")
            # Update password in case it's wrong
            admin.password_hash = get_password_hash("cantonese")
            db.commit()
            print("✅ Admin password reset to 'cantonese'")

        # Refresh to get the admin object with ID
        db.refresh(admin)

        # Check if demo deck exists
        demo_deck = db.query(Deck).filter(Deck.name == "Grade 1 - Basic Words").first()

        if not demo_deck:
            print("\nCreating Grade 1 demo deck...")

            # Create deck
            deck = Deck(
                name="Grade 1 - Basic Words",
                description="Simple Cantonese words for Grade 1 students learning to read and pronounce basic vocabulary."
            )
            db.add(deck)
            db.flush()

            # Add simple, common Cantonese words appropriate for Grade 1
            words_data = [
                # Numbers
                {"text": "一", "jyutping": "jat1"},
                {"text": "二", "jyutping": "ji6"},
                {"text": "三", "jyutping": "saam1"},
                {"text": "四", "jyutping": "sei3"},
                {"text": "五", "jyutping": "ng5"},
                {"text": "六", "jyutping": "luk6"},
                {"text": "七", "jyutping": "cat1"},
                {"text": "八", "jyutping": "baat3"},
                {"text": "九", "jyutping": "gau2"},
                {"text": "十", "jyutping": "sap6"},
                # Family
                {"text": "媽媽", "jyutping": "maa4 maa1"},
                {"text": "爸爸", "jyutping": "baa4 baa1"},
                {"text": "哥哥", "jyutping": "go4 go1"},
                {"text": "姐姐", "jyutping": "ze2 ze2"},
                {"text": "弟弟", "jyutping": "dai6 dai6"},
                {"text": "妹妹", "jyutping": "mui6 mui2"},
                # Basic greetings
                {"text": "你好", "jyutping": "nei5 hou2"},
                {"text": "早晨", "jyutping": "zou2 san4"},
                {"text": "再見", "jyutping": "zoi3 gin3"},
                # Common objects
                {"text": "學校", "jyutping": "hok6 haau6"},
                {"text": "老師", "jyutping": "lou5 si1"},
                {"text": "同學", "jyutping": "tung4 hok6"},
                {"text": "朋友", "jyutping": "pang4 jau5"},
                # Simple verbs
                {"text": "食", "jyutping": "sik6"},
                {"text": "飲", "jyutping": "jam2"},
                {"text": "瞓", "jyutping": "fan3"},
                {"text": "玩", "jyutping": "waan2"},
                {"text": "睇", "jyutping": "tai2"},
                {"text": "聽", "jyutping": "teng1"},
                {"text": "講", "jyutping": "gong2"},
                # Basic adjectives
                {"text": "大", "jyutping": "daai6"},
                {"text": "細", "jyutping": "sai3"},
                {"text": "好", "jyutping": "hou2"},
                {"text": "唔好", "jyutping": "m4 hou2"},
                {"text": "美麗", "jyutping": "mei5 lai6"},
                {"text": "開心", "jyutping": "hoi1 sam1"},
                # Colors
                {"text": "紅色", "jyutping": "hung4 sik1"},
                {"text": "藍色", "jyutping": "lam4 sik1"},
                {"text": "綠色", "jyutping": "luk6 sik1"},
                {"text": "白色", "jyutping": "baak6 sik1"},
                {"text": "黑色", "jyutping": "hak1 sik1"},
                # Animals
                {"text": "貓", "jyutping": "maau1"},
                {"text": "狗", "jyutping": "gau2"},
                {"text": "雞", "jyutping": "gai1"},
                {"text": "鴨", "jyutping": "aap3"},
                {"text": "魚", "jyutping": "jyu4"},
            ]

            for word_data in words_data:
                word = Word(
                    text=word_data["text"],
                    jyutping=word_data["jyutping"],
                    deck_id=deck.id
                )
                db.add(word)

            db.commit()
            print(f"✅ Demo deck '{deck.name}' created with {len(words_data)} words")
        else:
            print(f"ℹ️  Demo deck already exists with {len(demo_deck.words)} words")

        print("\n=== Summary ===")
        print(f"✅ Admin: admin / cantonese")
        print(f"✅ Demo Deck: {db.query(Deck).count()} deck(s), {db.query(Word).count()} word(s)")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
        engine.dispose()

if __name__ == "__main__":
    setup_admin_and_demo_deck()
