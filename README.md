**Set these files in the directory of the docker-compose.yml**

**.env**
```ini
# For development outside docker environment
DB_NAME = demo_db
DB_USER = demo_user
DB_PASSWORD = demo_password
FROM_DOCKER = False
JWT_SECRET_KEY = demo_key
SUPERUSER_PASSWORD = demo_admin
```

-------------------

**docker.env**
```ini
FROM_DOCKER = True
```

-------------------

**db.env**
```ini
POSTGRES_DB = demo_db
POSTGRES_USER = demo_user
POSTGRES_PASSWORD = demo_password
```

-------------------

**server.env**
```ini
DB_NAME = demo_db
DB_USER = demo_user
DB_PASSWORD = demo_password

JWT_SECRET_KEY = demo_key
SUPERUSER_PASSWORD = demo_admin
```

Then just:
```bash
docker compose up --build
```