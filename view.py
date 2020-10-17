from flask import Flask, render_template, redirect, request,flash
from googlesearch import search 
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

df_result_table = []
df_result_title = []
data_frame = []
search_url = ""
command = ""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/",methods=['GET', 'POST'])
def search_result():
    global df_result_table, data_frame ,search_url, command   
    
    df = [] 
    if request.method == "POST":
        # get url that the user has entered
        try:
            url = request.form['search']            
            keyword = url
            url = url.split(" ")
            count = 0
            if url[0] == "distint":
                
                 result = []
                 temp = [item for item in data_frame[0].iterrows()]
                 for item in temp:
                     if any(s in url[-1] for s in item[1]):
                         result.append(item)
                         
                 count = len(result)
                 #return redirect("/")
                 return render_template('index.html',  tables=df_result_table, table=df_result_table[0], url = search_url, command = command, count = count)                 

            try:
                df_result_table = []
                df_result_title = [] 
                data_frame = []
                
                for j in search("table of "+url[-1], tld="co.in", pause=2):
                    try:
                        r = requests.get(j)                
                        soup = BeautifulSoup(r.content, 'html.parser')
                        tb_list = soup.find_all('table')                       
                        
                        for tb in tb_list:
                            rows=tb.find_all('tr')
                            try:                         
                                if(rows [0].find('th')):
                                    columns=[v.text.replace('\n', '')for v in rows[0].find_all('th')]
                                   
                                    df= pd.DataFrame(columns=columns)                            
                                   
                                    for i in range(1, len(rows)):
                                        tds=rows[i].find_all('td')
                                        values = []
                                        for k in range(0, len(tds)):
                                            value =tds[k].text                                    
                                            values.append(value) 

                                        df=df.append(pd.Series(values,index=columns),ignore_index=True) 
                                    df_result_table.append(df.to_html(classes='data'))
                                    df_result_title.append([df.columns.values])                            
                                    data_frame.append(df)

                                elif(rows [0].find('td')):

                                    columns=[v.text.replace('\n', '') for v in rows[0].find_all('td')]
                                    #print(columns)
                                    df= pd.DataFrame(columns=columns)
                                    
                                    for i in range(1, len(rows)):
                                        tds=rows[i].find_all('td')
                                        values = []
                                        for k in range(1, len(tds)):
                                            value=tds[k].text
                                            values.append(value)
                                            
                                        df=df.append(pd.Series(values,index=columns),ignore_index=True) 
                                        
                                    df_result_table.append(df.to_html(classes='data'))
                                    df_result_title.append([df.columns.values])
                                    data_frame.append(df)
                            except:
                                print("dont find table!") 
                        search_url = j
                        command = keyword
                        return render_template('index.html',  tables=df_result_table, table=df_result_table[0], titles=df_result_title, url = j, command = keyword) 
                    except:
                        print("dont find data!")

            except:
                print("dont find keyword!")
        except:
            print("Unable to get URL. Please make sure it's valid and try again.")            
    

if __name__ == '__main__':
   
    app.run(debug=True)