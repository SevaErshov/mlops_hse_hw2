# HW2

1. Поместить [teta-ml-1-2025.zip](https://www.kaggle.com/t/1918f3f6435300327d38d6c596f97394) в `data/`. Используется весь `train.csv`
2. Выполнить:

```bash
docker compose up -d --wait
docker compose build app
docker compose run --rm app python scripts/produce.py
docker compose run --rm app python scripts/verify.py
```

3. Проверить `results/max_by_state.csv` и `results/verification.json`
4. Для отдельного выполнения запроса:

```bash
docker compose exec -T clickhouse clickhouse-client --user student --password student < sql/max_by_state.sql
```

5. Для сравнения использовать `sql/max_by_state_baseline.sql`. Базовая DDL: `sql/01_baseline.sql`. Оптимизированная: `sql/02_optimized.sql`
