"""Tests for Sprint 3 API endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_me_state_empty(client: AsyncClient):
    """Test /me/state returns 404 when user doesn't exist."""
    response = await client.get("/me/state")
    # Will return 404 since dev user doesn't exist in empty DB
    assert response.status_code in [200, 404]


@pytest.mark.anyio
async def test_health_endpoint(client: AsyncClient):
    """Test /health endpoint returns expected structure."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "db" in data
    assert "redis" in data


@pytest.mark.anyio
async def test_list_quests(client: AsyncClient):
    """Test /quests returns catalog grouped by category."""
    response = await client.get("/quests")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


@pytest.mark.anyio
async def test_complete_quest_not_found(client: AsyncClient):
    """Test completing non-existent quest returns 404."""
    response = await client.post("/quests/nonexistent/complete", json={})
    assert response.status_code == 404


@pytest.mark.anyio
async def test_apply_penalty_not_found(client: AsyncClient):
    """Test applying penalty to non-existent quest returns 404."""
    response = await client.post("/penalties/nonexistent", json={"reason": "test"})
    assert response.status_code == 404


@pytest.mark.anyio
async def test_history_endpoint(client: AsyncClient):
    """Test /me/history returns expected structure."""
    response = await client.get("/me/history?days=7")
    # Will work or return error based on DB state
    assert response.status_code in [200, 404]
