import numpy as np 
import pandas as pd  
import streamlit as st  
import warnings
import sys , os
import matplotlib.pyplot as plt  # visualization
import seaborn as sns  # visualization
import random
import docx2txt
import textract
import sqlite3
warnings.filterwarnings('ignore')


if 'page' not in st.session_state :
    st.session_state['page'] = 'Dashboard.py'
if 'file' not in st.session_state :
    st.session_state['file'] = None
if 'filename' not in st.session_state :
    st.session_state['filename'] = None
conn = sqlite3.connect('data.db')
c = conn.cursor()

def add_file(username , filename , file):
    c.execute('update userstable set filename = ? , file = ? where username = ?' , (filename , file , username))
    conn.commit()
    


st.set_page_config(
    page_title="Dashboard",
    page_icon=":bar_chart:",
    # layout="wide",
)

st.title(':bar_chart: Marketing Dashboard')
st.markdown('<style>div.block-container{padding-top:1rem;}</style>' , unsafe_allow_html=True)

docx_file = st.file_uploader(":page_with_curl: Upload Document" , type =["txt"])
if st.button("Process"):
    if docx_file is not None:
        file_details = {"filename":docx_file.name , "filetype":docx_file.type , "filesize":docx_file.size}
        st.write(file_details)
if st.button("Read"): 
    raw_text = str(docx_file.read() , "utf-8")
    st.text(raw_text)
st.warning('Please Upload Text file Contains Description for your Dataset')

if  'uploaded_file' not in st.session_state:
    st.session_state['uploaded_file'] = False
    
st.subheader('Logged in as : ' + str(st.session_state['username']))
def load_file():
    file = st.file_uploader(':file_folder: Upload your CSV file', type='csv')
    if file is None :
        st.warning('Please upload a valid  CSV file')
        sys.exit(0)
    bytes = file.getvalue()
    add_file(st.session_state['username'] , file.name , bytes)
    df = pd.read_csv(file)
    st.dataframe(df.head())
    data = df.copy()
    return data


data = load_file()
if data is not None :
    st.session_state['uploaded_file'] = True
    st.session_state['file'] = data
def report(content):
    report_file = open('report_file.txt', 'w')
    report_file.write(content)

# most_important_cols = ['education' , 'age' , 'campaign' , 'deposit' , 'job' , 'duration' , 'marital' , 'housing' , 'balance' , 'loan' ,'day' ]
# specificData = data[most_important_cols]

most_important_cols = ['education' , 'age' , 'campaign' , 'deposit' , 'job' , 'duration' , 'marital' , 'housing' , 'balance' , 'loan' ,'day' , 'contact' ]
for col in most_important_cols:
    if col not in data.columns :
        most_important_cols.remove(col)
specificData = data[most_important_cols]
print(data.head())
st.subheader("	:pushpin: Most important columns")
st.dataframe(specificData.head())
def grab_col_names(dataframe, cat_th=10, car_th=20):

    cat_cols = [col for col in dataframe.columns if dataframe[col].dtypes == "O"]
    num_but_cat = [col for col in dataframe.columns if dataframe[col].nunique() < cat_th and
                   dataframe[col].dtypes != "O"]
    cat_but_car = [col for col in dataframe.columns if dataframe[col].nunique() > car_th and
                   dataframe[col].dtypes == "O"]
    cat_cols = cat_cols + num_but_cat
    cat_cols = [col for col in cat_cols if col not in cat_but_car]

    # num_cols
    num_cols = [col for col in dataframe.columns if dataframe[col].dtypes != "O"]
    num_cols = [col for col in num_cols if col not in num_but_cat]

    st.write(f"observations: {dataframe.shape[0]}")
   
    st.write(f"variables: {dataframe.shape[1]}")
   
    st.write(f'Catigorical Columns: {len(cat_cols)}')
    
    st.write(f'Numerical Columns : {len(num_cols)}')
   
    st.write(f'List of cardinal variables with categorical view: {len(cat_but_car)}')
    
    st.write(f'num_but_cat: {len(num_but_cat)}')
    
    return cat_cols, num_cols, cat_but_car

cat_cols, num_cols, cat_but_car = grab_col_names(data)

def draw_vs(dataframe , x , y , title , legend ):
    plt.figure()
    plt.title(title)
    g = sns.countplot(x= x, hue = y, data=dataframe )
    plt.xticks(rotation=70)
    plt.yticks([])
    plt.legend(title=legend, ncol=1, fancybox=True, shadow=True)
    # plt.show()
    st.pyplot(plt ,clear_figure= True , use_container_width=True)
    
