def test_home(client):
    response = client.get("/")
    assert b"<title> Bienvendio </title>" in response.data
