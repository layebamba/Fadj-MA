# FadjMa

Application full-stack avec Django REST Framework et Next.js

##  Stack Technique

### Backend
- **Django 5.x** - Framework web Python
- **Django REST Framework** - API REST
- **PostgreSQL** - Base de données
- **Python 3.10+**

### Frontend
- **Next.js 14**
- **Node.js 22.x**
- **Tailwind CSS 4.x**
- **TypeScript**

---

##  Prérequis

- **Python 3.10+** : [Télécharger Python](https://www.python.org/downloads/)
- **Node.js 22.x** : [Télécharger Node.js](https://nodejs.org/)
- **PostgreSQL** : [Télécharger PostgreSQL](https://www.postgresql.org/download/)
- **Git** : [Télécharger Git](https://git-scm.com/)

### 1. Cloner le projet

git clone https://github.com/layebamba/Fadj-MA/
cd FadjMa

### 2. Configuration Backend (Django)

# Accéder au dossier backend
cd backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows:
venv\Scripts\activate
# Sur Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement dans .env
# DATABASE_URL=postgresql://user:password@localhost:5432/fadjma_db
# SECRET_KEY=votre-clé-secrète
# DEBUG=True

# Créer la base de données PostgreSQL
# Depuis psql ou pgAdmin,
créez une base de données nommée 'fadjma_db'

# Appliquer les migrations
python manage.py migrate
# Lancer le serveur de développement
python manage.py runserver
Le backend sera accessible sur :
**http://localhost:8000**

### 3. Configuration Frontend (Next.js)
# Ouvrir un nouveau terminal et accéder au dossier frontend
cd frontend
# Installer les dépendances
npm install
# Créer le fichier
.env.local
# Configurer les variables d'environnement dans
.env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Lancer le serveur de développement
npm run dev
Le frontend sera accessible sur : **http://localhost:3000**
### Backend (Django)
# Activer l'environnement virtuel
cd backend
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
# Lancer le serveur
python manage.py runserver

# Créer des migrations
python manage.py makemigrations
# Appliquer les migrations
python manage.py migrate

### Frontend (Next.js)
cd frontend
# Lancer en mode développement
npm run dev
