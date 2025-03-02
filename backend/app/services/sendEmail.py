import smtplib
import pandas as pd
import time
import os
import random
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formataddr
from email import encoders

# Function to send an email with optional attachments and CC
def send_email(to_email, subject, message, attachment_path=None, attachment_path2=None, cc_email=None):
    
    
    # Email configuration
    sender_email = "cuhyperloop@colorado.edu"  # Replace with your email
    sender_password = "obmq rbnx ncvx kmop"  # Replace with your app password
    # Create the MIME object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    # Add CC email if provided
    if cc_email:
        msg['Cc'] = cc_email
    # Attach the message to the email as HTML
    msg.attach(MIMEText(message, 'html'))
    # Attach the first file if provided
    if attachment_path:
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path)}"')
            msg.attach(part)
    # Attach the second file if provided
    if attachment_path2:
        with open(attachment_path2, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path2)}"')
            msg.attach(part)
    # Collect all recipients (to + cc) for the actual send operation
    recipients = [to_email]
    if cc_email:
        recipients += [cc_email]
    # Connect to the SMTP server (Gmail in this case)
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipients, msg.as_string())
# Load the data from the Excel file
data = pd.read_excel("ToContactList.xlsx")
# Define the filenames of the attachments
FILENAME = 'CU-HYPERLOOP.pdf'
FILENAME2 = 'Thanksgiving_Newsletter.pdf'
print("Start sending emails")
# Loop through the rows in the Excel file and send emails
for index, row in data.iterrows():
    name = row['Name']
    email = row['Email']
    company_name = row['CompanyName']
    cc_email = row.get('CC')  # Read the CC email from the spreadsheet
    print(f"Processing: {name}, {email}, {company_name}, MessageType: {row['MessageType']}, CC: {cc_email}")  # For debugging
    # Get the subject and message based on MessageType
    subject, message = get_email_message_subject(row, name, company_name)
    # Send the email with CC
    send_email(email, subject, message, FILENAME, FILENAME2, cc_email)
    print(f"Email sent to: {email} (CC: {cc_email})")  # For debugging
    # Wait for a random time between 45 and 60 seconds before sending the next email
    wait_time = random.randint(30, 45)
    print(f"Waiting for {wait_time} seconds before sending the next email...")
    time.sleep(wait_time)
print("All emails sent")