from google.cloud import bigquery
import bcrypt

def hash_existing_passwords():
    client = bigquery.Client()

    # Step 1: Fetch users with unhashed passwords (assumes hash is > 60 chars)
    query = """
    SELECT UserId, Password
    FROM `diegoperez16techx25.Committees.Users`
    WHERE LENGTH(Password) < 60
    """
    results = client.query(query).result()

    updated_count = 0

    for row in results:
        user_id = row.UserId
        plain_pw = row.Password

        # Step 2: Hash password
        hashed_pw = bcrypt.hashpw(plain_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Step 3: Update the user's password
        update_query = f"""
        UPDATE `diegoperez16techx25.Committees.Users`
        SET Password = '{hashed_pw}'
        WHERE UserId = '{user_id}'
        """
        client.query(update_query).result()
        updated_count += 1
        print(f"✅ Hashed password for {user_id}")

    print(f"🔐 Done! {updated_count} user passwords were hashed.")

if __name__ == "__main__":
    hash_existing_passwords()
