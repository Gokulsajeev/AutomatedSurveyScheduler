# from . import engine as db
from . import User, main
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.orm import sessionmaker
import openai
import time

# Importing database
db = create_engine('sqlite:///user_data.db', echo=False)

# Set your OpenAI API key here
openai.api_key = "YOUR-API-KEY"

def generate_engaging_message(name, survey_name):
    # prompt = f"create a engaging message to a user named {name} requesting to fill out a feedback survey of a workshop\n\n"
    prompt = f"create an engaging message for user named {name} to fill out a feedback survey form regarding a {survey_name} held last week"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1001,
        temperature=0.8
    )
    return response.choices[0].text.strip()

if __name__ == "__main__":

    main()
    # Accessing database
    Session = sessionmaker(bind=db)
    session = Session()
    query = session.query(User)
    for user in query.all():
        name = user.name
        engaging_message = generate_engaging_message(name, User.survey_name)
        
        # Printing the engageing message
        print(engaging_message)

        # For free trial users in openapi
        time.sleep(20)
    session.close()


    # survey_name = "Example Survey"
    # engaging_message = generate_engaging_message(survey_name)
    print(engaging_message)
