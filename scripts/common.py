import csv
import io
import os
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'data/teta-ml-1-2025.zip'


def rows():
    with zipfile.ZipFile(ARCHIVE) as archive:
        with archive.open('train.csv') as source:
            yield from csv.DictReader(io.TextIOWrapper(source, encoding='utf-8-sig'))


def query(sql, query_id=None):
    from urllib.parse import urlencode

    params = {'wait_end_of_query': '1'}
    if query_id:
        params['query_id'] = query_id
    request = Request(
        os.getenv('CLICKHOUSE_URL', 'http://clickhouse:8123') + '/?' + urlencode(params),
        data=sql.encode(),
        headers={
            'X-ClickHouse-User': os.getenv('CLICKHOUSE_USER', 'student'),
            'X-ClickHouse-Key': os.getenv('CLICKHOUSE_PASSWORD', 'student'),
        },
    )
    with urlopen(request, timeout=120) as response:
        return response.read().decode()
