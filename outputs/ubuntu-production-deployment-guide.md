# Mawahib Community Platform - Ubuntu Production Deployment Guide

This guide assumes a completely empty Ubuntu server and a domain such as:

```text
mawahib.example.com
```

Replace every example domain, email, and password before deployment.

Official references used:

- Docker Engine Ubuntu installation: https://docs.docker.com/engine/install/ubuntu/
- Docker Compose plugin installation: https://docs.docker.com/compose/install/linux/
- Certbot Nginx instructions: https://certbot.eff.org/instructions?ws=nginx&os=snap

## 1. Server Requirements

Recommended minimum:

- Ubuntu 22.04 LTS or 24.04 LTS
- 2 CPU cores
- 4 GB RAM
- 30 GB disk
- Root or sudo access
- Domain DNS access

Open ports:

- `22` for SSH
- `80` for HTTP and certificate issuance
- `443` for HTTPS

## 2. Initial Server Setup

SSH into the server:

```bash
ssh root@YOUR_SERVER_IP
```

Update packages:

```bash
apt update
apt upgrade -y
```

Install basic tools:

```bash
apt install -y git curl ca-certificates ufw nano openssl nginx snapd
```

Create a deployment user:

```bash
adduser deploy
usermod -aG sudo deploy
```

Log in as the deployment user:

```bash
su - deploy
```

Configure the firewall:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

## 3. Install Docker on Ubuntu

Set up Docker's official apt repository:

```bash
sudo apt update
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

Add the Docker repository:

```bash
sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
```

Install Docker Engine and Docker Compose plugin:

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Start and enable Docker:

```bash
sudo systemctl enable docker
sudo systemctl start docker
sudo systemctl status docker
```

Allow the deploy user to run Docker:

```bash
sudo usermod -aG docker deploy
```

Log out and back in so the group change takes effect:

```bash
exit
ssh deploy@YOUR_SERVER_IP
```

Verify Docker:

```bash
docker run hello-world
docker compose version
```

## 4. Upload or Clone the Project

Create an application directory:

```bash
sudo mkdir -p /opt/mawahib
sudo chown -R deploy:deploy /opt/mawahib
cd /opt/mawahib
```

If using Git:

```bash
git clone YOUR_REPOSITORY_URL .
```

If copying files manually, copy the project into `/opt/mawahib`.

Confirm expected files:

```bash
ls
```

You should see:

```text
backend
frontend
docker-compose.yml
nginx
uploads
.env.example
```

## 5. Configure the `.env` File

Create `.env`:

```bash
cp .env.example .env
nano .env
```

Use strong secrets. Generate values:

```bash
openssl rand -base64 48
```

Example production `.env`:

```env
POSTGRES_DB=mawahib
POSTGRES_USER=mawahib
POSTGRES_PASSWORD=REPLACE_WITH_STRONG_DATABASE_PASSWORD
DATABASE_URL=postgresql+psycopg://mawahib:REPLACE_WITH_STRONG_DATABASE_PASSWORD@db:5432/mawahib

SECRET_KEY=REPLACE_WITH_LONG_RANDOM_SECRET
ACCESS_TOKEN_EXPIRE_MINUTES=1440

CORS_ORIGINS=https://mawahib.example.com
ALLOWED_HOSTS=mawahib.example.com,localhost,127.0.0.1
DOCS_ENABLED=false
ENVIRONMENT=production

MAX_UPLOAD_MB=15
RATE_LIMIT_REQUESTS=180
RATE_LIMIT_WINDOW_SECONDS=60

INITIAL_OWNER_EMAIL=owner@mawahib.example.com
INITIAL_OWNER_PASSWORD=REPLACE_WITH_STRONG_OWNER_PASSWORD
INITIAL_OWNER_NAME=Mawahib Owner

