def test_como_funciona(client):
    response = client.get("/como-funciona")
    assert b"<h2>Publicar tu Auto para Alquilar</h2>" in response.data

    # Verifica que la respuesta sea correcta.
    assert response.status_code == 200
