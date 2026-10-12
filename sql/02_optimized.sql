CREATE TABLE IF NOT EXISTS hw2.transactions
(
    row_id UInt64 CODEC(Delta, ZSTD(3)),
    transaction_time DateTime('UTC') CODEC(Delta, ZSTD(3)),
    merch LowCardinality(String) CODEC(ZSTD(3)),
    cat_id LowCardinality(String) CODEC(ZSTD(3)),
    amount Decimal(18, 2) CODEC(ZSTD(3)),
    name_1 String CODEC(ZSTD(3)),
    name_2 String CODEC(ZSTD(3)),
    gender LowCardinality(String) CODEC(ZSTD(3)),
    street String CODEC(ZSTD(3)),
    one_city LowCardinality(String) CODEC(ZSTD(3)),
    us_state LowCardinality(String) CODEC(ZSTD(3)),
    post_code String CODEC(ZSTD(3)),
    lat Float64 CODEC(ZSTD(3)),
    lon Float64 CODEC(ZSTD(3)),
    population_city UInt32 CODEC(ZSTD(3)),
    jobs LowCardinality(String) CODEC(ZSTD(3)),
    merchant_lat Float64 CODEC(ZSTD(3)),
    merchant_lon Float64 CODEC(ZSTD(3)),
    target UInt8 CODEC(ZSTD(3))
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(transaction_time)
ORDER BY (us_state, transaction_time, row_id);

CREATE TABLE IF NOT EXISTS hw2.state_max
(
    us_state LowCardinality(String),
    winner AggregateFunction(argMax, Tuple(String, Decimal(18, 2)), Tuple(Decimal(18, 2), UInt64))
)
ENGINE = AggregatingMergeTree
ORDER BY us_state;

CREATE MATERIALIZED VIEW IF NOT EXISTS hw2.state_max_mv TO hw2.state_max AS
SELECT us_state,
       argMaxState(tuple(toString(cat_id), amount), tuple(amount, row_id)) AS winner
FROM hw2.transactions
GROUP BY us_state;

CREATE MATERIALIZED VIEW IF NOT EXISTS hw2.baseline_mv TO hw2.transactions_baseline AS
SELECT * FROM hw2.transactions;

CREATE TABLE IF NOT EXISTS hw2.transactions_kafka
(
    row_id UInt64,
    transaction_time DateTime('UTC'),
    merch String,
    cat_id String,
    amount Decimal(18, 2),
    name_1 String,
    name_2 String,
    gender String,
    street String,
    one_city String,
    us_state String,
    post_code String,
    lat Float64,
    lon Float64,
    population_city UInt32,
    jobs String,
    merchant_lat Float64,
    merchant_lon Float64,
    target UInt8
)
ENGINE = Kafka
SETTINGS kafka_broker_list = 'kafka:9092',
         kafka_topic_list = 'transactions',
         kafka_group_name = 'hw2-clickhouse',
         kafka_format = 'JSONEachRow',
         kafka_num_consumers = 1,
         kafka_max_block_size = 65536,
         kafka_flush_interval_ms = 1000;

CREATE MATERIALIZED VIEW IF NOT EXISTS hw2.kafka_mv TO hw2.transactions AS
SELECT * FROM hw2.transactions_kafka;
