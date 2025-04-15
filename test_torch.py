import torch

print("Version de PyTorch :", torch.__version__)
print("GPU disponible :", torch.cuda.is_available())  # Vérifie si un GPU est utilisable
print("Nombre de GPU :", torch.cuda.device_count())  # Affiche le nombre de GPU disponibles

if torch.cuda.is_available():
    for i in range(torch.cuda.device_count()):
        print(f"GPU {i} :", torch.cuda.get_device_name(i))  # Affiche le nom des GPU
else:
    print("Aucun GPU détecté par PyTorch. Vérifie ton installation ROCm.")
