
import html
import secrets
import time
from urllib.parse import urlparse

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from dotenv import load_dotenv

from scripts.review import review_code


load_dotenv()

app = FastAPI(title="Code Review")

REPORT_TTL = 900
reports_cache = {}


def save_report(report):
    token = secrets.token_urlsafe(24)
    reports_cache[token] = {
        "report": report,
        "expires": time.time() + REPORT_TTL
    }
    return token


def get_report(token):
    data = reports_cache.get(token)

    if not data:
        return None

    if time.time() > data["expires"]:
        reports_cache.pop(token, None)
        return None

    return data["report"]


def valid_github_url(url):
    parsed = urlparse(url.strip())

    if parsed.hostname not in {"github.com", "www.github.com"}:
        return False

    parts = parsed.path.strip("/").split("/")

    return len(parts) >= 2 and all(parts[:2])


HOME_PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#080b18">

<title>Code Review | Clear feedback for your code</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>

:root {
    --ink: #203247;
    --muted: #64788b;
    --blue: #3978c8;
    --blue-dark: #285f9f;
    --blue-pale: #edf5ff;
    --green: #4d9b78;
    --green-pale: #edf8f1;
    --line: #dce7ee;
    --white: #ffffff;
    --page: #f5f9fb;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
    min-height: 100vh;
    color: var(--ink);
    background: linear-gradient(180deg, #f7fbff 0%, #f3faf6 100%);
    font-family: "DM Sans", Arial, sans-serif;
    overflow-x: hidden;
}
a { color: inherit; text-decoration: none; }
button, input { font: inherit; }
.navbar {
    max-width: 1180px; margin: auto; padding: 20px 26px;
    display: flex; align-items: center; justify-content: space-between; gap: 20px;
}
.brand { display: flex; gap: 11px; align-items: center; font-size: 19px; font-weight: 700; }
.brand-icon {
    width: 42px; height: 42px; display: grid; place-items: center;
    border-radius: 12px; background: var(--blue); box-shadow: 0 5px 14px #3978c833;
}
.brand-icon svg { width: 24px; height: 24px; }
.nav-links { display: flex; align-items: center; gap: 25px; color: var(--muted); font-size: 13px; }
.nav-links a:hover, .footer-links a:hover { color: var(--blue); }
.status {
    border: 1px solid #cce7d7; background: var(--green-pale); color: #367653;
    border-radius: 30px; padding: 8px 13px; font-size: 12px;
}
.status-dot { display: inline-block; width: 7px; height: 7px; margin-right: 7px; border-radius: 50%; background: #58a77d; }
main { max-width: 1160px; margin: auto; padding: 38px 25px 85px; }
.hero { display: grid; grid-template-columns: 1.05fr .95fr; gap: 40px; align-items: center; min-height: 490px; }
.eyebrow {
    display: inline-flex; align-items: center; gap: 9px; border: 1px solid #d5e6f8;
    background: var(--blue-pale); padding: 8px 13px; border-radius: 30px;
    color: var(--blue-dark); font-size: 11px; letter-spacing: .4px; margin-bottom: 22px;
}
.eyebrow span { width: 7px; height: 7px; background: var(--green); border-radius: 50%; }
.hero h1 { font-size: clamp(40px, 5vw, 62px); letter-spacing: -2.5px; line-height: 1.1; max-width: 640px; }
.gradient-text { color: var(--blue); }
.hero-description { max-width: 520px; color: var(--muted); font-size: 15px; line-height: 1.8; margin: 20px 0 25px; }
.trust-row { display: flex; gap: 18px; flex-wrap: wrap; color: #526b7c; font-size: 12px; }
.trust-row span { display: flex; align-items: center; gap: 7px; }
.trust-row svg { width: 15px; color: var(--green); }
.visual { min-height: 360px; position: relative; display: flex; align-items: center; justify-content: center; animation: float 6s ease-in-out infinite; }
.visual-orbit {
    width: 300px; height: 300px; border: 1px solid #c9dfed; border-radius: 50%;
    position: absolute; box-shadow: 0 0 70px #80b5d51c, inset 0 0 45px #80b5d51a;
}
.visual-orbit::before, .visual-orbit::after {
    content: ""; position: absolute; inset: 32px; border: 1px dashed #b8d6e6;
    border-radius: 50%; animation: rotate 24s linear infinite;
}
.visual-orbit::after { inset: 65px; animation-direction: reverse; }
.core-art {
    position: relative; width: 190px; height: 190px; border-radius: 38px;
    display: grid; place-items: center; background: linear-gradient(145deg, #e5f1ff, #e8f7ef);
    border: 1px solid #cbdfea; box-shadow: 0 20px 55px #4b83a51c;
}
.core-art svg { width: 108px; height: 108px; }
.float-card {
    position: absolute; padding: 12px 15px; border: 1px solid var(--line); border-radius: 13px;
    background: #fff; box-shadow: 0 10px 28px #294d6414; font-size: 11px; color: #587083;
}
.float-card strong { display: block; font-size: 15px; margin-top: 4px; }
.card-a { top: 35px; right: 0; animation: bob 5s infinite ease-in-out; }
.card-b { bottom: 35px; left: 0; animation: bob 5s 1s infinite ease-in-out; }
.card-c { bottom: 2px; right: 25px; animation: bob 5s 2s infinite ease-in-out; }
.form-section { max-width: 790px; margin: 30px auto 0; }
.review-card {
    padding: 34px; border: 1px solid #dce8ef; border-radius: 20px;
    background: #fff; box-shadow: 0 18px 55px #315d7612; position: relative;
}
.card-heading { margin-bottom: 24px; }
.card-heading h2 { font-size: 25px; margin-bottom: 7px; }
.card-heading p, .feature p, .step p { color: var(--muted); font-size: 13px; line-height: 1.75; }
.field-label { display: block; margin-bottom: 9px; color: #344e63; font-size: 13px; font-weight: 600; }
.input-wrap { position: relative; }
.input-wrap svg { position: absolute; left: 16px; top: 16px; width: 19px; color: #7891a5; }
.repo-input {
    width: 100%; height: 52px; padding: 0 16px 0 46px; color: var(--ink);
    background: #fbfdff; border: 1px solid #d7e3eb; border-radius: 10px; outline: none; transition: .2s;
}
.repo-input::placeholder { color: #9aabb8; }
.repo-input:focus { border-color: #6c9ed4; box-shadow: 0 0 0 3px #3978c81a; background: #fff; }
.form-group { margin-bottom: 19px; }
.button {
    height: 53px; width: 100%; border: none; border-radius: 10px; cursor: pointer;
    color: #fff; font-size: 14px; font-weight: 700; background: var(--blue);
    box-shadow: 0 7px 18px #3978c82b; transition: .2s;
}
.button:hover { background: var(--blue-dark); transform: translateY(-1px); }
.button:disabled { opacity: .7; cursor: wait; transform: none; }
.form-note { text-align: center; color: #8294a2; font-size: 11px; margin-top: 14px; }
.features { display: grid; grid-template-columns: repeat(3, 1fr); gap: 17px; margin-top: 75px; }
.feature { padding: 23px; border: 1px solid var(--line); border-radius: 15px; background: #fff; transition: .2s; }
.feature:hover { transform: translateY(-4px); border-color: #bdd7e9; }
.feature-icon {
    width: 42px; height: 42px; border-radius: 12px; display: grid; place-items: center;
    background: var(--blue-pale); color: var(--blue); margin-bottom: 16px;
}
.feature-icon svg { width: 21px; }
.feature h3 { font-size: 15px; margin-bottom: 8px; }
.process-section { margin-top: 78px; text-align: center; }
.section-title { font-size: 29px; }
.section-subtitle { color: var(--muted); font-size: 13px; margin-top: 9px; }
.steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin-top: 30px; }
.step { padding: 20px; border: 1px solid var(--line); border-radius: 14px; background: #fff; }
.step-number { font-size: 24px; font-weight: 700; color: var(--green); }
.step h3 { font-size: 14px; margin: 9px 0 7px; }
.loader {
    display: none; margin-top: 20px; padding: 18px; border: 1px solid #dce8ef;
    border-radius: 13px; background: #f7fbff;
}
.loader.active { display: block; animation: appear .3s ease; }
.loader-top { display: flex; align-items: center; gap: 10px; font-size: 13px; color: #344e63; margin-bottom: 10px; }
.loader-message { color: var(--muted); font-size: 12px; }
.loader-spinner {
    width: 16px; height: 16px; border: 2px solid #cfe0ee; border-top-color: var(--blue);
    border-radius: 50%; animation: spin .8s linear infinite;
}
footer { border-top: 1px solid var(--line); padding: 38px 24px 24px; background: #fff; }
.footer-inner { max-width: 1160px; margin: auto; display: flex; justify-content: space-between; gap: 25px; align-items: center; }
.footer-left p { color: var(--muted); font-size: 12px; margin-top: 8px; }
.footer-links { display: flex; flex-wrap: wrap; gap: 20px; color: #526b7c; font-size: 12px; }
.footer-bottom { max-width: 1160px; margin: 25px auto 0; padding-top: 16px; border-top: 1px solid var(--line); color: #8193a1; display: flex; justify-content: space-between; font-size: 11px; }
@keyframes float { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
@keyframes rotate { to { transform: rotate(360deg); } }
@keyframes bob { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
@keyframes appear { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
@keyframes spin { to { transform: rotate(360deg); } }
@media(max-width:850px) {
    .hero { grid-template-columns: 1fr; text-align: center; }
    .hero-description { margin-left: auto; margin-right: auto; }
    .trust-row { justify-content: center; }
    .visual { min-height: 330px; }
    .features { grid-template-columns: 1fr; }
    .nav-links { display: none; }
}
@media(max-width:600px) {
    main { padding: 25px 15px 60px; }
    .navbar { padding: 16px; }
    .hero h1 { letter-spacing: -1.5px; }
    .visual-orbit { width: 255px; height: 255px; }
    .core-art { width: 155px; height: 155px; }
    .core-art svg { width: 85px; }
    .float-card { font-size: 10px; }
    .card-a { right: -3px; }
    .card-b { left: -3px; }
    .review-card { padding: 22px 17px; }
    .steps { grid-template-columns: 1fr; }
    .footer-inner, .footer-bottom { flex-direction: column; align-items: flex-start; }
}
@media(prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important; scroll-behavior: auto !important; transition-duration: .01ms !important; }
}

</style>
</head>

<body>

<nav class="navbar">
    <a class="brand" href="/">
        <div class="brand-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.8">
                <path d="M8 7 3 12l5 5M16 7l5 5-5 5M14 4l-4 16"/>
            </svg>
        </div>
        <span>Code Review</span>
    </a>

    <div class="nav-links">
        <a href="#features">Features</a>
        <a href="#workflow">How it works</a>
        <a href="#review">Start review</a>
    </div>

    <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;justify-content:flex-end">
        <a href="https://github.com/Raj-Rathod-Ai" target="_blank" rel="noopener noreferrer" style="font-size:12px;color:#3978c8;font-weight:700">Made by Raj Rathod ↗</a>
        <div class="status">
            <span class="status-dot"></span> Intelligent Review
        </div>
    </div>
</nav>


<main>

<section class="hero">

    <div>
        <div class="eyebrow">
            <span></span>
            A CLEARER LOOK AT YOUR CODE
        </div>

        <h1>
            Write better code.
            <span class="gradient-text">Ship with confidence.</span>
        </h1>

        <p class="hero-description">
            Review your latest GitHub commits.
            Find bugs, security risks and performance problems.
            Receive a detailed professional code review report
            directly in your inbox.
        </p>

        <div class="trust-row">
            <span>✓ Latest 5 commits</span>
            <span>✓ Clear code feedback</span>
            <span>✓ Email report</span>
        </div>
    </div>

    <div class="visual">
        <div class="visual-orbit"></div>

        <div class="core-art">
            <svg viewBox="0 0 120 120" fill="none">
                <path d="M35 35 13 60l22 25M85 35l22 25-22 25"
                      stroke="#75dfff" stroke-width="7"
                      stroke-linecap="round" stroke-linejoin="round"/>
                <path d="m70 20-20 80"
                      stroke="#b39aff" stroke-width="7"
                      stroke-linecap="round"/>
            </svg>
        </div>

        <div class="float-card card-a">
            Security analysis
            <strong style="color:#4d9b78">Ready</strong>
        </div>

        <div class="float-card card-b">
            Code intelligence
            <strong style="color:#3978c8">Code checks</strong>
        </div>

        <div class="float-card card-c">
            Commit review
            <strong style="color:#4d9b78">Latest 5</strong>
        </div>
    </div>

</section>


<section class="form-section" id="review">
    <div class="review-card">

        <div class="card-heading">
            <h2>Start your code review</h2>
            <p>Connect a public GitHub repository and receive your report.</p>
        </div>

        <form id="reviewForm" action="/review" method="POST">

            <div class="form-group">
                <label class="field-label" for="repo_url">
                    GitHub repository URL
                </label>

                <div class="input-wrap">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                        <circle cx="12" cy="12" r="9"/>
                        <path d="M9 19c0-2 0-3 3-3s3 1 3 3M9 9a3 3 0 1 0 6 0"/>
                    </svg>

                    <input
                        class="repo-input"
                        type="url"
                        id="repo_url"
                        name="repo_url"
                        placeholder="https://github.com/username/repository"
                        required
                    >
                </div>
            </div>

            <div class="form-group">
                <label class="field-label" for="email">
                    Email address
                </label>

                <div class="input-wrap">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                        <rect x="3" y="5" width="18" height="14" rx="3"/>
                        <path d="m4 7 8 6 8-6"/>
                    </svg>

                    <input
                        class="repo-input"
                        type="email"
                        id="email"
                        name="email"
                        placeholder="you@example.com"
                        required
                    >
                </div>
            </div>

            <button class="button" id="reviewButton" type="submit">
                Analyse latest 5 commits →
            </button>

            <p class="form-note">
                Public repositories only · Review findings delivered by email
            </p>

        </form>

        <div class="loader" id="loader">
            <div class="loader-top">
                <strong>Reviewing your changes</strong>
                <span>Usually takes a few minutes</span>
            </div>

            <div class="loader-message" id="loaderMessage">
                We are collecting the latest changes and preparing your report. Please keep this page open.
            </div>
        </div>

    </div>
</section>


<section class="features" id="features">

    <div class="feature">
        <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <path d="M4 5h16v14H4zM8 9h8M8 13h5"/>
            </svg>
        </div>
        <h3>Recent Commit Analysis</h3>
        <p>Focus on the latest five commits rather than scanning the entire repository.</p>
    </div>

    <div class="feature">
        <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <path d="M12 3 4 6v6c0 5 4 8 8 9 4-1 8-4 8-9V6z"/>
                <path d="m9 12 2 2 4-4"/>
            </svg>
        </div>
        <h3>Security & Bug Detection</h3>
        <p>Identify risky changes, potential defects, incorrect logic and performance issues.</p>
    </div>

    <div class="feature">
        <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <rect x="3" y="5" width="18" height="14" rx="3"/>
                <path d="m4 7 8 6 8-6"/>
            </svg>
        </div>
        <h3>Professional Email Reports</h3>
        <p>Receive organised findings with explanations, severity and recommended fixes.</p>
    </div>

</section>


<section class="process-section" id="workflow">
    <h2 class="section-title">How it works</h2>
    <p class="section-subtitle">A focused workflow from GitHub changes to actionable feedback.</p>

    <div class="steps">
        <div class="step">
            <div class="step-number">01</div>
            <h3>Connect repository</h3>
            <p>Submit your public GitHub repository URL and email address.</p>
        </div>

        <div class="step">
            <div class="step-number">02</div>
            <h3>Analyse changes</h3>
            <p>Fetch the last five commits and analyse their changed code.</p>
        </div>

        <div class="step">
            <div class="step-number">03</div>
            <h3>Get your report</h3>
            <p>Receive an organised HTML code review report through email.</p>
        </div>
    </div>
</section>

</main>


<footer>
    <div class="footer-inner">

        <div class="footer-left">
            <a class="brand" href="/">
                <div class="brand-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.8">
                        <path d="M8 7 3 12l5 5M16 7l5 5-5 5M14 4l-4 16"/>
                    </svg>
                </div>
                <span>Code Review</span>
            </a>

            <p>Clear code feedback. Better software.</p>
            <p>Made by <a href="https://github.com/Raj-Rathod-Ai" target="_blank" rel="noopener noreferrer" style="color:#3978c8;font-weight:700">Raj Rathod ↗</a></p>
            <span style="display:inline-flex;align-items:center;gap:7px;margin-top:10px;color:#8294a2;font-size:10px;letter-spacing:1px" aria-label="Creator brand mark"><span style="display:inline-grid;place-items:center;width:22px;height:22px;border-radius:7px;background:linear-gradient(135deg,#3978c8,#4d9b78);color:#fff;font-size:9px;font-weight:800">RR</span> RAJ RATHOD</span>
        </div>

        <div class="footer-links">
            <a href="https://github.com/Raj-Rathod-Ai/" target="_blank" rel="noopener noreferrer">GitHub</a>
            <a href="https://www.linkedin.com/in/raj-rathod-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
            <a href="https://rathodrajai.netlify.app/" target="_blank" rel="noopener noreferrer">Portfolio</a>
        </div>

    </div>

    <div class="footer-bottom">
        <span>© 2026 Code Review. All rights reserved.</span>
        <span>Built for developers.</span>
    </div>
</footer>


<script>
const form = document.getElementById("reviewForm");
const button = document.getElementById("reviewButton");
const loader = document.getElementById("loader");

form.addEventListener("submit", function () {
    button.disabled = true;
    button.textContent = "Reviewing your code...";
    loader.classList.add("active");
});
</script>

</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse(HOME_PAGE)


@app.post("/review")
def review(repo_url: str = Form(...), email: str = Form(...)):
    repo_url = repo_url.strip()
    email = email.strip()

    if not valid_github_url(repo_url):
        return HTMLResponse(
            "<h2>Invalid GitHub repository URL.</h2><a href='/'>Go back</a>",
            status_code=400
        )

    if not email or "@" not in email:
        return HTMLResponse(
            "<h2>Please enter a valid email address.</h2><a href='/'>Go back</a>",
            status_code=400
        )

    report = review_code(repo_url, email)

    token = save_report(report)

    return RedirectResponse(
        url=f"/report/{token}",
        status_code=303
    )


@app.get("/report/{token}", response_class=HTMLResponse)
def view_report(token: str):
    report = get_report(token)

    if not report:
        return HTMLResponse(
            "<h2>Report expired or not found.</h2><a href='/'>Start a new review</a>",
            status_code=404
        )

    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Code Review Report</title>
        <style>
            * {{ box-sizing: border-box; }}
            body {{
                margin: 0;
                padding: 25px;
                background: #f5f9fb;
                color: #203247;
                font-family: Arial, sans-serif;
            }}
            header {{
                max-width: 1200px;
                margin: 0 auto 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 15px;
            }}
            a {{
                color: #3978c8;
                text-decoration: none;
            }}
            iframe {{
                width: 100%;
                max-width: 1200px;
                height: 82vh;
                display: block;
                margin: auto;
                border: 0;
                border-radius: 12px;
                background: white;
                box-shadow: 0 8px 30px rgba(38, 75, 100, .10);
            }}
        </style>
    </head>
    <body>
        <header>
            <h2>Code Review Report</h2>
            <a href="/">← New review</a>
        </header>
        <iframe sandbox="" srcdoc="{html.escape(report, quote=True)}"></iframe>
    </body>
    </html>
    """)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
