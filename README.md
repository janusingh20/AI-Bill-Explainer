# AI Bill Explainer

**Live Demo**: http://18.224.143.33/

A Flask web application using Cohere’s LLM to analyze utility bills and deliver actionable insights, with user authentication, history, and compare functionality.

## Features

- **Bill Input**: Paste your bill text or upload a PDF/TXT file.
- **Compare Bills**: Optional checkbox to compare with your previous month's bill.
- **Multilingual Responses**: Choose from English, Spanish, French, German, or Chinese.
- **User Auth & History**: Secure registration/login; view past analyses.
- **LLM-Powered Analysis**:
  1. **Summary**: One-sentence overview.
  2. **Recurring Subscriptions**: Identify any subscription-style fees.
  3. **Cost‑Saving Tips**: Two actionable recommendations.
  4. **Category Breakdown**: Spending by bucket (Essential, Sneaky, Optional).
- **Container Ready**: Dockerfile included for easy deployment.
- **AWS EC2 Deployment**: Quickly run on an EC2 instance.

## Tech Stack

- **Backend**: Python 3 · Flask · Flask-Login · SQLAlchemy  
- **LLM**: Cohere API 
- **Frontend**: Jinja2 · Tailwind CSS  
- **Database**: SQLite (development)  
- **Container**: Docker  
- **Hosting**: AWS EC2  

---

## Getting Started

### Prerequisites

- Python 3.8+  
- Docker (optional for container run)  
- A Cohere API key  

### Local Development

1. **Clone the repo**  
   ```bash
   git clone https://github.com/<your-username>/ai-bill-explainer.git
   cd ai-bill-explainer
   ```

2. **Create & activate virtualenv**  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate    # macOS/Linux
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**  
   ```bash
   cp .env.example .env
   # then edit .env:
   # COHERE_API_KEY=your_cohere_key
   # SECRET_KEY=your_flask_secret
   ```

5. **Run the app**  
   ```bash
   flask run
   ```
   Open <http://127.0.0.1:5000> in your browser.

### Run with Docker

```bash
docker build -t ai-bill-explainer .
docker run -d \
  --name ai-bill-app \
  -p 80:5000 \
  --env-file .env \
  ai-bill-explainer
```

Visit <http://localhost> (or your server’s IP).

---

## AWS EC2 Deployment (Optional)

Skip if you already have EC2 & Docker configured.

1. **SSH into your EC2 instance**  
   ```bash
   ssh -i ~/path/to/key.pem ec2-user@<EC2_IP>
   cd ~
   ```

2. **Clone repo & configure**  
   ```bash
   git clone https://github.com/<your-username>/ai-bill-explainer.git
   cd ai-bill-explainer
   cat > .env <<EOF
   COHERE_API_KEY=your_cohere_key
   SECRET_KEY=your_flask_secret
   EOF
   ```

3. **Build & run Docker**  
   ```bash
   docker build -t ai-bill-explainer .
   docker run -d \
     --name ai-bill-app \
     -p 80:5000 \
     --env-file .env \
     ai-bill-explainer
   ```

4. **Open port 80** in your Security Group and browse to <http://<EC2_IP>>.

---

## Environment Variables

| Name             | Description                      |
| ---------------- | -------------------------------- |
| `COHERE_API_KEY` | Your Cohere API key for LLM calls|
| `SECRET_KEY`     | Flask session signing key        |

> **Note**: `.env` is in `.gitignore` to protect your secrets.

## Contributing

1. Fork the repo  
2. Create a feature branch  
3. Submit a Pull Request  

---

Enjoy analyzing your bills with AI! 🚀
