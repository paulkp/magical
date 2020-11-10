# =============================================================================
# author  : Vladislav
# date    : 2020_10_25
# client  : Paul.P.
# =============================================================================

from flask import Flask, render_template, redirect, request,flash, url_for
from googlesearch import search 
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from dateutil.parser import parse
from itertools import groupby
import re
import string
from IPython.core.display import HTML
import math

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

pd.set_option('display.max_colwidth', -1)

strip_search_list = []
search_list = []
table_count = []
df_result_table = []
df_state_result = ""
url = ""
data_frame_list = []
templateData = {}
ul_result_df = []
table_num = 0

@app.route('/')
def index():
    templateData = template()
    return render_template("index.html", **templateData)
#================= select option setting ===============
def template():
    templateDate = {
        'tvalues' : getTValues(),
        'selected_tvalue' : -1
    }
    return templateDate
#================= select option setting ===============
def getTValues():
    return ('Table of X', 'List of X', 'X table', 'X list', 'X')
#================== search keyword =====================
@app.route("/",methods=['GET', 'POST'])
def search_result(): 
    global  search_list, url, templateData
    search_list.clear()
    search_list = []
    templateData = {}
    if request.method == "POST":
        try:
            url = request.form['search']            

            search_type = request.form.get('search_type')
            templateData = template()
            templateData['selected_tvalue'] = search_type            

            if(search_type.split(' ')[0] == 'X'):
                search_keyword = url + search_type.replace('X', '')
            else:
                search_keyword = search_type.replace('X', '') + url

            try:
                for j in search(search_keyword, stop=10):
                    search_list.append(j)
                                        
                table_count = url_scrapping(search_list[0])    # dispplay table count
                list_scraping(search_list[0])
                return render_template('index.html', searchlist=search_list,  keyword = url, **templateData)
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
    table_count = url_scrapping(url_address)    # dispplay table count
    list_scraping(url_address)
    #state_tab(data_frame_list[0])  

    if len(table_count) != 0:        
        return render_template('index.html',tables=df_result_table,table=df_result_table[0],searchlist=search_list, tb_count = df_result_table , state_tables=df_state_result, keyword = url, **templateData, list_count = ul_result_df)       
    else:
        return render_template('index.html',searchlist=search_list, tb_count = df_result_table , state_tables=df_state_result, keyword = url , **templateData, list_count = ul_result_df)


#================ click side bar of table list =======================
@app.route("/table")
def table_response(): 
    global table_num
    table_num = 0
    table_num = int(request.args.get('val'))     

    state_tab(data_frame_list[table_num])   

    return render_template('index.html',tables=df_result_table,table=df_result_table[table_num],searchlist=search_list, tb_count = df_result_table, state_tables=df_state_result,keyword = url, **templateData, list_count = ul_result_df)

@app.route("/list")
def list_response(): 

   
    list_num = int(request.args.get('val')) 
    
    print(ul_result_df[list_num])
    if len(table_count) != 0:        
        return render_template('index.html',tables=df_result_table,table=df_result_table[0],searchlist=search_list, tb_count = df_result_table , state_tables=ul_result_df[list_num], keyword = url, **templateData, list_count = ul_result_df)       
    else:
        return render_template('index.html',searchlist=search_list, tb_count = df_result_table , state_tables=ul_result_df[list_num], keyword = url , **templateData, list_count = ul_result_df)

    #state_tab(data_frame_list[table_num])   

    

#================ click side bar of table list =======================

def list_scraping(string):
    global ul_result_df
    ul_result_df.clear()
    ul_result_df = []
    try:
        r = requests.get(string)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        raise SystemExit(e)
   
    soup = BeautifulSoup(r.content, 'html.parser') 
   
    ul_list = soup.find_all('ul') 
    columns = ['item','url']  
    df = pd.DataFrame(columns=columns)
    for tb in ul_list:
        items = tb.find_all('li')
        
        for item in items:
            value = []
            value.append(item.text.replace('\n', '<br>').replace('\r', '').replace('\t', ' '))           
            try:
                item_url = item.find('a')['href']
                
            except:
                item_url = ""
            value.append(item_url)
            
            df = df.append(pd.Series(value, index=columns), ignore_index=True)
            
        ul_result_df.append(df.to_html(escape=False))
    # print(ul_result_df)
    
