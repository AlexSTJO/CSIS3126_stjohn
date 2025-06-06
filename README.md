# 🐳 Orca: Cloud Data Orchestration
Heavily influences my current project: cli-flow
Orca is a lightweight cloud orchestration tool designed to simplify the execution of data pipelines on AWS infrastructure. It enables users to upload Python tasks, manage execution order, track logs, and automate AWS resource provisioning—all from a simple and extensible interface.

## 🚀 Features

- Upload and organize Python-based tasks  
- Define and manage execution order with an S3-hosted manifest  
- Orchestrate task execution on EC2 via AWS Systems Manager (SSM)  
- Stream live output and logs from your cloud instance  
- Bootstrap environments dynamically with dependency management  
- Secure credential handling via AWS Secrets Manager  
- Integrated with Flask (backend), Vue.js (frontend), and Nginx (deployment)

## 📘 Documentation

Full project documentation, including architecture breakdown, setup instructions, and future roadmap, is available here:

👉 [Orca Notion Documentation](https://voltaic-lunge-eb6.notion.site/Orca-Cloud-Data-Orchestration-171312282f2d80af8208e5875aea11bc)

## 🔧 Tech Stack

- **Frontend**: Vue.js + Nginx  
- **Backend**: Flask + Gunicorn  
- **Cloud Services**: AWS EC2, S3, IAM, SSM, Secrets Manager  
- **Security**: HTTPS via CertBot, firewalld, Fail2Ban  
- **Deployment**: Self-hosted on EC2 (Dockerization and SaaS version planned)

## ⚙️ Local Environment Setup

To run Orca locally, create a `.env` file in your backend directory and populate it with the following variables:

```env
DB_HOST=localhost
DB_NAME=orca
DB_USER=root
DB_PASS=<password>

E_KEY_ID_JWT=
E_KEY_ID_CLOUD=
SECRET_NAME=
E_KEY=<fernet encryption key>
```


## 📌 Next Steps

- Task scheduling with cron-like interface
- In-app log visualization
- Fine-grained IAM permissions validation
- Docker image for easier deployment
- Multi-tenant SaaS platform support

---

Feel free to fork, star, or contribute to the project!
