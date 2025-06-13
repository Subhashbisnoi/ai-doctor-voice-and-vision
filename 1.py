# test_history.py

from database import get_user_history

def main():
    user_id = 1  # Replace this with the actual user_id you want to test
    history = get_user_history(user_id)

    if not history:
        print(f"No consultation history found for user_id: {user_id}")
    else:
        for record in history:
            print(record)

if __name__ == "__main__":
    main()
