def test_home(client):
    response = client.get("/info")
    assert b"<p>o quieras poner el tuyo en alquiler.</p>" in response.data

    # Verifica que la respuesta sea correcta.
    assert response.status_code == 200
