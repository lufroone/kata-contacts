import sys
import subprocess
import time
import os
import matplotlib.pyplot as plt

# Définition des limites de temps maximales (en ms) pour chaque taille
TIME_LIMITS = {
    10: 100,      # 100ms max pour 10 contacts
    100: 200,     # 200ms max pour 100 contacts
    1000: 500,    # 500ms max pour 1000 contacts
    10000: 1000,  # 1s max pour 10000 contacts
    50000: 3000,  # 3s max pour 50000 contacts
    100000: 5000, # 5s max pour 100000 contacts
    1000000: 30000 # 30s max pour 1000000 contacts
}

def test_performance(size):
    if os.path.exists("contacts.sqlite3"):
        os.remove("contacts.sqlite3")
    
    start = time.time()
    result = subprocess.run(f"python contacts.py {size}", 
                          shell=True, 
                          capture_output=True,
                          text=True)
    end = time.time()
    elapsed_ms = (end - start) * 1000
    
    # Vérification du temps d'exécution
    time_limit = TIME_LIMITS.get(size)
    if time_limit and elapsed_ms > time_limit:
        print(f"\n⚠️  ATTENTION: Test pour {size:,} contacts a pris {elapsed_ms:.2f}ms")
        print(f"    Dépasse la limite de {time_limit}ms")
        if result.stderr:
            print(f"    Erreur: {result.stderr}")
        return None
    
    return elapsed_ms

# Tailles à tester
sizes = [10, 100, 1000, 10000, 50000, 100000, 1000000]

print("\nTests de performance :")
print("| Taille | Temps (ms) | Status |")
print("|---------|------------|--------|")

results_without_index = []
for size in sizes:
    time_ms = test_performance(size)
    if time_ms is not None:
        results_without_index.append(time_ms)
        status = "✅" if time_ms <= TIME_LIMITS[size] else "❌"
        print(f"| {size:,} | {time_ms:.2f} | {status} |")
    else:
        results_without_index.append(TIME_LIMITS[size])
        print(f"| {size:,} | TIMEOUT | ❌ |")

# Création du graphique uniquement pour les tests réussis
valid_results = [(s, r) for s, r in zip(sizes, results_without_index) if r is not None]
if valid_results:
    plt.figure(figsize=(10, 6))
    sizes_plot, times_plot = zip(*valid_results)
    plt.plot(sizes_plot, times_plot, marker='o', linestyle='-', linewidth=2, markersize=8)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Nombre de contacts')
    plt.ylabel('Temps (ms)')
    plt.title('Performance des requêtes')
    plt.grid(True)

    # Ajout des limites de temps sur le graphique
    for size, limit in TIME_LIMITS.items():
        plt.axhline(y=limit, color='r', linestyle='--', alpha=0.3)
        plt.annotate(f'Limite: {limit}ms', 
                    (size, limit),
                    textcoords="offset points",
                    xytext=(0,10),
                    ha='center')

    plt.savefig('performance_results.png')
    plt.close()
