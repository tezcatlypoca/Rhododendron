import sqlite3
from typing import Optional
from datetime import datetime

from ..models.domain.user import User

class UserRepository:
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialise la base de données et crée la table users si elle n'existe pas"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    roles TEXT,
                    created_at TEXT NOT NULL,
                    last_login TEXT
                )
            """)
            conn.commit()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Récupère un utilisateur par son email"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
                
            return User(
                id=row[0],
                username=row[1],
                email=row[2],
                hashed_password=row[3],
                is_active=bool(row[4]),
                roles=row[5].split(",") if row[5] else [],
                created_at=datetime.fromisoformat(row[6]),
                last_login=datetime.fromisoformat(row[7]) if row[7] else None
            )

    async def save(self, user: User) -> User:
        """Sauvegarde un utilisateur"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO users 
                (id, username, email, hashed_password, is_active, roles, created_at, last_login)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user.id,
                user.username,
                user.email,
                user._hashed_password,
                int(user.is_active),
                ",".join(user.roles),
                user.created_at.isoformat(),
                user.last_login.isoformat() if user.last_login else None
            ))
            conn.commit()
        return user

    async def update_last_login(self, user_id: str) -> None:
        """Met à jour la date de dernière connexion"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.now().isoformat(), user_id)
            )
            conn.commit() 