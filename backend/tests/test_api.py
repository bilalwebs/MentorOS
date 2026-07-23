"""
tests/test_api.py

Comprehensive integration tests for all MentorOS API endpoints.
Tests authentication, CRUD operations, memory engine, and AI integration.

Run with: python -m pytest tests/ -v
"""

import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Ensure the app module is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class FakeEmbeddingProvider:
    """Deterministic fake embedding for testing — no network calls."""

    def embed(self, texts: list[str]) -> list[list[float]]:
        import hashlib
        results = []
        for text in texts:
            h = hashlib.md5(text.encode()).hexdigest()
            vec = [float(int(h[i:i+2], 16)) / 255.0 for i in range(0, min(len(h), 32), 2)]
            vec += [0.0] * (128 - len(vec))
            results.append(vec[:128])
        return results

    def extract_structured(self, system_prompt: str, user_content: str) -> dict:
        return {
            "full_name": "Test User",
            "target_role": "Backend Developer",
            "skills": [
                {"name": "Python", "level": "advanced"},
                {"name": "FastAPI", "level": "intermediate"},
            ],
            "projects": [
                {"title": "Test Project", "description": "A test project", "tech_stack": ["Python", "FastAPI"]}
            ],
            "certificates": [
                {"title": "AWS Cloud Practitioner", "issuer": "AWS", "date_earned": "2024-01-15"}
            ],
            "summary": "Experienced backend developer",
        }

    def generate(self, system_prompt: str, user_content: str, temperature: float = 0.7) -> str:
        return (
            "## Learning Roadmap\n\n"
            "1. **Month 1**: Master advanced Python patterns\n"
            "2. **Month 2**: Learn cloud deployment on AWS\n"
            "3. **Month 3**: Build a portfolio project combining all skills\n\n"
            "This roadmap builds on your existing Python and FastAPI skills."
        )


@pytest.fixture(scope="session")
def fake_llm():
    return FakeEmbeddingProvider()


@pytest.fixture(scope="session")
def client():
    """Create a test client with SQLite in-memory database."""
    os.environ["DATABASE_URL"] = "sqlite:///./test_mentoros.db"
    os.environ["ENV"] = "development"
    os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
    os.environ["QWEN_API_KEY"] = "fake-key"
    os.environ["VECTOR_BACKEND"] = "chroma"
    os.environ["CHROMA_PERSIST_DIR"] = "./test_chroma_store"
    os.environ["FRONTEND_URL"] = "http://localhost:3000"

    from app.core.config import get_settings
    get_settings.cache_clear()

    from app.db.session import engine, Base, SessionLocal
    from app.db import base as _base

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    from app.main import app
    test_client = TestClient(app)
    yield test_client

    Base.metadata.drop_all(bind=engine)
    import shutil
    if os.path.exists("./test_chroma_store"):
        shutil.rmtree("./test_chroma_store", ignore_errors=True)
    if os.path.exists("./test_mentoros.db"):
        os.remove("./test_mentoros.db")


def register_user(client, email="test@example.com", password="testpass123"):
    return client.post("/auth/register", json={"email": email, "password": password})


def login_user(client, email="test@example.com", password="testpass123"):
    return client.post("/auth/login", json={"email": email, "password": password})


def get_auth_headers(client, email="test@example.com", password="testpass123"):
    register_user(client, email, password)
    resp = login_user(client, email, password)
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ============================================================
# HEALTH & DOCS
# ============================================================

class TestHealthAndDocs:
    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["app"] == "MentorOS"
        assert "database" in data
        assert "vector_backend" in data

    def test_swagger_docs_load(self, client):
        resp = client.get("/docs")
        assert resp.status_code == 200

    def test_openapi_schema(self, client):
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        schema = resp.json()
        assert "paths" in schema
        assert "/auth/register" in schema["paths"]
        assert "/auth/login" in schema["paths"]


# ============================================================
# AUTH
# ============================================================

