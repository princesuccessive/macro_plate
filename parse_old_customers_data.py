import csv
import json

json_data = list()
with open('./customer_api_logs.csv') as src:
    for line in src.readlines():
        line = line.replace('"{', '{').replace('}"', '}').replace('""', '\"')
        json_data.append(json.loads(line))

with open('./customers.json', 'w') as f:
    json.dump(json_data, f)

with open('./customers.csv', 'w', newline='') as csv_file:
    # Get all headers from all dicts
    headers = list()
    for d in json_data:
        headers += d.keys()
    headers = list(set(headers))

    writer = csv.DictWriter(csv_file, fieldnames=headers)
    writer.writeheader()
    for row in json_data:
        writer.writerow(row)
