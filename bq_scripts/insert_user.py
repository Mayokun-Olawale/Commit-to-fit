# Utilized GPT-4o to generate script
from google.cloud import bigquery
from datetime import datetime

client = bigquery.Client()
table_id = "diegoperez16techx25.Committees.Users"


def get_next_user_id():
    query = f"""
        SELECT MAX(CAST(REGEXP_EXTRACT(UserId, r'user(\\d+)') AS INT64)) AS max_id
        FROM `{table_id}`
        WHERE REGEXP_CONTAINS(UserId, r'^user\\d+$')
    """
    result = client.query(query).result()
    row = next(result)
    return f"user{(row.max_id + 1) if row.max_id else 1}"


def add_user():
    name = input("🧑 Enter full name: ")
    username = input("🔠 Enter username: ")
    image_url = input("🖼️  Enter image URL: ")
    date_of_birth = input("📅 Enter date of birth (YYYY-MM-DD): ")
    password = input("🔑 Enter password: ")

    user_id = get_next_user_id()

    query = f"""
        INSERT INTO `{table_id}` (UserId, Name, Username, ImageUrl, DateOfBirth, Password)
        VALUES (
            '{user_id}',
            '{name.replace("'", "\\'")}',
            '{username}',
            '{image_url}',
            DATE '{date_of_birth}',
            '{password}'
        )
    """
    client.query(query).result()
    print(f"\n✅ User '{user_id}' successfully added.")


def update_user_image_url():
    user_id = input("🆔 Enter User ID to update: ")
    new_url = input("🔗 Enter new image URL: ")

    query = f"""
        UPDATE `{table_id}`
        SET ImageUrl = '{new_url}'
        WHERE UserId = '{user_id}'
    """
    client.query(query).result()
    print(f"\n🔄 Image URL updated for user '{user_id}'.")

def update_user_password():
    user_id = input("🆔 Enter User ID to update password: ")
    new_password = input("🔑 Enter new password: ")

    query = f"""
        UPDATE `{table_id}`
        SET Password = '{new_password}'
        WHERE UserId = '{user_id}'
    """
    client.query(query).result()
    print(f"\n🔄 Password updated for user '{user_id}'.")



# Main flow
def main():
    print("👥 Welcome to the User Manager!")
    print("Options: 'add' = create user, 'update' = change image URL, 'passwd' = change password")
    choice = input("Enter choice: ").strip().lower()

    if choice == "add":
        add_user()
    elif choice == "update":
        update_user_image_url()
    elif choice == "passwd":
        update_user_password()
    else:
        print("❗ Invalid choice. Please type 'add', 'update', or 'passwd'.")


if __name__ == "__main__":
    main()