#================ scrapping by each url of sidebar ==================
def url_scrapping(string):   
    global  df_result_table, data_frame_list

    df_result_table.clear()
    df_result_table = []

    data_frame_list.clear()
    data_frame_list = []

    try:
        r = requests.get(string)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        raise SystemExit(e)
   
    soup = BeautifulSoup(r.content, 'html.parser') 
   
    tb_list = soup.find_all('table')
    # print("***********************")
    # print(tb_list[8])
    # print("**********************")
    for tb in tb_list:
        rows = tb.find_all('tr')
        
        try:
            if (rows[0].find('th')):
                columns = [v.text.replace('\n', '<br>').replace('\r', '') for v in rows[0].find_all('th') if v.text != ""] # 10/28/2020
                
            elif (rows[0].find('td')):
                columns = [v.text.replace('\n', '<br>').replace('\r', '') for v in rows[0].find_all('td') if v.text != ""]  # 10/28/2020
              
            if len(columns) != 0: # 10/28/2020
                df = pd.DataFrame(columns=columns)
                
                for i in range(1, len(rows)):
                    tds = rows[i].find_all('td')
                    values = []
                    for k in range(0, len(tds)):
                        value = tds[k].text.replace('\n', '').replace('\r', '')
                        values.append(value)                       

                    df = df.append(pd.Series(values, index=columns), ignore_index=True)
                df_result_table.append(df.to_html(escape=False))
                data_frame_list.append(df)    

        except:
            print("dont'find")  

    return tb_list
