def test_admin_home(client):
    response = client.get("/")
    assert b"<title> Bienvenido </title>" in response.data

    # Verifica que la respuesta sea correcta.
    assert response.status_code == 200
