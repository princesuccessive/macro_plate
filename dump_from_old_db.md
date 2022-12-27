# Dumping data from Old production DB

## 1. Connect to old DB

Use [these](https://keys.saritasa.com/cred/detail/11418/) credentials

## 2. Get users data

Run `old_users.sql` to get users data, then save results to `csv` file.

## 3. Get customers info sent to production API

1. Run `old_customers.sql`, then save results to `csv` file.
2. Process `csv` with `parse_old_customers_data.py` script to get cleaned results
in `json` and `csv` files.
