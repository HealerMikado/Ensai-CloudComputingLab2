#!/bin/bash
echo "=== UserData start ==="

# Met à jour le système et installe Python 3.12 + pip
apt update -y
apt install -y software-properties-common git curl

# Ajoute le PPA officiel pour Python 3.12 (si non présent)
add-apt-repository ppa:deadsnakes/ppa -y
apt update -y
apt install -y python3.12 python3-pip  python3.12-venv

# Clone du dépôt
cd /opt
git clone https://github.com/HealerMikado/Ensai-CloudComputingLab1.git api
cd api

# Création venv
python3.12 -m venv venv

# Installe les dépendances
venv/bin/pip install -r requirements.txt 

# Exécute l’application
# (Si app.py est une API Flask ou FastAPI, on peut la lancer en arrière-plan)
nohup venv/bin/python3.12 app.py > /var/log/app.log 2>&1 &

echo "=== UserData end ==="