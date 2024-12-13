import sys
import subprocess
import time
import os
import matplotlib.pyplot as plt
import random
from pathlib import Path
from contacts import Contacts

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

def test_performance(size, with_index=False):
    if os.path.exists("contacts.sqlite3"):
        os.remove("contacts.sqlite3")
    
    start = time.time()
    cmd = f"python contacts.py {size}"
    if with_index:
        cmd += " --with-index"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    end = time.time()
    elapsed_ms = (end - start) * 1000
    
    time_limit = TIME_LIMITS.get(size)
    if time_limit and elapsed_ms > time_limit:
        print(f"\n⚠️  ATTENTION: Test pour {size:,} contacts a pris {elapsed_ms:.2f}ms")
        print(f"    Dépasse la limite de {time_limit}ms")
        if result.stderr:
            print(f"    Erreur: {result.stderr}")
        return None
    
    return elapsed_ms

def test_select_performance(size, with_index=False):
    """Test la performance des requêtes SELECT uniquement"""
    if os.path.exists("contacts.sqlite3"):
        os.remove("contacts.sqlite3")
    
    try:
        # Préparation de la base de données
        db = Contacts(Path("contacts.sqlite3"))
        contacts = [(f"name-{i}", f"email-{i}@domain.tld") for i in range(1, size + 1)]
        db.insert_contacts(contacts)
        
        if with_index:
            db.create_email_index()
        
        # Test de 100 requêtes SELECT aléatoires
        total_time = 0
        num_queries = 100
        
        for _ in range(num_queries):
            random_id = random.randint(1, size)
            email = f"email-{random_id}@domain.tld"
            _, query_time = db.get_name_for_email(email)
            total_time += query_time
        
        return total_time / num_queries
    finally:
        # Fermeture de la connexion
        if 'db' in locals():
            db.connection.close()
        time.sleep(0.1)  # Petit délai pour s'assurer que le fichier est libéré

def test_all_performances(size, with_index=False):
    """Test les performances d'insertion et de SELECT sur la même base"""
    max_retries = 3
    retry_delay = 0.5
    
    for attempt in range(max_retries):
        try:
            if os.path.exists("contacts.sqlite3"):
                # Forcer la fermeture de toutes les connexions SQLite
                import gc
                gc.collect()
                time.sleep(retry_delay)
                os.remove("contacts.sqlite3")
            break
        except PermissionError:
            if attempt == max_retries - 1:
                print(f"Impossible de supprimer le fichier après {max_retries} tentatives")
                raise
            time.sleep(retry_delay)
    
    try:
        # Test d'insertion
        start = time.time()
        db = Contacts(Path("contacts.sqlite3"))
        contacts = [(f"name-{i}", f"email-{i}@domain.tld") for i in range(1, size + 1)]
        db.insert_contacts(contacts)
        if with_index:
            db.create_email_index()
        insert_time = (time.time() - start) * 1000

        # Test de 100 requêtes SELECT aléatoires
        total_select_time = 0
        num_queries = 100
        
        for _ in range(num_queries):
            random_id = random.randint(1, size)
            email = f"email-{random_id}@domain.tld"
            _, query_time = db.get_name_for_email(email)
            total_select_time += query_time
        
        select_time = total_select_time / num_queries
        return insert_time, select_time
    finally:
        if 'db' in locals():
            db.connection.close()
            time.sleep(0.1)  # Petit délai avant la prochaine opération

# Tailles à tester
sizes = [10, 100, 1000, 10000, 50000, 100000, 1000000]

# Tests de performance
print("\n=== Tests de performance ===")
print("\nPhase 1: Tests sans index")
print("-" * 50)

insert_without_times = []
insert_with_times = []
select_without_times = []
select_with_times = []

