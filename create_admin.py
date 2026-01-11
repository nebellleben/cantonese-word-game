#!/usr/bin/env python3
"""Quick script to create admin user and demo deck in the running container."""
import sys
sys.path.insert(0, '/app')

from app.db.base import SessionLocal
from app.db.models import User, Deck, Word

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "cantonese"

def main():
    db = SessionLocal()
    try:
        # Create admin user
        admin = db.query(User).filter(User.username == ADMIN_USERNAME).first()
        if not admin:
            from app.db.base import get_password_hash
            admin = User(
                username=ADMIN_USERNAME,
                password_hash=get_password_hash(ADMIN_PASSWORD),
                role="admin"
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"Created admin user: {ADMIN_USERNAME}")
        else:
            print(f"Admin user already exists: {ADMIN_USERNAME}")
            db.refresh(admin)

        # Create demo deck
        demo_deck = db.query(Deck).filter(Deck.name == "Grade 1 - Basic Words").first()
        if not demo_deck:
            deck = Deck(
                name="Grade 1 - Basic Words",
                description="Simple Cantonese words for Grade 1 students learning basic vocabulary."
            )
            db.add(deck)
            db.flush()

            # Add 50 simple Cantonese words
            words_data = [
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
                {"text": "媽媽", "jyutping": "maa4 maa1"},
                {"text": "爸爸", "jyutping": "baa4 baa1"},
                {"text": "哥哥", "jyutping": "go4 go1"},
                {"text": "姐姐", "jyutping": "ze2 ze2"},
                {"text": "弟弟", "jyutping": "dai6 dai6"},
                {"text": "妹妹", "jyutping": "mui6 mui2"},
                {"text": "你好", "jyutping": "nei5 hou2"},
                {"text": "早晨", "jyutping": "zou2 san4"},
                {"text": "再見", "jyutping": "zoi3 gin3"},
                {"text": "學校", "jyutping": "hok6 haau6"},
                {"text": "老師", "jyutping": "lou5 si1"},
                {"text": "同學", "jyutping": "tung4 hok6"},
                {"text": "朋友", "jyutping": "pang4 jau5"},
                {"text": "食飯", "jyutping": "sik6 faan6"},
                {"text": "飲水", "jyutping": "jam2 seoi2"},
                {"text": "瞓覺", "jyutping": "fan3 gaau3"},
                {"text": "玩耍", "jyutping": "waan2 so2"},
                {"text": "讀書", "jyutping": "duk6 syu1"},
                {"text": "寫字", "jyutping": "se2 zi6"},
                {"text": "大", "jyutping": "daai6"},
                {"text": "細", "jyutping": "sai3"},
                {"text": "多", "jyutping": "do1"},
                {"text": "少", "jyutping": "siu2"},
                {"text": "好", "jyutping": "hou2"},
                {"text": "美麗", "jyutping": "mei5 lai6"},
                {"text": "聰明", "jyutping": "sing1 ming4"},
                {"text": "開心", "jyutping": "hoi1 sam1"},
                {"text": "快樂", "jyutping": "faai3 lok6"},
                {"text": "紅色", "jyutping": "hung4 sik1"},
                {"text": "藍色", "jyutping": "lam4 sik1"},
                {"text": "藍色", "jyutping": "lam4 sik1"},
                {"text": "綠色", "jyutping": "luk6 sik1"},
                {"text": "白色", "jyutping": "baak6 sik1"},
                {"text": "黑色", "jyutping": "hak1 sik1"},
                {"text": "貓", "jyutping": "maau1"},
                {"text": "狗", "jyutping": "gau2"},
                {"text": "雞", "jyutping": "gai1"},
                {"text": "鴨", "jyutping": "aap3"},
                {"text": "牛", "jyutping": "ngau4"},
                {"text": "魚", "jyutping": "jyu4"},
                {"text": "鳥", "jyutping": "niu5"},
                {"text": "花", "jyutping": "faa1"},
                {"text": "草", "jyutping": "chou2"},
                {"text": "樹", "jyutping": "syu6"},
                {"text": "屋企", "jyutping": "uk1 kei2"},
                {"text": "學生", "jyutping": "hok6 sang1"},
                {"text": "書包", "jyutping": "syu1 baau1"},
                {"text": "鉛筆", "jyutping": "aa1 bat1"},
            ]

            for word_data in words_data:
                word = Word(
                    text=word_data["text"],
                    jyutping=word_data["jyutping"],
                    deck_id=deck.id
                )
                db.add(word)

            db.commit()
            print(f"Created deck '{deck.name}' with {len(words_data)} words")
        else:
            print(f"Demo deck already exists")

        # Summary
        user_count = db.query(User).count()
        deck_count = db.query(Deck).count()
        word_count = db.query(Word).count()
        print(f"\n✅ Setup complete!")
        print(f"   Users: {user_count}")
        print(f"   Decks: {deck_count}")
        print(f"   Words: {word_count}")
        print(f"\n🔑 Admin login: admin / cantonese")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