#================ tab state  ==================
def state_tab(data_frame):
    global df_state_result   
    
    header = ['Type:head']
    for row in data_frame.columns:
        header.append(row)
    try:
        df_state = pd.DataFrame(columns=header)
        pro_df = pd.DataFrame(columns=header)
        pro_df1 = pd.DataFrame(columns=header)
    except AttributeError:
        df_state = pd.DataFrame(columns=[header])
        pro_df = pd.DataFrame(columns=[header])
        pro_df1 = pd.DataFrame(columns=[header])
    state_value = [" "]
   

    for row in data_frame.columns:
        if data_frame[row].empty == True:
                data = "empty"
                state_value.append(data)                
        else:
            try:
                data_frame[row] = data_frame[row].astype(str).str.replace(',','').replace('n/a','').replace('.N.A','')          
            except AttributeError:
                data_frame[row] = data_frame[row].str.replace(',','').replace('n/a','').replace('.N.A','')          
            
            num_df = []
            for i in range(0,len(data_frame[row])):
                if(data_frame[row][i] != '0' or data_frame[row][i] != 'n/a'or data_frame[row][i] != '' or data_frame[row][i] != 'N/A'or data_frame[row][i] != '.N.A'):
                    num_df.append(data_frame[row][i])         

            number_list = []
            low_list = []
            high_list = []
            is_match = False
            for i in range(0,len(num_df)):
                print(type_data(num_df[i].replace("m","FF")))
                if type_data(num_df[i].replace("m","FF")) == "match":
                    is_match = True
            print(num_df[i])
            print(is_match)               
            for i in range(0,len(num_df)):           

                if(type_data(num_df[0]) == type_data(num_df[i]) or is_match == True):
                    data = type_data(num_df[0])
                    if(data == "match" or is_match == True):                        
                        String = "@p" + num_df[i] + "@p"
                        val = re.findall("\d+\.\d+|\d+|\d*\D+", String)
                        if(type_data(val[1]) == "int"):
                            low_list.append(int(val[1]))
                        elif (type_data(val[1]) == "float" or type_data(val[1]) == "floating_with_2_decimal_places"):
                            low_list.append(float(val[1]))                        

                        if(type_data(val[-2]) == "int"):
                            high_list.append(int(val[-2]))
                        elif (type_data(val[-2]) == "float" or type_data(val[1]) == "floating_with_2_decimal_places"):
                            high_list.append(float(val[-2]))

                        #=============== standard deviations ===========================
                        low_stdev = calc_stdev(low_list, sum(low_list)/len(low_list) )
                        high_stdev = calc_stdev(high_list, sum(high_list)/len(high_list))
                        #===============================================================

                        data = "type: range"+"<br>"
                        data = data + "Prefix: "+ val[0].replace('@p','') + "<br>"
                        data = data + "Surfix: "+ val[-1].replace('@p','') + "<br>"

                        data =  data + "low_max : " +str(max(low_list))+"<br>"
                        data =  data + "low_min : " + str(min(low_list))+"<br>"
                        data =  data + "low_av : " + str(significant_detect(sum(low_list)/len(low_list)))+"<br>"
                        data =  data + "low_stdev : " + str(significant_detect(low_stdev))+"<br>" 
                        
                        data =  data + "high_max : " +str(max(high_list))+"<br>" 
                        data =  data + "high_min : " + str(min(high_list))+"<br>" 
                        data =  data + "high_av : " + str(significant_detect(sum(high_list)/len(high_list)))+"<br>"
                        data =  data + "high_stdev : " + str(significant_detect(high_stdev))+"<br>"                                                      
                   
                    #=================== if there are duplicates in a List ===============================
                    elif(data == "char"):
                        dupl_check_list = []
                        for item in num_df:
                            try:
                                if item[-1] == " ":
                                    dupl_check_list.append(item.replace(" ",""))
                                else:
                                    dupl_check_list.append(item)
                            except:
                                dupl_check_list.append(item)

                        dupl_result = checkIfDuplicates_1(dupl_check_list)
                        if(dupl_result):
                            data = "Type: categorical" + "<br>"
                            dupl_dict = {k:dupl_check_list.count(k) for k in dupl_check_list}
                            
                            keys = [] 
                            values = [] 
                            items = dupl_dict.items() 
                            for item in items: 
                                keys.append(item[0]), values.append(item[1])
                            data = data + "category_count: " + str(len(values)) + "<br>"
                            data = data + "category_list: " + str(keys) + "<br>"
                            data = data + "category_freqs: " + str(values)
                        else:
                            data = "char"
                    elif(data == "s_char"):
                        String = "p" + num_df[i] + "p"
                        val = re.findall("\d+\.\d+|\d+|\d*\D+", String)
                      
                        data = ""
                        prefix = val[0].replace("p","")
                        if(prefix == ""):
                            data = "prefix : empty"+"<br>"
                        else:
                            data = "Prefix : "+prefix+"<br>"

                        surfix = val[2].replace("p", "")
                        number = val[1]                                   

                        data = data + "type : " + type_data(number)+"<br>"

                        if(surfix == ""):
                            data = data + "surfix : empty"+"<br>"
                        else:
                            data = data +"surfix : "+ surfix+"<br>"

                        if(type_data(number) == "int"):
                            number_list.append(int(number))
                        elif (type_data(number) == "float" or type_data(number) == "floating_with_2_decimal_places"):
                            number_list.append(float(number))

                        if i == (len(num_df)-1):
                            data =  data + "max : " +str(max(number_list))+"<br>"
                            data =  data + "min : " + str(min(number_list))+"<br>"
                            data =  data + "av : " + str(significant_detect(sum(number_list)/len(number)))+"<br>"
                        
                    else:
                        print("don't find data")
                    data = data + ""
                else:
                    data = "mix"
                    #break                             
                    
            state_value.append(data)
            
    df_state=df_state.append(pd.Series(state_value,index=header),ignore_index=True)   
   
    cols = list(data_frame)
    state_value.pop(0)
    for k in range(0, len(data_frame.index)):
        pro_value = [" "]
        
        for i in range(0,len(cols)):
            #pro_value.append(data_frame[cols[i]][k])
            if (state_value[i].startswith("type: range")):
                print(data_frame[cols[i]][k])
                
                #pro_value.append(data_frame[cols[i]][k])
                rep = data_frame[cols[i]][k].replace('-', " to ")
                val = re.findall("\d+\.\d+|\d+|\d*\D+", rep)
                rep1 = ''
                val.insert(-1," ")
                for item in val:
                    rep1 = rep1 + item
                print(rep)
                print("************")

                res = [j for j in rep1.split() if type_data(j) == "int" or type_data(j) == "floating_with_2_decimal_places" or type_data(j) == "float"]
                
                #range_val = str(res[0]) + "-" + str(res[1])
                try:
                    range_val = "<table style ='width:100%;'><tr ><td style = 'width:50%;border-right: 1px solid #808080;'>"+str(res[0])+"</td><td>"+str(res[1])+"</td></tr></table>"
                except:                    
                    range_val = "<table style ='width:100%;'><tr ><td style = 'width:50%;border-right: 1px solid #808080;'>"+str(res[0])+"</td><td>"+str(res[0])+"</td></tr></table>"

                print(range_val)
                pro_value.append(range_val)
                #pro_value.append(range_val)
            elif(state_value[i].startswith("prefix")):
                #pro_value.append(data_frame[cols[i]][k])
                
                p_text ="p" + data_frame[cols[i]][k] + "P"
                
                val = re.findall("\d+\.\d+|\d+|\d*\D+", p_text)
                try:                    
                    temp_val = val[1]
                except:
                    pass
                pro_value.append(temp_val)
                
            else:           
                pro_value.append(data_frame[cols[i]][k])                           
        
        pro_df = pro_df.append(pd.Series(pro_value, index=header), ignore_index=True) 
    
    df_state = df_state.append(pro_df) #2020/11/2

    #----------------------- footer part ------------------------------    
    pro_value1 = ["Type:Total"]
    pro_value1.append("Total")
    for i in range(1,len(cols)):
        pro_value1.append(" ")           
        
    pro_df1 = pro_df1.append(pd.Series(pro_value1, index=header), ignore_index=True)
   
    df_state = df_state.append(pro_df1) ##2020/11/2
  
    df_state_result = df_state.to_html(escape=False)