def draw_vs_new(dataframe  , listofColumns , title):
    plt.figure()
    plt.title(title)
    for col in listofColumns : 
        sns.countplot(x= col, data=dataframe )
        plt.xticks(rotation=70)
        plt.yticks([])
        plt.legend(title=random.choice(str(listofColumns)), ncol=1, fancybox=True, shadow=True)
        st.pyplot(plt , clear_figure= True , use_container_width=True )

try:
    
    selected_columns = st.multiselect("Select two columns", data.columns)
    if len(selected_columns) == 2 :
        draw_vs(data , selected_columns[0] , selected_columns[1] , title = str(selected_columns[0] + ' ' + selected_columns[1]) , legend=selected_columns[1])
    elif len(selected_columns) == 3 :
        draw_vs_new(data , selected_columns , title = "multi Columns Comparison" )
except:
    pass
draw_vs(data  , 'marital' , 'housing' , 'marital vs housing' , 'marital')

        
st.subheader(':bar_chart: Categorical Variables vs Target')

def outlier_thresholds(dataframe, col_name, q1=0.05, q3=0.95):
    quartile1 = dataframe[col_name].quantile(q1)
    quartile3 = dataframe[col_name].quantile(q3)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    return low_limit, up_limit

# outlier_thresholds(data, "age")
def grab_outliers(dataframe, col_name, index=False):
    low, up = outlier_thresholds(dataframe, col_name)

    if dataframe[((dataframe[col_name] < low) | (dataframe[col_name] > up))].shape[0] > 10:
        print(dataframe[((dataframe[col_name] < low) | (dataframe[col_name] > up))].head())
        
    else:
        print(dataframe[((dataframe[col_name] < low) | (dataframe[col_name] > up))])
        

    if index:
        outlier_index = dataframe[((dataframe[col_name] < low) | (dataframe[col_name] > up))].index
        return outlier_index

def remove_outlier(dataframe, col_name):
    low_limit, up_limit = outlier_thresholds(dataframe, col_name)
    df_without_outliers = dataframe[~((dataframe[col_name] < low_limit) | (dataframe[col_name] > up_limit))]
    return df_without_outliers


def cat_summary(dataframe, col_name, plot=False):
     print(pd.DataFrame({col_name: dataframe[col_name].value_counts(),
                         "Ratio": 100 * dataframe[col_name].value_counts() / len(dataframe)}))
     if plot:
         sns.countplot(x=dataframe[col_name], data=dataframe)
         plt.xticks(rotation=90)
        #  plt.show(block=True)
         st.pyplot(plt , clear_figure=True , use_container_width=True)
st.subheader('Catigorical Summary')
for col in cat_cols:
    cat_summary(data, col, True)


    
st.subheader(':bar_chart:Numerical Statistics on columns')

def num_summary(dataframe, numerical_col, plot=False):
    quantiles = [0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.90, 0.95, 0.99]
    print(dataframe[numerical_col].describe(quantiles).T)

    if plot:
        dataframe[numerical_col].hist(bins=50, figsize=(9,5))
        plt.xlabel(numerical_col)
        plt.title(numerical_col)
        #plt.show()
        st.pyplot(plt , clear_figure=True , use_container_width=True)

for col in num_cols:
    num_summary(data, col, True)

# for col in most_important_cols:
#     num_summary(data, col, True)
    
st.subheader('🧬 Correlation summary')
def correlation_matrix(df, cols):
     fig = plt.gcf()
    #  fig.set_size_inches(8, 6)
     plt.xticks(fontsize=10)
     plt.yticks(fontsize=10)
     plt.title('Correlation Matrix')
     fig = sns.heatmap(df[cols].corr(), annot=True, linewidths=0.5, annot_kws={'size': 12}, linecolor='w', cmap='RdBu')
    #  plt.show(block=True)
     st.pyplot(plt , clear_figure=True , use_container_width=True)
     
correlation_matrix(data, num_cols)



    
   
st.subheader(':bar_chart: Categorical Variables vs Target')
# make the user choose 2 values 
try:
    
    selected_columns = st.multiselect("Select two columns", data.columns)
    if len(selected_columns) == 2 :
        draw_vs(data , selected_columns[0] , selected_columns[1] , title = str(selected_columns[0] + ' ' + selected_columns[1]) , legend=selected_columns[1])
    elif len(selected_columns) == 3 :
        draw_vs_new(data , selected_columns , title = "multi Columns Comparison" )
except:
    pass
draw_vs(data  , 'marital' , 'education' , 'marital vs education' , 'marital')
