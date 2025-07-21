from email.message import EmailMessage
import getpass
import smtplib
import sys


def send_email(result: str, mode: str) -> None:
    """
    Send the encoded text to the user's email.
    Args:
        file: Path to the file containing the encoded text.
    """
    from UI import parse_args

    args = parse_args()

    if args.send_email:
        if mode == "encode":
            subject = "Encoded Text"
        else:
            subject = "Key"
        user_email = args.my_email
        sender_email = args.email_to
        add_msg = args.email_body
        msg = EmailMessage()
        msg.set_content(result+'\n'+add_msg)
        msg["Subject"] = subject
        msg["From"] = user_email
        msg["To"] = sender_email
        password = args.app_password
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(user_email, password)
            server.send_message(msg)
            print("Email sent successfully!")
            sys.exit()
    else:
        subject, email = get_subject(mode)
    
    if email == "y":
        user_email = input("Enter your email: ").strip() 
        sender_email = input("Enter the recipient's email: ").strip()
        add_msg = input("Enter any information besides the text and key you want to send: ").strip()
        msg = EmailMessage()
        msg.set_content(result+'\n'+add_msg)
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

def get_subject(mode: str) -> tuple[str, str]:
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
    return subject, email