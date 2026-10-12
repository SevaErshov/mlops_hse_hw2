import csv
import hashlib
import io
import json
import time
import uuid
from decimal import Decimal
from statistics import median

from common import ARCHIVE, ROOT, query, rows


def parsed(text):
    return [(r['us_state'], r['category'], Decimal(r['amount'])) for r in csv.DictReader(io.StringIO(text))]


def main():
    metadata = json.loads((ROOT / 'results/load.json').read_text())
    digest = hashlib.sha256()
    with ARCHIVE.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    if digest.hexdigest() != metadata['archive_sha256']:
        raise RuntimeError('Архив отличается от загруженного')
    winners = {}
    count = 0
    for count, row in enumerate(rows(), 1):
        candidate = (Decimal(row['amount']), count, row['cat_id'])
        state = row['us_state']
        if state not in winners or candidate > winners[state]:
            winners[state] = candidate
    if count != metadata['rows']:
        raise RuntimeError('Число отправленных строк отличается от CSV')
    expected = [(state, value[2], value[0]) for state, value in sorted(winners.items())]
    queries = {name: (ROOT / f'sql/{file}').read_text() for name, file in (
        ('baseline', 'max_by_state_baseline.sql'), ('optimized', 'max_by_state.sql'))}
    deadline = time.monotonic() + 600
    while True:
        counts = {table: int(query(f'SELECT uniqExact(row_id) FROM hw2.{table}')) for table in ('transactions', 'transactions_baseline')}
        outputs = {name: query(sql) for name, sql in queries.items()}
        if all(value == count for value in counts.values()) and all(parsed(value) == expected for value in outputs.values()):
            break
        if time.monotonic() > deadline:
            raise TimeoutError(f'Проверка не пройдена: {counts}, ожидается {count}')
        time.sleep(3)
    (ROOT / 'results/max_by_state.csv').write_text(outputs['optimized'])
    run = uuid.uuid4().hex
    ids = []
    elapsed = {name: [] for name in queries}
    for repetition in range(6):
        for name in queries:
            identifier = f'hw2-{run}-{name}-{repetition}'
            start = time.perf_counter()
            result = query(queries[name], identifier)
            if parsed(result) != expected:
                raise AssertionError(name)
            if repetition:
                elapsed[name].append((time.perf_counter() - start) * 1000)
                ids.append(identifier)
    query('SYSTEM FLUSH LOGS')
    literals = ','.join("'" + value + "'" for value in ids)
    metrics = json.loads(query(f"SELECT query_id, query_duration_ms, read_rows, read_bytes, memory_usage FROM system.query_log WHERE type = 'QueryFinish' AND query_id IN ({literals}) ORDER BY query_id FORMAT JSON"))['data']
    storage = json.loads(query("SELECT table, sum(rows) AS rows, sum(data_compressed_bytes) AS compressed_bytes, sum(data_uncompressed_bytes) AS uncompressed_bytes FROM system.parts WHERE active AND database = 'hw2' GROUP BY table ORDER BY table FORMAT JSON"))['data']
    report = {
        'source_rows': count,
        'states': len(expected),
        'archive_sha256': metadata['archive_sha256'],
        'verified': True,
        'http_median_ms': {name: round(median(values), 3) for name, values in elapsed.items()},
        'query_metrics': metrics,
        'storage': storage,
    }
    (ROOT / 'results/verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