class TestAuth:
    def test_register_success(self, client):
        resp = register_user(client, "new@example.com")
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "new@example.com"
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client):
        register_user(client, "dup@example.com")
        resp = register_user(client, "dup@example.com")
        assert resp.status_code == 400

    def test_register_short_password(self, client):
        resp = client.post("/auth/register", json={"email": "short@example.com", "password": "123"})
        assert resp.status_code == 422

    def test_login_success(self, client):
        register_user(client, "login@example.com")
        resp = login_user(client, "login@example.com")
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, client):
        register_user(client, "wrong@example.com")
        resp = login_user(client, "wrong@example.com", "wrongpassword")
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = login_user(client, "nonexistent@example.com")
        assert resp.status_code == 401

    def test_auth_me(self, client):
        headers = get_auth_headers(client, "me@example.com")
        resp = client.get("/auth/me", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "me@example.com"

    def test_auth_me_no_token(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code == 403

    def test_auth_refresh(self, client):
        headers = get_auth_headers(client, "refresh@example.com")
        resp = client.post("/auth/refresh", headers=headers)
        assert resp.status_code == 200
        assert "access_token" in resp.json()


# ============================================================
# PROFILE
# ============================================================

class TestProfile:
    def test_get_profile_auto_creates(self, client):
        headers = get_auth_headers(client, "profile@example.com")
        resp = client.get("/profile/me", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["full_name"] == ""

    def test_update_profile(self, client):
        headers = get_auth_headers(client, "update@example.com")
        resp = client.put("/profile/me", headers=headers, json={
            "full_name": "John Doe",
            "target_role": "ML Engineer",
            "bio": "Passionate about AI",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["full_name"] == "John Doe"
        assert data["target_role"] == "ML Engineer"
        assert data["bio"] == "Passionate about AI"


# ============================================================
# SKILLS
# ============================================================

class TestSkills:
    def test_add_skill(self, client):
        headers = get_auth_headers(client, "skills@example.com")
        resp = client.post("/skills", headers=headers, json={"name": "Python", "level": "advanced"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Python"
        assert data["level"] == "advanced"

    def test_list_skills(self, client):
        headers = get_auth_headers(client, "listskills@example.com")
        client.post("/skills", headers=headers, json={"name": "Python", "level": "advanced"})
        client.post("/skills", headers=headers, json={"name": "FastAPI", "level": "intermediate"})
        resp = client.get("/skills", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_delete_skill(self, client):
        headers = get_auth_headers(client, "delskill@example.com")
        create_resp = client.post("/skills", headers=headers, json={"name": "Python", "level": "advanced"})
        skill_id = create_resp.json()["id"]
        resp = client.delete(f"/skills/{skill_id}", headers=headers)
        assert resp.status_code == 204

    def test_delete_nonexistent_skill(self, client):
        headers = get_auth_headers(client, "delnone@example.com")
        resp = client.delete("/skills/99999", headers=headers)
        assert resp.status_code == 404


# ============================================================
# PROJECTS
# ============================================================

class TestProjects:
    def test_add_project(self, client):
        headers = get_auth_headers(client, "projects@example.com")
        resp = client.post("/projects", headers=headers, json={
            "title": "MentorOS",
            "description": "AI mentoring platform",
            "tech_stack": ["Python", "FastAPI", "Next.js"],
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "MentorOS"
        assert isinstance(data["tech_stack"], list)
        assert len(data["tech_stack"]) == 3

    def test_list_projects(self, client):
        headers = get_auth_headers(client, "listproj@example.com")
        client.post("/projects", headers=headers, json={"title": "P1"})
        client.post("/projects", headers=headers, json={"title": "P2"})
        resp = client.get("/projects", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_delete_project(self, client):
        headers = get_auth_headers(client, "delproj@example.com")
        create_resp = client.post("/projects", headers=headers, json={"title": "To Delete"})
        project_id = create_resp.json()["id"]
        resp = client.delete(f"/projects/{project_id}", headers=headers)
        assert resp.status_code == 204


# ============================================================
# CERTIFICATES
# ============================================================

class TestCertificates:
    def test_add_certificate(self, client):
        headers = get_auth_headers(client, "certs@example.com")
        resp = client.post("/certificates", headers=headers, json={
            "title": "AWS Cloud Practitioner",
            "issuer": "Amazon Web Services",
            "date_earned": "2024-01-15",
        })
        assert resp.status_code == 201
        assert resp.json()["title"] == "AWS Cloud Practitioner"

    def test_list_certificates(self, client):
        headers = get_auth_headers(client, "listcerts@example.com")
        client.post("/certificates", headers=headers, json={"title": "C1"})
        resp = client.get("/certificates", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 1


# ============================================================
# CAREER GOALS
# ============================================================

class TestCareerGoals:
    def test_add_career_goal(self, client):
        headers = get_auth_headers(client, "goals@example.com")
        resp = client.post("/career-goals", headers=headers, json={"goal_text": "Become a ML Engineer"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["goal_text"] == "Become a ML Engineer"
        assert data["status"] == "active"

    def test_supersede_career_goal(self, client):
        headers = get_auth_headers(client, "supersede@example.com")
        client.post("/career-goals", headers=headers, json={"goal_text": "Become a Backend Dev"})
        resp = client.post("/career-goals", headers=headers, json={"goal_text": "Become an ML Engineer"})
        assert resp.status_code == 201

        goals_resp = client.get("/career-goals", headers=headers)
        goals = goals_resp.json()
        active = [g for g in goals if g["status"] == "active"]
        superseded = [g for g in goals if g["status"] == "superseded"]
        assert len(active) == 1
        assert len(superseded) == 1
        assert active[0]["goal_text"] == "Become an ML Engineer"
        assert superseded[0]["superseded_by_id"] == active[0]["id"]


# ============================================================
# MEMORY TIMELINE
# ============================================================

class TestMemory:
    def test_memory_timeline_empty(self, client):
        headers = get_auth_headers(client, "memempty@example.com")
        resp = client.get("/memory/timeline", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_memory_after_skill_add(self, client):
        headers = get_auth_headers(client, "memskill@example.com")
        client.post("/skills", headers=headers, json={"name": "Python", "level": "advanced"})
        resp = client.get("/memory/timeline", headers=headers)
        assert resp.status_code == 200
        memories = resp.json()
        assert len(memories) >= 1
        assert any("Python" in m["content_text"] for m in memories)

    def test_memory_delete(self, client):
        headers = get_auth_headers(client, "memdel@example.com")
        client.post("/skills", headers=headers, json={"name": "ToDelete", "level": "beginner"})
        timeline = client.get("/memory/timeline", headers=headers).json()
        mem_id = timeline[0]["id"]
        resp = client.delete(f"/memory/{mem_id}", headers=headers)
        assert resp.status_code == 204

    def test_career_goal_supersession_creates_memory(self, client):
        headers = get_auth_headers(client, "memgoal@example.com")
        client.post("/career-goals", headers=headers, json={"goal_text": "Goal A"})
        client.post("/career-goals", headers=headers, json={"goal_text": "Goal B"})
        resp = client.get("/memory/timeline", headers=headers)
        memories = resp.json()
        goal_memories = [m for m in memories if m["memory_type"] == "career_goal"]
        assert len(goal_memories) >= 2


# ============================================================
# RESUME UPLOAD
# ============================================================

class TestResume:
    def test_upload_text_resume(self, client):
        headers = get_auth_headers(client, "resume@example.com")
        resume_content = """
John Smith
Backend Developer

Skills: Python (5 years), FastAPI (2 years), PostgreSQL (3 years)
Experience:
- Built REST APIs serving 10k+ requests/second
- Designed microservices architecture

Education:
- BS Computer Science, MIT 2020

Certifications:
- AWS Solutions Architect (2023)
"""
        resp = client.post(
            "/resume/upload",
            headers=headers,
            files={"file": ("resume.txt", resume_content.encode(), "text/plain")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "resume_id" in data
        assert "extracted" in data

    def test_upload_unsupported_file(self, client):
        headers = get_auth_headers(client, "resume2@example.com")
        resp = client.post(
            "/resume/upload",
            headers=headers,
            files={"file": ("resume.exe", b"binary content", "application/octet-stream")},
        )
        assert resp.status_code == 400

    def test_list_resumes(self, client):
        headers = get_auth_headers(client, "resumelist@example.com")
        client.post(
            "/resume/upload",
            headers=headers,
            files={"file": ("resume.txt", b"Test resume content", "text/plain")},
        )
        resp = client.get("/resume", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1


# ============================================================
# CORS
# ============================================================

class TestCORS:
    def test_cors_preflight(self, client):
        resp = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.status_code == 200
        assert "access-control-allow-origin" in resp.headers

    def test_cors_vercel_origin(self, client):
        resp = client.options(
            "/health",
            headers={
                "Origin": "https://mentor-os-6h67.vercel.app",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.status_code == 200
        assert "access-control-allow-origin" in resp.headers


# ============================================================
# USER ISOLATION
# ============================================================

class TestUserIsolation:
    def test_users_cannot_see_each_others_data(self, client):
        headers_a = get_auth_headers(client, "userA@example.com")
        headers_b = get_auth_headers(client, "userB@example.com")

        client.post("/skills", headers=headers_a, json={"name": "Python", "level": "advanced"})
        client.post("/skills", headers=headers_b, json={"name": "JavaScript", "level": "beginner"})

        skills_a = client.get("/skills", headers=headers_a).json()
        skills_b = client.get("/skills", headers=headers_b).json()

        assert len(skills_a) == 1
        assert skills_a[0]["name"] == "Python"
        assert len(skills_b) == 1
        assert skills_b[0]["name"] == "JavaScript"
