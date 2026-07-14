#!/usr/bin/env bash
# Build and (re)run the Drafter backend container on EC2.
# Rerun this after `git pull` to deploy updates.
#
# Prereqs:
#   - ec2-setup.sh has been run (Docker installed, repo cloned)
#   - /home/ec2-user/drafter.env exists with your environment values
#
# Create /home/ec2-user/drafter.env like this (no quotes needed):
#   DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
#   JWT_SECRET=<a long random string>
#   FRONTEND_URL=http://localhost:3000,https://your-frontend-domain
#   ALPHA_EMAILS=you@example.com
#   NVIDIA_API_KEY=nvapi-...            # optional
#   NVIDIA_MODEL=mistralai/mistral-small-4-119b-2603   # optional
#   SEARCH_PROVIDER=tavily              # optional
#   TAVILY_API_KEY=tvly-...             # optional
#   IMAGE_SEARCH_PROVIDER=pexels        # optional
#   PEXELS_API_KEY=...                  # optional
set -euo pipefail

cd /home/ec2-user/Drafter/backend
git -C /home/ec2-user/Drafter pull --ff-only || true

echo "==> Building image"
docker build -t drafter-backend .

echo "==> Restarting container"
docker rm -f drafter-backend 2>/dev/null || true
docker run -d \
  --name drafter-backend \
  --restart unless-stopped \
  --env-file /home/ec2-user/drafter.env \
  -e PORT=8000 \
  -p 80:8000 \
  drafter-backend

echo
echo "Running. The container listens on host port 80 (mapped to app port 8000)."
echo "Test:  curl http://localhost/health"
echo "Public: http://<your-ec2-public-ip>/health"
docker ps --filter name=drafter-backend
