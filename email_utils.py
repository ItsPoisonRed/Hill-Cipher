from email.message import EmailMessage
import getpass
import smtplib

def send_email(result: str, mode: str) -> None:
    """
    Send the encoded text to the user's email.
    Args:
        file: Path to the file containing the encoded text.
    """
    if mode == "encode":
        email = (
            input("Would you like to send the encoded text and key to another email? (y/n): ")
            .strip()
            .lower()
        )
        subject = "Encoded Text"
    else:
        email = (
            input("Would you like to send the key to another email? (y/n): ")
            .strip()
            .lower()
        )
        subject = "Key"
    if email == "y":
        user_email = input("Enter your email: ").strip()
        sender_email = input("Enter the recipient's email: ").strip()
        msg = EmailMessage()
        msg.set_content(result)
        msg["Subject"] = subject
        msg["From"] = user_email
        msg["To"] = sender_email
        password = getpass.getpass("Enter your app password: ")
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(user_email, password)
            server.send_message(msg)
            print("Email sent successfully!")
    else:
        print("Email not sent.")