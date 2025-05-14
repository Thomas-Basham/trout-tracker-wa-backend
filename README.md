# 🐟 Troutlytics Backend

## Description

**Troutlytics** is a data-driven Python application that scrapes and stores trout stocking data for Washington State lakes. It runs on a scheduled AWS Fargate task and stores results in an Aurora PostgreSQL database for use in dashboards, maps, and analysis tools.

---

## 📦 Project Structure

```bash
.
├── api/                   # API backend (Flask/Werkzeug or WSGI-based)
│   ├── main.py            # API entry point
│   ├── wsgi.py            # WSGI server config
│   ├── config.py          # Environment + DB config
│   ├── database.py        # SQLAlchemy or DB layer
│   ├── requirements.txt   # API Python dependencies
│   ├── Dockerfile         # API container
│   ├── Procfile           # For deployment (e.g., Heroku-style)
│   ├── nginx/             # Custom NGINX config (for reverse proxying)
│   └── sqlite.db          # Local dev/test DB
│
├── web_scraper/           # Python scraper + data processing
│   ├── scraper.py         # Main scraper logic
│   ├── lake_names.txt     # List of lakes to scrape
│   ├── backup_data.sql    # Optional dump of scraped data
│   ├── requirements.txt   # Scraper Python dependencies
│   ├── Dockerfile         # Scraper container
│   ├── Procfile           # Optional process spec
│   ├── tests/             # Unit tests for scraper
│   └── google_cloud_billing.py # (Optional utility for GCP cost tracking?)
│
├── docker-compose.yml     # Local orchestration for API + scraper
├── fargate-rds-secrets.yaml     # CloudFormation for scheduled scraper + RDS
├── configure-aws-credentials-latest.yml # GitHub Actions AWS auth config
├── sample.env             # Example environment variables
├── pyproject.toml         # Optional global Python project config
├── vercel.json            # Vercel config (if frontend served there)
├── README.md              # You are here 📘
├── LICENSE
├── CODE_OF_CONDUCT.md
└── CONTRIBUTING.md
```

⸻

🚀 Deployment Overview

AWS Infrastructure:

- Fargate runs the scraper every 24 hours via EventBridge.
- Secrets Manager securely stores DB credentials.
- Aurora PostgreSQL stores structured stocking data.
- CloudWatch Logs tracks runtime output for visibility.

GitHub → ECR Workflow:

- Automatically builds and pushes Docker image on main branch updates.
- Uses secure OIDC GitHub Actions role to push to ECR.

⸻

📋 Prerequisites

- AWS CLI configured with appropriate permissions
- Docker installed (for local dev builds)
- Python 3.11+

⸻

🧪 Run Locally

## 🚀 Docker Compose Commands Cheat Sheet

| Action                           | Command                                      | Notes                                                    |
| :------------------------------- | :------------------------------------------- | :-------------------------------------------------------- |
| **Build all services**           | `docker compose build`                       | Build all images                                          |
| **Start all services**           | `docker compose up`                          | Start API(s), Scraper                                     |
| **Start all + rebuild**          | `docker compose up --build`                  | Force rebuild before starting                             |
| **Start dev API only**           | `docker compose up api-dev`                  | Starts API Dev service                                    |
| **Start prod API only**          | `docker compose up api-prod`                 | Starts API Prod service                                   |
| **Start scraper only**           | `docker compose up web-scraper`              | Starts Scraper                                            |
| **Stop all services**            | `docker compose down`                        | Stops and removes all containers and networks             |
| **Rebuild dev API only**         | `docker compose build api-dev`               | Rebuild only the dev API image                            |
| **Rebuild prod API only**        | `docker compose build api-prod`              | Rebuild only the prod API image                           |
| **Rebuild scraper only**         | `docker compose build web-scraper`           | Rebuild only the scraper image                            |
| **View running containers**      | `docker compose ps`                          | Show status of all services                               |
| **View logs (all services)**     | `docker compose logs`                        | View logs for all services                                |
| **Follow logs live**             | `docker compose logs -f`                     | Stream logs in real time                                  |
| **Stop dev API**                 | `docker compose stop api-dev`                | Stop only the dev API container                           |
| **Stop prod API**                | `docker compose stop api-prod`               | Stop only the prod API container                          |
| **Stop scraper**                 | `docker compose stop web-scraper`            | Stop only the scraper container                           |
| **Restart all containers**       | `docker compose restart`                     | Restart all running services                              |

---

✅ After renaming your config to `docker-compose.yml`, you no longer need `-f` flags!  
✅ `docker compose` (no hyphen) is the new modern standard.

Edit environment variables via sample.env or inject them via Docker secrets.

⸻

🛠️ Cloud Setup

Deploy the CloudFormation Stack:

```bash
aws cloudformation deploy \
 --template-file aws_config/fargate-rds-secrets.yaml \
 --stack-name troutlytics-scraper \
 --capabilities CAPABILITY_NAMED_IAM \
 --parameter-overrides \
 ECRImageUri=<your-ecr-image-uri> \
 VpcId=<your-vpc-id> \
 SubnetIds=subnet-xxxx,subnet-yyyy \
 SecurityGroupId=sg-xxxxxx \
 SecretArn=arn:aws:secretsmanager:us-west-2:xxx:secret:troutlytics-db
```

⸻

🔐 GitHub → ECR Deploy (CI/CD)

To enable GitHub Actions auto-deploy:

1. Deploy the github_oidc_ecr_access.yaml CloudFormation template.
2. Add the output IAM Role ARN to your GitHub Actions secrets or workflows.
3. Push to main — your image builds and publishes to ECR automatically.

⸻

📈 Roadmap Ideas

- Add support for weather/streamflow overlays
- Enable historical trend analysis by lake
- Integrate public stocking alerts
- Expand scraper coverage to other regions or species

⸻

🧠 Credits

Created by @thomas-basham — U.S. Army veteran, full-stack developer, and passionate angler 🎣

⸻

License

MIT
