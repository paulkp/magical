# =============================================================================
# author  : Vladislav
# date    : 2020_10_16
# client  : Paul.P.
# =============================================================================

from flask import Flask, render_template, redirect, request,flash, url_for
from googlesearch import search 
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from dateutil.parser import parse

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

strip_search_list = []
search_list = []
table_count = []
df_result_table = []
df_state_result = []
data_frame_list = []

@app.route('/')
def index():
    return render_template("index.html")



#=========== search keyword =================
@app.route("/",methods=['GET', 'POST'])
def search_result():    
    global  strip_search_list, search_list
    if request.method == "POST":
        try:
            url = request.form['search']
            url = url.split(" ")         

            try:
                for j in search("table of "+url[-1], stop=10):
                    search_list.append(j)
                    strp_str = str(j)[0:30] + "..." # url is longer
                    strip_search_list.append(strp_str)
                # table_count = url_scrapping(search_list[0])    # dispplay table count
                return render_template('index.html', searchlist=search_list, strip_searchlist=strip_search_list)
            except:
                print("don't find data")  

        except:
            return("Unable to get URL. Please make sure it's valid and try again.")

#================ click side bar of url list =======================
@app.route("/search")
def url_response(): 
    global table_count
    table_count.clear()
    table_count = []   
    url_address = request.args.get('val')
  
    # state_tab(data_frame_list[0]) 
    table_count = url_scrapping(url_address)    # dispplay table count  
 

    return render_template('index.html',tables=df_result_table,table=df_result_table[0],searchlist=search_list, strip_searchlist=strip_search_list, 
    tb_count = table_count)

#================ click side bar of table list =======================
@app.route("/table")
def table_response(): 
    
    table_num = int(request.args.get('val')) 

    state_tab(data_frame_list[table_num])   

    return render_template('index.html',tables=df_result_table,table=df_result_table[table_num],searchlist=search_list, strip_searchlist=strip_search_list, 
    tb_count = table_count, state_tables=df_state_result)

#================ click side bar of table list =======================

#================ scrapping by each url of sidebar ==================
def url_scrapping(string): 
    global  df_result_table, data_frame_list

    df_result_table.clear()
    df_result_table = []

    data_frame_list.clear()
    data_frame_list = []

    r = requests.get(string) 
   
    soup = BeautifulSoup(r.content, 'html.parser') 
   
    tb_list = soup.find_all('table')
    for tb in tb_list:
        rows = tb.find_all('tr')
        try:
            if (rows[0].find('th')):
                columns = [v.text for v in rows[0].find_all('th')]
                
            elif (rows[0].find('td')):
                columns = [v.text for v in rows[0].find_all('td')]                

            df = pd.DataFrame(columns=columns)
               
            for i in range(1, len(rows)):
                tds = rows[i].find_all('td')
                values = []
                for k in range(0, len(tds)):
                    value = tds[k].text.replace('\n', '').replace('\r', '')
                    values.append(value)

                df = df.append(pd.Series(values, index=columns), ignore_index=True)
            df_result_table.append(df.to_html(classes='data'))
            data_frame_list.append(df)    

        except:
            print("")  

    return tb_list
#================ tab state  ==================
def state_tab(data_frame):
    global df_state_result
    #df_state_result.clear()
    df_state_result = []

    df_state_result  = []
    
    header = []

    for row in data_frame.columns:
        header.append(row)
    df_state = pd.DataFrame(columns=header)

    state_value = []
    for row in data_frame.columns:

        if data_frame[row].empty == True:
                data = "empty"
                state_value.append(data)
                #print(data)
        else:
            data_frame[row] = data_frame[row].astype(str).str.replace(',','').replace('n/a','')
            try:
                int_data = [int_data for int_data in data_frame[row] if int_data.isdigit()]
                data_frame[row] = pd.to_numeric(data_frame[row])
                if(len(int_data) == len(data_frame[row])):
                    data = "int"
                else:
                    data = "float"
                state_value.append(data)
            except ValueError:
                date_frame = [ date_frame for date_frame in data_frame[row] if is_date(date_frame) is True]
                if("$" in data_frame[row]):
                    data = "contains$"
                elif  len(data_frame[row]) == len(date_frame):
                    data = "date"
                else:
                    data = "char"
                state_value.append(data)
                #print(state_value)
    df_state=df_state.append(pd.Series(state_value,index=header),ignore_index=True)
    #print(df_state)
    df_state_result = df_state.to_html(classes='data')
    print(df_state_result)

def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False

if __name__ == '__main__':   
    app.run(debug=True)
