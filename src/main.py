# Libraries for Scheduling and threading
import time
import subprocess
import datetime
import threading
import schedule

# Libraries for Gmail API
from io import StringIO
import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Libraries for streamlit and SQL database
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Library for ChatGPT
import openai

# Importing SQL data and form data
from __init__ import User, main
from models import Org, Schedule

# Including database
db = create_engine('sqlite:///user_data.db', echo=False)

# Set your OpenAI API key here
openai.api_key = "YOUR-API-KEY"

def generate_engaging_message(name):
    link = Org.survey_link
    survey_name = Org.survey_name
    incharge = Org.per_name
    orgname = Org.org_name

    # Prompt provided to GPT
    prompt = f"create an engaging message for user named {name} to fill out a feedback survey of {link} regarding a {survey_name} held last week by {orgname} with incharge person {incharge}\n\n"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1001,
        temperature=0.8
    )

    # Returns the response
    return response.choices[0].text.strip()

# Gmail Integration below
# Scope required for sending emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_credentials():
    creds = None

    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('src/token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('src/credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def create_message(sender, receiver, subject, message_text):
    message = MIMEMultipart()
    message['to'] = receiver
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text, 'plain')
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_email(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f"Message Id: {message['id']}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def mailmain(receiver_email, subject, body):
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)

    sender_email = 'your_email@example.com'  

    message = create_message(sender_email, receiver_email, subject, body)
    send_email(service, 'me', message)



# Scheduling
def send_email_thread(receiver_email, subject, body):
    # Runs only once
    email_thread = threading.Thread(target=mailmain, args=(receiver_email, subject, body))
    email_thread.start()
    return schedule.CancelJob

def send_email_thread_multi(receiver_email, subject, body):
    # Runs multiple times
    email_thread = threading.Thread(target=mailmain, args=(receiver_email, subject, body))
    email_thread.start()

def schedule_emails(emails_data):
    
    for email_data in emails_data:
        receiver_email, subject, body = email_data
        if Schedule.time and not Schedule.days:
            times = Schedule.time
            schedule.every().day.at(times).do(send_email_thread, receiver_email, subject, body)

        elif Schedule.days:
            # if Schedule.time:
            #     time = Schedule.time

            
            for day in Schedule.days:
                if day == "Monday":
                    schedule.every().monday.do(send_email_thread_multi, receiver_email, subject, body)
                
                if day == "Tuesday":
                    schedule.every().tuesday.do(send_email_thread_multi, receiver_email, subject, body)

                if day == "Wednesday":
                    schedule.every().wednesday.do(send_email_thread_multi, receiver_email, subject, body)

                if day == "Thursday":
                    schedule.every().thursday.do(send_email_thread_multi, receiver_email, subject, body)

                if day == "Friday":
                    schedule.every().friday.do(send_email_thread_multi, receiver_email, subject, body)

                if day == "Saturday":
                    schedule.every().saturday.do(send_email_thread_multi, receiver_email, subject, body)

                if day == "Sunday":
                    schedule.every().sunday.do(send_email_thread_multi, receiver_email, subject, body)

        if Schedule.date:
            schedule_date = datetime.datetime.strptime(Schedule.date, '%Y-%m-%d')
            now = datetime.datetime.now()

            time_difference = (schedule_date - now).total_seconds

            if time_difference > 0:
                schedule.every(int(time_difference)).seconds.do(send_email_thread, receiver_email, subject, body)

    while True:
        schedule.run_pending()
        time.sleep(1)



if __name__ == "__main__":

    # Starts the front-end
    main()

    if st.button("Schedule Surveys"):

        # Accessing database
        Session = sessionmaker(bind=db)
        session = Session()
        query = session.query(User)
        email_data = []
        for user in query.all():
            name = user.name
            engaging_message = generate_engaging_message(name)
            st.write(engaging_message)
            data = (user.email, Org.subject, engaging_message)
            email_data.append(data)

        session.close()
        schedule_emails(email_data)