#============= detection duplicate value in a list =================
def checkIfDuplicates_1(listOfElems):
    ''' Check if given list contains any duplicates '''
    if len(listOfElems) == len(set(listOfElems)):
        return False
    else:
        return True
#============== calculate standard deviations =======================
def calc_stdev(data_list, data_av):
    sum  = 0
    for i in range(0,len(data_list)):
        sum = sum + pow((data_list[i] - data_av),2)
    st_dev = math.sqrt(sum/len(data_list))

    return st_dev
#================= significant_detect ================================
def significant_detect(num):
    if num > 1:
        return float(format(num,'.2f'))
    else:
        try:
            z_cnt = int(abs(math.log10(num)))+2
        except:
            return 0
        temp = '.' + str(z_cnt) + 'f'
        return float(format(num,temp))
        
#================= get type of string data ================================
def type_data(string):
    try:
        int_val = int(string)
        data = "int"
        return data
    except ValueError:
        try:
            float_val = float(string)
            if(len(string.split(".")[1]) == 2):
                data = "floating_with_2_decimal_places"
                return data
            else:
                data = "float"
                return data
        except ValueError:
            if is_date(string)== True:
                data = "date"
                return data
            else:
                String = "p" + string + "p"                   

                val = re.findall("\d+\.\d+|\d+|\d*\D+", String)
                
                if len(val) == 1:
                    data = "char"
                    return data
                else:
                    #======= detection range ==================
                    s = re.sub(r"\s+","",String)
                    match = re.match(r"([a-z]+)([0-9]+)(to|-)([0-9]+)([a-z]+)", s, re.I)
                    if match:
                        data = "match"
                        return data                    
                    else:
                        data = "s_char"
                        return data                    
#============ detection date ====================================
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
    app.run(debug=True,host='0.0.0.0', port='5000')
