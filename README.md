# SecureForum
Secure web app

## Technologie
Django, PostgreSQL, Docker

## Uruchomienie

```bash
git clone https://github.com/rosemint5/secure-forum.git

cd secure-forum

docker compose up --build

docker compose exec web python manage.py migrate
```

## Wirtualne środowisko Pythona

```bash
python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

## Dostęp do bazy danych

```bash
docker compose exec db psql -U forumuser -d secureforum
```