for size in sizes:
    # Test sans index
    insert_time_without, select_time_without = test_all_performances(size, False)
    print(f"\nTaille: {size:,} contacts")
    print(f"  ↳ Insertion: {insert_time_without:.2f} ms")
    print(f"  ↳ SELECT moyen: {select_time_without:.2f} ms")
    
    insert_without_times.append(insert_time_without)
    select_without_times.append(select_time_without)

print("\nPhase 2: Tests avec index")
print("-" * 50)

for size in sizes:
    # Test avec index
    insert_time_with, select_time_with = test_all_performances(size, True)
    improvement = ((select_time_without - select_time_with) / select_time_without) * 100
    
    print(f"\nTaille: {size:,} contacts")
    print(f"  ↳ Insertion: {insert_time_with:.2f} ms")
    print(f"  ↳ SELECT moyen: {select_time_with:.2f} ms")
    print(f"  ↳ Amélioration des SELECT: {improvement:.1f}%")
    
    insert_with_times.append(insert_time_with)
    select_with_times.append(select_time_with)

# Création du graphique comparatif
plt.figure(figsize=(12, 8))

# Tracer les résultats sans index
valid_results_without = [(s, r) for s, r in zip(sizes, insert_without_times) if r is not None]
if valid_results_without:
    sizes_plot, times_plot = zip(*valid_results_without)
    plt.plot(sizes_plot, times_plot, marker='o', linestyle='-', 
             label='Sans index', color='blue', linewidth=2, markersize=8)

# Tracer les résultats avec index
valid_results_with = [(s, r) for s, r in zip(sizes, insert_with_times) if r is not None]
if valid_results_with:
    sizes_plot, times_plot = zip(*valid_results_with)
    plt.plot(sizes_plot, times_plot, marker='s', linestyle='-', 
             label='Avec index', color='green', linewidth=2, markersize=8)

plt.xscale('log')
plt.yscale('log')
plt.xlabel('Nombre de contacts')
plt.ylabel('Temps (ms)')
plt.title('Comparaison des performances avec et sans index')
plt.grid(True)
plt.legend()

# Ajout des limites de temps
for size, limit in TIME_LIMITS.items():
    plt.axhline(y=limit, color='r', linestyle='--', alpha=0.3)
    plt.annotate(f'Limite: {limit}ms', 
                (size, limit),
                textcoords="offset points",
                xytext=(0,10),
                ha='center')

# Création d'un nouveau graphique pour les performances SELECT
plt.figure(figsize=(12, 8))
plt.plot(sizes, select_without_times, marker='o', label='Sans index', color='blue')
plt.plot(sizes, select_with_times, marker='s', label='Avec index', color='green')
plt.xscale('log')
plt.yscale('log')
plt.xlabel('Nombre de contacts')
plt.ylabel('Temps moyen de requête (ms)')
plt.title('Performance des requêtes SELECT avec et sans index')
plt.grid(True)
plt.legend()
plt.savefig('select_performance_comparison.png')
plt.close()

# Création d'un graphique comparatif global
plt.figure(figsize=(12, 8))

# Tracer toutes les courbes
plt.plot(sizes, insert_without_times, marker='o', label='Insertion sans index', color='blue')
plt.plot(sizes, insert_with_times, marker='s', label='Insertion avec index', color='green')
plt.plot(sizes, select_without_times, marker='^', label='SELECT sans index', color='red')
plt.plot(sizes, select_with_times, marker='D', label='SELECT avec index', color='purple')

plt.xscale('log')
plt.yscale('log')
plt.xlabel('Nombre de contacts')
plt.ylabel('Temps (ms)')
plt.title('Comparaison globale des performances')
plt.grid(True)
plt.legend()

# Ajout des limites de temps
for size, limit in TIME_LIMITS.items():
    plt.axhline(y=limit, color='gray', linestyle='--', alpha=0.3)
    plt.annotate(f'Limite: {limit}ms', 
                (size, limit),
                textcoords="offset points",
                xytext=(0,10),
                ha='center')

plt.savefig('global_performance_comparison.png')
plt.close()

plt.savefig('performance_comparison.png')
plt.close()
