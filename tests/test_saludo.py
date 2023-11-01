def test_saludo(client):
    response = client.get("/")
    assert b"<h2>Rent Agile</h2>" in response.data

    # Verifica que la respuesta sea correcta.
    assert response.status_code == 200