HTTP_PORT=8080
```

Important:

- `POSTGRES_PASSWORD` and the password inside `DATABASE_URL` must match.
- `SECRET_KEY` must be random and private.
- `DOCS_ENABLED=false` is required in production by the backend config.
- `CORS_ORIGINS` must use the final HTTPS domain.
- `ALLOWED_HOSTS` must include the final domain.
- `HTTP_PORT=8080` keeps the Docker app available only to local host Nginx through `127.0.0.1:8080`.

Lock file permissions:

```bash
chmod 600 .env
```

## 6. Start PostgreSQL

PostgreSQL is managed by Docker Compose in this project.

Start only the database:

```bash
docker compose up -d db
```

Check database status:

```bash
docker compose ps
docker compose logs db
```

Verify PostgreSQL health:

```bash
docker compose exec db pg_isready -U mawahib -d mawahib
```

The `postgres_data` Docker volume stores database data persistently.

## 7. Run Docker Compose

Validate the Compose file:

```bash
docker compose config
```

Build and start all services:

```bash
docker compose up -d --build
```

Check containers:

```bash
docker compose ps
```

Watch logs:

```bash
docker compose logs -f
```

Check backend health through the internal Docker Nginx port:

```bash
curl http://127.0.0.1:8080/health
```

Expected response:

```json
{"status":"ok","service":"Mawahib Community Platform"}
```

Backend startup automatically runs:

```bash
alembic upgrade head
```

So the database schema is migrated during deployment.

## 8. Connect a Domain

In your DNS provider, create:

```text
Type: A
Name: mawahib
Value: YOUR_SERVER_IP
TTL: Auto or 300
```

For root domain deployment:

```text
Type: A
Name: @
Value: YOUR_SERVER_IP
```

Optional:

```text
Type: CNAME
Name: www
Value: mawahib.example.com
```

Wait for DNS propagation:

```bash
dig mawahib.example.com
```

The result should show your server IP.

## 9. Configure Host Nginx Reverse Proxy

This project includes an internal Docker Nginx container. For production HTTPS, use host Nginx as the public reverse proxy:

```text
Internet -> Host Nginx HTTPS -> 127.0.0.1:8080 -> Docker Nginx -> frontend/backend
```

Create an Nginx site:

```bash
sudo nano /etc/nginx/sites-available/mawahib
```

Paste:

```nginx
server {
    listen 80;
    server_name mawahib.example.com;

    client_max_body_size 20m;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_redirect off;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/mawahib /etc/nginx/sites-enabled/mawahib
sudo nginx -t
sudo systemctl reload nginx
```

Test HTTP:

```bash
curl -I http://mawahib.example.com
```

## 10. Enable HTTPS with Certbot and Nginx

Install Certbot using snap:

```bash
sudo snap install core
sudo snap refresh core
sudo apt-get remove -y certbot || true
sudo snap install --classic certbot
sudo ln -sf /snap/bin/certbot /usr/local/bin/certbot
```

Issue and install the certificate:

```bash
sudo certbot --nginx -d mawahib.example.com
```

Follow the prompts:

- Enter an admin email.
- Agree to the terms.
- Choose redirect HTTP to HTTPS.

Test renewal:

```bash
sudo certbot renew --dry-run
```

Verify:

```bash
curl -I https://mawahib.example.com
```

Open:

```text
https://mawahib.example.com
```

You should see the login page and a browser lock icon.

## 11. First Login

The first owner account is seeded from `.env`:

```env
INITIAL_OWNER_EMAIL=owner@mawahib.example.com
INITIAL_OWNER_PASSWORD=REPLACE_WITH_STRONG_OWNER_PASSWORD
```

After first successful login:

1. Change the owner password if needed.
2. Create admin users.
3. Create student users.
4. Create teams.
5. Create the first task.
6. Test one student submission.

## 12. Common Operations

Restart the platform:

```bash
docker compose restart
```

Stop the platform:

```bash
docker compose down
```

Update after code changes:

```bash
git pull
docker compose up -d --build
```

View logs:

```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f nginx
docker compose logs -f db
```

Run database migrations manually:

```bash
docker compose exec backend alembic upgrade head
```

Backup:

```bash
sh scripts/backup.sh
```

Restore database from a SQL backup:

```bash
cat backups/mawahib_YYYYMMDD_HHMMSS.sql | docker compose exec -T db psql -U mawahib -d mawahib
```

## 13. Troubleshooting

If `docker compose up` fails because `.env` is missing:

```bash
cp .env.example .env
nano .env
```

If backend exits immediately, inspect logs:

```bash
docker compose logs backend
```

If production config fails:

- Ensure `ENVIRONMENT=production`
- Ensure `DOCS_ENABLED=false`
- Replace default `SECRET_KEY`
- Remove wildcard `*` from `CORS_ORIGINS`
- Remove wildcard `*` from `ALLOWED_HOSTS`

If Nginx cannot connect:

```bash
curl http://127.0.0.1:8080/health
sudo nginx -t
sudo systemctl status nginx
```

If HTTPS issuance fails:

- Confirm DNS points to the server.
- Confirm ports `80` and `443` are open.
- Confirm Nginx site has the correct `server_name`.
- Run:

```bash
sudo certbot --nginx -d mawahib.example.com
```

