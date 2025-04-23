# 🐟 Troutlytics Backend

## Scraper

**Troutlytics** is a data-driven Python application that scrapes and stores trout stocking data for Washington State lakes. It runs on a scheduled AWS Fargate task and stores results in an Aurora PostgreSQL database for use in dashboards, maps, and analysis tools.


---

## 📦 Project Structure

```bash
.
├── web_scraper/           # Main scraping logic
│   ├── scraper.py         # Entry point for scraping
│   ├── requirements.txt   # Python dependencies
│   └── tests/             # Pytest unit tests
├── api/                   # Optional API backend (future expansion)
│   ├── main.py
│   └── Dockerfile
├── Dockerfile             # Base Dockerfile for scraper container
├── scraper.yaml           # Docker Compose config for local development
├── fargate-rds-secrets.yaml # CloudFormation for Fargate + RDS deployment
└── github_oidc_ecr_access.yaml # CloudFormation for GitHub OIDC + ECR deploy access



⸻

🚀 Deployment Overview

AWS Infrastructure:
	•	Fargate runs the scraper every 10 minutes via EventBridge.
	•	Secrets Manager securely stores DB credentials.
	•	Aurora PostgreSQL stores structured stocking data.
	•	CloudWatch Logs tracks runtime output for visibility.

GitHub → ECR Workflow:
	•	Automatically builds and pushes Docker image on main branch updates.
	•	Uses secure OIDC GitHub Actions role to push to ECR.

⸻

📋 Prerequisites
	•	AWS CLI configured with appropriate permissions
	•	Docker installed (for local dev builds)
	•	Python 3.11+

⸻

🧪 Run Locally

docker-compose -f scraper.yaml build
docker-compose -f scraper.yaml up

Edit environment variables via sample.env or inject them via Docker secrets.

⸻

🛠️ Cloud Setup

Deploy the CloudFormation Stack:

aws cloudformation deploy \
  --template-file fargate-rds-secrets.yaml \
  --stack-name troutlytics-scraper \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    ECRImageUri=<your-ecr-image-uri> \
    VpcId=<your-vpc-id> \
    SubnetIds=subnet-xxxx,subnet-yyyy \
    SecurityGroupId=sg-xxxxxx \
    SecretArn=arn:aws:secretsmanager:us-west-2:xxx:secret:troutlytics-db



⸻

🔐 GitHub → ECR Deploy (CI/CD)

To enable GitHub Actions auto-deploy:
	1.	Deploy the github_oidc_ecr_access.yaml CloudFormation template.
	2.	Add the output IAM Role ARN to your GitHub Actions secrets or workflows.
	3.	Push to main — your image builds and publishes to ECR automatically.

⸻

📈 Roadmap Ideas
	•	Add support for weather/streamflow overlays
	•	Enable historical trend analysis by lake
	•	Integrate public stocking alerts
	•	Expand scraper coverage to other regions or species

⸻

🧠 Credits

Created by @thomas-basham — U.S. Army veteran, full-stack developer, and passionate angler 🎣

⸻

License

MIT
```
