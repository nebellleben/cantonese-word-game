"""
Quick test script to verify database is working properly.
"""
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.db.base import SessionLocal, engine
from app.db.models import User, Deck, Word, GameSession
from app.core.security import get_password_hash, verify_password
from sqlalchemy import inspect


def test_database_connection():
    """Test basic database connectivity."""
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60)
    
    # Test 1: Check if engine is connected
    print("\n1. Testing database engine connection...")
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
        print("   ✓ Database engine connection successful")
    except Exception as e:
        print(f"   ✗ Database engine connection failed: {e}")
        return False
    
    # Test 2: Check if tables exist
    print("\n2. Checking database tables...")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    expected_tables = ['users', 'decks', 'words', 'game_sessions', 'game_attempts', 
                      'student_teacher_associations', 'user_streaks']
    
    for table in expected_tables:
        if table in tables:
            print(f"   ✓ Table '{table}' exists")
        else:
            print(f"   ✗ Table '{table}' missing")
            return False
    
    # Test 3: Test database session
    print("\n3. Testing database session...")
    db = SessionLocal()
    try:
        # Count users
        user_count = db.query(User).count()
        print(f"   ✓ Database session working (found {user_count} users)")
    except Exception as e:
        print(f"   ✗ Database session failed: {e}")
        return False
    finally:
        db.close()
    
    # Test 4: Test CRUD operations
    print("\n4. Testing CRUD operations...")
    db = SessionLocal()
    try:
        # Create a test deck
        test_deck = Deck(
            name="Test Deck",
            description="Database connectivity test"
        )
        db.add(test_deck)
        db.commit()
        db.refresh(test_deck)
        print(f"   ✓ Created test deck (ID: {test_deck.id})")
        
        # Read it back
        retrieved_deck = db.query(Deck).filter(Deck.id == test_deck.id).first()
        assert retrieved_deck is not None
        assert retrieved_deck.name == "Test Deck"
        print(f"   ✓ Retrieved test deck successfully")
        
        # Update it
        retrieved_deck.description = "Updated description"
        db.commit()
        db.refresh(retrieved_deck)
        assert retrieved_deck.description == "Updated description"
        print(f"   ✓ Updated test deck successfully")
        
        # Delete it
        db.delete(retrieved_deck)
        db.commit()
        deleted_deck = db.query(Deck).filter(Deck.id == test_deck.id).first()
        assert deleted_deck is None
        print(f"   ✓ Deleted test deck successfully")
        
    except Exception as e:
        print(f"   ✗ CRUD operations failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    # Test 5: Check admin user
    print("\n5. Checking admin user...")
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print(f"   ✓ Admin user exists (ID: {admin.id}, Role: {admin.role})")
            # Test password verification
            if verify_password("cantonese", admin.password_hash):
                print("   ✓ Admin password verification works")
            else:
                print("   ⚠ Admin password verification failed (may need to reset)")
        else:
            print("   ⚠ Admin user not found (run init_db.py to create it)")
    except Exception as e:
        print(f"   ✗ Admin user check failed: {e}")
        return False
    finally:
        db.close()
    
    # Test 6: Test foreign key relationships
    print("\n6. Testing foreign key relationships...")
    db = SessionLocal()
    try:
        # Create a deck
        test_deck = Deck(name="Relationship Test Deck")
        db.add(test_deck)
        db.commit()
        db.refresh(test_deck)
        
        # Create a word linked to the deck
        test_word = Word(
            text="測試",
            jyutping="ci3 si3",
            deck_id=test_deck.id
        )
        db.add(test_word)
        db.commit()
        db.refresh(test_word)
        
        # Test relationship
        assert test_word.deck.id == test_deck.id
        assert len(test_deck.words) == 1
        print("   ✓ Foreign key relationships working")
        
        # Cleanup
        db.delete(test_word)
        db.delete(test_deck)
        db.commit()
        
    except Exception as e:
        print(f"   ✗ Foreign key relationships failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    print("\n" + "=" * 60)
    print("✓ All database tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)

