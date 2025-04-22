FROM python:3.11-slim-bullseye


# Créer un utilisateur non-root
RUN useradd -m appuser

WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt .
COPY . .

# Mettre à jour pip et installer les dépendances
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --progress-bar off -r requirements.txt

# Changer les permissions
RUN chown -R appuser:appuser /app


# Passer à l'utilisateur non-root
USER appuser

# Le conteneur écoutera sur le port 80
EXPOSE 8000

CMD ["sh", "-c","python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
