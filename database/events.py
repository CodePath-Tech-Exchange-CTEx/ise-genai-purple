from google.cloud import bigquery

def create_events_table():
    client = bigquery.Client()

    table_id = "joshua-stevenson-hu.team_purple_dataset.events_table"

    schema = [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("start_date_time", "DATETIME", mode="REQUIRED"),
        bigquery.SchemaField("end_date_time", "DATETIME", mode="REQUIRED"),
    ]

    table = bigquery.Table(table_id, schema=schema)

    table = client.create_table(table, exists_ok=True)

    print(f"Table {table.project}.{table.dataset_id}.{table.table_id} ready.")