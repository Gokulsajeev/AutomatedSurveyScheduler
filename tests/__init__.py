import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
import csv

# Create an SQLite database and table
engine = create_engine('sqlite:///user_data.db', echo=False)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    email = Column(String(100))
    age = Column(Integer)
    survey_name = ''

# Create the table if it doesn't exist
Base.metadata.create_all(engine)

def main():
    st.title("User Details App")

    # Add a form to enter user details
    with st.form("user_details_form"):
        st.write("Enter User Details")
        name = st.text_input("Name")
        email = st.text_input("Email")
        age = st.number_input("Age", min_value=0, max_value=150)
        User.survey_name = st.text_input("Survey type")

        submit_button = st.form_submit_button("Submit")

    # If the form is submitted, store the user details in the database
    if submit_button:
        # Create a new user object
        user = User(name=name, email=email, age=age)

        # Add the user to the database
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(user)
        session.commit()
        session.close()

    # Add file uploader for CSV files
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        # Display the uploaded CSV data
        st.write("Uploaded CSV data:")
        st.dataframe(df)

        # CSV to SQL
        df.to_sql('users', engine, if_exists='append', index=False)

        # You can further process the data as per your requirements.

    # Display the table with user details
    with st.expander("User Details Table"):
        display_user_table()

def display_user_table():
    # Retrieve data from the database and display it in a table
    Session = sessionmaker(bind=engine)
    session = Session()
    query = session.query(User)
    user_data = [{'Name': user.name, 'Email': user.email, 'Age': user.age} for user in query.all()]
    session.close()

    if user_data:
        st.dataframe(user_data)
    else:
        st.write("No user data available.")


