def test_create_and_list_jobs(client):
    payload = {
        "company": "Netflix",
        "title": "ML Engineer",
        "country": "USA",
        "location": "Remote",
        "status": "wishlist",
        "url": "https://example.com",
        "description": "Need Python, ML systems, Docker."
    }

    res = client.post("/jobs", json=payload)
    assert res.status_code == 201
    job = res.json()
    assert job["company"] == "Netflix"
    assert job["status"] == "wishlist"

    res2 = client.get("/jobs")
    assert res2.status_code == 200
    jobs = res2.json()
    assert len(jobs) >= 1


def test_update_status(client):
    res = client.post("/jobs", json={
        "company": "Google",
        "title": "Data Scientist",
        "country": "India",
        "location": "Bangalore",
        "status": "wishlist",
        "url": None,
        "description": "Python, statistics."
    })
    job_id = res.json()["id"]

    res2 = client.patch(f"/jobs/{job_id}/status", params={"status": "applied"})
    assert res2.status_code == 200
    assert res2.json()["status"] == "applied"
