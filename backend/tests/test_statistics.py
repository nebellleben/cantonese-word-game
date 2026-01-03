import pytest
from fastapi.testclient import TestClient


def test_get_statistics(client, student_user):
    """Test getting statistics."""
    token, user = student_user
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/statistics", headers=headers)
    assert response.status_code == 200
    stats = response.json()
    assert "totalGames" in stats
    assert "averageScore" in stats
    assert "bestScore" in stats
    assert "currentStreak" in stats
    assert "longestStreak" in stats
    assert "scoresByDate" in stats
    assert "topWrongWords" in stats


def test_get_students_as_teacher(client, teacher_user):
    """Test getting students as teacher."""
    token, _ = teacher_user
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/students", headers=headers)
    assert response.status_code == 200
    students = response.json()
    assert isinstance(students, list)


def test_get_students_as_student_forbidden(client, student_user):
    """Test that students cannot get students list."""
    token, _ = student_user
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/students", headers=headers)
    assert response.status_code == 403


def test_get_word_error_ratios(client, student_user):
    """Test getting word error ratios."""
    token, _ = student_user
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/words/error-ratios", headers=headers)
    assert response.status_code == 200
    words = response.json()
    assert isinstance(words, list)


