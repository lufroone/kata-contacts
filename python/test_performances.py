import sys
import subprocess
import time
import os
import matplotlib.pyplot as plt

def test_performance(size):
    # Supprimer l'ancien fichier sqlite si existe
    if os.path.exists("contacts.sqlite3"):
        os.remove("contacts.sqlite3")
    
    # Exécuter le programme avec différentes tailles
    start = time.time()
    result = subprocess.run(f"python contacts.py {size}", 
                          shell=True, 
                          capture_output=True,
                          text=True)
    end = time.time()
    
    # Afficher uniquement les erreurs si présentes
    if result.returncode != 0:
        print(f"\nErreur pour taille {size}:")
        print(result.stderr)
        
    return (end - start) * 1000  # conversion en millisecondes

# Tailles à tester
sizes = [10, 100, 1000, 10000, 50000, 100000, 1000000]

# Test sans index
print("\nTests sans index :")
print("| Taille | Temps (ms) |")
print("|---------|------------|")

results_without_index = []
for size in sizes:
    time_ms = test_performance(size)
    results_without_index.append(time_ms)
    print(f"| {size:,} | {time_ms:.2f} |")
