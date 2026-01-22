# AWS Deployment Guide

## Deployment Options

### Option 1: AWS EC2 Deployment (Recommended for Full Control)

#### Prerequisites
- AWS Account
- AWS CLI installed
- SSH key pair

#### Steps

1. **Launch EC2 Instance**
```bash
# Launch Ubuntu 22.04 instance (t2.medium or higher)
# Configure security groups:
# - Port 22 (SSH)
# - Port 8000 (Backend API)
# - Port 8501 (Streamlit)
```

2. **Connect and Setup**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+
sudo apt install python3.9 python3.9-venv python3-pip -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y
```

3. **Clone and Configure**
```bash
git clone https://github.com/ashwinraiyani/ramayana-sustainability-training.git
cd ramayana-sustainability-training

# Setup
python3 scripts/setup.py

# Configure .env with production credentials
```

4. **Start Services with systemd**

Backend service:
```bash
sudo nano /etc/systemd/system/ramayana-backend.service
```

```ini
[Unit]
Description=Ramayana Sustainability Training Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ramayana-sustainability-training
Environment="PATH=/home/ubuntu/ramayana-sustainability-training/venv/bin"
ExecStart=/home/ubuntu/ramayana-sustainability-training/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

Frontend service:
```bash
sudo nano /etc/systemd/system/ramayana-frontend.service
```

```ini
[Unit]
Description=Ramayana Sustainability Training Frontend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ramayana-sustainability-training
Environment="PATH=/home/ubuntu/ramayana-sustainability-training/venv/bin"
ExecStart=/home/ubuntu/ramayana-sustainability-training/venv/bin/streamlit run frontend/app.py --server.port 8501

[Install]
WantedBy=multi-user.target
```

Start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ramayana-backend
sudo systemctl enable ramayana-frontend
sudo systemctl start ramayana-backend
sudo systemctl start ramayana-frontend
```

### Option 2: AWS RDS + EC2

1. **Create RDS PostgreSQL Instance**
   - Engine: PostgreSQL 15
   - Instance: db.t3.micro (free tier)
   - Enable public access
   - Note endpoint and credentials

2. **Update .env on EC2**
```bash
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_PORT=5432
DB_NAME=ramayana_training
DB_USER=postgres
DB_PASSWORD=your-password
```

### Option 3: Streamlit Cloud (Frontend Only)

1. Push code to GitHub
2. Go to https://streamlit.io/cloud
3. Connect repository
4. Deploy with one click!
5. Set environment variables in Streamlit dashboard

### Option 4: Docker Deployment

```dockerfile
# Dockerfile included in repository
docker build -t ramayana-training .
docker run -p 8000:8000 -p 8501:8501 ramayana-training
```

## Security Best Practices

1. Use SSL/TLS certificates (Let's Encrypt)
2. Enable firewall (ufw)
3. Regular security updates
4. Use strong passwords
5. Enable MFA on AWS

## Monitoring

- CloudWatch for logs
- Set up health check endpoints
- Configure auto-scaling groups

## Backup Strategy

- Daily PostgreSQL backups
- S3 for file storage
- Automated snapshots

## Cost Estimation

- EC2 t2.medium: ~$35/month
- RDS db.t3.micro: ~$15/month
- Total: ~$50/month

---

For production support, contact: admin@ramayana-training.com