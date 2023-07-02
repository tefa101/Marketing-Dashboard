from st_pages import Page, add_page_title, show_pages
show_pages(
    [
        Page('startup.py' , "Authentication" , ":lock:"),
        Page('pages/About_Us.py' , "About_Us" , "👩🏻‍💻"),
        Page('pages/Contact_Us.py' , "Contact" , "💬"),
        
    ]
)

from pathlib import Path
import pandas as pd 
import plotly.express as px
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_lottie import st_lottie 
import hashlib
import sqlite3
import streamlit as st 
import warnings
from streamlit_extras.switch_page_button import switch_page

if 'page' not in st.session_state:
    st.session_state['page'] = 'startup.py'

warnings.filterwarnings('ignore')
st.set_option('deprecation.showPyplotGlobalUse', False)


def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False
# DB Management

conn = sqlite3.connect('data.db')
c = conn.cursor()
# DB  Functions
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(id INTEGER primary key , username TEXT unique,password TEXT)')

def create_admin_table():
    c.execute('create table if not exists admintable(adminname text,password text)')

def add_user(username,password):
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data

def add_admin(adminname , password):
    c.execute('insert into admintable (adminname , password) values (?,?)' , (adminname , password))
    conn.commit()
    
def login_admin(adminname , password):
    c.execute('select * from admintable where adminname = ? and password = ?' , (adminname , password))
    data = c.fetchall()
    return data

def view_all_admins():
    c.execute('select * from admintable')
    data = c.fetchall()
    return data    
def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data

create_admin_table()


if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'password' not in st.session_state:
    st.session_state['password'] = None
if 'database' not in st.session_state:
    st.session_state['database'] = conn
if 'login_after' not in st.session_state:
    st.session_state['login_after'] = False
if 'admin_name' not in st.session_state:
    st.session_state['admin_name'] = None
if 'admin_password' not in st.session_state:
    st.session_state['admin_password'] = None
login_after = st.session_state['login_after']
print(st.session_state['login_after'])

for item in st.session_state:
    print(item , st.session_state[item])



def main():

    menu = ["Login", "SignUp" , "Admin-login" ]
    choice = st.selectbox(
        "Select Login or SignUp from dropdown box ▾",
        menu,
    )
    st.markdown(
        "<h10 style='text-align: left; color: #ffffff;'> If you do not have an account, create an accouunt by select SignUp option from above dropdown box.</h10>",
        unsafe_allow_html=True,
    )
    if choice == "Login":
        st.subheader("Login Section")
        username = st.text_input("User Name")
        password = st.text_input("Password" , type='password')
        if st.button("Login"):
            hashed_password = make_hashes(password)
            result = login_user(username , check_hashes(password , hashed_password))
            if result:
                st.success("Logged in as {}".format(username))
                st.subheader("Welcome to the dashboard")
                show_pages(
                        [
                        Page("startup.py" , "Authentication" , ":lock:"),
                        Page("pages/About_Us.py", "About_Us", "👩🏻‍💻"),
                        Page("pages/Contact_Us.py", "Contact", "💬"),
                        Page("pages/Dashboard.py", "Dashboard" , ":bar_chart:"),
                        ]
                )
                
                st.session_state['username'] = username
                st.session_state['password'] = password
                st.session_state['login_after'] = True   
                switch_page("Dashboard")
            else:
                st.warning("Incorrect Username/Password")
                

       
         
        else :
            html_temp = """<div style="background-color:tomato"><p style ="color:white;font-size:25px;">please login first</p></div>"""
            st.markdown(html_temp,unsafe_allow_html=True)
            
        # signup -> choices ?? 
    elif choice == "SignUp":
            st.write("-----")
            st.subheader("Create New Account")
            new_user = st.text_input("Username", placeholder="name")
            new_password = st.text_input("Password", type="password")

            if st.button("Signup"):
                if new_user == "": 
                    st.warning("Inavlid user name")
                elif new_password == "": 
                    st.warning("Invalid password")
                else:
                    create_usertable()
                    add_user(new_user,  make_hashes(new_password))
                    st.success("You have successfully created a valid Account")
                    st.info("Go up and Login to you account")
                    
    elif choice == "Admin-login":
        st.subheader("Admin Login Section")
        admin_name = st.text_input("Admin Name")
        password  = st.text_input("Password" , type='password')
        if st.button("Login"):
            hashed_password = make_hashes(password)
            result = login_admin(admin_name , check_hashes(password , hashed_password))
            if result:
                st.subheader("Welcome to the dashboard")
                
                    
                    
                    
main()                 