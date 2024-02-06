from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import mysql.connector as mcon
import streamlit as st
import pandas as pd
import plotly.express as px
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime

st.title("Scraping Automation Project")

link = "https://www.ebay.com/itm/134638042371?_trkparms=pageci%3A8027356b-65d0-11ee-9540-da19176fc09b%7Cparentrq%3A0f1d672118b0a24212b358bfffffd76e%7Ciid%3A1&var=434175605789"

response = urlopen(link)
html_data = response.read()
soup_data = soup(html_data, "html.parser")

name = soup_data.find('h1',{'class':"x-item-title__mainTitle"}).text.replace('"',"")[0:18].strip()
price = float(soup_data.find('div',{'class':"x-price-primary"}).text.strip("US $"))

db = mcon.connect(host="localhost", user="root", password="aquib123")

cursor = db.cursor()    # create a cursor

cursor.execute("create database if not exists automation")
cursor.execute("use automation")
cursor.execute("create table if not exists macbook(date datetime,product_name varchar(255),price float(20))")

cursor.execute("select * from Macbook") 
data = pd.DataFrame(cursor.fetchall(),columns = ["Date","Product Name","Price"])

# Making a Line Plot
fig = px.line(data_frame = data,
              x = 'Date',
              y = 'Price',
              title = 'Treand Analysis of Macbook Price')
st.plotly_chart(fig)

# Displaying data which is stored in SQL Database
st.table(data)  

# Inserting a new record into the database
cursor.execute("select price from macbook order by date desc limit 1")
last_price = cursor.fetchall()[0][0]

cursor.execute(f"insert into macbook values (current_timestamp(),'{name}',{price})")
st.write(f"Record ({name},{price}) Inserted Successfully")

# SENDING MAIL

def send_mail():
    # Outlook SMTP server and port
    smtp_server = 'smtp-mail.outlook.com'
    smtp_port = 587

    # Your Outlook email address and password
    email_address = 'hackingscraping@outlook.com'
    email_password = '$ABcd1234$'

    # Recipient's email address
    recipient_email = 'faisalfarooqui077@gmail.com'

    # Create the email message
    subject = 'Macbook Current Price'
    message = f"""
    # Product Information

    **Date**: {datetime.datetime.now().strftime("%d-%m-%Y")}
    **Product**: {name}
    **Price**: ${price:.2f}

    This is the best time to buy!
    The price dropped from ${last_price} to ${price}.
    Price Difference: ${last_price-price}

    Best Regards,
    Faisal
    """


    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    # Establish an SMTP connection with Outlook
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_address, email_password)
        server.sendmail(email_address, recipient_email, msg.as_string())
        server.quit()
        st.write("Email sent successfully.")
    except Exception as e:
        st.write("Error: Could not send email.")
        st.write(e)
if price<last_price:
    send_mail()
else:
    st.write("No price change! Email not sent!")

db.commit()
db.close()