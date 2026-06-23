# Mawahib Production Deployment Checklist

## Server

- [ ] Ubuntu server provisioned.
- [ ] SSH access works.
- [ ] System packages updated.
- [ ] `deploy` user created.
- [ ] Firewall enabled.
- [ ] Ports `22`, `80`, and `443` allowed.

## Docker

- [ ] Docker official apt repository added.
- [ ] Docker Engine installed.
- [ ] Docker Compose plugin installed.
- [ ] Docker service enabled and running.
- [ ] `deploy` user added to Docker group.
- [ ] `docker run hello-world` passes.
- [ ] `docker compose version` passes.

## Project

- [ ] Project copied or cloned to `/opt/mawahib`.
- [ ] `.env` created from `.env.example`.
- [ ] Strong `POSTGRES_PASSWORD` configured.
- [ ] `DATABASE_URL` password matches `POSTGRES_PASSWORD`.
- [ ] Strong `SECRET_KEY` configured.
- [ ] `ENVIRONMENT=production`.
- [ ] `DOCS_ENABLED=false`.
- [ ] `CORS_ORIGINS=https://your-domain`.
- [ ] `ALLOWED_HOSTS=your-domain,localhost,127.0.0.1`.
- [ ] `INITIAL_OWNER_EMAIL` configured.
- [ ] Strong `INITIAL_OWNER_PASSWORD` configured.
- [ ] `.env` permissions set to `600`.

## Database

- [ ] `docker compose up -d db` succeeds.
- [ ] `docker compose ps` shows db healthy.
- [ ] `docker compose exec db pg_isready -U mawahib -d mawahib` passes.
- [ ] `postgres_data` volume exists.

## Application

- [ ] `docker compose config` passes.
- [ ] `docker compose up -d --build` succeeds.
- [ ] Backend migrations complete.
- [ ] `docker compose ps` shows all services healthy/running.
- [ ] `curl http://127.0.0.1:8080/health` returns ok.

## Domain

- [ ] DNS `A` record points domain to server IP.
- [ ] `dig your-domain` returns server IP.
- [ ] Host Nginx site created in `/etc/nginx/sites-available/mawahib`.
- [ ] Nginx site enabled.
- [ ] `sudo nginx -t` passes.
- [ ] `curl -I http://your-domain` works.

## HTTPS

- [ ] Certbot installed through snap.
- [ ] `sudo certbot --nginx -d your-domain` succeeds.
- [ ] HTTP redirects to HTTPS.
- [ ] `sudo certbot renew --dry-run` passes.
- [ ] Browser shows lock icon.

## First Functional Test

- [ ] Owner can log in.
- [ ] Admin user can be created.
- [ ] Student user can be created.
- [ ] Team can be created.
- [ ] Student can join team.
- [ ] Task can be created.
- [ ] Student can submit work.
- [ ] Admin/team leader can review submission.
- [ ] Accepted submission awards points.
- [ ] Dashboard and leaderboard update.

## Operations

- [ ] Backup script tested.
- [ ] Restore procedure documented.
- [ ] Logs reviewed after first deployment.
- [ ] Monitoring plan selected.
- [ ] Update procedure tested in staging or maintenance window.

