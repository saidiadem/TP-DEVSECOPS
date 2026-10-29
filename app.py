"""Petite application de démonstration du pipeline DevSecOps."""
from flask import Flask, render_template_string, request

app = Flask(__name__)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def index():
    return render_template_string(
        '<!doctype html><html lang="fr"><title>TP DevSecOps</title>'
        '<h1>Bonjour {{ name | safe }}</h1>'
        '<form method="get"><label>Nom <input name="name"></label>'
        '<button>Afficher</button></form></html>',
        name=request.args.get("name", "visiteur"),
    )


@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response
