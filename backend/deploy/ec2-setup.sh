#!/usr/bin/env bash
# One-time setup for running the Drafter backend on a fresh Amazon Linux 2023
# EC2 instance (t3.micro / free tier) with Docker.
#
# Usage (on the EC2 box, after SSH-ing in):
#   curl -fsSL <raw-url-of-this-file> -o ec2-setup.sh   # or scp it over
#   bash ec2-setup.sh
#
# Then create /home/ec2-user/drafter.env with your secrets (see ec2-run.sh)
# and run ec2-run.sh.
set -euo pipefail

echo "==> Installing Docker + git"
sudo dnf update -y
sudo dnf install -y docker git
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user

echo "==> Cloning the repo (if not already present)"
cd /home/ec2-user
if [ ! -d Drafter ]; then
  git clone https://github.com/NoiceHax/Drafter.git
fi

echo
echo "Docker installed. Log out and back in (so 'docker' works without sudo),"
echo "then create /home/ec2-user/drafter.env and run ec2-run.sh."
