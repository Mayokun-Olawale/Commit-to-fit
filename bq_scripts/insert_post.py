# Utilized GPT 4o to generate script
from google.cloud import bigquery
from datetime import datetime

client = bigquery.Client()
table_id = "diegoperez16techx25.Committees.Posts"


def get_next_post_id():
    query = f"""
        SELECT MAX(CAST(REGEXP_EXTRACT(PostId, r'post(\\d+)') AS INT64)) AS max_id
        FROM `{table_id}`
        WHERE REGEXP_CONTAINS(PostId, r'^post\\d+$')
    """
    result = client.query(query).result()
    row = next(result)
    return f"post{(row.max_id + 1) if row.max_id else 1}"

def add_post():
    user_id = input("👤 Enter user ID: ")
    image_url = input("🖼️  Enter image URL: ")
    content = input("📝 Enter post content: ")

    post_id = get_next_post_id()
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    query = f"""
        INSERT INTO `{table_id}` (PostId, AuthorId, Timestamp, ImageUrl, Content)
        VALUES (
            '{post_id}',
            '{user_id}',
            DATETIME '{timestamp}',
            '{image_url}',
            '{content.replace("'", "\\'")}'
        )
    """
    client.query(query).result()
    print(f"\n✅ Post '{post_id}' successfully added for user '{user_id}'.")

# Update a post's image
def update_post_image_url():
    post_id = input("🆔 Enter Post ID to update: ")
    new_url = input("🔗 Enter new image URL: ")

    query = f"""
        UPDATE `{table_id}`
        SET ImageUrl = '{new_url}'
        WHERE PostId = '{post_id}'
    """
    client.query(query).result()
    print(f"\n🔄 Image URL updated for '{post_id}'.")

# Main flow
def main():
    print("📬 Welcome to the Post Manager!")
    choice = input("Type 'add' to create a post or 'update' to change an image URL: ").strip().lower()

    if choice == "add":
        add_post()
    elif choice == "update":
        update_post_image_url()
    else:
        print("❗ Invalid choice. Please type 'add' or 'update'.")

if __name__ == "__main__":
    main()
