import json
import boto3
import os
import psycopg2
from passlib.context import CryptContext
from uuid import uuid4

def get_db_connection():
    """Get database connection using AWS Secrets Manager."""
    client = boto3.client('secretsmanager', region_name='us-east-1')

    # Get RDS secret
    response = client.get_secret_value(SecretId='CantoneseWordGameStackPostg-ho5tqD7nznHr')
    secret = json.loads(response['SecretString'])

    # Connect to database
    conn = psycopg2.connect(
        host=secret['host'],
        database=secret['dbname'],
        user=secret['username'],
        password=secret['password'],
        port=secret['port'],
        connect_timeout=10
    )
    return conn

def hash_password(password):
    """Simple password hash."""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

def lambda_handler(event, context):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Create admin user
        admin_id = str(uuid4())
        password_hash = hash_password("cantonese")

        cur.execute("""
            INSERT INTO users (id, username, password_hash, role, created_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (username) DO UPDATE SET password_hash = EXCLUDED.password_hash
            RETURNING id, username
        """, (admin_id, "admin", password_hash, "admin"))

        result = cur.fetchone()

        # Create demo deck
        deck_id = str(uuid4())

        cur.execute("""
            INSERT INTO decks (id, name, description, created_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT DO NOTHING
            RETURNING id
        """, (deck_id, "Grade 1 - Basic Words", "Simple Cantonese words for Grade 1 students"))

        deck_result = cur.fetchone()
        if deck_result:
            # Add words
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

            for text, jyutping in words:
                word_id = str(uuid4())
                cur.execute(
                    "INSERT INTO words (id, text, jyutping, deck_id, created_at) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)",
                    (word_id, text, jyutping, deck_id)
                )

        conn.commit()

        # Get counts
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM decks")
        deck_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM words")
        word_count = cur.fetchone()[0]

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Admin user and demo deck created successfully',
                'admin': result[1],
                'users': user_count,
                'decks': deck_count,
                'words': word_count,
                'login': 'admin / cantonese'
            })
        }

    except Exception as e:
        if conn:
            conn.rollback()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
