import os
import tempfile
from datetime import datetime

import fitz       # PyMuPDF
import cohere
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin,
    login_user, login_required, logout_user, current_user
)
from dotenv import load_dotenv

# ─── App & DB setup ────────────────────────────────────────────────────────
load_dotenv()
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret"),
    SQLALCHEMY_DATABASE_URI="sqlite:///db.sqlite3",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    MAX_CONTENT_LENGTH=5 * 1024 * 1024
)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# ─── Models ────────────────────────────────────────────────────────────────
class User(db.Model, UserMixin):
    id       = db.Column(db.Integer, primary_key=True)
    email    = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    reports  = db.relationship("Report", backref="user", lazy=True)

class Report(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    bill      = db.Column(db.Text, nullable=False)
    analysis  = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id   = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ─── Cohere client ──────────────────────────────────────────────────────────
co = cohere.Client(os.getenv("COHERE_API_KEY"))

# ─── Helpers ────────────────────────────────────────────────────────────────
def extract_text(file):
    fn = file.filename.lower()
    if fn.endswith(".pdf"):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file.save(tmp.name)
            doc = fitz.open(tmp.name)
            return "".join(page.get_text() for page in doc)
    if fn.endswith(".txt"):
        return file.read().decode("utf-8")
    return ""

# ─── Routes ─────────────────────────────────────────────────────────────────

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        email = request.form["email"]
        pwd   = request.form["password"]
        if User.query.filter_by(email=email).first():
            flash("Email already registered","error")
        else:
            user = User(email=email,password=pwd)
            db.session.add(user); db.session.commit()
            login_user(user)
            return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and user.password==request.form["password"]:
            login_user(user)
            return redirect(url_for("index"))
        flash("Invalid credentials","error")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
@login_required
def analyze():
    # 1) Gather text
    bill_text = request.form.get("bill","").strip()
    uploaded  = request.files.get("file")
    if uploaded and uploaded.filename:
        bill_text = extract_text(uploaded).strip()
    if not bill_text:
        flash("Please paste or upload a bill.","error")
        return redirect(url_for("index"))

    # 2) Language + compare checkbox
    lang       = request.form.get("language","English")
    do_compare = bool(request.form.get("compare"))
    previous   = None
    if do_compare:
        previous = (Report.query
                    .filter_by(user_id=current_user.id)
                    .order_by(Report.timestamp.desc())
                    .first())

    # 3) Build prompt
    if do_compare and previous:
        prompt = f"""
You are a helpful financial assistant. Respond in {lang}.  
Compare last month’s bill (from {previous.timestamp:%B %Y}) with this month’s.

Last bill text:
{previous.bill}

This bill text:
{bill_text}

Output:
1) Comparison Summary:
   - One sentence comparing totals.
2) Recurring Subscriptions:
   - …
3) Cost-Saving Tips:
   - …
4) Category Breakdown:
   • Essential: $XXX (YY%)
   • Sneaky: $XXX (YY%)
   • Optional: $XXX (YY%)
"""
    else:
        prompt = f"""
You are a helpful financial assistant. Respond in {lang}.  
Analyze this bill and output:

1) Summary:
   - One-sentence overview.
2) Recurring Subscriptions:
   - …
3) Cost-Saving Tips:
   - …
4) Category Breakdown:
   • Essential: $XXX (YY%)
   • Sneaky: $XXX (YY%)
   • Optional: $XXX (YY%)

Bill text:
{bill_text}
"""

    # 4) Call LLM
    response = co.generate(
        model="command-r-plus",
        prompt=prompt,
        max_tokens=600,
        temperature=0.7
    )
    raw = response.generations[0].text.strip()

    # 5) Save and render
    rpt = Report(bill=bill_text, analysis=raw, user_id=current_user.id)
    db.session.add(rpt); db.session.commit()

    return render_template("index.html",
                           result_text=raw,
                           compare=do_compare)


@app.route("/history")
@login_required
def history():
    reports = Report.query \
                    .filter_by(user_id=current_user.id) \
                    .order_by(Report.timestamp.desc()) \
                    .all()
    return render_template("history.html", reports=reports)


if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
