import sys
import sqlite3
from pathlib import Path
from datetime import datetime
import time


class Contacts:
    """Gère les opérations sur la base de données des contacts"""
    
    def __init__(self, db_path):
        """Initialise la connexion à la base de données et crée les tables si nécessaire"""
        self.db_path = db_path
        if not db_path.exists():
            self._initialize_database()
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row

    def _initialize_database(self):
        """Crée la structure initiale de la base de données"""
        print("Initialisation de la base de données...")
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        
        # Création de la table uniquement
        cursor.execute("""
            CREATE TABLE contacts(
              id INTEGER PRIMARY KEY,
              name TEXT NOT NULL,
              email TEXT NOT NULL
            )
        """)
        connection.commit()

    def create_email_index(self):
        """Crée l'index sur l'email après l'insertion des données"""
        print("Vérification/Création de l'index sur l'email...")
        cursor = self.connection.cursor()
        
        # Vérifier si l'index existe déjà
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='index_contacts_email'
        """)
        
        if not cursor.fetchone():
            cursor.execute("""
                CREATE INDEX index_contacts_email 
                ON contacts(email)
            """)
            print("Index créé avec succès")
        else:
            print("L'index existe déjà")
        
        self.connection.commit()

    def insert_contacts(self, contacts):
        """Insère les contacts par lots pour optimiser les performances"""
        print("Insertion des contacts...")
        cursor = self.connection.cursor()
        
        BATCH_SIZE = 1000  # Constante pour la taille du lot
        batch = []
        
        with self.connection:  # Utilisation du context manager pour la transaction
            for contact in contacts:
                batch.append(contact)
                if len(batch) >= BATCH_SIZE:
                    self._insert_batch(cursor, batch)
                    batch = []
            
            # Insertion du dernier lot
            if batch:
                self._insert_batch(cursor, batch)

    def _insert_batch(self, cursor, batch):
        """Insère un lot de contacts"""
        cursor.executemany(
            "INSERT INTO contacts (name, email) VALUES (?, ?)",
            batch
        )

    def get_name_for_email(self, email):
        """Recherche un contact par email et mesure le temps de la requête"""
        print(f"Recherche du contact avec l'email: {email}")
        cursor = self.connection.cursor()
        
        start = time.time()  # Utilisation de time.time() pour plus de précision
        
        cursor.execute(
            "SELECT name FROM contacts WHERE email = ?",
            (email,)
        )
        row = cursor.fetchone()
        
        elapsed = (time.time() - start) * 1000  # Conversion en millisecondes
        print(f"Requête effectuée en {elapsed:.2f} ms")
        
        if row:
            name = row["name"]
            print(f"Contact trouvé: '{name}'")
            return name
        print("Contact non trouvé")
        return None


def yield_contacts(num_contacts):
    """Générateur de contacts pour les tests"""
    for i in range(1, num_contacts + 1):
        yield (f"name-{i}", f"email-{i}@domain.tld")


def main():
    """Point d'entrée principal"""
    if len(sys.argv) != 2:
        print("Usage: python contacts.py <nombre_de_contacts>")
        sys.exit(1)
        
    num_contacts = int(sys.argv[1])
    db_path = Path("contacts.sqlite3")
    contacts = Contacts(db_path)
    contacts.insert_contacts(yield_contacts(num_contacts))
    contacts.create_email_index()
    contacts.get_name_for_email(f"email-{num_contacts}@domain.tld")


if __name__ == "__main__":
    main()
