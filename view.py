# =============================================================================
# author  : Vladislav
# date    : 2020_10_16
# client  : Paul.P.
# =============================================================================

from flask import Flask, render_template, redirect, request,flash
from googlesearch import search 
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from dateutil.parser import parse

#============================================================================

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

#=================== global varable inital part  ============================

df_result_table = [] 
df_result_title = []
data_frame_list = []
search_url = ""
command = ""
command_title = ""
url_tile = ""
distint_num = ""

#========================   end inital  ======================================

#========================   first url part====================================

@app.route("/")
def index():
    return render_template("index.html")

#========================   after google search  ==============================

@app.route("/",methods=['GET', 'POST'])
def search_result():
    #------------ global varable define part ----------------------------------------
    global df_result_table, data_frame_list ,search_url, command ,command_title, url_tile, distint_num  
    #--------------------------------------------------------------------------------
    df = [] 
    #--------if request is "post"---------------------------------------------------
    if request.method == "POST":
        # get url that the user has entered
        try:
            url = request.form['search']            
            keyword = url
            url = url.split(" ")
            count = 0

            #------------ get distint of number ------------------------------------

            if url[0] == "distint":                
                 result = []
                 temp = [item for item in data_frame_list[0].iterrows()]
                 for item in temp:
                     if any(s in url[-1] for s in item[1]):
                         result.append(item)
                         
                 count = len(result)

                 return render_template('index.html',  tables=df_result_table, table=df_result_table[0], url = search_url, command = command, count = count, url_title = url_tile, command_title= command_title, distint_num = distint_num)                 
            #------------ end distint of number ------------------------------------

            #------------ get table of google search -------------------------------
            try:
                # inital array of global varable 
                df_result_table = []
                df_result_title = []
                data_frame_list = []
                search_url = ""
                command = ""
                command_title = ""
                url_tile = ""
                distint_num = ""
                
                for j in search("table of "+url[-1], tld="co.in", pause=2):
                    try:
                        r = requests.get(j)                
                        soup = BeautifulSoup(r.content, 'html.parser')
                        #soup.replace('text-aling:right', 'text-aling:left')
                        tb_list = soup.find_all('table') 
                        
                        for tb in tb_list:
                            #tb.replace('text-align: right;', 'text-align: left;')
                            rows=tb.find_all('tr')                                                  
                            
                            try:
                                #-----------------------  if the header of table use "th" tag  ----------------------------------                        
                                if(rows[0].find('th')):
                                    columns=[v.text for v in rows[0].find_all('th')]
                                    #------------------------  put dataframe in header of table    ------------------------------
                                    df= pd.DataFrame(columns=columns)                            
                                    #---------------------------------------------------------------------------------------------
                                    #---------------------- table content part  ------------------------------------------------
                                    for i in range(1, len(rows)):
                                        tds=rows[i].find_all('td')
                                        values = []
                                        for k in range(0, len(tds)):
                                            value =tds[k].text                                    
                                            values.append(value) 

                                        df=df.append(pd.Series(values,index=columns),ignore_index=True) 
                                    df_result_table.append(df.to_html(classes='data'))
                                    df_result_title.append([df.columns.values])                            
                                    data_frame_list.append(df)
                                    #---------------------- end content part  ------------------------------------------------
                                
                                #-----------------------------------------------------------------------------------------------
                                #-----------------------  if the header of table use "tb" tag  ----------------------------------                        
                                elif(rows[0].find('td')):                                   

                                    columns=[v.text for v in rows[0].find_all('td')]                                    
                                    #------------------------  put dataframe in header of table    -----------------------------
                                    df= pd.DataFrame(columns=columns)
                                    #-------------------------------------------------------------------------------------------
                                    #---------------------- table content part  ------------------------------------------------
                                    
                                    for i in range(1, len(rows)):
                                        tds=rows[i].find_all('td')
                                        values = []
                                        for k in range(0, len(tds)):
                                            value=tds[k].text.replace('\n', '').replace('\r', '')
                                            values.append(value)
                                            
                                        df=df.append(pd.Series(values,index=columns),ignore_index=True) 
                                        
                                    df_result_table.append(df.to_html(classes='data'))
                                    df_result_title.append([df.columns.values])
                                    data_frame_list.append(df)
                                    #---------------------- end content part  ------------------------------------------------
                                #---------------------------   end "tb" tag   ------------------------------------------------
                            except:
                                print("dont find table")
                        #---------------------- set value of global varable  ------------------------------------------------            
                        search_url = j
                        command = keyword
                        command_title = "Command: "
                        url_tile = "Url: "
                        distint_num = "The Number of Element: "

                        #********************** second part  **************************

                        df_state_result  = []

                        for data_frame in data_frame_list:
                            #print(data_frame.columns)
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
                                    data_frame[row] = data_frame[row].str.replace(',','').replace('n/a','')  
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
                            print(df_state)
                            df_state_result.append(df_state.to_html(classes='data'))

                        #*********************  end second part ***********************
                        
                        #---------------------- end set value of global varable   ------------------------------------------------
                        return render_template('index.html',  tables=df_result_table, table=df_result_table[0], titles=df_result_title, url = j, command = keyword, url_title = url_tile, command_title= command_title,state_tables = df_state_result ) 
                        #------------ end table of google search -------------------------------
                    except:
                        return("dont find data")

            except:
                return("dont find keyword!")
        except:
            return("Unable to get URL. Please make sure it's valid and try again.")
                  
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
#============================= main funtion part  ================================================

if __name__ == '__main__':   
    app.run(debug=True)

#===============================  end main  ===========================================