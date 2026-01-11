"""Create admin user and demo deck

Revision ID: a3f5b8c2d9e1
Revises: 2f3b65c6a7c6
Create Date: 2025-01-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a3f5b8c2d9e1'
down_revision: Union[str, None] = '2f3b65c6a7c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Import password hashing
from passlib.context import CryptContext

def hash_password(password: str) -> str:
    """Hash a password for storage."""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

def upgrade() -> None:
    # Get database connection
    conn = op.get_bind()

    # Create admin user
    admin_id = "00000000-0000-0000-0000-000000000001"
    password_hash = hash_password("cantonese")

    conn.execute(
        sa.text("""
            INSERT INTO users (id, username, password_hash, role, created_at)
            VALUES (:id, :username, :password_hash, :role, CURRENT_TIMESTAMP)
            ON CONFLICT (username) DO UPDATE SET password_hash = EXCLUDED.password_hash
        """),
        {"id": admin_id, "username": "admin", "password_hash": password_hash, "role": "admin"}
    )

    # Create demo deck
    deck_id = "00000000-0000-0000-0000-000000000002"

    conn.execute(
        sa.text("""
            INSERT INTO decks (id, name, description, created_at)
            VALUES (:id, :name, :description, CURRENT_TIMESTAMP)
            ON CONFLICT DO NOTHING
        """),
        {"id": deck_id, "name": "Grade 1 - Basic Words", "description": "Simple Cantonese words for Grade 1 students"}
    )

    # Add words to deck
    words = [
        ("一", "jat1"), ("二", "ji6"), ("三", "saam1"), ("四", "sei3"), ("五", "ng5"),
        ("六", "luk6"), ("七", "cat1"), ("八", "baat3"), ("九", "gau2"), ("十", "sap6"),
        ("媽媽", "maa4 maa1"), ("爸爸", "baa4 baa1"), ("哥哥", "go4 go1"), ("姐姐", "ze2 ze2"),
        ("弟弟", "dai6 dai6"), ("妹妹", "mui6 mui2"), ("你好", "nei5 hou2"), ("早晨", "zou2 san4"),
        ("再見", "zoi3 gin3"), ("學校", "hok6 haau6"), ("老師", "lou5 si1"), ("同學", "tung4 hok6"),
        ("朋友", "pang4 jau5"), ("食飯", "sik6 faan6"), ("飲水", "jam2 seoi2"), ("瞓覺", "fan3 gaau3"),
        ("玩耍", "waan2 so2"), ("讀書", "duk6 syu1"), ("寫字", "se2 zi6"), ("大", "daai6"),
        ("細", "sai3"), ("多", "do1"), ("少", "siu2"), ("好", "hou2"), ("美麗", "mei5 lai6"),
        ("聰明", "sing1 ming4"), ("開心", "hoi1 sam1"), ("快樂", "faai3 lok6"), ("紅色", "hung4 sik1"),
        ("藍色", "lam4 sik1"), ("綠色", "luk6 sik1"), ("白色", "baak6 sik1"), ("黑色", "hak1 sik1"),
        ("貓", "maau1"), ("狗", "gau2"), ("雞", "gai1"), ("鴨", "aap3"), ("牛", "ngau4"),
        ("魚", "jyu4"), ("鳥", "niu5"), ("花", "faa1"), ("草", "chou2"), ("樹", "syu6"),
        ("屋企", "uk1 kei2"), ("學生", "hok6 sang1"), ("書包", "syu1 baau1"), ("鉛筆", "aa1 bat1")
    ]

    for word_text, word_jyutping in words:
        conn.execute(
            sa.text("""
                INSERT INTO words (id, text, jyutping, deck_id, created_at)
                VALUES (gen_random_uuid(), :text, :jyutping, :deck_id, CURRENT_TIMESTAMP)
            """),
            {"text": word_text, "jyutping": word_jyutping, "deck_id": deck_id}
        )

def downgrade() -> None:
    conn = op.get_bind()

    # Delete words from demo deck
    conn.execute(
        sa.text("DELETE FROM words WHERE deck_id = :deck_id"),
        {"deck_id": "00000000-0000-0000-0000-000000000002"}
    )

    # Delete demo deck
    conn.execute(
        sa.text("DELETE FROM decks WHERE id = :deck_id"),
        {"deck_id": "00000000-0000-0000-0000-000000000002"}
    )

    # Delete admin user
    conn.execute(
        sa.text("DELETE FROM users WHERE username = :username"),
        {"username": "admin"}
    )
