import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the OpenVPN management API"}

def test_install_openvpn():
    response = client.post(
        "/install",
        json={
            "ipv4_address": "192.168.1.1",
            "public_ip": "203.0.113.1",
            "protocol": "tcp",
            "port": 1194,
            "dns": 2,
            "client_name": "client1"
        },
        auth=(ADMIN_USERNAME, ADMIN_PASSWORD)
    )
    assert response.status_code == 200

def test_add_client():
    response = client.post(
        "/add-client",
        json={"name": "client1"},
        auth=(ADMIN_USERNAME, ADMIN_PASSWORD)
    )
    assert response.status_code == 200
    assert "Client client1 added successfully" in response.json()["message"]

def test_revoke_client():
    response = client.post(
        "/revoke-client",
        json={"name": "client1"},
        auth=(ADMIN_USERNAME, ADMIN_PASSWORD)
    )
    assert response.status_code == 200
    assert "Client client1 revoked successfully" in response.json()["message"]

def test_remove_openvpn():
    response = client.delete("/remove", auth=(ADMIN_USERNAME, ADMIN_PASSWORD))
    assert response.status_code == 200
    assert "OpenVPN removed successfully" in response.json()["message"]

def test_invalid_credentials():
    response = client.post(
        "/install",
        json={
            "ipv4_address": "192.168.1.1",
            "public_ip": "203.0.113.1",
            "protocol": "tcp",
            "port": 1194,
            "dns": 2,
            "client_name": "client1"
        },
        auth=("invalid", "invalid")
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}

