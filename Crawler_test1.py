# -*- coding: utf-8 -*-
"""
Created on Wed May 22 12:07:30 2024

@author: Brian
"""
import tqdm
import pandas
import requests
import urllib3


from tqdm import tqdm
import pandas as pd
import requests
import glob
import time
import os
import urllib3
import csv
import json
import re


def save_result_page():
    id_number = ''
    Inventor_name = ''
    num =''
    d = pd.DataFrame(columns = ["Failed_Number","Application Number"]) 
    data = pd.DataFrame(columns = ["Number","Application Number"]) 
    df = pd.read_csv("D:/test/new_result無亂碼.csv")    
    for rows in tqdm(df.index):
    
        num = ''.join([y for y in df["Display Key"][rows] if y.isdigit()])
        id_number = num[:-1]
        """
        if len(str(num)) > 10:
            id_number = num[-6:]
        else:
            id_number = num[:6]
        # id_list = set([patent_id.strip() for patent_id in open("id/id_A", 'r')])
        
        Inventors = df["Inventors"][rows]
        Total_Inventors = Inventors.split(";;")
        Inventor_name = Total_Inventors[0]
        """
        # for id_number in tqdm(id_list):
        if os.path.exists("result_id_A/%s.html" % id_number) == True:
            continue

        result_url = 'https://appft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%%2Fnetahtml%%2FPTO%%2Fsearch-adv.html&r=1&f=G&l=50&d=PG01&p=1&S1=%s.PGNR.&OS=DN/%s&RS=DN/%s' % (id_number, id_number, id_number)

        while True:
            try:
                headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
                #response = urllib3.PoolManager().request('GET', result_url, preload_content=False, timeout=10)
                result = requests.get(result_url, headers=headers, timeout=10)
                #result = response.data.decode('utf-8')
                #response.close()  # 注意關閉response
                if judge_status(result.status_code, id_number) == True:
                    with open('%s.html' % id_number, 'w') as file:
                        file.write(result.text)
                        data = data.append({'Number': id_number,'Application Number': num}, ignore_index=True)
                        #file.write(result)
                        data.to_csv('D:/test/data.csv')
                        time.sleep(3)

                break
            except requests.Timeout:
                print("Timeout! id = %s" % id_number)

            except requests.ConnectionError as e:
                print("Connection failure : " + str(e))
                print("Connection Error! id = %s" % id_number)
                d = d.append({'Failed_Number': id_number,'Application Number': num}, ignore_index=True)
                d.to_csv('D:/test/failed.csv')
                time.sleep(10)
                #continue
                break
            except urllib3.exceptions.HTTPError as e:
                print('Request failed:', e.pool)
                print("\n" + "Connection Error! id = %s" % id_number)
                d = d.append({'Failed_Number': id_number,'Application Number': num}, ignore_index=True)
                d.to_csv('D:/test/failed.csv')
                #time.sleep(10)
                #continue
                break
            
    d.to_csv('D:/test/failed.csv')
    data.to_csv('D:/test/data.csv')

def judge_status(status_code, params):
    if 400 <= status_code <= 499:
        print("Error Querying Format or Value: {}".format(params))
        return False
    elif status_code >= 500:
        print("Server error when querying {} ! Maybe exceeding the maximum API request size (1GB).".format(params))
        return False
    else:
        return True


