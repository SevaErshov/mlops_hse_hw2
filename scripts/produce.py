import hashlib
import json
import os
from datetime import datetime
from decimal import Decimal

from kafka import KafkaProducer

from common import ARCHIVE, ROOT, query, rows


def main():
    marker = ROOT / 'results/load.json'
    if marker.exists() or int(query('SELECT count() FROM hw2.transactions')):
        raise SystemExit('Данные уже загружены. Для повторной загрузки выполните сброс из README.')
    digest = hashlib.sha256()
    with ARCHIVE.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    producer = KafkaProducer(
        bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092'),
        value_serializer=lambda value: json.dumps(value, allow_nan=False).encode(),
        acks='all',
        enable_idempotence=True,
        compression_type='gzip',
        linger_ms=20,
        batch_size=131072,
    )
    pending = []
    count = 0
    try:
        for count, row in enumerate(rows(), 1):
            row['row_id'] = count
            row['transaction_time'] = datetime.strptime(row['transaction_time'], '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M:%S')
            amount = Decimal(row['amount'])
            if not amount.is_finite() or amount != amount.quantize(Decimal('0.01')):
                raise ValueError(f'Некорректная сумма в строке {count}')
            row['amount'] = format(amount, '.2f')
            for field in ('population_city', 'target'):
                row[field] = int(row[field])
            for field in ('lat', 'lon', 'merchant_lat', 'merchant_lon'):
                row[field] = float(row[field])
            pending.append(producer.send('transactions', key=str(count).encode(), value=row))
            if len(pending) == 10000:
                for future in pending:
                    future.get(timeout=120)
                pending.clear()
                print(f'Отправлено: {count}', flush=True)
        for future in pending:
            future.get(timeout=120)
        producer.flush(timeout=120)
    finally:
        producer.close(timeout=120)
    marker.write_text(json.dumps({'rows': count, 'archive_sha256': digest.hexdigest(), 'member': 'train.csv'}, indent=2) + '\n')
    print(f'Kafka подтвердила {count} сообщений')


if __name__ == '__main__':
    main()
