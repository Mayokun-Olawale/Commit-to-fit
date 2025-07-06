from google.cloud import bigquery

def backup_users_table():
    client = bigquery.Client()

    source_table = "diegoperez16techx25.Committees.Users"
    backup_table = "diegoperez16techx25.Committees.Users_backup"

    job = client.copy_table(source_table, backup_table)

    job.result()  # Wait for the job to complete

    print("✅ Backup complete: Users → Users_backup")

backup_users_table()
