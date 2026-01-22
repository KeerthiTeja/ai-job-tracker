def test_tailor_for_job_saves_run_and_history(client):
    res = client.post("/jobs", json={
        "company": "Amazon",
        "title": "Backend Engineer",
        "country": "Germany",
        "location": "Berlin",
        "status": "wishlist",
        "url": None,
        "description": "FastAPI, Docker, AWS, CI/CD."
    })
    assert res.status_code == 201
    job_id = res.json()["id"]

    bullets = [
        "Built FastAPI services and deployed with Docker.",
        "Implemented CI pipelines and improved test coverage."
    ]

    res2 = client.post(f"/jobs/{job_id}/tailor", json={"resume_bullets": bullets})
    assert res2.status_code == 200
    data = res2.json()

    assert "run_id" in data
    assert "tailored_bullets" in data
    assert len(data["tailored_bullets"]) == len(bullets)
    assert "missing_skills" in data

    res3 = client.get(f"/jobs/{job_id}/tailor-runs")
    assert res3.status_code == 200
    runs = res3.json()
    assert len(runs) >= 1
