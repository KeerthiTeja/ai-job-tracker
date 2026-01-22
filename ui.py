import streamlit as st
import requests
import os

API = os.getenv("API","http://127.0.0.1:8001")

st.set_page_config(page_title="AI Job Tracker", layout="wide")
st.title("AI Job Tracker (Global)")

if "base_bullets" not in st.session_state:
    st.session_state["base_bullets"] = ""


with st.sidebar:
    st.header("Filters")
    f_country = st.text_input("Country contains")
    f_company = st.text_input("Company contains")
    f_status = st.selectbox("Status", ["", "wishlist", "applied", "interview", "offer", "rejected"])
    f_q = st.text_input("Search (title/company/location)")
    st.divider()
    st.header("Add Job")

    with st.form("add_job", clear_on_submit=True):
        company = st.text_input("Company*")
        title = st.text_input("Role*")
        country = st.text_input("Country*")
        location = st.text_input("Location*")
        status = st.selectbox("Status*", ["wishlist", "applied", "interview", "offer", "rejected"])
        url = st.text_input("Job URL")
        description = st.text_area("Job Description*", height=120)
        submitted = st.form_submit_button("Add")

        if submitted:
            r = requests.post(f"{API}/jobs", json={
                "company": company,
                "title": title,
                "country": country,
                "location": location,
                "status": status,
                "url": url or None,
                "description": description
            })
            if r.status_code == 201:
                st.success("Added!")
            else:
                st.error(f"Failed: {r.status_code} - {r.text}")

params = {}
if f_country: params["country"] = f_country
if f_company: params["company"] = f_company
if f_status: params["status"] = f_status
if f_q: params["q"] = f_q

jobs = requests.get(f"{API}/jobs", params=params).json()

st.subheader(f"Jobs ({len(jobs)})")

for job in jobs:
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 2, 2])

        with col1:
            st.markdown(f"### {job['company']} — {job['title']}")
            st.caption(f"{job['location']} | {job['country']}")
            if job.get("url"):
                st.write(job["url"])
            with st.expander("Description"):
                st.write(job["description"])
            bullets = st.text_area(
                "Paste resume bullets (one per line)",
                key=f"bullets_{job['id']}",
                height=120,
                value=st.session_state["base_bullets"]
            )

            colA, colB = st.columns([1, 2])
            with colA:
                if st.button("Save as default bullets", key=f"save_default_{job['id']}"):
                    st.session_state["base_bullets"] = bullets
                    st.success("Saved default bullets for this session.")


                if st.button("Tailor for this job", key=f"tailor_job_{job['id']}"):
                    payload = {
                        "resume_bullets": [b.strip() for b in bullets.split("\n") if b.strip()]
                    }
                    r = requests.post(f"{API}/jobs/{job['id']}/tailor", json=payload)

                    if r.status_code != 200:
                        st.error(r.text)
                    else:
                        data = r.json()
                        st.success("Tailored and saved")

                        st.subheader("Tailored Bullets")
                        for b in data["tailored_bullets"]:
                            st.write("•", b)

                        st.caption("Missing skills: " + ", ".join(data["missing_skills"]))

            with st.expander("Tailoring history"):
                r = requests.get(f"{API}/jobs/{job['id']}/tailor-runs")

                if r.status_code == 200:
                    runs = r.json()
                    if not runs:
                        st.info("No tailoring runs yet.")
                    else:
                        for run in runs[:5]:
                            st.write(f"Run #{run['id']} — {run['created_at']}")
                            for b in run["tailored_bullets"]:
                                st.write("•", b)
                            st.caption("Missing skills: " + ", ".join(run["missing_skills"]))
                            st.divider()

        with col2:
            st.write("Status")
            new_status = st.selectbox(
                " ",
                ["wishlist", "applied", "interview", "offer", "rejected"],
                index=["wishlist", "applied", "interview", "offer", "rejected"].index(job["status"]),
                key=f"status_{job['id']}"
            )
            if st.button("Update status", key=f"btn_{job['id']}"):
                r = requests.patch(f"{API}/jobs/{job['id']}/status", params={"status": new_status})
                if r.status_code == 200:
                    st.success("Updated. Refresh the page.")
                else:
                    st.error(r.text)

        with col3:
            st.write("Danger zone")
            if st.button("Delete job", key=f"del_{job['id']}"):
                r = requests.delete(f"{API}/jobs/{job['id']}")
                if r.status_code == 204:
                    st.warning("Deleted. Refresh the page.")
                else:
                    st.error(r.text)
st.divider()
st.header("Resume Tailor (AI-ready)")

resume_text = st.text_area("Paste resume bullets (one per line)", height=140, key="resume_bullets")
jd_text = st.text_area("Paste job description", height=200, key="job_desc")

if st.button("Tailor Resume", key="tailor_resume_btn"):
    payload = {
        "resume_bullets": [b.strip() for b in resume_text.split("\n") if b.strip()],
        "job_description": jd_text.strip(),
    }
    r = requests.post(f"{API}/resume/tailor", json=payload)
    if r.status_code != 200:
        st.error(r.text)
    else:
        data = r.json()
        st.success("Tailored and saved")

    # Show score only when response includes it
        if "score" in data:
            st.metric("Match score", f"{data.get('score', 0)} / 100")

            missing_kw = data.get("missing_keywords", [])
            if missing_kw:
                st.write("**Missing keywords (top):**")
                st.write(", ".join(missing_kw[:20]))

        st.subheader("Tailored Bullets")
        for b in data["tailored_bullets"]:
            st.write("•", b)

        st.subheader("Missing Skills")
        st.write(", ".join(data["missing_skills"]))

        st.subheader("Copy-ready bullets")
        st.code("\n".join([f"• {b}" for b in data["tailored_bullets"]]))
        export_text = "\n".join([f"• {b}" for b in data["tailored_bullets"]])

        st.download_button(
            label="Download tailored bullets (.txt)",
            data=export_text,
            file_name=f"tailored_bullets_job_{job['id']}.txt",
            mime="text/plain",
            key=f"dl_{job['id']}_{data.get('run_id','x')}"
        )

        st.caption("Missing skills: " + ", ".join(data["missing_skills"]))