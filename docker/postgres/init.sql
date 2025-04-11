-- Проверяем существование БД перед созданием
SELECT 'CREATE DATABASE rocket_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'rocket_db')\gexec

-- Подключаемся к БД
\c rocket_db

-- Создаем пользователя (если не существует)
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'rocket_user') THEN
    CREATE USER rocket_user WITH PASSWORD 'rocket_pass';
  END IF;
END
$$;

-- Даем права
GRANT ALL PRIVILEGES ON DATABASE rocket_db TO rocket_user;