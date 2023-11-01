def test_home(client):
    response = client.get("/")
    assert b'<p class="lead">Tu Auto, Tu Aventura</p>' in response.data

    # Verifica que la respuesta sea correcta.
    assert response.status_code == 200
