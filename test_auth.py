def test_register_and_login(client):
    res = client.post(
        "/register",
        data={"email": "a@example.com", "password": "pass1234"},
        follow_redirects=True,
    )
    assert res.status_code == 200

    res = client.post(
        "/login",
        data={"email": "a@example.com", "password": "pass1234"},
        follow_redirects=True,
    )
    assert "ダッシュボード".encode() in res.data

def test_login_with_wrong_password(client):
    client.post(
        "/register",
        data={"email": "b@example.com", "password": "pass1234"},
    )
    res = client.post(
        "/login",
        data={"email": "b@example.com", "password": "wrong"},
        follow_redirects=True,
    )
    assert "メールアドレスまたはパスワードが違います".encode() in res.data

def test_dashboard_requires_login(client):
    res = client.get("/", follow_redirects=True)
    assert "ログイン".encode() in res.data