def extract_data_from_page(filename, dataframe):
    # files = "result_id_A/4922925.html"
    pattern1_start = "<BR><CENTER><B>Abstract</B></CENTER>"
    pattern2_start = "<CENTER><b><i>Claims</b></i></CENTER>"
    pattern_end = "<HR>"
    Inventors_start = '<TR> <TD VALIGN="TOP" ALIGN="LEFT" WIDTH="10%">Inventors:</TD>'
    Inventors_end = "</TD>"
    Applicant_start = '</TR> <TABLE WIDTH="100%"> <TR><TH scope="row" VALIGN="TOP" ALIGN="LEFT" WIDTH="10%">Applicant: </TH><TD ALIGN="LEFT" WIDTH="90%"> <TABLE> <TR> <TH scope="column" ALIGN="center">Name</TH> <TH scope="column" ALIGN="center">City</TH> <TH scope="column"'
    Applicant_end = "</AANM> --> </TD></TR>" 
    Assignee_start = '<TR> <TD VALIGN="TOP" ALIGN="LEFT" WIDTH="10%">Assignee:</TD>'
    Assignee_end = "</TD>" 
    
    with open(filename, 'r') as f:
        content = [line for line in f.readlines()]
        abstract = []
        claim = []
        Inventors = []
        Applicants = []
        Assignees = []

        i = 0
        total_line = len(content)
        while i < total_line:
            if pattern1_start in content[i]:
                i += 1
                while pattern_end not in content[i]:
                    if "</p>" not in content[i]:
                        abstract.append(str(content[i]).strip().strip('<p>'))
                    i += 1
            # "<p>" not in content[i] and
            """
            if pattern2_start in content[i]:
                claim.append(str(content[i]).strip('<CENTER><b><i>Claims</b></i></CENTER> <HR> <BR><BR>'))
                i += 1
                while pattern_end not in content[i]:
                    claim.append(str(content[i]).strip())
                    i += 1
            """
            if Inventors_start in content[i]:
                #Inventors.append(str(content[i]).strip('<TR> <TD VALIGN="TOP" ALIGN="LEFT" WIDTH="10%">Inventors:</TD> <TD ALIGN="LEFT" WIDTH="90%">'))
                i += 2
                while Inventors_end not in content[i]:
                    Inventor = re.sub("\<B>|\</B>|\<I>|\</I>|\;","",str(content[i]))
                    Inventor = re.sub("\(.*?\\)","",Inventor)
                    Inventor = Inventor.strip(';').strip()
                    Inventors.append(Inventor)
                    i += 1
            if Applicant_start in content[i]:
                #Inventors.append(str(content[i]).strip('<TR> <TD VALIGN="TOP" ALIGN="LEFT" WIDTH="10%">Inventors:</TD> <TD ALIGN="LEFT" WIDTH="90%">'))
                i += 4
                while Applicant_end not in content[i]:
                    if '</TD><TD ALIGN="center">' in content[i]:
                        i += 1
                    elif '</TD><TD> </TD> </TR> </TABLE> <!--' in content[i]:
                        i += 1
                    else:
                        Applicant = re.sub("\~AANM|\~AACI|\~AAST|\~AACO|\<br>|\<AANM>","",str(content[i]))
                        Applicant = Applicant.replace('</B> </TD><TD> ',';;')
                        Applicant = Applicant.strip(';').strip()
                        Applicants.append(Applicant)
                        i += 1
            if Assignee_start in content[i]:
                #Inventors.append(str(content[i]).strip('<TR> <TD VALIGN="TOP" ALIGN="LEFT" WIDTH="10%">Inventors:</TD> <TD ALIGN="LEFT" WIDTH="90%">'))
                i += 2
                while Assignee_end not in content[i]:
                    Assignee = re.sub("\<B>|\</B>|\<BR>","",str(content[i]))
                    Assignee = Assignee.strip(';').strip()
                    Assignees.append(Assignee)
                    i += 1       
            i += 1
            
    abstract = ''.join(abstract)
    claim = ''.join(claim).replace("<BR>", "")
    Inventors = list(filter(None, Inventors)) 
    Inventors = ';;'.join(Inventors)
    Applicants = list(filter(None, Applicants)) 
    Applicants = ';;'.join(Applicants)
    Assignees = list(filter(None, Assignees)) 
    Assignees = ';;'.join(Assignees)
    
    basename = os.path.basename(filename)
    
    results = {
        "patent_id": str(os.path.splitext(basename)[0]),
        "Inventors": Inventors,
        "Applicants": Applicants,
        "Assignees": Assignees
    }

    dataframe = dataframe.append(results, ignore_index=True)

    return dataframe


def parse_and_merge_data():
    files = [i for i in glob.iglob("*.html")]
    #data = pd.DataFrame(columns=["patent_id", "abstract", "claim", "Inventors", "Applicants", "Assignees"])
    data = pd.DataFrame(columns=["patent_id", "Inventors", "Applicants", "Assignees"])

    for file in tqdm(files):
        data = extract_data_from_page(file, data)

    data["patent_id"] = data["patent_id"].astype(str)
    data.to_csv("result.csv", index=False)
    data.to_json(r'result.json')

    df_json = data.to_json(orient='records', force_ascii=False)
    ss = json.loads(df_json)

    """
    with open("result/result.json", 'w') as f:
        f.write(json.dumps(ss, indent=4))
        f.write('\n')
    f.close()
    """

def seperate_abnormal_and_normal():
    data = pd.read_csv("result/id_A.csv", sep=",")
    data["patent_id"] = data["patent_id"].astype(str)
    no_result = data[data.isnull().any(axis=1)]
    result = data[data.notnull().any(axis=1)]
    abnormal_id = list(no_result.patent_id)

    with open("abnormal_id.txt", 'w') as f:
        for number in abnormal_id:
            f.write("%s\n" % number)

    result.to_csv("result/normal_id_A.csv", index=False)


if __name__ == "__main__":
    #save_result_page()  # fetch all request which contained id
    parse_and_merge_data() # parse and merge all html files

    # seperate_abnormal_and_normal()# split normal and abnormal id
