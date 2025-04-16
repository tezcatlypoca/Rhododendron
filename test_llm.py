import torch_directml
import llama_cpp
import os

# Vérifier que DirectML est disponible
print(f"DirectML disponible: {torch_directml.is_available()}")
if torch_directml.is_available():
    # Obtenir le nombre de devices disponibles
    device_count = torch_directml.device_count()
    print(f"Nombre de devices disponibles: {device_count}")
    
    # Pour chaque device, afficher ses informations
    for i in range(device_count):
        device = torch_directml.device(i)
        print(f"\nDevice {i}:")
        print(f"  Type: {device.type}")
        print(f"  Index: {device.index}")
        print(f"  Nom: {torch_directml.device_name(i)}")

# Vérifier la configuration de llama.cpp
print("\nConfiguration llama.cpp:")
print(f"Version: {llama_cpp.__version__}")
print(f"Support GPU: {'LLAMA_DML' in os.environ}")

# Vérifier les variables d'environnement DirectML
print("\nVariables d'environnement DirectML:")
print(f"LLAMA_DML: {os.environ.get('LLAMA_DML', 'Non défini')}")
print(f"DML_GPU_LAYERS: {os.environ.get('DML_GPU_LAYERS', 'Non défini')}")
print(f"DML_MAIN_GPU: {os.environ.get('DML_MAIN_GPU', 'Non défini')}")