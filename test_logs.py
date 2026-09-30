def register_and_login(client, email):
    client.post("/register", data={"email": email, "password": "pass1234"})
    client.post("/login", data={"email": email, "password": "pass1234"})

def test_add_log_appears_in_list(client):
    register_and_login(client, "c@example.com")
    client.post("/subjects", data={"name": "Python", "color": "#4A90E2"})
    client.post(
        "/logs/new",
        data={"subject_id": 1, "date": "2026-10-01", "hours": 1, "minutes": 30, "memo": "復習"},
    )

    res = client.get("/logs")
    assert "復習".encode() in res.data

def test_other_users_log_is_hidden(client):
    register_and_login(client, "d@example.com")
    client.post("/subjects", data={"name": "英語", "color": "#E24A90"})
    client.post(
        "/logs/new",
        data={"subject_id": 1, "date": "2026-10-01", "hours": 2, "minutes": 0, "memo": "単語"},
    )
    client.post("/logout")

    register_and_login(client, "e@example.com")
    res = client.get("/logs")
    assert "単語".encode() not in res.data
