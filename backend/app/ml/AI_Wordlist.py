import csv
import os

class AIWordlist:
    def __init__(self, csv_file_path: str):
        """
        Initializes the AIWordlist class with a CSV file path for storing credentials.

        :param csv_file_path: The file path where credentials should be stored.
        """
        self.csv_file_path = csv_file_path
        os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)  # Ensure directory exists

    def save_credentials_to_csv(self, credentials: dict[str, str]) -> None:
        """
        Saves username-password pairs to a CSV file.

        :param credentials: A dictionary containing usernames as keys and passwords as values.
        """
        if not credentials:
            print("[ERROR] No credentials to save.")
            return
        
        with open(self.csv_file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Username", "Password"])
            for username, password in credentials.items():
                writer.writerow([username, password])

        print(f"Credentials saved to {self.csv_file_path}")

    def display_credentials(self, credentials: dict[str, str]) -> None:
        """
        Displays stored credentials in a readable format.

        :param credentials: A dictionary containing usernames as keys and passwords as values.
        """
        if not credentials:
            print("[ERROR] No credentials to display.")
            return 
        
        print("\n---------- Stored Credentials ----------")
        for username, password in credentials.items():
            print(f"Username: {username} | Password: {password}")
        print("----------------------------------------\n")


def main():
    """
    Main function to test AIWordlist class.
    """
    csv_path = "/Users/anthonytrancoso/Desktop/Trace/stored_credentials.csv"
    
    # Create AIWordlist instance
    wordlist_manager = AIWordlist(csv_path)

    # Define credentials
    credentials = {
        "admin": "secure123",
        "user1": "mypassword",
        "guest": "welcome"
    }

    # Save credentials to CSV file
    wordlist_manager.save_credentials_to_csv(credentials)

    # Display credentials in the console
    wordlist_manager.display_credentials(credentials)


# Run the main function
if __name__ == "__main__":
    main()
