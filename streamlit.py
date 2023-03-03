#coding:utf-8

import streamlit as st
import numpy as np
import sqlite3
import csv
import datetime
import pandas as pd

class Insert:
    def __init__(self, csv_path):
        self.path = csv_path

    def insert_data(self):
        # 连接数据库
        database=sqlite3.connect(r'./fraud.db') 
        if database:
            print("Read file success")
        else:
            print("Read file fail") 
        db = database.cursor()

        # 读取 CSV 文件
        with open(self.path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')

        # CSV 格式 Social_media、Date、Type、Details、NameValue
            for row in reader:
                social_media = row[0]
                date = row[1]
                date_format = '%Y-%m-%d'
                time_obj = datetime.datetime.strptime(date, date_format)
                # formatted_time = time_obj.strftime(date_format)
                fraud_type = row[2]
                details = row[3]
                names = row[4:]

                person_data = (social_media, date, fraud_type, details)
                 # 插入数据库的sql文本
                person_sql = '''INSERT INTO Person (FraudType, FDate, Social_media, Details) VALUES (?,?,?,?);'''
                
                # 数据库插入
                db.execute(person_sql, person_data)
                
                last_insert_id = db.lastrowid
                name_sql = '''INSERT INTO Name (PersonID, NameValue) VALUES (?, ?);'''
                for name in names:
                    name_data = (last_insert_id, name)
                    db.execute(name_sql, name_data)
                database.commit()
        db.close()
        

class Query:
    def __init__(self, db):
        self.db = db
        self.ids = []

    def FraudRecordQuery(self):
        records = []
        query_sql = '''SELECT * FROM Person where PersonID=?;'''
        for id in self.ids:
            ret = self.db.execute(query_sql, (id,))
            data = ret.fetchall()[0]
            records.append(list(data)[1:])
        return records
        
    def AliasNameQuery(self, keyword):
        query_sql = '''SELECT PersonID FROM Name where NameValue LIKE ?;'''
        keyword_value = ('%'+keyword+'%',)
        ret = self.db.execute(query_sql, keyword_value)

        for id in ret:
            self.ids.append(id[0])
        
        results = []
        for personid in self.ids:
            query_name_sql = '''SELECT NameValue FROM Name where PersonID=?;''' 
            alias_names = self.db.execute(query_name_sql, (personid,))
            names = alias_names.fetchall()
            for name in names:
                results.append(name[0])
            
        return results

    def CasnumberQuery(self):
        db = conn_db()
        cursor = db.cursor()

        result_list_0=[]
        row=0
        cas_query_0='''SELECT * FROM Name;'''
        # cas_query_1=cas_query_0.replace('condition',str(self.__casno))
        result_0 = db.execute(cas_query_0)

        for chem in result_0:#解包到列表中
            result_list_0.append(chem)
        result_set_0=set(result_list_0)#转换列表为集合（可去重）
        return result_list_0
        if len(result_set_0)==0:    #如果列表为空，意味着未检索到结果
            return None
        else:
            leg_query='''SELECT leg_cn,leg_en,pub_date FROM CNLAWS WHERE legid='LEG_X';'''
            leg_arr=np.empty((len(result_set_0)+1,3),object)#为储存查询结果，预制了一个空数组
            leg_arr[0,:]=(['法规中文名称','English Title','发布日期'])#标题列
            for leg_id in result_set_0: #将数据库检索结果写入数组
                leg_query_1=leg_query.replace('LEG_X',leg_id)
                leg_result_1=chemicals.execute(leg_query_1).fetchone()
                row+=1
                leg_arr[row,:]=([leg_result_1[0],leg_result_1[1],leg_result_1[2]])
            return leg_arr#返回数组

def findillegalchar(casnum):
    '''
    检验查询输入字符，防止注入攻击
    '''
    safetynum=['0','1','2','3','4','5','6','7','8','9','-']
    for char in casnum:
        if char not in safetynum:            
            return char


# if whichcasno!='':
#     if findillegalchar(whichcasno):
#         st.write(whichcasno,'包含非法字符：',findillegalchar(whichcasno))
#     else:
#         st.write(whichcasno,'的关联法规为：')

# 数据库连接    
def conn_db():
    db = sqlite3.connect(r'./fraud.db') 
    if db:
        st.write("Read file success")
    else:
        st.write("Read file fail") 
    return db

def framework():
    st.title('数据库查询')
    db = conn_db()
    cursor = db.cursor()
 
    keyword = st.text_input('输入ID或名称', value='', max_chars=None, key=None, type='default', help='输入小红书、微信、支付宝或中文姓名')

    if keyword == '':
        return
    
    query_test = Query(db)
    df_result_0 = query_test.AliasNameQuery(keyword)
    df_result_1 = query_test.FraudRecordQuery()

    fraud_record = pd.DataFrame(df_result_1, columns = ('平台', '日期', '诈骗类型', '细节'))
    alias = pd.DataFrame(df_result_0, columns = ('别名',))
    # st.write(df_result_0) # 检查结果是否为空
    if len(df_result_0) != 0:
        st.subheader('包含关键字的诈骗记录')
        st.table(data=fraud_record)
        st.subheader('搜索到以下关联昵称或姓名')
        st.table(data=alias) 
    else:
        st.header('oops!未检索到关联数据')


if __name__ == '__main__':
    framework()
    # 数据插入
    # data = Insert('file.csv')
    # data.insert_data()
