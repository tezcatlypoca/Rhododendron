import sqlite3

def check_tables():
    conn = sqlite3.connect('agents.db')
    cursor = conn.cursor()
    
    # Récupérer la liste des tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("Tables présentes dans la base de données :")
    for table in tables:
        print(f"- {table[0]}")
        
        # Afficher la structure de chaque table
        cursor.execute(f"PRAGMA table_info({table[0]});")
        columns = cursor.fetchall()
        print("  Colonnes :")
        for col in columns:
            print(f"    - {col[1]} ({col[2]})")
        print()
    
    conn.close()

if __name__ == "__main__":
    check_tables() 