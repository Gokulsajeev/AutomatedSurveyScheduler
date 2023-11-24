# Automated Survey Scheduler
It is an AI-powered system that can automatically schedule and distribute surveys to users based on their availability, preferences, and other factors. The system also use machine learning algorithms and GPT-3's language generation capabilities to generate targeted and engaging messages, improving the overall response rate and providing a more comprehensive view of survey results

## Setup
Before getting into development there are prerequisite python packages that are needed to be installed
```
# Streamlit is used as the UI of the web app
$ pip install streamlit pandas

# OpenAI is used to generate engaging message as body of the mail
$ pip install openai

# SQL Alchemy for sql queries
$ pip install sqlalchemy

# Scheduling libraries
$ pip install schedule

# Gmail API
$ pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```
- Make sure to attach your own APIs and Tokens to use the program.
- Properly setup google credentials to utilise Gmail API

## Running
To run the program, you must run it through streamlit
```
$ streamlit run /src/main.py
```
