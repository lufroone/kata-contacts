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
    subprocess.run(f"python contacts.py {size}", shell=True, check=True)
    end = time.time()
    
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

# Création du graphique
plt.figure(figsize=(10, 6))
plt.plot(sizes, results_without_index, marker='o', linestyle='-', linewidth=2, markersize=8)
plt.xscale('log')  # Échelle logarithmique pour l'axe x
plt.yscale('log')  # Échelle logarithmique pour l'axe y
plt.xlabel('Nombre de contacts')
plt.ylabel('Temps (ms)')
plt.title('Performance des requêtes sans index')
plt.grid(True)

# Ajout des annotations pour chaque point
for i, (size, time) in enumerate(zip(sizes, results_without_index)):
    plt.annotate(f'{time:.0f}ms', 
                (size, time),
                textcoords="offset points",
                xytext=(0,10),
                ha='center')

plt.savefig('performance_sans_index.png')
plt.close()
