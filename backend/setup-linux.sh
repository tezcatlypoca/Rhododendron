#!/bin/bash

# Mise à jour du système
echo "Mise à jour du système..."
sudo apt-get update
sudo apt-get upgrade -y

# Installation des dépendances système
echo "Installation des dépendances système..."
sudo apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-venv \
    git \
    wget \
    curl \
    libopenblas-dev \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    gfortran

# Installation des drivers ROCm
echo "Installation des drivers ROCm..."
sudo apt-get install -y \
    rocm-opencl-runtime \
    rocm-opencl-dev \
    rocm-hip-runtime \
    rocm-hip-dev

# Configuration des variables d'environnement
echo "Configuration des variables d'environnement..."
echo 'export PATH=$PATH:/opt/rocm/bin:/opt/rocm/profiler/bin:/opt/rocm/opencl/bin' >> ~/.bashrc
echo 'export HSA_OVERRIDE_GFX_VERSION=9.0.0' >> ~/.bashrc
echo 'export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512' >> ~/.bashrc

# Création de l'environnement virtuel
echo "Création de l'environnement virtuel..."
python3 -m venv venv
source venv/bin/activate

# Installation des dépendances Python
echo "Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements-linux.txt

# Vérification de l'installation
echo "Vérification de l'installation..."
python3 -c "import torch; print('PyTorch version:', torch.__version__); print('ROCm available:', torch.cuda.is_available()); print('Number of GPUs:', torch.cuda.device_count())"

echo "Installation terminée !"
echo "Pour activer l'environnement virtuel, exécutez: source venv/bin/activate" 