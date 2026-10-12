CREATE DATABASE IF NOT EXISTS hw2;

CREATE TABLE IF NOT EXISTS hw2.transactions_baseline
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
ENGINE = MergeTree
ORDER BY tuple();
