# -*- coding: utf-8 -*-

import pandas as pd
from flask import Flask, render_template, request  
import sys


app = Flask(__name__)             # create an app instance

data = pd.read_csv("https://raw.githubusercontent.com/joe608939/test/master/hklit_test.csv")
author_data = pd.read_csv('https://raw.githubusercontent.com/joe608939/test/master/(Draft)%20HKLit%20Author%20list%202019_v.6_20190920.csv')

def generate_statistics(new_df, all_name_of_input_writer):
    temp_df = new_df
    temp_df.insert(temp_df.shape[1], 'Number of times being metioned in title', '')
    temp_df.insert(temp_df.shape[1], 'Number of times being mentioned in the fulltext', '')
    temp_df['Number of times being metioned in title'] = temp_df['Number of times being metioned in title'].astype(object)
    temp_df['Number of times being mentioned in the fulltext'] = temp_df['Number of times being mentioned in the fulltext'].astype(object)
    if temp_df.shape[0] == 0:
        return temp_df
    else:
        df_column = temp_df.keys()
        df_2 = pd.DataFrame(columns = df_column)
        title_count_match_for_each_name = {}
        full_text_count_match_for_each_name = {}
        for element in all_name_of_input_writer:
            title_count_match_for_each_name[element] = 0
            full_text_count_match_for_each_name[element] = 0
        for i in range(0, temp_df.shape[0]): 
            title = temp_df.iloc[i]['title']
            full_text = temp_df.iloc[i]['fullText']
            if str(title) == 'nan':
                title = ' '
            if str(full_text) == 'nan':
                full_text = ' '
            temp_mentioned_in_title = []
            temp_mentioned_in_fulltext = []
            for element in all_name_of_input_writer:
                title_count_match_for_each_name[element] += title.count(element)
                full_text_count_match_for_each_name[element] += full_text.count(element)
                temp_mentioned_in_title.append(element + ' : ' + str(title.count(element)))
                temp_mentioned_in_fulltext.append(element + ' : ' + str(full_text.count(element)))
            temp_df['Number of times being metioned in title'][i] = temp_mentioned_in_title
            temp_df['Number of times being mentioned in the fulltext'][i] = temp_mentioned_in_fulltext
        all_mentioned_in_title = []
        all_mentioned_in_fulltext = []
        for element in all_name_of_input_writer:
            all_mentioned_in_title.append(element + ' : ' + str(title_count_match_for_each_name[element]))
            all_mentioned_in_fulltext.append(element + ' : ' + str(full_text_count_match_for_each_name[element]))
        df_2 = pd.DataFrame(columns = df_column)
        df_2 = df_2.append({'url' : 'total number of articles retrieved' , 'Number of times being metioned in title' : temp_df.shape[0]} , ignore_index=True)
        df_2 = df_2.append({'url' : 'total number of mention in title' , 'Number of times being metioned in title' : all_mentioned_in_title} , ignore_index=True)
        df_2 = df_2.append({'url' : 'total number of mention in fulltext' , 'Number of times being metioned in title' : all_mentioned_in_fulltext} , ignore_index=True)
        df_2 = df_2.fillna(' ')
        temp_df = pd.concat([temp_df, df_2])
        return temp_df

def generating_combined_result_file(input_get_statistics, search_field, data, name_list):
    list_for_name_and_frequency = []
    df = pd.DataFrame()
    for each_name in name_list:
        if search_field == 'author':
            temp_df = data[data["creator"].str.contains(each_name, na = False)]
        elif search_field == 'content':
            temp_df = data[~(data["creator"].str.contains(each_name, na = False)) & ((data["title"].str.contains(each_name, na = False)) | (data["fullText"].str.contains(each_name, na = False)))]
        list_for_name_and_frequency.append(each_name + ' : ' + str(temp_df.shape[0])) 
        df = pd.concat([df,temp_df])
    df = df.reset_index()
    if input_get_statistics == "T":
        df = generate_statistics(df, name_list)  
    return df


def check_name(name_str):
    name_list = []
    name_list.append(name_str)
    for i in range(0,author_data.shape[0]):
        temp_name_list = list(set(author_data.iloc[i]['Be Known as ':]))
        temp_name_list = [str(x) for x in temp_name_list if str(x) != 'nan' and not str(x).isspace() and str(x)!='same as column 1']    
        if name_str in temp_name_list:
            name_list = name_list + temp_name_list
    name_list = list(set(name_list))
    return name_list

def get_result_for_creator_name(data,name):
    df = data[data["creator"].str.contains(name, na = False)]
    df = df.reset_index()
    return df

def get_result_for_content(data,name):
    df = data[~(data["creator"].str.contains(name, na = False)) & ((data["title"].str.contains(name, na = False)) | (data["fullText"].str.contains(name, na = False)))]
    df = df.reset_index()
    return df

    

@app.route("/",methods = ['GET','POST'])                   # at the end point /
def hello():  
    if request.method == 'POST':
        name = request.form['author_name']
        search_field = request.form['search_field']
        get_stat = request.form['get_stat']
        result = get_result_for_title(data,name)
        return render_template('result.html',  tables=[result.to_html(classes='data')], titles=result.columns.values)
              # call method hello       # which returns "hello world"

    return render_template('ask_for_input.html')              # call method hello       # which returns "hello world"

@app.route("/send",methods = ['GET','POST'])                   # at the end point /
def print_result():  
    if request.method == 'POST':
        name = request.form['author_name']
        search_field = request.form['search_field']
        get_stat = request.form['get_stat']
        get_name_list = request.form['get_name_list']
        separte_name = request.form['separte_name']
        if get_name_list =='F':
            name_list = []
            name_list.append(name)
        elif get_name_list == 'T':
            name_list = check_name(name)
        dataframe_collection = {}        
        if search_field == 'author':
            if separte_name =='T':
                for name in name_list:
                    result = get_result_for_creator_name(data,name)
                    if get_stat == 'T':
                        result = generate_statistics(result,name_list)
                    dataframe_collection[name] = result
            elif separte_name =='F':
                result = generating_combined_result_file(get_stat, search_field, data, name_list)
                dataframe_collection[name] = result
        elif search_field == 'content':
            if separte_name == 'T':
                for name in name_list:
                    result = get_result_for_content(data,name)
                    if get_stat == 'T':
                        result = generate_statistics(result,name_list)
                    dataframe_collection[name] = result
            elif separte_name =='F':
                result = generating_combined_result_file(get_stat, search_field, data, name_list)
                dataframe_collection[name] = result
        return render_template('result.html',dataframe_collection = dataframe_collection) 
if __name__ == "__main__":        # on running python app.py
    app.run()           