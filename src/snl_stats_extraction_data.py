import itertools
import re
import os, sys

script_path=os.path.realpath(os.path.dirname("IBPY"))
os.chdir(script_path)
sys.path.append("..")

import json
import pympi
import numpy as np
from IBPY.interaction_analysis import *
from src.preprocessing import *
from IBPY.utils import *
from IBPY.db import *
from IBPY.extract_data import *
import pandas as pd
from src.json_creation import create_json_from_directory

#JSON____________________________________________________________________
# Creates JSON file with the directory structure and annotation information
create_json_from_directory()
current_dir=os.getcwd()
json_file_path=os.path.join(current_dir, 'data.json')
#________________________________________________________________________

def get_parameters_tag():

    try :
        current_dir=os.getcwd()
        json_file_path2=os.path.join(current_dir, 'base_data.json')
        if os.path.exists(json_file_path2):
            # Read the data from the JSON file
            with open(json_file_path2, 'r') as f:
                parameters1=json.load(f)
        tier_lists=parameters1["TIER_LISTS"]
        tiers = {}
        
        for tier_name, tier_list in parameters1["TIER_LISTS"].items():
            tiers[f"intensity_{tier_name.lower()}"]=tier_list
        return tier_lists, tiers
    except :
        return None, None

def get_parameters():
    """ This function get the parameters from the json file.
    
    Args:
        None
    Returns:
        A tuple with the parameters
    """
    if os.path.exists(json_file_path):
        # Read the data from the JSON file
        with open(json_file_path, 'r') as f:
            parameters=json.load(f)
    else:
        # Handle the case when the JSON file doesn't exist
        print("data.json file not found.")
    DIR=parameters["FOLDER_PATHS"]["DIR"]
    databases_pair_paths=parameters["DATABASES_PAIR_PATHS"]
    databases_paths=parameters["DATABASES_PATHS"]
    tier_lists=parameters["TIER_LISTS"]
    databases={}
    databases_pairs={}
    tiers={}
    # Browsing pairs datasets
    for db_name, db_path in parameters["DATABASES_PAIR_PATHS"].items():
        databases_pairs[db_name]=db_path
    # Browsing datasets
    for db_name, db_path in parameters["DATABASES_PATHS"].items():
        databases[db_name]=db_path
    # Browsing expression tiers
    for tier_name, tier_list in parameters["TIER_LISTS"].items():
        tiers[f"intensity_{tier_name.lower()}"]=tier_list
    return DIR, databases_pair_paths, databases_paths, tier_lists, databases, databases_pairs, tiers

def correct_dict_role_smiles(dict_, listpaths, string):
    """ This function set to 0 intensities that doesn't exist in our eaf files for smiles.
    
    Args:
        dict_ (list): list of the tuple we have to fix
        listpaths (list): list of eaf paths of a database
        string (str): nae of the dataset concerned
    Returns:
        A list with previously non-existent intensities set to 0   
    """
    dict_sub=[]
    dict_present_subject=[]
    label_present_subject=[]
    DIR, databases_pair_paths, databases_paths, tier_lists, databases, databases_pairs, tiers=get_parameters()
    subjects=[i for i in range(1, len(listpaths)+1)]
    for _ in dict_: dict_sub.append(_[0])
    for subject in subjects:
        if subject not in dict_sub:
            for i in tier_lists["Smiles"]:
                dict_.append((subject, string, i, 0, 0, dict_[0][5]))
        else:
            for _ in dict_: 
                if _[0]==subject: 
                    dict_present_subject.append(_) 
                    for i in dict_present_subject: label_present_subject.append(i[2]) 
                    for l in tier_lists["Smiles"]:
                        if l not in label_present_subject:
                            dict_.append((subject, string, l, 0, 0, dict_[0][5]))
    return dict_

def correct_dict_role_laughs(dict_, listpaths, string):
    """ This function set to 0 intensities that doesn't exist in our eaf files for laughs.
    
    Args:
        dict_ (list): list of the tuple we have to fix
        listpaths (list): list of eaf paths of a database
        string (str): nae of the dataset concerned
    Returns:
        A list with previously non-existent intensities set to 0   
    """
    dict_sub=[]
    dict_present_subject=[]
    label_present_subject=[]
    DIR, databases_pair_paths, databases_paths, tier_lists, databases, databases_pairs, tiers=get_parameters()
    subjects=[i for i in range(1,len(listpaths)+1)]
    for _ in dict_: dict_sub.append(_[0])
    for subject in subjects:
        if subject not in dict_sub:
            for i in tier_lists["Laughs"]:
                dict_.append((subject, string, i, 0, 0, dict_[0][5]))
        else: 
            for _ in dict_: 
                if _[0]==subject: 
                    dict_present_subject.append(_) 
                    for i in dict_present_subject: label_present_subject.append(i[2]) 
                    for l in tier_lists["Laughs"]:
                        if l not in label_present_subject:
                            dict_.append((subject, string, l, 0, 0, dict_[0][5]))
    return dict_

def correct_dict_role_tier(dict_, listpaths, string, tier):
    """ This function set to 0 intensities that doesn't exist in our eaf files for tier.
    
    Args:
        dict_ (list): list of the tuple we have to fix
        listpaths (list): list of eaf paths of a database
        string (str): name of the dataset concerned
        tier (str): name of the tier concerned
    Returns:
        A list with previously non-existent intensities set to 0    
    """

    real_tier_lists , real_tiers = get_parameters_tag()

    dict_sub=[]
    dict_present_subject=[]
    label_present_subject=[]
    DIR, databases_pair_paths, databases_paths, tier_lists, databases, databases_pairs, tiers=get_parameters()
    subjects=[i for i in range(1, len(listpaths)+1)]
    for _ in dict_: dict_sub.append(_[0])
    for subject in subjects:
        if subject not in dict_sub:
            for i in real_tier_lists[tier]['Intensities']:
                dict_.append((subject, string, i, 0, 0, dict_[0][5]))
        else:
            for _ in dict_: 
                if _[0]==subject: 
                    dict_present_subject.append(_) 
                    for i in dict_present_subject: label_present_subject.append(i[2])
                    for l in real_tier_lists[tier]['Intensities']:
                        if l not in label_present_subject:
                            dict_.append((subject, string, l, 0, 0, dict_[0][5]))
    return dict_

def get_SLdict(root):
    """ Return a list of S&L with the label corresponding to the Smiles_0 and Laughs_0 dictionnaries.
    
    Args:
        root (str): Path of the file
    Returns:
        lst (list): List of S&L
    """
    lst1=get_Sdict(root)
    lst2=get_Ldict(root)
    to_dict=read_eaf_to_dict(root, mark=True, tiers=None)
    lst=to_dict["S&L_0"]
    nb=0
    for _ in range (0, len(lst),1): 
        for j in lst1:
            if (lst[_][0]==j[0]) and (lst[_][1]==j[1]):
                nb+=1
                y=list(lst[_])
                y[2]='S'
                lst[_]=tuple(y)
    #print(f"Nb smiles in S&L : {nb}", lst)
    nb=0
    for _ in range (0, len(lst),1): 
        for j in lst2:
            if (lst[_][0]==j[0]) and (lst[_][1]==j[1]):
                nb+=1
                y=list(lst[_])
                y[2]='L'
                lst[_]=tuple(y)
    #print(f"Nb laughs in S&L : {nb}", lst)
    return lst

def get_TCdict(root, track, check):
    """ Return a list of Track & Check tier with the label corresponding to the track and check tiers dictionnaries.
    
    Args:
        root (str): Path of the file
        track (str): Name of the track tier
        check (str): Name of the check tier
    Returns:
        lst (list): List of Track & Check
    """
    lst1=get_tier_dict(root, track)
    lst2=get_tier_dict(root, check)
    to_dict=read_eaf_to_dict(root, mark=True, tiers=None)
    lst=to_dict[track] + to_dict[check]
    nb=0
    for _ in range (0, len(lst),1):
        for j in lst1:
            if (lst[_][0]==j[0]) and (lst[_][1]==j[1]):
                nb+=1
                y=list(lst[_])
                y[2]=track
                lst[_]=tuple(y)
    #print(f"Nb track in TC : {nb}", lst)
    nb=0
    for _ in range (0, len(lst),1):
        for j in lst2:
            if (lst[_][0] == j[0]) and (lst[_][1] == j[1]):
                nb+=1
                y=list(lst[_])
                y[2]=check
                lst[_]=tuple(y)
    #print(f"Nb check in TC : {nb}", lst)
    return lst

def get_Sdict(root):
    """ Give the list of smiles from a file.
    
    Args: 
        root (str): path of the file
    Returns:
        lst (list): list of smiles
    """
    to_dict=read_eaf_to_dict(root, mark=True, tiers=None)
    lst=to_dict["Smiles_0"]
    return lst

def get_Ldict(root):
    """ Give the laughs's list from a file.
    
    Args: 
        root (str): path of the file
    Returns:
        lst (list): list of laughs
    """
    to_dict=read_eaf_to_dict (root, mark=True, tiers=None)
    lst=to_dict["Laughs_0"]
    return lst

def get_Rdict(root):
    """ Give the role's list from a file.
    
    Args: 
        root (str): path of the file
    Returns:
        lst (list): list of roles
    """
    to_dict=read_eaf_to_dict(root, mark=True, tiers=None)
    lst=to_dict["Role"]
    return lst

def get_tier_dict(root, tier):
    """ Retrieve the list of a specific tier from a file.
    
    Args:
        root (str): Path of the file
        tier (str): Tier name
    Returns:
        list: List of the specified tier from the file
    """
    to_dict=read_eaf_to_dict(root, mark=True, tiers=None)
    lst=None
    lst = to_dict[tier]
    return lst

def get_tier_dict_by_express(root, tier):
    """ Retrieve the list of a specific tier from a file.
    
    Args:
        root (str): Path of the file
        tier (str): Tier name
    Returns:
        list: List of the specified tier from the file
    """
    real_tier_lists , real_tiers = get_parameters_tag()
    to_dict = read_eaf_to_dict(root, mark=True, tiers=None)
    if real_tier_lists[tier]['Replace_Value'] != "":
        for i, item in enumerate(to_dict[tier]):
            if item[2] != "":
                to_dict[tier][i] = (item[0], item[1], real_tier_lists[tier]['Replace_Value'])
            else:
                to_dict[tier][i] = (item[0], item[1], "No_" + real_tier_lists[tier]['Replace_Value'])
    lst = to_dict[tier]
    # print("La liste : ", lst)
    return lst

def get_IR_list(root, expression, intensity):
    """ Give the list of tier from a file for a given entity or a given role.
    
    Args:
        root (str): path of the file
        expression (str): tier name
        intensity (str): entity or role of the tier
    Returns:
        lst (list): list of tier
    """
    tier=get_tier_from_file(root, expression, intensity, 'base_data')
    lst=tier[expression]
    return lst

def get_tier_dict_folder(filespaths, database, tier):
    """ Retrieve the dataframe of a specified tier from a folder.
    
    Args:
        filespaths (list): List of file paths in the folder
        database (str): Dataset name (e.g., "ccdb", "ifadv", "ndc")
        tier (str): Tier name to retrieve the data from
    Returns:
        A list of tuples and the column names
    """
    startime, endtime, label, subject, duration=([] for _ in range(5))
    s=1
    for file in filespaths:
        lst_=get_tier_dict(file, tier)
        eaf=pympi.Elan.Eaf(file)
        c=check_duration(eaf)
        for i in range(len(lst_)):
            subject.append(s)
            startime.append(lst_[i][0])
            endtime.append(lst_[i][1])
            with open('base_data.json') as json_file:
                data = json.load(json_file) 
            replace_value = data['TIER_LISTS'][tier]['Replace_Value'] 
            if data['TIER_LISTS'][tier]['Replace_Value'] != "" :
                if lst_[i][2] != "" :
                    label.append(data['TIER_LISTS'][tier]['Replace_Value'])
                else :
                    label.append(str("No_" + data['TIER_LISTS'][tier]['Replace_Value']))
            else :
                label.append(lst_[i][2])
            duration.append(c)
        s+=1  
    df=pd.DataFrame({'database': list_of_words(f"{database}", len(subject)), 'subject': subject, 'startime': startime, 
    'endtime': endtime, 'label': label, 'duration': duration})
    df['diff_time']=df['endtime']-df['startime']
    df.columns = ['database', 'subject', 'startime', 'endtime', 'label', 'duration', 'diff_time']
    df = df.reindex(columns=['startime', 'endtime', 'label', 'subject', 'diff_time', 'duration', 'database'])
    lst = df_to_list(df)
    col = ['startime', 'endtime', 'label', 'subject', 'diff_time', 'duration', 'database']
    return lst, col

def get_smiles_dict_folder(filespaths, database):
    """ Give the dataframe of smiles from a folder.
    
    Args: 
        filespaths (list): Cointain the filespath of the folder
        database (str): Dataset name (e.g., "ccdb", "ifadv", "ndc")
    Returns:
        A list of tuple and the list L=['startime', 'endtime', 'label', 'subject', 'diff_time', 'duration', 'database'] 
    """
    startime, endtime, label, subject, duration=([] for _ in range(5))
    s=1
    for _ in filespaths:
        lst_=get_Sdict(_)
        eaf=pympi.Elan.Eaf(_)
        c=check_duration(eaf)
        for i in range(len(lst_)):
            subject.append(s)
            startime.append(lst_[i][0])
            endtime.append(lst_[i][1])
            label.append(lst_[i][2])
            duration.append(c)
        s+=1
    df=pd.DataFrame({'database': list_of_words(f"{database}", len(subject)), 'subject': subject, 'startime': startime, 
    'endtime': endtime, 'label': label, 'duration': duration})
    df['diff_time']=df['endtime']-df['startime']
    df.columns=['database', 'subject', 'startime', 'endtime', 'label', 'duration', 'diff_time']
    df=df.reindex(columns=['startime', 'endtime', 'label', 'subject', 'diff_time', 'duration','database'])
    lst=df_to_list(df)
    col=['startime', 'endtime', 'label', 'subject', 'diff_time', 'duration', 'database']
    return lst, col

def get_laughs_dict_folder(filespaths, database):
    """ Give the dataframe of laughs from a folder.
    
    Args: 
        filespaths (list): Cointain the filespath of the folder
        database (str): Dataset name (e.g., "ccdb", "ifadv", "ndc")
    Returns:
        A list of tuple and the list L=['startime', 'endtime', 'label', 'subject', 'diff_time', 'duration', 'database'] 
    """
    startime, endtime, label, subject, duration=([] for _ in range(5))
    s=1
    n=1
    for _ in filespaths:
        lst_=get_Ldict(_)
        eaf=pympi.Elan.Eaf(_)
        c=check_duration(eaf)
        for i in range(len(lst_)):
            subject.append(s)
            startime.append(lst_[i][0])
            endtime.append(lst_[i][1])
            label.append(lst_[i][2])
            duration.append(c)
            n+=1
        s+=1
    df=pd.DataFrame({'database': list_of_words(f"{database}", len(subject)), 'subject': subject, 'startime': startime, 
    'endtime': endtime, 'label': label, 'duration': duration})
    df['diff_time']=df['endtime']-df['startime']
    df.columns=['database', 'subject', 'startime', 'endtime', 'label', 'duration', 'diff_time']
    df=df.reindex(columns=['startime', 'endtime', 'label', 'subject', 'diff_time', 'duration', 'database'])
    lst=df_to_list(df)
    col=['startime', 'endtime', 'label', 'subject', 'diff_time', 'duration', 'database']
    return lst, col

def get_smiles_dict_conv_folder(filespaths, database):
    """ Give the dataframe of smiles from a folder.
    
    Args: 
        filespaths (list): Cointain the filespath of the folder
        database (str): Dataset name (e.g., "ccdb", "ifadv", "ndc")
    Returns:
        A list of tuple and the list L=['startime', 'endtime', 'label', 'subject', 'diff_time', 'duration', 'database'] 
    """
    startime, endtime, label, subject, duration=([] for _ in range(5))
    s=1
    n=0
    for _ in range (len(filespaths)):
        lst_=get_Sdict(filespaths[_])
        eaf=pympi.Elan.Eaf(filespaths[n])
        eaf2=pympi.Elan.Eaf(filespaths[n+1])
        c=check_duration(eaf)
        c2=check_duration(eaf2)
        for i in range(len(lst_)):
            subject.append(s)
            startime.append(lst_[i][0])
            endtime.append(lst_[i][1])
            label.append(lst_[i][2])
            duration.append(max(c,c2))
        s+=1
        if ((s-1)%2==0):
            n+=2
    df=pd.DataFrame({'database': list_of_words(f"{database}", len(subject)), 'subject': subject, 'startime': startime, 
    'endtime': endtime, 'label': label, 'duration': duration})
    df['diff_time']=df['endtime']-df['startime']
    df.columns=['database', 'subject', 'startime', 'endtime', 'label', 'duration', 'diff_time']
    df=df.reindex(columns=['startime', 'endtime', 'label', 'subject', 'diff_time', 'duration', 'database'])
    lst=df_to_list(df)
    col=['startime', 'endtime', 'label', 'subject', 'diff_time', 'duration', 'database']
    return lst, col

def get_laughs_dict_conv_folder(filespaths, database):
    """ Give the dataframe of laughs from a folder.

    Args: 
        filespaths (list): Cointain the filespath of the folder
        database (str): Dataset name (e.g., "ccdb", "ifadv", "ndc")
    Returns:
        A list of tuple and the list L=['startime', 'endtime', 'label', 'subject', 'diff_time', 'duration', 'database'] 
    """
    startime, endtime, label, subject, duration=([] for _ in range(5))
    s=1
    n=0
    for _ in range (len(filespaths)):
        lst_=get_Ldict(filespaths[_])
        eaf=pympi.Elan.Eaf(filespaths[n])
        eaf2=pympi.Elan.Eaf(filespaths[n+1])
        c=check_duration(eaf)
        c2=check_duration(eaf2)
        for i in range(len(lst_)):
            subject.append(s)
            startime.append(lst_[i][0])
            endtime.append(lst_[i][1])
            label.append(lst_[i][2])
            duration.append(max(c,c2))
        s+=1
        if ((s-1)%2==0):
            n+=2
    df=pd.DataFrame({'database': list_of_words(f"{database}", len(subject)), 'subject': subject, 'startime': startime, 
    'endtime': endtime, 'label': label, 'duration': duration})
    df['diff_time']=df['endtime']-df['startime']
    df.columns=['database', 'subject', 'startime', 'endtime', 'label', 'duration', 'diff_time']
    df=df.reindex(columns=['startime', 'endtime', 'label', 'subject', 'diff_time', 'duration', 'database'])
    lst=df_to_list(df)
    col=['startime', 'endtime', 'label', 'subject', 'diff_time', 'duration', 'database']
    return lst, col

def get_tier_dict_conv_folder(filespaths, database, tier):
    """ Give the dataframe of a tier from a folder.
    
    Args:
        filespaths (list): Cointain the filespath of the folder
        database (str): your dataset selected
        tier (str): tier name
    Returns:
        A list of tuple and the list L=['startime', 'endtime', 'label', 'subject', 'diff_time', 'duration', 'database']
    """
    real_tier_lists , real_tiers = get_parameters_tag()

    startime, endtime, label, subject, duration=([] for _ in range(5))
    s=1
    n=0
    for _ in range (len(filespaths)):
        lst_=get_tier_dict(filespaths[_],tier)
        eaf=pympi.Elan.Eaf(filespaths[n])
        eaf2=pympi.Elan.Eaf(filespaths[n+1])
        c=check_duration(eaf)
        c2=check_duration(eaf2)
        for i in range(len(lst_)):
            subject.append(s)
            startime.append(lst_[i][0])
            endtime.append(lst_[i][1])
            if real_tier_lists[tier]['Replace_Value'] != "" :
                if lst_[i][2] != "" :
                    label.append(real_tier_lists[tier]['Replace_Value'])
                else :
                    label.append(str("No_" + real_tier_lists[tier]['Replace_Value']))
            else :
                label.append(lst_[i][2])
            duration.append(max(c,c2))
        s+=1
        if ((s-1)%2==0):
            n+=2
    df=pd.DataFrame({'database': list_of_words(f"{database}", len(subject)), 'subject': subject, 'startime': startime, 
    'endtime': endtime, 'label': label, 'duration': duration})
    df['diff_time']=df['endtime']-df['startime']
    df.columns=['database', 'subject', 'startime', 'endtime', 'label', 'duration', 'diff_time']
    df=df.reindex(columns=['startime', 'endtime', 'label', 'subject', 'diff_time', 'duration', 'database' ])
    lst=df_to_list(df)
    col=['startime', 'endtime', 'label', 'subject', 'diff_time', 'duration', 'database' ]
    return lst, col

#By file _____________________________________________________________________________________________________________________________
#Here, the get_overlapping_seg function (defined in interaction_analysis.py) makes directly intersection between the segments.
def get_smiles_from_spk(root):
    """ Give a list of smiles when the subject is a speaker.
    
    Args:
        root (str): file path
    Returns:
        A list of tuple and the list L=['startime', 'endtime', 'label', 'duration', 'diff_time', 'subject']
    """
    """
    Process: 
    We want the overlap of speaker's segments and smiles segments
    """
    spk_lst=get_IR_list(root, "Role", "spk")
    smiles_lst=get_Sdict(root)
    startime, endtime, label, duration, diff_time, subject=([] for _ in range(6))
    b=get_overlapping_seg(spk_lst, smiles_lst)
    sub=1
    eaf=pympi.Elan.Eaf(root)
    c=check_duration(eaf)
    for _ in range(0, len(b), 1):     
        startime.append(b[_][0])
        endtime.append(b[_][1])
        diff_time.append(b[_][1]-b[_][0])
        label.append(b[_][2])
        duration.append(c)
        subject.append(sub)
        sub+=1
    lst=[(i, j, k, l, m, n) for i, j, k, l, m, n in zip(startime, endtime, label, duration, diff_time, subject)]
    col=['startime', 'endtime', 'label', 'duration', 'diff_time', 'subject']
    return lst, col

def get_smiles_from_lsn(root):
    """ Give a list of smiles when the subject is a listener.
    
    Args:
        root (str): file path
    Returns:
        A list of tuple and the list L=['startime', 'endtime', 'label', 'duration', 'diff_time', 'subject']
    """
    lsn_lst=get_IR_list(root, "Role", "lsn")
    lst=get_Sdict(root)
    startime, endtime, label, duration, diff_time, subject=([] for _ in range(6))
    b=get_overlapping_seg(lsn_lst, lst)
    sub=1
    eaf = pympi.Elan.Eaf(root)
    c=check_duration(eaf)
    for _ in range(0, len(b), 1):     
        startime.append(b[_][0])
        endtime.append(b[_][1])
        diff_time.append(b[_][1]-b[_][0])
        label.append(b[_][2])
        duration.append(c)
        subject.append(sub)
        sub+=1
    lst=[(i, j, k, l, m, n) for i, j, k, l, m, n in zip(startime, endtime, label, duration, diff_time, subject)]
    col=['startime', 'endtime', 'label', 'duration', 'diff_time', 'subject']
    return lst, col

def get_laughs_from_spk(root):
    """ Give a list of laughs when the subject is a speaker.
    
    Args:
        root (str) -> file path
    Returns:
        A list of tuple and the list L=['startime', 'endtime', 'label', 'duration', 'diff_time', 'subject']
    """
    spk_lst=get_IR_list(root, "Role", "spk")
    lst=get_Ldict(root)
    startime, endtime, label, duration, diff_time, subject=([] for _ in range(6))
    b=get_overlapping_seg(spk_lst, lst)
    eaf=pympi.Elan.Eaf(root)
    c=check_duration(eaf)
    sub=1
    for _ in range(0, len(b), 1):     
        startime.append(b[_][0])
        endtime.append(b[_][1])
        diff_time.append(b[_][1]-b[_][0])
        label.append(b[_][2])
        duration.append(c)
        subject.append(sub)
        sub+=1
    lst=[(i, j, k, l, m, n) for i, j, k, l, m, n in zip(startime, endtime, label, duration, diff_time, subject)]
    col=['startime', 'endtime', 'label', 'duration', 'diff_time', 'subject']
    return lst, col

def get_laughs_from_lsn(root):
    """ Give a list of laughs when the subject is a listener.
    
    Args:
        root (str): file path
    Returns:
        A list of tuple and the list L=['startime', 'endtime', 'label', 'duration', 'diff_time', 'subject']
    """
    lsn_lst=get_IR_list(root, "Role", "lsn")
    lst=get_Ldict(root)
    startime, endtime, label, duration, diff_time, subject=([] for _ in range(6))
    b=get_overlapping_seg(lsn_lst, lst)
    eaf=pympi.Elan.Eaf(root)
    c=check_duration(eaf)
    sub=1
    for _ in range(0, len(b), 1):     
        startime.append(b[_][0])
        endtime.append(b[_][1])
        diff_time.append(b[_][1]-b[_][0])
        label.append(b[_][2])
        duration.append(c)
        subject.append(sub)
        sub+=1
    lst=[(i, j, k, l, m, n) for i, j, k, l, m, n in zip(startime, endtime, label, duration, diff_time, subject)]
    col=['startime', 'endtime', 'label', 'duration', 'diff_time','subject']
    return lst, col

#Here, the get_overlapping_segments function (defined in interaction_analysis.py) doesn't make directly intersection between the segments.
def get_smiles_from_spk2(root):
    """ Give a list of smiles when the subject is a speaker.
    
    Args:
        root (str): file path
    Returns:
        A list of tuple and the list L=['startime', 'endtime', 'label', 'duration']
    """
    """
    Process: 
    We want the overlap of speaker's segments and smiles segments
    """
    spk_lst=get_IR_list(root, "Role", "spk")
    smiles_lst=get_Sdict(root)
    startime, endtime, label, nsmile, role_ind, duration=([] for _ in range(6))
    b=list(get_overlapping_segments(spk_lst, smiles_lst).values())
    b=list(itertools.chain(*b))
    eaf=pympi.Elan.Eaf(root)
    c=check_duration(eaf)
    for _ in range(0, len(b), 1):     
        startime.append(b[_][0])
        endtime.append(b[_][1])
        label.append(b[_][2])
        duration.append(c)
    lst=[(i, j, k, l) for i, j, k, l in zip(startime, endtime, label, duration)]
    col=['startime', 'endtime', 'label', 'duration']
    return lst, col

def get_smiles_from_lsn2(root):
    """ Give a list of smiles when the subject is a listener.
    
    Args:
        root (str): file path
    Returns:
        A list of tuple and the list L=['startime', 'endtime', 'label', 'duration']
    """
    lsn_lst=get_IR_list(root, "Role", "lsn")
    lst=get_Sdict(root)
    startime, endtime, label, duration=([] for _ in range(4))
    b=list(get_overlapping_segments(lsn_lst, lst).values())
    b=list(itertools.chain(*b))
    eaf=pympi.Elan.Eaf(root)
    c=check_duration(eaf)
    for _ in range(0, len(b), 1):     
        startime.append(b[_][0])
        endtime.append(b[_][1])
        label.append(b[_][2])
        duration.append(c)
    lst=[(i, j, k, l) for i, j, k, l in zip(startime, endtime, label, duration)]
    col=['startime', 'endtime', 'label', 'duration']
    return lst, col

def get_laughs_from_spk2(root):
    """ Give a list of laughs when the subject is a speaker.
    
    Args:
        root (str): file path
    Return:
        A list of tuple and the list L=['startime', 'endtime', 'label', 'duration']
    """
    spk_lst=get_IR_list(root, "Role", "spk")
    lst=get_Ldict(root)
    startime, endtime, label, duration=([] for _ in range(4))
    b=list(get_overlapping_segments(spk_lst, lst).values())
    b=list(itertools.chain(*b))
    eaf=pympi.Elan.Eaf(root)
    c=check_duration(eaf)
    for _ in range(0, len(b), 1):     
        startime.append(b[_][0])
        endtime.append(b[_][1])
        label.append(b[_][2])
        duration.append(c)
    lst=[(i, j, k, l) for i, j, k, l in zip(startime, endtime, label, duration)]
    col=['startime', 'endtime', 'label', 'duration']
    return lst, col

def get_laughs_from_lsn2(root):
    """ Give a list of laughs when the subject is a listener.
    
    Args:
        root (str): file path
    Returns:
        A list of tuple and the list L=['startime', 'endtime', 'label', 'duration']
    """
    lsn_lst=get_IR_list(root, "Role", "lsn")
    lst=get_Ldict(root)
    startime, endtime, label, duration=([] for _ in range(4))
    b=list(get_overlapping_segments(lsn_lst, lst).values())
    b=list(itertools.chain(*b))
    eaf=pympi.Elan.Eaf(root)
    c=check_duration(eaf)
    for _ in range(0, len(b), 1):     
        startime.append(b[_][0])
        endtime.append(b[_][1])
        label.append(b[_][2])
        duration.append(c)
    lst=[(i, j, k, l) for i, j, k, l in zip(startime, endtime, label, duration)]
    col=['startime', 'endtime', 'label', 'duration']
    return lst, col

def get_tier_from_lsn2(root, tier):
    """ Retrieve a specified tier from a file when the subject is a listener.
    
    Args:
        root (str): File path
        tier (str): Name of the tier to retrieve
    Returns:
        tuple: A list of tuples representing the specified tier and the list of column names
    """
    lsn_lst=get_IR_list(root, "Role", "lsn")
    lst=get_tier_dict(root, tier)
    startime, endtime, label, duration=([] for _ in range(4))
    b=list(get_overlapping_segments(lsn_lst, lst).values())
    b=list(itertools.chain(*b))
    eaf=pympi.Elan.Eaf(root)
    duration=check_duration(eaf)
    for item in b:     
        startime.append(item[0])
        endtime.append(item[1])
        label.append(item[2])
    lst=[(i, j, k, duration) for i, j, k in zip(startime, endtime, label)]
    columns=['startime', 'endtime', 'label', 'duration']
    return lst, columns

def get_tier_from_spk2(root, tier):
    """ Retrieve a specified tier from a file when the subject is a speaker.
    
    Args:
        root (str): File path
        tier (str): Name of the tier to retrieve
    Returns:
        tuple: A list of tuples representing the specified tier and the list of column names
    """
    spk_lst=get_IR_list(root, "Role", "spk")
    lst=get_tier_dict(root, tier)
    startime, endtime, label, duration=([] for _ in range(4))
    b=list(get_overlapping_segments(spk_lst, lst).values())
    b=list(itertools.chain(*b))
    eaf=pympi.Elan.Eaf(root)
    duration=check_duration(eaf)
    for item in b:     
        startime.append(item[0])
        endtime.append(item[1])
        label.append(item[2])
    lst=[(i, j, k, duration) for i, j, k in zip(startime, endtime, label)]
    columns=['startime', 'endtime', 'label', 'duration']
    return lst, columns

def get_tier_from_entity(root, tier1, tier2, entity):
    """ Retrieve a specified tier from another tier.
    
    Args:
        root (str): File path
        tier1 (str): Name of the tier from which one retrieves the other
        tier2 (str): Name of the tier to retrieve
        entity (str): Name of the entity of the tier1
        
    Returns:
        tuple: A list of tuples representing the specified tier and the list of column names
    """
    real_tier_lists , real_tiers = get_parameters_tag()

    lsn_lst=get_IR_list(root, tier1, entity)
    #print("lsn_lst : ", lsn_lst)
    lst=get_tier_dict_by_express(root, tier2)
    #print("lst : ", lst)
    startime, endtime, label, duration=([] for _ in range(4))
    b=list(get_overlapping_segments(lsn_lst, lst).values())
    b=list(itertools.chain(*b))
    eaf=pympi.Elan.Eaf(root)
    duration=check_duration(eaf)
    for item in b:     
        startime.append(item[0])
        endtime.append(item[1])
        label.append(item[2])
    lst=[(i, j, k, duration) for i, j, k in zip(startime, endtime, label)]
    columns=['startime', 'endtime', 'label', 'duration']
    #print("STP bro : ", lst)
    return lst, columns

#By folder
def get_smiles_from_spk_folder(listpaths, string):
    """ Same as get_smiles_from_spk but from a folder.

    Args: 
        listpaths (list): list of folder's filespath 
    Returns:
        A list of tuple and the list L=['subject', 'diff_time', 'label', 'duration', 'database']
    """
    L=[]
    subject=[]
    i=1
    for _ in listpaths:
        df0=list_to_df(get_smiles_from_spk2(_)[0], get_smiles_from_spk2(_)[1])
        subject.append(list_of_words(i, len(df0['startime'])))
        L.append(df0)
        i+=1
    S=[]
    for _ in subject:
        S=S+_
    df=pd.concat([L[_] for _ in range (len(L))])
    df['subject']=S
    df['database']=list_of_words(string, len(df['subject']))
    df['diff_time']=df['endtime']-df['startime']
    df.drop(df.columns[[0,1]], axis=1, inplace=True)
    df=df.reindex(columns=['subject', 'diff_time', 'label', 'duration', 'database'])
    lst=df_to_list(df)
    columns=['subject', 'diff_time', 'label', 'duration', 'database']
    return lst, columns

def get_smiles_from_lsn_folder(listpaths, string):
    """ Same as get_smiles_from_spk but from a folder.

    Args: 
        listpaths (list): list of folder's filespath 
    Returns:
        A list of tuple and the list L=['subject', 'diff_time', 'label', 'duration', 'database']
    """
    L=[]
    subject=[]
    i=1
    for _ in listpaths:
        df0=list_to_df(get_smiles_from_lsn2(_)[0], get_smiles_from_lsn2(_)[1])
        subject.append(list_of_words(i, len(df0['startime'])))
        L.append(df0)
        i+=1
    S=[]
    for _ in subject:
        S=S+_
    df=pd.concat([L[_] for _ in range (len(L))])
    df['subject']=S
    df['database']=list_of_words(string, len(df['subject']))
    df['diff_time']=df['endtime']-df['startime']
    df.drop(df.columns[[0,1]], axis=1, inplace=True)
    df=df.reindex(columns=['subject', 'diff_time', 'label', 'duration', 'database'])
    lst=df_to_list(df)
    columns=['subject', 'diff_time', 'label', 'duration', 'database']
    return lst, columns

def get_laughs_from_spk_folder(listpaths, string):
    """ Same as get_smiles_from_spk but from a folder.

    Args:
        listpaths (list): list of folder's filespath 
    Returns:
        A list of tuple and the list L=['subject', 'diff_time', 'label', 'duration', 'database']
    """
    L=[]
    subject=[]
    i=1
    for _ in listpaths:
        df0=list_to_df(get_laughs_from_spk2(_)[0], get_laughs_from_spk2(_)[1])
        subject.append(list_of_words(i, len(df0['startime'])))
        L.append(df0)
        i+=1
    S=[]
    for _ in subject:
        S=S+_
    df=pd.concat([L[_] for _ in range (len(L))])
    df['subject']=S
    df['database']=list_of_words(string, len(df['subject']))
    df['diff_time']=df['endtime']-df['startime']
    df.drop(df.columns[[0,1]], axis=1, inplace=True)
    df=df.reindex(columns=['subject', 'diff_time', 'label', 'duration', 'database'])
    lst=df_to_list(df)
    columns=['subject', 'diff_time', 'label', 'duration', 'database']
    return lst, columns

def get_laughs_from_lsn_folder(listpaths, string):
    """ Same as get_smiles_from_spk but from a folder.

    Args : 
        listpaths (list): list of folder's filespath 
    Return :
        A list of tuple and the list L=['subject', 'diff_time', 'label', 'duration', 'database']
    """
    L=[]
    subject=[]
    i=1
    for _ in listpaths:
        df0=list_to_df(get_laughs_from_lsn2(_)[0], get_laughs_from_lsn2(_)[1])
        subject.append(list_of_words(i, len(df0['startime'])))
        L.append(df0)
        i+=1
    S=[]
    for _ in subject:
        S=S+_
    df=pd.concat([L[_] for _ in range (len(L))])
    df['subject']=S
    df['database']=list_of_words(string, len(df['subject']))
    df['diff_time']=df['endtime']-df['startime']
    df.drop(df.columns[[0,1]], axis=1, inplace=True)
    df=df.reindex(columns=['subject', 'diff_time', 'label', 'duration', 'database'])
    lst=df_to_list(df)
    columns=['subject', 'diff_time', 'label', 'duration', 'database']
    return lst, columns

def get_tier_from_spk_folder(listpaths, string, tier):
    """ Retrieve specified tiers from files in a folder.
    
    Args:
        listpaths (list): List of folder file paths
        string (str): Name of the dataset
        tier (str): Name of the tier to retrieve
    Returns:
        tuple: A list of tuples representing the specified tier and the list of column names
    """
    L=[]
    subject=[]
    i=1
    for path in listpaths:
        df0=list_to_df(get_tier_from_spk2(path, tier)[0], get_tier_from_spk2(path, tier)[1])
        subject.append(list_of_words(i, len(df0['startime'])))
        L.append(df0)
        i+=1
    S=[]
    for _ in subject:
        S=S+_
    df=pd.concat([L[_] for _ in range (len(L))])
    df['subject']=S
    df['database']=list_of_words(string, len(df['subject']))
    df['diff_time']=df['endtime']-df['startime']
    df.drop(df.columns[[0, 1]], axis=1, inplace=True)
    df=df.reindex(columns=['subject', 'diff_time', 'label', 'duration', 'database'])
    lst=df_to_list(df)
    columns=['subject', 'diff_time', 'label', 'duration', 'database']
    return lst, columns

def get_tier_from_lsn_folder(listpaths, string, tier):
    """ Retrieve specified tiers from files in a folder.
    
    Args:
        listpaths (list): List of folder file paths
        string (str): Name of the dataset
        tier (str): Name of the tier to retrieve
    Returns:
        tuple: A list of tuples representing the specified tier and the list of column names
    """
    L=[]
    subject=[]
    i=1
    for path in listpaths:
        df0=list_to_df(get_tier_from_lsn2(path, tier)[0], get_tier_from_lsn2(path, tier)[1])
        subject.append(list_of_words(i, len(df0['startime'])))
        L.append(df0)
        i+=1
    S=[]
    for _ in subject:
        S=S+_
    df=pd.concat([L[_] for _ in range (len(L))])
    df['subject']=S
    df['database']=list_of_words(string, len(df['subject']))
    df['diff_time']=df['endtime']-df['startime']
    
    df.drop(df.columns[[0, 1]], axis=1, inplace=True)
    df=df.reindex(columns=['subject', 'diff_time', 'label', 'duration', 'database'])
    lst=df_to_list(df)
    columns=['subject', 'diff_time', 'label', 'duration', 'database']
    return lst, columns

def get_tier_from_tier(listpaths, string, tier1, tier2, entity):
    """ Retrieve specified tiers from TIER files in a folder.

    Args:
        listpaths (list): List of folder file paths
        string (str): Name of the dataset
        tier1 (str): Name of the first tier
        tier2 (str): Name of the second tier
        entity (str): Name of the entity of the tier1
    Returns:
        tuple: A list of tuples representing the specified tier and the list of column names
    """
    L=[]
    subject=[]
    i=1
    for path in listpaths:
        df0=list_to_df(get_tier_from_entity(path, tier1, tier2, entity)[0], get_tier_from_entity(path, tier1, tier2, entity)[1])
        subject.append(list_of_words(i, len(df0['startime'])))
        L.append(df0)
        i+=1
    S=[]
    for _ in subject:
        S=S+_
    df=pd.concat([L[_] for _ in range(len(L))])
    df['subject']=S
    df['database']=list_of_words(string, len(df['subject']))
    df['diff_time']=df['endtime']-df['startime']

    df.drop(df.columns[[0, 1]], axis=1, inplace=True)
    df=df.reindex(columns=['subject', 'diff_time', 'label', 'duration', 'database'])
    lst=df_to_list(df)
    columns=['subject', 'diff_time', 'label', 'duration', 'database']
    return lst, columns

#Roles versus _____________________________________________________________________________________________________________________________
def get_smiles_from_spk_vs_lsn_folder(listpaths, string):
    """This function gives the list of smiles when a speaker is in front of a listener.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        list of tuple and a description of what is inside the tuple: (list of tuple, ['conv', 'role', 'label', 'subject', 'diff_time', 'duration', 'database'])
    """
    df=list_to_df(get_smiles_from_spk_folder(listpaths, string)[0], get_smiles_from_spk_folder(listpaths, string)[1]) 
    df['role']=list_of_words('spk', len(df['label']))
    dg=list_to_df(get_smiles_from_lsn_folder(listpaths, string)[0], get_smiles_from_lsn_folder(listpaths, string)[1])     
    dg['role']=list_of_words('lsn', len(dg['label'])) 
    df=df.loc[:,['subject', 'database', 'label', 'duration', 'diff_time', 'role']]
    dict_=list(df.to_records(index=False))
    dg=dg.loc[:,['subject', 'database', 'label', 'duration', 'diff_time', 'role']]
    dict_2=list(dg.to_records(index=False))
    df=correct_dict_role_smiles(dict_, listpaths, string)
    dg=correct_dict_role_smiles(dict_2, listpaths, string)
    df=pd.DataFrame.from_records(df, columns=['subject', 'database', 'label', 'duration', 'diff_time', 'role'])
    dg=pd.DataFrame.from_records(dg, columns=['subject', 'database', 'label', 'duration', 'diff_time', 'role'])
    L1=[]
    L2=[]
    subj=list(np.unique((df.subject)))
    for i in subj:
        if i%2!=0:     #if the number of the subject is unpair
            L1.append(df[df.subject.eq(i)])
        else:
            L2.append(dg[dg.subject.eq(i)])
    df=pd.concat(L1)
    dg=pd.concat(L2)
    #Put together these dataframes ordered by subject
    db=pd.concat([df, dg])
    db=pd.DataFrame(db.loc[:,['label', 'duration', 'diff_time', 'subject', 'database', 'role']]).reset_index()
    db=db.drop(['index'], axis=1)
    db=db.sort_values(['subject'], ascending=[True])
    c=1
    conv=[]
    for i in range (1, len(db.duration), 2):
        values=[i, i+1]
        dgg=db[db.subject.isin(values)]
        conv+=list_of_words(c, len(dgg.subject))
        c+=1
    db['conv']=conv
    #If subject change, take duration
    duration=[]
    for _ in list(np.unique((db.subject))):
        duration+=(list(np.unique(db.loc[db.subject.eq(_), 'duration'])))
    if 0 not in duration: pass
    else: duration.remove(0)
    conv=list(np.unique((db.conv)))
    d=[]
    for _ in range(0, len(duration), 2):
        if(_+1) < len(duration):
            d.append((duration[_], duration[_+1]))
    d=list(reversed(d))
    for i, j in zip(conv, d):
        db.loc[db.conv.eq(i), 'duration']=max(j)
    db=db.reindex(columns=['conv', 'role', 'label', 'subject', 'diff_time', 'duration', 'database'])
    lst=df_to_list(db)
    col=['conv', 'role', 'label', 'subject', 'diff_time', 'duration', 'database']
    return lst, col

def get_smiles_from_lsn_vs_spk_folder(listpaths, string):
    """ This function gives the list of smiles when a listener is in front of a speaker.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        list of tuple and a description of what is inside the tuple: (list of tuple, ['conv', 'role', 'label', 'subject', 'diff_time', 'duration', 'database'])
    """
    df=list_to_df(get_smiles_from_lsn_folder(listpaths, string)[0], get_smiles_from_lsn_folder(listpaths, string)[1])
    df['role']=list_of_words('lsn', len(df['subject'])) 
    df=pd.DataFrame(df).reset_index()
    df.drop(df.columns[[0]], axis=1, inplace=True) 
    dg=list_to_df(get_smiles_from_spk_folder(listpaths, string)[0], get_smiles_from_spk_folder(listpaths, string)[1])    
    dg['role']=list_of_words('spk', len(dg['subject'])) 
    dg=pd.DataFrame(dg).reset_index()
    dg.drop(dg.columns[[0]], axis=1, inplace=True)
    df=df.loc[:,['subject', 'database', 'label', 'duration', 'diff_time', 'role']]
    dict_=list(df.to_records(index=False))
    dg=dg.loc[:,['subject', 'database', 'label', 'duration', 'diff_time', 'role']]
    dict_2=list(dg.to_records(index=False))
    df=correct_dict_role_smiles(dict_, listpaths, string)
    dg=correct_dict_role_smiles(dict_2, listpaths, string)
    df=pd.DataFrame.from_records(df, columns=['subject', 'database', 'label', 'duration', 'diff_time', 'role'])
    dg=pd.DataFrame.from_records(dg, columns=['subject', 'database', 'label', 'duration', 'diff_time', 'role'])
    L1=[]
    L2=[]
    subj=list(np.unique((df.subject)))
    for i in subj:
        if i%2!=0:     #if the number of the subject is unpair
            L1.append(df[df.subject.eq(i)])
        else:
            L2.append(dg[dg.subject.eq(i)])
    df=pd.concat(L1)
    dg=pd.concat(L2)
    #Put together these dataframes ordered by subject
    db=pd.concat([df, dg])
    db=pd.DataFrame(db.loc[:,['label', 'duration', 'diff_time', 'subject', 'database', 'role']]).reset_index()
    db=db.drop(['index'], axis=1)
    db=db.sort_values(['subject'], ascending=[True])
    c=1
    conv=[]
    for i in range (1, len(db.duration), 2):
        values=[i, i+1]
        dgg=db[db.subject.isin(values)]
        conv+=list_of_words(c, len(dgg.subject))
        c+=1
    db['conv']=conv
    #If subject change, take duration
    duration=[]
    for _ in list(np.unique((db.subject))):
        duration+=(list(np.unique(db.loc[db.subject.eq(_), 'duration'])))
    if 0 not in duration: pass
    else: duration.remove(0)
    conv=list(np.unique((db.conv)))
    d=[]
    for _ in range(0, len(duration), 2):
        if(_+1) < len(duration):
            d.append((duration[_], duration[_+1]))
    d=list(reversed(d))
    for i, j in zip(conv, d):
        db.loc[db.conv.eq(i), 'duration']=max(j)
    db=db.reindex(columns=['conv', 'role', 'label', 'subject', 'diff_time', 'duration', 'database'])
    lst=df_to_list(db)
    col=['conv', 'role', 'label', 'subject', 'diff_time', 'duration', 'database']
    return lst, col

def get_laughs_from_spk_vs_lsn_folder(listpaths, string):
    """ This function gives the list of laughs when a speaker is in front of a listener.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        list of tuple and a description of what is inside the tuple: (list of tuple, ['conv', 'role', 'label', 'subject', 'diff_time',v 'duration', 'database'])
    """
    df=list_to_df(get_laughs_from_spk_folder(listpaths, string)[0], get_laughs_from_spk_folder(listpaths, string)[1])    
    df['role']=list_of_words('spk', len(df['label'])) 
    df=pd.DataFrame(df).reset_index()
    df.drop(df.columns[[0]], axis=1, inplace=True) 
    dg=list_to_df(get_laughs_from_lsn_folder(listpaths, string)[0], get_laughs_from_lsn_folder(listpaths, string)[1])    
    dg['role']=list_of_words('lsn', len(dg['label'])) 
    dg=pd.DataFrame(dg).reset_index()
    dg.drop(dg.columns[[0]], axis=1, inplace=True) 
    #Some corrections
    df=df.loc[:,['subject', 'database', 'label', 'duration', 'diff_time', 'role']]
    dict_=list(df.to_records(index=False))
    dg=dg.loc[:,['subject', 'database', 'label', 'duration', 'diff_time', 'role']]
    dict_2=list(dg.to_records(index=False))
    df=correct_dict_role_smiles(dict_, listpaths, string)
    dg=correct_dict_role_smiles(dict_2, listpaths, string)
    df=pd.DataFrame.from_records(df, columns=['subject', 'database', 'label', 'duration', 'diff_time', 'role'])
    dg=pd.DataFrame.from_records(dg, columns=['subject', 'database', 'label', 'duration', 'diff_time', 'role'])
    L1=[]
    L2=[]
    subj=list(np.unique((df.subject)))
    for i in subj:
        if i%2!=0:     #if the number of the subject is unpair
            L1.append(df[df.subject.eq(i)])
        else:
            L2.append(dg[dg.subject.eq(i)])
    df=pd.concat(L1)
    dg=pd.concat(L2)
    #Put together these dataframes ordered by subject
    db=pd.concat([df, dg])
    db=pd.DataFrame(db.loc[:,['label', 'duration', 'diff_time', 'subject', 'database', 'role']]).reset_index()
    db=db.drop(['index'], axis=1)
    db=db.sort_values(['subject'], ascending=[True])
    c=1
    conv=[]
    for i in range (1, len(db.duration), 2):
        values=[i, i+1]
        dgg=db[db.subject.isin(values)]
        conv+=list_of_words(c, len(dgg.subject))
        c+=1
    db['conv']=conv
    #If subject change, take duration
    duration=[]
    for _ in list(np.unique((db.subject))) :
        duration+=(list(np.unique(db.loc[db.subject.eq(_), 'duration'])))
    if 0 not in duration: pass
    else: duration.remove(0)
    conv=list(np.unique((db.conv)))
    d=[]
    for _ in range(0, len(duration), 2):
        if (_+1) < len(duration): 
            d.append((duration[_], duration[_+1]))
    d=list(reversed(d))
    for i, j in zip(conv, d):
        db.loc[db.conv.eq(i), 'duration']=max(j)
    db=db.reindex(columns=['conv', 'role', 'label', 'subject', 'diff_time', 'duration', 'database'])
    lst=df_to_list(db)
    col=['conv', 'role', 'label', 'subject', 'diff_time', 'duration', 'database']
    return lst, col

def get_laughs_from_lsn_vs_spk_folder(listpaths, string):
    """ This function gives the list of laughs when a listener is in front of a speaker.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        list of tuple and a description of what is inside the tuple: (list of tuple, ['conv', 'role', 'label', 'subject', 'diff_time', 'duration', 'database'])
    """
    df=list_to_df(get_laughs_from_lsn_folder(listpaths, string)[0], get_laughs_from_lsn_folder(listpaths, string)[1])
    df['role']=list_of_words('lsn', len(df['label'])) 
    dg=list_to_df(get_laughs_from_spk_folder(listpaths, string)[0], get_laughs_from_spk_folder(listpaths, string)[1])   
    dg['role']=list_of_words('spk', len(dg['label']))
    df=df.loc[:,['subject', 'database', 'label', 'duration', 'diff_time', 'role']]
    dict_=list(df.to_records(index=False))
    dg=dg.loc[:,['subject', 'database', 'label', 'duration', 'diff_time', 'role']]
    dict_2=list(dg.to_records(index=False))
    df=correct_dict_role_smiles(dict_, listpaths, string)
    dg=correct_dict_role_smiles(dict_2, listpaths, string)
    df=pd.DataFrame.from_records(df, columns=['subject', 'database', 'label', 'duration', 'diff_time', 'role'])
    dg=pd.DataFrame.from_records(dg, columns=['subject', 'database', 'label', 'duration', 'diff_time', 'role'])
    L1=[]
    L2=[]
    subj=list(np.unique((df.subject)))
    for i in subj:
        if i%2!=0:     #if the number of the subject is unpair
            L1.append(df[df.subject.eq(i)])
        else:
            L2.append(dg[dg.subject.eq(i)])
    df=pd.concat(L1)
    dg=pd.concat(L2)
    #Put together these dataframes ordered by subject
    db=pd.concat([df, dg])
    db=pd.DataFrame(db.loc[:,['label', 'duration', 'diff_time', 'subject', 'database', 'role']]).reset_index()
    db=db.drop(['index'], axis=1)
    db=db.sort_values(['subject'], ascending=[True])
    c=1
    conv=[]
    for i in range (1, len(db.duration), 2):
        values=[i, i+1]
        dgg=db[db.subject.isin(values)]
        conv+=list_of_words(c, len(dgg.subject))
        c+=1
    db['conv']=conv
    #If subject change, take duration
    duration=[]
    for _ in list(np.unique((db.subject))):
        duration+=(list(np.unique(db.loc[db.subject.eq(_), 'duration'])))
    if 0 not in duration: pass
    else: duration.remove(0)
    conv=list(np.unique((db.conv)))
    d=[]
    for _ in range(0, len(duration), 2):
        if (_+1) < len(duration): 
            d.append((duration[_], duration[_+1]))
    d=list(reversed(d))
    for i, j in zip(conv, d):
        db.loc[db.conv.eq(i), 'duration']=max(j)
    db=db.reindex(columns=['conv', 'role', 'label', 'subject', 'diff_time', 'duration', 'database'])
    lst=df_to_list(db)
    col=['conv', 'role', 'label', 'subject', 'diff_time', 'duration', 'database']
    return lst, col

def get_tier_from_entity1_vs_entity2_folder(listpaths, string, tier1, tier2, entity1, entity2):
    """ This function gives the list of tier when entity1 is in front of entity2.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
        tier1 (str): name of the tier of entity1
        tier2 (str): name of the tier of entity2
        entity1 (str): name of the entity1
        entity2 (str): name of the entity2
    Returns:
        list of tuple and a description of what is inside the tuple: (list of tuple, ['conv', 'role', 'label', 'subject', 'diff_time', 'duration', 'database'])
    """
    real_tier_lists , real_tiers = get_parameters_tag()

    try :
        df=list_to_df(get_tier_from_tier(listpaths, string, tier1, tier2, entity1)[0], get_tier_from_tier(listpaths, string, tier1, tier2, entity1)[1])
        df['role']=list_of_words(entity1, len(df['label']))
    except :
        0
    try :
        dg=list_to_df(get_tier_from_tier(listpaths, string, tier1, tier2, entity2)[0], get_tier_from_tier(listpaths, string, tier1, tier2, entity2)[1])
        dg['role']=list_of_words(entity2, len(dg['label']))
    except :
        0
    #Some corrections
    try :
        df=df.loc[:,['subject', 'database', 'label', 'duration', 'diff_time', 'role']]
        dict_=list(df.to_records(index=False))
    except :
        0
    
    try :
        dg=dg.loc[:,['subject', 'database', 'label','duration', 'diff_time', 'role']]
        dict_2=list(dg.to_records(index=False))
    except :
        0

    if real_tier_lists[tier2]['Replace_Value'] == "" :
        dg=correct_dict_role_tier(dict_2, listpaths, string, tier2)
        try :
            df=correct_dict_role_tier(dict_, listpaths, string, tier2)
        except :
            0

    df=pd.DataFrame.from_records(df, columns=['subject', 'database', 'label', 'duration', 'diff_time', 'role'])
    dg=pd.DataFrame.from_records(dg, columns=['subject', 'database', 'label', 'duration', 'diff_time', 'role'])
    L1=[]
    L2=[]
    subj=list(np.unique((df.subject)))
    for i in subj:
        if i%2!=0:     #if the number of the subject is unpair
            L1.append(df[df.subject.eq(i)])
        else:
            L2.append(dg[dg.subject.eq(i)])
    try :
        df=pd.concat(L1)
    except :
        0
    try :
        dg=pd.concat(L2)
    except : 
        0
    #Put together these dataframes ordered by subject*
    try :
        db=pd.concat([df, dg])
    except :
        db = dg
    db=pd.DataFrame(db.loc[:,['label', 'duration', 'diff_time', 'subject', 'database', 'role']]).reset_index()
    db=db.drop(['index'], axis=1)
    db=db.sort_values(['subject'], ascending=[True])
    c=1
    conv=[]
    for i in range (1, len(db.duration), 2):
        values=[i, i+1]
        dgg=db[db.subject.isin(values)]
        conv+=list_of_words(c, len(dgg.subject))
        c+=1
    db['conv']=conv
    #If subject change, take duration
    duration=[]
    for _ in list(np.unique((db.subject))):
        duration+=(list(np.unique(db.loc[db.subject.eq(_), 'duration'])))
    if 0 not in duration: pass
    else: duration.remove(0)
    conv=list(np.unique((db.conv)))
    d=[]
    for _ in range(0, len(duration), 2):
        if (_+1) < len(duration):
            d.append((duration[_], duration[_+1]))
    d=list(reversed(d))
    for i, j in zip(conv, d):
        db.loc[db.conv.eq(i), 'duration']=max(j)
    db=db.reindex(columns=['conv', 'role', 'label', 'subject', 'diff_time', 'duration', 'database'])
    lst=df_to_list(db)
    col=['conv', 'role', 'label', 'subject', 'diff_time', 'duration', 'database']
    return lst, col

#Mean, Std, median, max, min from all datasets _________________________________________________________________
def get_rd_stats(df):
    """ This function calculate the mean, median and standard deviation of the relative duration of list of tuple.
    
    Args:
        df (list): list of tuple
    Returns:
        list of tuple and a description of what is inside the tuple: (list of tuple, ['database', 'label', 'mean_p', 'median_p', 'std_p', 'min_p', 'max_p']))
    """
    dg1=df.loc[:,['subject', 'database', 'label', 'duration', 'diff_time']]
    dg1=dg1.groupby(['subject', 'database', 'label', 'duration']).sum(numeric_only=True).reset_index()
    dg1['percentage']=(dg1['diff_time']/dg1['duration'])*100
    dg1=dg1.drop(['subject', 'duration', 'diff_time'], axis=1)
    dg=dg1.loc[:,['database', 'label', 'percentage']]

    df_mean=dg1.loc[:,['database', 'label', 'percentage']]
    df_mean=df_mean.groupby(['database', 'label']).mean().reset_index()

    df_median=dg1.loc[:,['database', 'label', 'percentage']]
    df_median=df_median.groupby(['database', 'label']).median().reset_index()

    df_std=dg1.loc[:,['database', 'label', 'percentage']]
    df_std=df_std.groupby(['database', 'label']).std().reset_index()
    
    df_min=dg1.loc[:, ['database', 'label', 'percentage']]
    df_min=df_min.groupby(['database', 'label']).min().reset_index()

    df_max=dg1.loc[:, ['database', 'label', 'percentage']]
    df_max=df_max.groupby(['database', 'label']).max().reset_index()

    df_mean.columns=['database', 'label', 'mean_p']
    df_median.columns=['database', 'label', 'median_p']
    df_std.columns=['database', 'label', 'std_p']
    df_min.columns=['database', 'label', 'min_p']
    df_max.columns=['database', 'label', 'max_p']

    dg=df_mean.merge(df_median, on=['database', 'label'])
    dg=dg.merge(df_std, on=['database', 'label'])
    dg=dg.merge(df_min, on=['database', 'label'])
    dg=dg.merge(df_max, on=['database', 'label'])
    
    lst=df_to_list(dg)
    col=['database', 'label', 'mean_p', 'median_p', 'std_p', 'min_p', 'max_p']
    return lst, col

def get_rd_stats_byrole(df):
    """ This function calculate the mean, median and standard deviation of the relative duration of list of tuple filtered by role.
    
    Args:
        df (list): list of tuple
    Returns:
        list of tuple and a description of what is inside the tuple: (list of tuple, ['database', 'label', 'mean_p', 'median_p', 'std_p', 'min_p', 'max_p'])
    """
    dg1=df.loc[:,['subject', 'database', 'label', 'duration', 'diff_time']]
    dg1=dg1.groupby(['subject', 'database', 'label', 'duration']).sum(numeric_only=True).reset_index()
    dg1['percentage']=(dg1['diff_time']/dg1['duration'])*100
    dg1=dg1.drop(['subject', 'duration', 'diff_time'], axis=1)
    dg=dg1.loc[:,['database', 'label', 'percentage']]

    df_mean=dg1.loc[:,['database', 'label', 'percentage']]
    df_mean=df_mean.groupby(['database', 'label']).mean().reset_index()
    
    df_median=dg1.loc[:,['database', 'label', 'percentage']]
    df_median=df_median.groupby(['database', 'label']).median().reset_index()
    
    df_std=dg1.loc[:,['database', 'label', 'percentage']]
    df_std=df_std.groupby(['database', 'label']).std().reset_index()
    
    df_min=dg1.loc[:, ['database', 'label', 'percentage']]
    df_min=df_min.groupby(['database', 'label']).min().reset_index()

    df_max=dg1.loc[:, ['database', 'label', 'percentage']]
    df_max=df_max.groupby(['database', 'label']).max().reset_index()

    df_mean.columns=['database', 'label', 'mean_p']
    df_median.columns=['database', 'label', 'median_p']
    df_std.columns=['database', 'label', 'std_p']
    df_min.columns=['database', 'label', 'min_p']
    df_max.columns=['database', 'label', 'max_p']

    dg=df_mean.merge(df_median, on=['database', 'label'])
    dg=dg.merge(df_std, on=['database', 'label'])
    dg=dg.merge(df_min, on=['database', 'label'])
    dg=dg.merge(df_max, on=['database', 'label'])
    
    lst=df_to_list(dg)
    col=['database', 'label', 'mean_p', 'median_p', 'std_p', 'min_p', 'max_p']
    return lst, col

#Intra _________________________________________________________________________________________________________________________
#By folder 
def get_intra_smiles_absolute_duration_folder(listpaths, string):
    """ This function calculates absolute duration for smiles in a dataset considering one person.
    
    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        Tuple: (list of tuple, description of tuples) -> ([], ['subject', 'database', 'label', 'sum_time', 'time'])
    """
    df1=list_to_df(get_smiles_dict_folder(listpaths, string)[0], get_smiles_dict_folder(listpaths, string)[1])
    dg1=df1.loc[:,['subject', 'database', 'label', 'diff_time']]
    dg1['label'] = dg1['label'].str.replace(' ', '')
    dg1=dg1.groupby(['subject', 'database', 'label']).sum(numeric_only=True).reset_index()
    dg1['time']=seconds_to_hmsms_list(dg1['diff_time'])
    dg1.columns=['subject', 'database', 'label', 'sum_time', 'time']
    lst=df_to_list(dg1)
    col=['subject', 'database', 'label', 'sum_time', 'time']
    return lst, col

def get_intra_laughs_absolute_duration_folder(listpaths, string):
    """ This function calculates absolute duration for laughs in a dataset considering one person.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        Tuple: (list of tuple, description of tuples) -> ([], ['subject','database','label','sum_time','time'])
    """
    df2=list_to_df(get_laughs_dict_folder(listpaths, string)[0], get_laughs_dict_folder(listpaths, string)[1])
    dg2=df2.loc[:,['subject', 'database', 'label', 'diff_time']]
    dg2['label'] = dg2['label'].str.replace(' ', '')
    dg2=dg2.groupby(['subject', 'database', 'label']).sum(numeric_only=True).reset_index()
    dg2['time']=seconds_to_hmsms_list(dg2['diff_time'])
    dg2.columns=['subject', 'database', 'label', 'sum_time', 'time']
    lst=df_to_list(dg2)
    col=['subject', 'database', 'label', 'sum_time', 'time']
    return lst, col

def get_intra_tiers_absolute_duration_folder(listpaths, string, expression_choice):
    """ This function calculates absolute duration for tiers in a dataset considering one person.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
        expression_choice (str): name of the expression
    Returns:
        Tuple: (list of tuple, description of tuples) -> ([], ['subject', 'database', 'label', 'sum_time', 'time'])
    """
    df3=list_to_df(get_tier_dict_folder(listpaths, string, expression_choice)[0], get_tier_dict_folder(listpaths, string, expression_choice)[1])
    dg3=df3.loc[:,['subject', 'database', 'label', 'diff_time']]
    dg3['label'] = dg3['label'].str.replace(' ', '')
    dg3=dg3.groupby(['subject', 'database', 'label']).sum(numeric_only=True).reset_index()
    dg3['time']=seconds_to_hmsms_list(dg3.groupby('database')['diff_time'].transform('sum'))
    dg3.columns=['subject', 'database', 'label', 'sum_time', 'time']
    lst=df_to_list(dg3)
    col=['subject', 'database', 'label', 'sum_time', 'time']
    return lst, col

def get_intra_smiles_relative_duration_folder(listpaths, string):
    """ This function calculates relative duration for smiles in a dataset considering one person.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        Tuple: (list of tuple, description of tuples) -> ([], ['subject', 'database', 'label', 'duration', 'sum_time', 'percentage'])
    """
    df1=list_to_df(get_smiles_dict_folder(listpaths, string)[0], get_smiles_dict_folder(listpaths, string)[1])
    dg1=df1.loc[:,['subject', 'database', 'label', 'duration', 'diff_time']]
    dg1['label'] = dg1['label'].str.replace(' ', '')
    dg1=dg1.groupby(['subject', 'database', 'label', 'duration']).sum(numeric_only=True).reset_index()
    dg1['percentage']=round(((dg1['diff_time']/dg1['duration'])*100),2)
    dg1.columns=['subject', 'database', 'label', 'duration', 'sum_time', 'percentage']
    lst=df_to_list(dg1)
    col=['subject', 'database', 'label', 'duration', 'sum_time', 'percentage']
    return lst, col

def get_intra_laughs_relative_duration_folder(listpaths, string):
    """ This function calculates relative duration for laughs in a dataset considering one person.
    
    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        Tuple: (list of tuple, description of tuples) -> ([], ['subject', 'database', 'label', 'duration', 'sum_time', 'percentage'])
    """
    df2=get_laughs_dict_folder(listpaths, string)
    df2=list_to_df(df2[0], df2[1])
    dg2=df2.loc[:,['subject', 'database', 'label', 'duration', 'diff_time']]
    dg2['label'] = dg2['label'].str.replace(' ', '')
    dg2=dg2.groupby(['subject', 'database', 'label', 'duration']).sum(numeric_only=True).reset_index()
    dg2['percentage']=round(((dg2['diff_time']/dg2['duration'])*100),2)
    dg2.columns=['subject', 'database', 'label', 'duration', 'sum_time', 'percentage']
    lst=df_to_list(dg2)
    col=['subject', 'database', 'label', 'duration', 'sum_time', 'percentage']
    return lst, col

def get_intra_tiers_relative_duration_folder(listpaths, string, expression_choice):
    """ This function calculates relative duration for tiers in a dataset considering one person.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
        expression_choice (str): name of the expression
    Returns:
        Tuple: (list of tuple, description of tuples) -> ([], ['subject', 'database', 'label', 'duration', 'sum_time', 'percentage'])
    """
    df3=get_tier_dict_folder(listpaths, string, expression_choice)
    df3=list_to_df(df3[0], df3[1])
    dg3=df3.loc[:,['subject', 'database', 'label', 'duration', 'diff_time']]
    dg3['label'] = dg3['label'].str.replace(' ', '')
    dg3=dg3.groupby(['subject', 'database', 'label', 'duration']).sum(numeric_only=True).reset_index()
    dg3['percentage']=round(((dg3['diff_time']/dg3.groupby('database')['diff_time'].transform('sum'))*100),2)
    dg3.columns=['subject', 'database', 'label', 'duration', 'sum_time', 'percentage']
    lst=df_to_list(dg3)
    col=['subject', 'database', 'label', 'duration', 'sum_time', 'percentage']
    return lst, col

#By roles
def get_intra_smiles_ad_from_lsn_folder(listpaths, string):
    """ This function calculates absolute duration for smiles in a dataset considering one person who is listener.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        Tuple: (list of tuple, description of tuples) -> ([], ['subject', 'database', 'label', 'sum_time', 'time'])
    """
    df1=list_to_df(get_smiles_from_lsn_folder(listpaths, string)[0], get_smiles_from_lsn_folder(listpaths, string)[1])
    dg1=df1.loc[:,['subject', 'database', 'label', 'diff_time']]
    dg1['label'] = dg1['label'].str.replace(' ', '')
    dg1=dg1.groupby(['subject', 'database', 'label']).sum(numeric_only=True).reset_index()
    dg1['time']=seconds_to_hmsms_list(dg1['diff_time'])
    dg1.columns=['subject', 'database', 'label', 'sum_time', 'time']
    lst=df_to_list(dg1)
    col=['subject', 'database', 'label', 'sum_time', 'time']
    return lst, col

def get_intra_smiles_rd_from_lsn_folder(listpaths,string):
    """ This function calculates relative duration for smiles in a dataset considering one person who is listener.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        Tuple: (list of tuple, description of tuples) -> ([], ['subject', 'database', 'label', 'percentage'])
    """
    df1=list_to_df(get_smiles_from_lsn_folder(listpaths, string)[0], get_smiles_from_lsn_folder(listpaths, string)[1])
    dg1=df1.loc[:,['subject', 'database', 'label', 'duration', 'diff_time']]
    dg1['label'] = dg1['label'].str.replace(' ', '')
    dg1=dg1.groupby(['subject', 'database', 'label', 'duration']).sum(numeric_only=True).reset_index()
    dg1['percentage']=round(((dg1['diff_time']/dg1['duration'])*100),2)
    dg1.columns=['subject', 'database', 'label', 'duration', 'sum_time', 'percentage']
    dg1.drop(dg1.columns[[3, 4]], axis=1, inplace=True)
    lst=df_to_list(dg1)
    col=['subject', 'database', 'label', 'percentage']
    return lst, col

def get_intra_smiles_ad_from_spk_folder(listpaths, string):
    """ This function calculates absolute duration for smiles in a dataset considering one person who is speaker.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        Tuple: (list of tuple, description of tuples) -> ([], ['subject', 'database', 'label', 'sum_time', 'time'])
    """
    df1=list_to_df(get_smiles_from_spk_folder(listpaths, string)[0], get_smiles_from_spk_folder(listpaths, string)[1])
    dg1=df1.loc[:,['subject', 'database', 'label', 'diff_time']]
    dg1['label'] = dg1['label'].str.replace(' ', '')
    dg1=dg1.groupby(['subject', 'database', 'label']).sum(numeric_only=True).reset_index()
    dg1['time']=seconds_to_hmsms_list(dg1['diff_time'])
    dg1.columns=['subject', 'database', 'label', 'sum_time', 'time']
    lst=df_to_list(dg1)
    col=['subject', 'database', 'label', 'sum_time', 'time']
    return lst, col

def get_intra_smiles_rd_from_spk_folder(listpaths, string):
    """ This function calculates relative duration for smiles in a dataset considering one person who is speaker.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        Tuple: (list of tuple, description of tuples) -> ([], ['subject', 'database', 'label', 'percentage'])
    """
    df1=list_to_df(get_smiles_from_spk_folder(listpaths, string)[0], get_smiles_from_spk_folder(listpaths, string)[1])
    dg1=df1.loc[:,['subject', 'database', 'label', 'duration', 'diff_time']]
    dg1['label'] = dg1['label'].str.replace(' ', '')
    dg1=dg1.groupby(['subject', 'database', 'label', 'duration']).sum(numeric_only=True).reset_index()
    dg1['percentage']=round(((dg1['diff_time']/dg1['duration'])*100),2)
    dg1.columns=['subject', 'database', 'label', 'duration', 'sum_time', 'percentage']
    dg1.drop(dg1.columns[[3, 4]], axis=1, inplace=True)
    lst=df_to_list(dg1)
    col=['subject', 'database', 'label', 'percentage']
    return lst, col

def get_intra_laughs_ad_from_lsn_folder(listpaths, string):
    """ This function calculates absolute duration for laughs in a dataset considering one person who is listener.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        Tuple: (list of tuple, description of tuples) -> ([], ['subject', 'database', 'label', 'sum_time', 'time'])
    """
    df1=list_to_df(get_laughs_from_lsn_folder(listpaths, string)[0], get_laughs_from_lsn_folder(listpaths, string)[1])
    dg1=df1.loc[:,['subject', 'database', 'label', 'diff_time']]
    dg1['label'] = dg1['label'].str.replace(' ', '')
    dg1=dg1.groupby(['subject', 'database', 'label']).sum(numeric_only=True).reset_index()
    dg1['time']=seconds_to_hmsms_list(dg1['diff_time'])
    dg1.columns=['subject', 'database', 'label', 'sum_time', 'time']
    lst=df_to_list(dg1)
    col=['subject', 'database', 'label', 'sum_time', 'time']
    return lst, col

def get_intra_laughs_rd_from_lsn_folder(listpaths, string):
    """ This function calculates relative duration for laughs in a dataset considering one person who is listener.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        Tuple: (list of tuple, description of tuples) -> ([], ['subject', 'database', 'label', 'percentage'])
    """
    df1=list_to_df(get_laughs_from_lsn_folder(listpaths, string)[0], get_laughs_from_lsn_folder(listpaths, string)[1])
    dg1=df1.loc[:,['subject', 'database', 'label', 'duration', 'diff_time']]
    dg1['label'] = dg1['label'].str.replace(' ', '')
    dg1=dg1.groupby(['subject', 'database', 'label', 'duration']).sum(numeric_only=True).reset_index()
    dg1['percentage']=round(((dg1['diff_time']/dg1['duration'])*100),2)
    dg1.columns=['subject', 'database', 'label', 'duration', 'sum_time', 'percentage']
    dg1.drop(dg1.columns[[3, 4]], axis=1, inplace=True)
    lst=df_to_list(dg1)
    col=['subject', 'database', 'label', 'percentage']
    return lst, col

def get_intra_laughs_ad_from_spk_folder(listpaths, string):
    """ This function calculates absolute duration for laughs in a dataset considering one person who is speaker.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        Tuple: (list of tuple, description of tuples) -> ([], ['subject', 'database', 'label', 'sum_time', 'time'])
    """
    df1=list_to_df(get_laughs_from_spk_folder(listpaths, string)[0], get_laughs_from_spk_folder(listpaths, string)[1])
    dg1=df1.loc[:,['subject', 'database', 'label', 'diff_time']]
    dg1['label'] = dg1['label'].str.replace(' ', '')
    dg1=dg1.groupby(['subject', 'database', 'label']).sum(numeric_only=True).reset_index()
    dg1['time']=seconds_to_hmsms_list(dg1['diff_time'])
    dg1.columns=['subject', 'database', 'label', 'sum_time', 'time']
    lst=df_to_list(dg1)
    col=['subject', 'database', 'label', 'sum_time', 'time']
    return lst, col

def get_intra_laughs_rd_from_spk_folder(listpaths, string):
    """ This function calculates relative duration for laughs in a dataset considering one person who is speaker.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        Tuple: (list of tuple, description of tuples) -> ([], ['subject', 'database', 'label', 'percentage'])
    """
    df1=list_to_df(get_laughs_from_spk_folder(listpaths, string)[0], get_laughs_from_spk_folder(listpaths, string)[1])
    dg1=df1.loc[:,['subject', 'database', 'label', 'duration', 'diff_time']]
    dg1['label'] = dg1['label'].str.replace(' ', '')
    dg1=dg1.groupby(['subject', 'database', 'label', 'duration']).sum(numeric_only=True).reset_index()
    dg1['percentage']=round(((dg1['diff_time']/dg1['duration'])*100),2)
    dg1.columns=['subject', 'database', 'label', 'duration', 'sum_time', 'percentage']
    dg1.drop(dg1.columns[[3, 4]], axis=1, inplace=True)
    lst=df_to_list(dg1)
    col=['subject', 'database', 'label', 'percentage']
    return lst, col

#By tier 
def get_intra_tier_ad_from_tier_folder(listpaths, string, tier1, tier2, entity):
    """ This function calculates absolute duration for a tier in a dataset considering one entity.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
        tier1 (str): name of the tier 
        tier2 (str): name of the tier to retrieve
        entity (str): name of the entity of tier1
    Returns:
        Tuple: (list of tuple, description of tuples) -> ([], ['subject', 'database', 'label', 'sum_time', 'time'])
    """
    df1=list_to_df(get_tier_from_tier(listpaths, string, tier1, tier2, entity)[0], get_tier_from_tier(listpaths, string, tier1, tier2, entity)[1])
    dg1=df1.loc[:,['subject', 'database', 'label', 'diff_time']]
    dg1['label'] = dg1['label'].str.replace(' ', '')
    dg1=dg1.groupby(['subject', 'database', 'label']).sum(numeric_only=True).reset_index()
    #dg1['time']=seconds_to_hmsms_list(dg1['diff_time'])
    dg1['time']=seconds_to_hmsms_list(dg1.groupby('database')['diff_time'].transform('sum'))
    dg1.columns=['subject', 'database', 'label', 'sum_time', 'time']
    lst=df_to_list(dg1)
    col=['subject', 'database', 'label', 'sum_time', 'time']
    return lst, col

def get_intra_tier_rd_from_tier_folder(listpaths, string, tier1, tier2, entity):
    """ This function calculates relative duration for a tier in a dataset considering one entity.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
        tier1 (str): name of the tier 
        tier2 (str): name of the tier to retrieve
        entity (str): name of the entity of tier1
    Returns:
        Tuple: (list of tuple, description of tuples) -> ([], ['subject', 'database', 'label', 'percentage'])
    """
    df1=list_to_df(get_tier_from_tier(listpaths, string, tier1, tier2, entity)[0], get_tier_from_tier(listpaths, string, tier1, tier2, entity)[1])
    dg1=df1.loc[:,['subject', 'database', 'label', 'duration', 'diff_time']]
    dg1['label'] = dg1['label'].str.replace(' ', '')
    dg1=dg1.groupby(['subject', 'database', 'label', 'duration']).sum(numeric_only=True).reset_index()
    # dg1['percentage']=round(((dg1['diff_time']/dg1['duration'])*100),2)
    dg1['percentage'] = round(((dg1['diff_time'] / dg1.groupby('database')['diff_time'].transform('sum')) * 100), 2)
    dg1.columns=['subject', 'database', 'label', 'duration', 'sum_time', 'percentage']
    dg1.drop(dg1.columns[[3, 4]], axis=1, inplace=True)
    lst=df_to_list(dg1)
    col=['subject', 'database', 'label', 'percentage']
    return lst, col

#Inter _________________________________________________________________________________________________________________________
#By folder
def get_inter_smiles_absolute_duration_folder(listpaths, string):
    """ This function calculates absolute duration for smiles in a dataset considering one interaction.
    
    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:    
        Tuple: (list of tuple, description of tuples) -> (list, ['conv', 'label', 'duration', 'database', 'time'])
    """
    df=get_smiles_dict_conv_folder(listpaths, string)
    df=list_to_df(df[0], df[1])
    dg1=df.loc[:,['subject', 'database', 'label', 'diff_time']]
    dg1['label'] = dg1['label'].str.replace(' ', '')
    dg1=dg1.groupby(['subject', 'database', 'label']).sum(numeric_only=True).reset_index()
    dg1['time']=seconds_to_hmsms_list(dg1['diff_time'])
    dg1.columns=['subject', 'database', 'label', 'sum_time', 'time']
    DIR, databases_pair_paths, databases_paths, tier_lists, databases, databases_pairs, tiers=get_parameters()
    c=1
    conv=[]
    for i in range (1, len(listpaths), 2):
        values=[i, i+1]
        dgg=dg1[dg1.subject.isin(values)]
        conv+=list_of_words(c, len(dgg.subject))
        c+=1
    dg1['conv']=conv
    dg1.columns=['subject', 'database', 'label', 'sum_time', 'time', 'conv']
    roles=[]
    for r in range(1, len(listpaths), 2):
        dgf=dg1[dg1.subject.eq(r)]
        roles+=list_of_words("A", len(dgf.subject))
        r+=1
        dgf=dg1[dg1.subject.eq(r)]
        roles+=list_of_words("B", len(dgf.subject))
    dg1['roles']=roles
    dg1.columns=['subject', 'database', 'label', 'sum_time', 'time', 'conv', 'roles']
    #correct lines (replace the row in A which is not in B and same in te other sens with 0)
    dg1=dg1.loc[:,['label', 'sum_time', 'conv', 'roles']]
    dg1=dg1.reindex(columns=['conv', 'label', 'sum_time', 'roles'])
    dict_=list(dg1.to_records(index=False))
    conv=list(np.unique(conv))
    labels=tier_lists["Smiles"]
    for a in conv:
        J_A=[]
        J_B=[]
        label_B=[]
        label_A=[]
        for _ in dict_:
            if _[0]==a and _[3]=='A':
                J_A.append(_)
            if _[0]==a and _[3]=='B':
                J_B.append(_)
        for i in J_B: label_B.append(i[1])
        for j in J_A: label_A.append(j[1])
        for _ in labels:
            if _ in label_B:
                pass
            else:
                dict_.append((a, _, 0, 'B'))
            if _ in label_A:
                pass
            else:
                dict_.append((a, _, 0, 'A'))
    conv=[]
    label=[]
    sum_time=[]
    roles=[]
    for _ in range(len(dict_)):
        conv.append(dict_[_][0])
        label.append(dict_[_][1])
        sum_time.append(dict_[_][2])
        roles.append(dict_[_][3])
    dg1=pd.DataFrame({'conv': conv, 'label': label, 'sum_time': sum_time, 'roles': roles})
    dg1=dg1.sort_values(['conv', 'label'], ascending=[True, True]).reset_index()
    dg1.drop(dg1.columns[[0]], axis=1, inplace=True)
    dfA=dg1[dg1.roles.eq('A')]
    dfB=dg1[dg1.roles.eq('B')]
    difA=pd.DataFrame(dfA).reset_index()
    difB=pd.DataFrame(dfB).reset_index()
    dg=difA.merge(difB, how='left', left_index=True, right_index=True)
    diff_time=[]
    for i, j in zip(dg.sum_time_x, dg.sum_time_y):
        diff_time.append(max(i,j)-min(i,j))
    dg['diff_time']=diff_time
    dg.drop(dg.columns[[0, 3, 4, 5, 6, 7, 8, 9]], axis=1, inplace=True) 
    dg['database']=list_of_words(string, len(dg.conv_x))
    dg.columns=['conv', 'label', 'duration', 'database']
    dg['time']=seconds_to_hmsms_list(dg['duration'])
    dg.columns=['conv', 'label', 'duration', 'database', 'time']
    lst=df_to_list(dg)
    col=['conv', 'label', 'duration', 'database', 'time']
    return lst, col

def get_inter_smiles_relative_duration_folder(listpaths, string):
    """ This function calculates relative duration for smiles in a dataset considering one interaction.
    
    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:        
        Tuple: (list of tuple , description of tuples) -> (list, ['conv', 'label', 'percentage', 'database'])
    """
    df1=get_smiles_dict_conv_folder(listpaths, string)
    df1=list_to_df(df1[0], df1[1])
    dg1=df1.loc[:,['subject', 'database', 'label', 'duration', 'diff_time']]
    dg1['label'] = dg1['label'].str.replace(' ', '')
    dg1=dg1.groupby(['subject', 'database', 'label', 'duration']).sum(numeric_only=True).reset_index()
    dg1['percentage']=round(((dg1['diff_time']/dg1['duration'])*100),2)
    dg1.columns=['subject', 'database', 'label', 'duration', 'sum_time', 'percentage']
    c=1
    conv=[]
    for i in range(1, len(listpaths), 2):
        values=[i, i+1]
        dgg= dg1[dg1.subject.isin(values)]
        conv+=list_of_words(c, len(dgg.subject))
        c+=1
    dg1['conv']=conv
    dg1.columns=['subject', 'database', 'label', 'duration', 'sum_time', 'percentage', 'conv']
    roles=[]
    for r in range(1, len(listpaths), 2):
        dgf=dg1[dg1.subject.eq(r)]
        roles+=list_of_words("A", len(dgf.subject))
        r+=1
        dgf=dg1[dg1.subject.eq(r)]
        roles+=list_of_words("B", len(dgf.subject))
    dg1['roles']=roles
    dg1.columns=['subject', 'database', 'label', 'duration', 'sum_time', 'percentage', 'conv', 'roles']
    #correct lines (replace the row in A which is not in B and same in te other sens with 0)
    dg1=dg1.loc[:,['label', 'percentage', 'conv', 'roles']]
    dg1=dg1.reindex(columns=['conv', 'label', 'percentage', 'roles'])
    dict_=list(dg1.to_records(index=False))
    DIR, databases_pair_paths, databases_paths, tier_lists, databases, databases_pairs, tiers=get_parameters()
    conv=list(np.unique(conv))
    labels=tier_lists["Smiles"]
    for a in conv:
        J_A=[]
        J_B=[]
        label_B=[]
        label_A=[]
        for _ in dict_:
            if _[0]==a and _[3]=='A':
                J_A.append(_)
            if _[0]==a and _[3]=='B':
                J_B.append(_)
        for i in J_B: label_B.append(i[1])
        for j in J_A: label_A.append(j[1])
        for _ in labels:
            if _ in label_B:
                pass
            else:
                dict_.append((a, _, 0, 'B'))
            if _ in label_A:
                pass
            else:
                dict_.append((a, _, 0, 'A'))
    conv=[]
    label=[]
    pct=[]
    roles=[]
    for _ in range(len(dict_)):
        conv.append(dict_[_][0])
        label.append(dict_[_][1])
        pct.append(dict_[_][2])
        roles.append(dict_[_][3])
    dg1=pd.DataFrame({'conv': conv, 'label': label, 'percentage': pct, 'roles': roles})
    dg1=dg1.sort_values(['conv', 'label'], ascending=[True, True]).reset_index()
    dg1.drop(dg1.columns[[0]], axis=1, inplace=True) 
    dfA=dg1[dg1.roles.eq('A')]
    dfB=dg1[dg1.roles.eq('B')]
    difA=pd.DataFrame(dfA).reset_index()
    difB=pd.DataFrame(dfB).reset_index()
    dg=difA.merge(difB, how='left', left_index=True, right_index=True)
    diff_pct=[]
    for i, j in zip(dg.percentage_x, dg.percentage_y):
        diff_pct.append(max(i,j)-min(i,j))
    dg['diff_pct']=diff_pct
    dg.drop(dg.columns[[0,3,4,5,6,7,8,9]], axis=1, inplace=True) 
    dg['database']=list_of_words(string, len(dg.conv_x))
    dg.columns=['conv', 'label', 'percentage', 'database']
    lst=df_to_list(dg)
    col=['conv', 'label', 'percentage', 'database']
    return lst, col

def get_inter_laughs_absolute_duration_folder(listpaths, string):
    """ This function calculates absolute duration for laughs in a dataset considering one interaction.
    
    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:    
        Tuple: (list of tuple, description of tuples) -> (list, ['conv', 'label', 'duration', 'database', 'time'])
    """
    df=get_laughs_dict_conv_folder(listpaths, string)
    df=list_to_df(df[0], df[1])
    dg1=df.loc[:,['subject', 'database', 'label', 'diff_time']]
    dg1['label'] = dg1['label'].str.replace(' ', '')
    dg1=dg1.groupby(['subject', 'database', 'label']).sum(numeric_only=True).reset_index()
    dg1['time']=seconds_to_hmsms_list(dg1['diff_time'])
    dg1.columns=['subject', 'database', 'label', 'sum_time', 'time']
    c=1
    conv=[]
    for i in range(1, len(listpaths), 2):
        values=[i, i+1]
        dgg= dg1[dg1.subject.isin(values)]
        conv+=list_of_words(c, len(dgg.subject))
        c+=1
    dg1['conv']=conv
    dg1.columns=['subject', 'database', 'label', 'sum_time', 'time', 'conv']
    roles=[]
    for r in range(1, len(listpaths), 2):
        dgf=dg1[dg1.subject.eq(r)]
        roles+=list_of_words("A", len(dgf.subject))
        r+=1
        dgf=dg1[dg1.subject.eq(r)]
        roles+=list_of_words("B", len(dgf.subject))
    dg1['roles']=roles
    dg1.columns=['subject', 'database', 'label', 'sum_time', 'time', 'conv', 'roles']
    #correct lines (replace the row in A which is not in B and same in te other sens with 0)
    dg1=dg1.loc[:,['label', 'sum_time', 'conv', 'roles']]
    dg1=dg1.reindex(columns=['conv', 'label', 'sum_time', 'roles'])
    dict_=list(dg1.to_records(index=False))
    DIR, databases_pair_paths, databases_paths, tier_lists, databases, databases_pairs, tiers=get_parameters()
    conv=list(np.unique(conv))
    labels=tier_lists["Laughs"]
    for a in conv:
        J_A=[]
        J_B=[]
        label_B=[]
        label_A=[]
        for _ in dict_:
            if _[0]==a and _[3]=='A':
                J_A.append(_)
            if _[0]==a and _[3]=='B':
                J_B.append(_)
        for i in J_B: label_B.append(i[1])
        for j in J_A: label_A.append(j[1])
        for _ in labels:
            if _ in label_B:
                pass
            else:
                dict_.append((a, _, 0, 'B'))
            if _ in label_A:
                pass
            else:
                dict_.append((a, _, 0, 'A'))
    conv=[]
    label=[]
    sum_time=[]
    roles=[]
    for _ in range(len(dict_)):
        conv.append(dict_[_][0])
        label.append(dict_[_][1])
        sum_time.append(dict_[_][2])
        roles.append(dict_[_][3])
    dg1=pd.DataFrame({'conv': conv, 'label': label, 'sum_time': sum_time, 'roles': roles})
    dg1=dg1.sort_values(['conv', 'label'], ascending=[True, True]).reset_index()
    dg1.drop(dg1.columns[[0]], axis=1, inplace=True) 
    dfA=dg1[dg1.roles.eq('A')]
    dfB=dg1[dg1.roles.eq('B')]
    difA=pd.DataFrame(dfA).reset_index()
    difB=pd.DataFrame(dfB).reset_index()
    dg= difA.merge(difB, how='left', left_index=True, right_index=True)
    diff_time=[]
    for i, j in zip(dg.sum_time_x, dg.sum_time_y):
        diff_time.append(max(i,j)-min(i,j))
    dg['diff_time']=diff_time
    dg.drop(dg.columns[[0, 3, 4, 5, 6, 7, 8, 9]], axis=1, inplace=True) 
    dg['database']=list_of_words(string, len(dg.conv_x))
    dg.columns=['conv', 'label', 'duration', 'database']
    dg['time']=seconds_to_hmsms_list(dg['duration'])
    dg.columns=['conv', 'label', 'duration', 'database', 'time']
    lst=df_to_list(dg)
    col=['conv', 'label', 'duration', 'database', 'time']
    return lst, col

def get_inter_laughs_relative_duration_folder(listpaths, string):
    """ This function calculates relative duration for laughs in a dataset considering one interaction.
    
    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:        
        Tuple: (list of tuple, description of tuples) -> (list, ['conv', 'label', 'percentage', 'database'])
    """
    df1=get_laughs_dict_conv_folder(listpaths, string)
    df1=list_to_df(df1[0], df1[1])
    dg1=df1.loc[:,['subject', 'database', 'label', 'duration', 'diff_time']]
    dg1['label'] = dg1['label'].str.replace(' ', '')
    dg1=dg1.groupby(['subject', 'database', 'label', 'duration']).sum(numeric_only=True).reset_index()
    dg1['percentage']=round(((dg1['diff_time']/dg1['duration'])*100),2)
    dg1.columns=['subject', 'database', 'label', 'duration', 'sum_time', 'percentage']
    c=1
    conv=[]
    for i in range(1, len(listpaths), 2):
        values=[i, i+1]
        dgg= dg1[dg1.subject.isin(values)]
        conv+=list_of_words(c, len(dgg.subject))
        c+=1
    dg1['conv']=conv
    dg1.columns=['subject', 'database', 'label', 'duration', 'sum_time', 'percentage', 'conv']
    roles=[]
    for r in range(1, len(listpaths), 2):
        dgf=dg1[dg1.subject.eq(r)]
        roles+=list_of_words("A", len(dgf.subject))
        r+=1
        dgf=dg1[dg1.subject.eq(r)]
        roles+=list_of_words("B", len(dgf.subject))
    dg1['roles']=roles
    dg1.columns=['subject', 'database', 'label', 'duration', 'sum_time', 'percentage', 'conv', 'roles']
    #correct lines (replace the row in A which is not in B and same in te other sens with 0)
    dg1=dg1.loc[:,['label', 'percentage', 'conv', 'roles']]
    dg1=dg1.reindex(columns=['conv', 'label', 'percentage', 'roles'])
    dict_=list(dg1.to_records(index=False))
    DIR, databases_pair_paths, databases_paths, tier_lists, databases, databases_pairs, tiers=get_parameters()
    labels=tier_lists["Laughs"]
    for a in conv:
        J_A=[]
        J_B=[]
        label_B=[]
        label_A=[]
        for _ in dict_:
            if _[0]==a and _[3]=='A':
                J_A.append(_)
            if _[0]==a and _[3]=='B':
                J_B.append(_)
        for i in J_B: label_B.append(i[1])
        for j in J_A: label_A.append(j[1])
        for _ in labels:
            if _ in label_B:
                pass
            else:
                dict_.append((a, _, 0, 'B'))
            if _ in label_A:
                pass
            else:
                dict_.append((a, _, 0, 'A'))
    conv=[]
    label=[]
    pct=[]
    roles=[]
    for _ in range(len(dict_)):
        conv.append(dict_[_][0])
        label.append(dict_[_][1])
        pct.append(dict_[_][2])
        roles.append(dict_[_][3])
    dg1=pd.DataFrame({'conv': conv, 'label': label, 'percentage': pct, 'roles': roles})
    dg1=dg1.sort_values(['conv', 'label'], ascending=[True, True]).reset_index()
    dg1.drop(dg1.columns[[0]], axis=1, inplace=True) 
    dfA=dg1[dg1.roles.eq('A')]
    dfB=dg1[dg1.roles.eq('B')]
    difA=pd.DataFrame(dfA).reset_index()
    difB=pd.DataFrame(dfB).reset_index()
    dg=difA.merge(difB, how='left', left_index=True, right_index=True)
    diff_pct=[]
    for i, j in zip(dg.percentage_x, dg.percentage_y):
        diff_pct.append(max(i,j)-min(i,j))
    dg['diff_pct']=diff_pct
    dg.drop(dg.columns[[0, 3, 4, 5, 6, 7, 8, 9]], axis=1, inplace=True) 
    dg['database']=list_of_words(string, len(dg.conv_x))
    dg.columns=['conv', 'label', 'percentage', 'database']
    lst=df_to_list(dg)
    col=['conv', 'label', 'percentage', 'database']
    return lst, col

def get_inter_tier_absolute_duration_folder(listpaths, string, tier, label):
    """ This function calculates the absolute duration for a specific tier in a dataset considering one interaction.
    
    Args:
        listpaths (list): List of filespaths
        string (str): Name of the dataset
        tier (str): Tier name
    Returns:
        Tuple: (list of tuple, description of tuples) -> (list, ['conv', 'label', 'duration', 'database', 'time'])
    """
    df=get_tier_dict_conv_folder(listpaths, string, tier)
    df=list_to_df(df[0], df[1])
    dg1=df.loc[:, ['subject', 'database', 'label', 'diff_time']]
    dg1['label'] = dg1['label'].str.replace(' ', '')
    dg1=dg1.groupby(['subject', 'database', 'label']).sum(numeric_only=True).reset_index()
    dg1['time']=seconds_to_hmsms_list(dg1.groupby('database')['diff_time'].transform('sum'))
    dg1.columns=['subject', 'database', 'label', 'sum_time', 'time']
    c=1
    conv=[]
    for i in range(1, len(listpaths), 2):
        values=[i, i+1]
        dgg=dg1[dg1.subject.isin(values)]
        conv+=list_of_words(c, len(dgg.subject))
        c+=1
    dg1['conv']=conv
    dg1.columns=['subject', 'database', 'label', 'sum_time', 'time', 'conv']
    roles=[]
    for r in range(1, len(listpaths), 2):
        dgf=dg1[dg1.subject.eq(r)]
        roles+=list_of_words("A", len(dgf.subject))
        r+=1
        dgf=dg1[dg1.subject.eq(r)]
        roles+=list_of_words("B", len(dgf.subject))
    dg1['roles']=roles
    dg1.columns=['subject', 'database', 'label', 'sum_time', 'time', 'conv', 'roles']
    dg1=dg1.loc[:, ['label', 'sum_time', 'conv', 'roles']]
    dg1=dg1.reindex(columns=['conv', 'label', 'sum_time', 'roles'])
    dict_=list(dg1.to_records(index=False))
    conv=list(np.unique(conv))
    if label[tier]['Replace_Value'] != "" :
        labels= [label[tier]['Replace_Value'], str("No_" + label[tier]['Replace_Value'])]
    else :
        labels = label[tier]['Intensities']
    for a in conv:
        J_A=[]
        J_B=[]
        label_B=[]
        label_A=[]
        for _ in dict_:
            if _[0]==a and _[3]=='A':
                J_A.append(_)
            if _[0]==a and _[3]=='B':
                J_B.append(_)
        for i in J_B:
            label_B.append(i[1])
        for j in J_A:
            label_A.append(j[1])
        for _ in labels:
            if _ in label_B:
                pass
            else:
                dict_.append((a, _, 0, 'B'))
            if _ in label_A:
                pass
            else:
                dict_.append((a, _, 0, 'A'))
    conv=[]
    label=[]
    sum_time=[]
    roles=[]
    for _ in range(len(dict_)):
        conv.append(dict_[_][0])
        label.append(dict_[_][1])
        sum_time.append(dict_[_][2])
        roles.append(dict_[_][3])
    dg1=pd.DataFrame({'conv': conv, 'label': label, 'sum_time': sum_time, 'roles': roles})
    dg1=dg1.sort_values(['conv', 'label'], ascending=[True, True]).reset_index()
    dg1.drop(dg1.columns[[0]], axis=1, inplace=True)
    dfA=dg1[dg1.roles.eq('A')]
    dfB=dg1[dg1.roles.eq('B')]
    difA=pd.DataFrame(dfA).reset_index()
    difB=pd.DataFrame(dfB).reset_index()
    dg=difA.merge(difB, how='left', left_index=True, right_index=True)
    diff_time=[]
    for i, j in zip(dg.sum_time_x, dg.sum_time_y):
        diff_time.append(max(i, j)-min(i, j))
    dg['diff_time']=diff_time
    dg.drop(dg.columns[[0, 3, 4, 5, 6, 7, 8, 9]], axis=1, inplace=True)
    dg['database']=list_of_words(string, len(dg.conv_x))
    dg.columns=['conv', 'label', 'duration', 'database']
    dg['time']=seconds_to_hmsms_list(dg['duration'])
    dg.columns=['conv', 'label', 'duration', 'database', 'time']
    lst=df_to_list(dg)
    col=['conv', 'label', 'duration', 'database', 'time']
    return lst, col

def get_inter_tier_relative_duration_folder(listpaths, string, tier, label):
    """ This function calculates relative duration for a specific tier in a dataset considering one interaction.
    
    Args:
        listpaths (list): List of filespaths
        string (str): Name of the dataset
        tier (str): Tier name
    Returns:
        Tuple: (list of tuple, description of tuples) -> (list, ['conv', 'label', 'percentage', 'database'])
    """
    df=get_tier_dict_conv_folder(listpaths, string, tier)
    df=list_to_df(df[0], df[1])
    dg1=df.loc[:, ['subject', 'database', 'label', 'duration', 'diff_time']]
    dg1['label'] = dg1['label'].str.replace(' ', '')
    dg1=dg1.groupby(['subject', 'database', 'label', 'duration']).sum(numeric_only=True).reset_index()
    dg1['percentage']=round(((dg1['diff_time']/dg1.groupby('database')['diff_time'].transform('sum'))*100),2)
    dg1.columns=['subject', 'database', 'label', 'duration', 'sum_time', 'percentage']
    c=1
    conv=[]
    for i in range(1, len(listpaths), 2):
        values=[i, i+1]
        dgg=dg1[dg1.subject.isin(values)]
        conv+=list_of_words(c, len(dgg.subject))
        c+=1
    dg1['conv']=conv
    dg1.columns=['subject', 'database', 'label', 'duartion', 'sum_time', 'time', 'conv']
    roles=[]
    for r in range(1, len(listpaths), 2):
        dgf=dg1[dg1.subject.eq(r)]
        roles+=list_of_words("A", len(dgf.subject))
        r+=1
        dgf=dg1[dg1.subject.eq(r)]
        roles+=list_of_words("B", len(dgf.subject))
    dg1['roles']=roles
    dg1.columns=['subject', 'database', 'label', 'duartion', 'sum_time', 'percentage', 'conv', 'roles']
    dg1=dg1.loc[:, ['label', 'percentage', 'conv', 'roles']]
    dg1=dg1.reindex(columns=['conv', 'label', 'percentage', 'roles'])
    dict_=list(dg1.to_records(index=False))
    if label[tier]['Replace_Value'] != "" :
        labels= [label[tier]['Replace_Value'], str("No_" + label[tier]['Replace_Value'])]
    else :
        labels = label[tier]['Intensities']
    for a in conv:
        J_A=[]
        J_B=[]
        label_B=[]
        label_A=[]
        for _ in dict_:
            if _[0]==a and _[3]=='A':
                J_A.append(_)
            if _[0]==a and _[3]=='B':
                J_B.append(_)
        for i in J_B:
            label_B.append(i[1])
        for j in J_A:
            label_A.append(j[1])
        for _ in labels:
            if _ in label_B:
                pass
            else:
                dict_.append((a, _, 0, 'B'))
            if _ in label_A:
                pass
            else:
                dict_.append((a, _, 0, 'A'))
    conv=[]
    label=[]
    pct=[]
    roles=[]
    for _ in range(len(dict_)):
        conv.append(dict_[_][0])
        label.append(dict_[_][1])
        pct.append(dict_[_][2])
        roles.append(dict_[_][3])
    dg1=pd.DataFrame({'conv': conv, 'label': label, 'percentage': pct, 'roles': roles})
    dg1=dg1.sort_values(['conv', 'label'], ascending=[True, True]).reset_index()
    dg1.drop(dg1.columns[[0]], axis=1, inplace=True)
    dfA=dg1[dg1.roles.eq('A')]
    dfB=dg1[dg1.roles.eq('B')]
    difA=pd.DataFrame(dfA).reset_index()
    difB=pd.DataFrame(dfB).reset_index()
    dg=difA.merge(difB, how='left', left_index=True, right_index=True)
    diff_pct=[]
    for i, j in zip(dg.percentage_x, dg.percentage_y):
        diff_pct.append(max(i, j)-min(i, j))
    dg['diff_pct']=diff_pct
    dg.drop(dg.columns[[0, 3, 4, 5, 6, 7, 8, 9]], axis=1, inplace=True)
    dg['database']=list_of_words(string, len(dg.conv_x))
    dg.columns=['conv', 'label', 'percentage', 'database']
    lst=df_to_list(dg)
    col=['conv', 'label', 'percentage', 'database']
    return lst, col

#By roles
#Smiles
def get_inter_smiles_ad_spk_vs_lsn_folder(listpaths, string):
    """ This function calculates absolute duration for smiles when a speaker is in front of a listener.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        Tuple (list, description of the list) -> (list, ['database', 'conv', 'role', 'label', 'sum_time', 'time']) 
    """
    df=get_smiles_from_spk_vs_lsn_folder(listpaths, string)
    df=list_to_df(df[0], df[1])
    dg1=df.loc[:,['database', 'conv', 'role', 'label', 'diff_time']]
    dg1=dg1.groupby(['database', 'conv', 'role', 'label']).sum(numeric_only=True).reset_index()
    dg1['time']=seconds_to_hmsms_list(dg1['diff_time'])
    dg1.columns=['database', 'conv', 'role', 'label', 'sum_time', 'time']
    lst=df_to_list(dg1)
    col=['database', 'conv', 'role', 'label', 'sum_time', 'time']
    return lst, col

def get_inter_smiles_rd_spk_vs_lsn_folder(listpaths, string):
    """ This function calculates relative duration for smiles when a speaker is in front of a listener.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        Tuple (list, description of the list) -> (list, ['database', 'conv', 'label', 'percentage', 'role'])
    """
    df=get_smiles_from_spk_vs_lsn_folder(listpaths, string)
    df=list_to_df(df[0], df[1])
    dg1=df.loc[:,['database', 'label', 'duration', 'conv', 'role', 'diff_time']]
    dg1=dg1.groupby(['database', 'label', 'duration', 'conv', 'role']).sum(numeric_only=True).reset_index()
    dg1['percentage']=round(((dg1['diff_time']/dg1['duration'])*100),2)
    dg1.columns=['database', 'label', 'duration', 'conv', 'role', 'sum_time', 'percentage']
    dg1.drop(dg1.columns[[2, 5]], axis=1, inplace=True)
    dg1=dg1.reindex(columns=['database', 'conv', 'label', 'percentage', 'role'])
    lst=df_to_list(dg1)
    col=['database', 'conv', 'label', 'percentage', 'role']
    return lst, col

def get_inter_smiles_ad_lsn_vs_spk_folder(listpaths, string):
    """ This function calculates absolute duration for smiles when a listener is in front of a speaker.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        Tuple (list, description of the list) -> (list, ['database', 'label', 'conv', 'role', 'sum_time', 'time']) 
    """
    df=get_smiles_from_lsn_vs_spk_folder(listpaths, string)
    df=list_to_df(df[0], df[1])
    dg1=df.loc[:,['database', 'label', 'conv', 'role', 'diff_time']]
    dg1=dg1.groupby(['database', 'label', 'conv', 'role']).sum(numeric_only=True).reset_index()
    dg1['time']=seconds_to_hmsms_list(dg1['diff_time'])
    dg1.columns=['database', 'label', 'conv', 'role', 'sum_time', 'time']
    lst=df_to_list(dg1)
    col=['database', 'label', 'conv', 'role', 'sum_time', 'time']
    return lst, col

def get_inter_smiles_rd_lsn_vs_spk_folder(listpaths, string):
    """ This function calculates relative duration for smiles when a listener is in front of a speaker.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        Tuple (list, description of the list) -> (list, ['database', 'conv', 'label', 'percentage', 'role'])
    """
    df=get_smiles_from_lsn_vs_spk_folder(listpaths, string)
    df=list_to_df(df[0], df[1])
    dg1=df.loc[:,['database', 'label', 'duration', 'conv', 'role', 'diff_time']]
    dg1=dg1.groupby(['database', 'label', 'duration', 'conv', 'role']).sum(numeric_only=True).reset_index()
    dg1['percentage']=round(((dg1['diff_time']/dg1['duration'])*100),2)
    dg1.columns=['database', 'label', 'duration', 'conv', 'role', 'sum_time', 'percentage']
    dg1.drop(dg1.columns[[2, 5]], axis=1, inplace=True)
    dg1=dg1.reindex(columns=['database', 'conv', 'label', 'percentage', 'role'])
    lst=df_to_list(dg1)
    col=['database', 'conv', 'label', 'percentage', 'role']
    return lst, col

#Laughs
def get_inter_laughs_ad_spk_vs_lsn_folder(listpaths, string):
    """ This function calculates absolute duration for laughs when a speaker is in front of a listener.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        Tuple (list, description of the list) -> (list, ['database', 'label', 'conv', 'role', 'sum_time', 'time']) 
    """
    df=get_laughs_from_spk_vs_lsn_folder(listpaths, string)
    df=list_to_df(df[0], df[1])
    dg1=df.loc[:,['database', 'label', 'conv', 'role', 'diff_time']]
    dg1=dg1.groupby(['database', 'label', 'conv', 'role']).sum(numeric_only=True).reset_index()
    dg1['time']=seconds_to_hmsms_list(dg1['diff_time'])
    dg1.columns=['database', 'label', 'conv', 'role', 'sum_time', 'time']
    lst=df_to_list(dg1)
    col=['database', 'label', 'conv', 'role', 'sum_time', 'time']
    return lst, col

def get_inter_laughs_rd_spk_vs_lsn_folder(listpaths, string):
    """ This function calculates relative duration for laughs when a speaker is in front of a listener.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        Tuple (list, description of the list) -> (list, ['database', 'conv', 'label', 'percentage', 'role'])
    """
    df=get_laughs_from_spk_vs_lsn_folder(listpaths, string)
    df=list_to_df(df[0], df[1])
    dg1=df.loc[:,['database', 'label', 'duration', 'conv', 'role', 'diff_time']]
    dg1=dg1.groupby(['database', 'label', 'duration', 'conv', 'role']).sum(numeric_only=True).reset_index()
    dg1['percentage']=round(((dg1['diff_time']/dg1['duration'])*100),2)
    dg1.columns=['database', 'label', 'duration', 'conv', 'role', 'sum_time', 'percentage']
    dg1.drop(dg1.columns[[2, 5]], axis=1, inplace=True)
    dg1=dg1.reindex(columns=['database', 'conv', 'label', 'percentage', 'role'])
    lst=df_to_list(dg1)
    col=['database', 'conv', 'label', 'percentage', 'role']
    return lst, col

def get_inter_laughs_ad_lsn_vs_spk_folder(listpaths, string):
    """ This function calculates absolute duration for laughs when a listener is in front of a speaker.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        Tuple (list, description of the list) -> (list, ['database', 'label', 'conv', 'role', 'sum_time', 'time']) 
    """
    df=get_laughs_from_lsn_vs_spk_folder(listpaths, string)
    df=list_to_df(df[0], df[1])
    dg1=df.loc[:,['database', 'label', 'conv', 'role', 'diff_time']]
    dg1=dg1.groupby(['database', 'label', 'conv', 'role']).sum(numeric_only=True).reset_index()
    #dg1['time']=seconds_to_hmsms_list(dg1['diff_time'])
    dg1['time'] = seconds_to_hmsms_list(dg1.groupby('database')['diff_time'].transform('sum'))
    dg1.columns=['database', 'label', 'conv', 'role', 'sum_time', 'time']
    lst=df_to_list(dg1)
    col=['database', 'label', 'conv', 'role', 'sum_time', 'time']
    return lst, col

def get_inter_laughs_rd_lsn_vs_spk_folder(listpaths, string):
    """ This function calculates relative duration for laughs when a listener is in front of a speaker.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
    Returns:
        Tuple (list, description of the list) -> (list, ['database', 'conv', 'label', 'percentage', 'role'])
    """
    df=get_laughs_from_lsn_vs_spk_folder(listpaths, string)
    df=list_to_df(df[0], df[1])
    dg1=df.loc[:,['database', 'label', 'duration', 'conv', 'role', 'diff_time']]
    dg1=dg1.groupby(['database', 'label', 'duration', 'conv', 'role']).sum(numeric_only=True).reset_index()
    dg1['percentage']=round(((dg1['diff_time']/dg1['duration'])*100),2)
    dg1.columns=['database', 'label', 'duration', 'conv', 'role', 'sum_time', 'percentage']
    dg1.drop(dg1.columns[[2, 5]], axis=1, inplace=True)
    dg1=dg1.reindex(columns=['database', 'conv', 'label', 'percentage', 'role'])
    lst=df_to_list(dg1)
    col=['database', 'conv', 'label', 'percentage', 'role']
    return lst, col

#Tiers
def get_inter_tier_ad_entity1_vs_entity2_folder(listpaths, string, tier1, tier2, entity1, entity2):
    """ This function calculates absolute duration for a tier when entity1 is in front of entity2.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
        tier1 (str): name of the tier1
        tier2 (str): name of the tier2
        entity1 (str): name of the entity1
        entity2 (str): name of the entity2
    Returns:
        Tuple (list, description of the list) -> (list, ['database', 'label', 'conv', 'role', 'sum_time', 'time']) """
    df=get_tier_from_entity1_vs_entity2_folder(listpaths, string, tier1, tier2, entity1, entity2)
    df=list_to_df(df[0], df[1])
    dg1=df.loc[:,['database', 'label', 'conv', 'role', 'diff_time']]
    dg1['label'] = dg1['label'].str.replace(' ', '')
    dg1=dg1.groupby(['database', 'label', 'conv', 'role']).sum(numeric_only=True).reset_index()
    #dg1['time']=seconds_to_hmsms_list(dg1['diff_time'])
    dg1['time'] = seconds_to_hmsms_list(dg1.groupby('database')['diff_time'].transform('sum'))
    dg1.columns=['database', 'label', 'conv', 'role', 'sum_time', 'time']
    lst=df_to_list(dg1)
    col=['database', 'label', 'conv', 'role', 'sum_time', 'time']
    return lst, col

def get_inter_tier_rd_entity1_vs_entity2_folder(listpaths, string, tier1, tier2, entity1, entity2):
    """ This function calculates relative duration for a tier when entity1 is in front of entity2.

    Args:
        listpaths (list): list of filespath
        string (str): name of the dataset
        tier1 (str): name of the tier1
        tier2 (str): name of the tier2
        entity1 (str): name of the entity1
        entity2 (str): name of the entity2
        tier_lists (dict): dictionary of tiers
    Returns:
        Tuple (list, description of the list) -> (list, ['database', 'label', 'conv', 'role', 'sum_time', 'percentage']) """
    df=get_tier_from_entity1_vs_entity2_folder(listpaths, string, tier1, tier2, entity1, entity2)
    df=list_to_df(df[0], df[1])
    dg1=df.loc[:,['database', 'label', 'duration', 'conv', 'role', 'diff_time']]
    dg1['label'] = dg1['label'].str.replace(' ', '')
    dg1=dg1.groupby(['database', 'label', 'duration', 'conv', 'role']).sum(numeric_only=True).reset_index()
    # dg1['percentage']=round(((dg1['diff_time']/dg1['duration'])*100),2)
    dg1['percentage'] = round(((dg1['diff_time'] / dg1.groupby('database')['diff_time'].transform('sum')) * 100), 2)
    dg1.columns=['database', 'label', 'duration', 'conv', 'role', 'sum_time', 'percentage']
    dg1.drop(dg1.columns[[2, 5]], axis=1, inplace=True)
    dg1=dg1.reindex(columns=['database', 'conv', 'label', 'percentage', 'role'])
    lst=df_to_list(dg1)
    col=['database', 'conv', 'label', 'percentage', 'role']
    return lst, col

#Expressions track _____________________________________________________________________________________________________________________________ 
def fill_expression_track(track, check, folder, database):
    """ This function fill some lists where we put previous and next expressions concerning a tracked expression.

    Args:
        track (string): expression tracked
        check (string): expression checked
        folder (list): eaf paths
        database (string): database concerned
    Returns:
        tuple: (database concerned, number of the expression, list of previous expressions, list of next expressions). Each element of the tuple is a list
    """
    string=database.lower()
    track_p, track_f, sl_number, subjects=([] for _ in range(4))
    for root in range(0, len(folder), 1):
        sl_lst=get_TCdict(folder[root], track, check)
        track_lst=eval('get_tier_dict')(folder[root], track)
        #For all elements in track_lst
        i=1
        for _ in range(0, len(track_lst), 1):
            stt=track_lst[_][0]
            stp=track_lst[_][1]
            subjects.append(string)
            for _ in range(0, len(sl_lst), 1):
                if (sl_lst[_][0]==stt) and (sl_lst[_][1]==stp):
                    if (sl_lst[_]==sl_lst[0]):    #we check if we are with the first element of the list
                            track_p.append('No')
                    else:
                        if (sl_lst[_-1][2]==check):           
                            track_p.append('Yes')
                        else:
                            track_p.append('No')
                    if (sl_lst[_]==sl_lst[len(sl_lst)-1]):    #we check if we are with the last element of the list
                        track_f.append('No')
                    else:
                        if (sl_lst[_+1][2]==check):       
                            track_f.append('Yes')
                        else:
                            track_f.append('No')
                    sl_number.append(i)     
            i+=1 
    return subjects, sl_number, track_p, track_f

def fill_trackfp_byIR(folder, string, function_to_lst_check, function_to_lst_track, track, check, tier_lists, special=bool):
    """ This function fill some lists where we put previous and next expressions concerning a tracked expression filtered by entity.

    Args:
        folder (function):  list of filespath
        string (str): name of the dataset
        function_to_lst_check (function): function to apply to get the list of checked expressions
        function_to_lst_track (function): function to apply to get the list of tracked expressions
        track (str): name of the tracked expression
        check (str): name of the checked expression
        special (str, optional): True or False. Defaults to bool.
    Returns:
        tuple -> (database, current_level, track_number, trackp, trackf). Each element of the tuple is a list
    """
    """This function fill some lists where we put previous and next expressions concerning a tracked expression filtered by entity
    Return two databases : for previous and next expressions 
    """
    #Variables

    real_tier_lists , real_tiers = get_parameters_tag()

    trackp, trackf, track_number, current_level, database=([] for _ in range(5))
    for root in folder:
        n=1
        sl_lst=get_TCdict(root, track, check)
        lst_check=eval('function_to_lst_check')(root, check)
        if real_tier_lists[check]['Replace_Value'] != "" :
             for i, item in enumerate(lst_check):
                if item[2] != "":
                    lst_check[i] = (item[0], item[1], real_tier_lists[check]['Replace_Value'])
                else:
                    lst_check[i] = (item[0], item[1], "No_" + real_tier_lists[check]['Replace_Value'])
        lst_track=eval('function_to_lst_track')(root, track)
        if real_tier_lists[track]['Replace_Value'] != "" :
             for i, item in enumerate(lst_track):
                if item[2] != "":
                    lst_track[i] = (item[0], item[1], real_tier_lists[track]['Replace_Value'])
                else:
                    lst_track[i] = (item[0], item[1], "No_" + real_tier_lists[track]['Replace_Value'])
        level_list=[]
        current_level=[]
        if real_tier_lists[track]['Replace_Value'] != "" :
            values_track = [real_tier_lists[track]['Replace_Value'], str("No_" + real_tier_lists[track]['Replace_Value'])]
        else :
            values_track = real_tier_lists[track]['Intensities']
        for entity in values_track:
            lst=keep_info_with_lab(lst_track, entity, 2)
            level_list+=lst
            current_level+=list_of_words(entity.lower(), len(lst))
        all_stt_s=[k[0] for k in lst_check]
        if len(level_list)==0:
            pass
        else:
            for j in level_list:
                stt_l=j[0]
                stp_l=j[1]
                database.append(string)
                for _ in range(0, len(sl_lst), 1):
                    if (sl_lst[_][0]==stt_l) and (sl_lst[_][1]==stp_l):     #(1)
                        if (sl_lst[_]==sl_lst[0]):    #we check if we are with the first element of the list
                            trackp.append('null')
                        else:
                            if (sl_lst[_-1][2]==check):  #(2)
                                index_=0
                                stt_s=0
                                for k in all_stt_s:
                                    if sl_lst[_-1][0] in all_stt_s:
                                        if sl_lst[_-1][0]==k:
                                            stt_s=k
                                    else:
                                        pass
                                if len(lst_check)==0:
                                    pass
                                else:
                                    for i in range(len(lst_check)):
                                        if stt_s==lst_check[i][0]:
                                            index_=lst_check.index(lst_check[i])
                                    if stt_s==lst_check[index_][0]: 
                                        trackp.append(lst_check[index_][2])   #(4) 
                                    else: 
                                        trackp.append('null')
                            else:
                                trackp.append('null')
                        if (sl_lst[_]==sl_lst[len(sl_lst)-1]):    #we check if we are with the last element of the list
                            trackf.append('null')
                        else:
                            if (sl_lst[_+1][2]==check):       #(2)
                                index_=0
                                stt_s=0
                                for k in all_stt_s:
                                    if sl_lst[_+1][0] in all_stt_s:
                                        if sl_lst[_+1][0]==k:
                                            stt_s=k
                                    else:
                                        pass
                                if len(lst_check)==0:
                                    pass
                                else:
                                    for i in range(len(lst_check)):
                                        if stt_s==lst_check[i][0]:
                                            index_=lst_check.index(lst_check[i])
                                    if stt_s==lst_check[index_][0]: 
                                        trackf.append(lst_check[index_][2])   #(4) 
                                    else: 
                                        trackf.append('null')                                
                            else:
                                trackf.append('null')
                        track_number.append(n)
                n+=1
    return database, current_level, track_number, trackp, trackf

def expression_track(check, track, dir, databases_name):
    """ This function determines the previous and next expressions we have concerning a tracked expression.

    Args:
        check (str): It's the expression which preceed or follow
        track (str): It's the expression of which we want to know what is before and after
        dir (str) : path of the folder containing all databasets
        databases_name (list) : list of the databasets names
    Returns:
        database : A database containing the quantity of previous and next expressions
    """
    dg=[]
    n=0
    L=[]
    for path in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, path)):
            n+=1
            for i in databases_name:
                if path==i.lower():
                    L.append(get_all_filepaths((os.path.join(dir, path)), "eaf", None))   
    for i in range(len(L)):
        a=fill_expression_track(track, check, L[i], databases_name[i])
        # Check list lengths
        if len(a[0])==len(a[1])==len(a[2])==len(a[3]):
            df1=pd.DataFrame({'Database': a[0], 'N°'+track: a[1], 'Trackp': a[2], 'Trackf': a[3]})
            dg.append(df1)
        else:
            desired_length=min(len(a[0]), len(a[1]), len(a[2]), len(a[3]))  # Desired length based on existing listings
            # Create a new tuple with the first desired length elements
            a=(a[0][:desired_length], a[1][:desired_length], a[2][:desired_length], a[3][:desired_length])
            df1=pd.DataFrame({'Database': a[0], 'N°'+track: a[1], 'Trackp': a[2], 'Trackf': a[3]})
            dg.append(df1)
    df=pd.concat(dg)
    #Previous expression's track    
    df_g=df.groupby(['Trackp', 'Database']).size().reset_index()
    df_g.columns=['Trackp', 'Database', 'Countp']
    df_t=df_g.groupby(['Database'])['Countp'].sum(numeric_only=True).reset_index()
    tot=[]
    for _ in list(df_g["Database"]):
        for i in list(df_t['Database']):
            if _==i:
                tot.append(int(df_t[df_t.Database.eq(_)]['Countp']))
    df_g['tot']=tot
    df_g['Percentagep']=round(((df_g["Countp"]/df_g['tot'])*100), 2)
    df_g.columns=['Trackp', 'Databasep', 'Countp', 'tot', 'Percentagep']
    #Following expression's track 
    df1_g=df.groupby(['Trackf', 'Database']).size().reset_index()
    df1_g.columns=['Trackf', 'Database', 'Countf']
    df_t1=df1_g.groupby(['Database'])['Countf'].sum(numeric_only=True).reset_index()
    tot=[]
    for _ in list(df1_g["Database"]):
        for i in list(df_t1['Database']):
            if _==i:
                tot.append(int(df_t1[df_t1.Database.eq(_)]['Countf']))
    df1_g['tot']=tot
    df1_g['Percentagef']=round(((df1_g["Countf"]/df1_g['tot'])*100), 2)
    df1_g.columns=['Trackf', 'Databasef', 'Countf', 'tot', 'Percentagef']   
    dg=pd.concat([df_g, df1_g],axis=1)
    return dg

def expression_track_byI(check, track, DIR, databases_name, tier_lists):
    """ This function determines the previous and next expression taking into account the entities.
    
    Args :
        check (str): It's the expression which preced or follow
        track (str): It's the expression of which we want to know what is before and after
        dir (str) : path of the folder containing all databasets
        databases_name (list) : list of the datasets names
        tier_lists (list) : list of the tiers names
    Returns:
        tuple: (database for previous expressions, database for next expressions)
    """
    #Variables
    dg=[]
    n=0
    L=[]
    for path in os.listdir(DIR):
        if os.path.isdir(os.path.join(DIR, path)):
            n+=1
            for i in databases_name:
                if path==i.lower():
                    L.append((get_all_filepaths((os.path.join(DIR, path)), "eaf", None), path))
    for i in range(len(L)) :
        a=fill_trackfp_byIR(L[i][0], L[i][1], get_tier_dict, get_tier_dict, track, check, tier_lists, False)
        # Check list lengths
        if len(a[0])==len(a[1])==len(a[2])==len(a[3])==len(a[4]):
            df1 = pd.DataFrame({'Database':a[0],'Current_level_'+track : a[1], 'N°'+track: a[2],'Intensityp': a[3],
    'Intensityf':a[4]}) 
            dg.append(df1)
        else:
            desired_length=min(len(a[0]), len(a[1]), len(a[2]), len(a[3]), len(a[4]))  # Desired length based on existing listings
            # Create a new tuple with the first desired length elements
            a=(a[0][:desired_length], a[1][:desired_length], a[2][:desired_length], a[3][:desired_length], a[4][:desired_length])
            df1=pd.DataFrame({'Database':a[0],'Current_level_'+track : a[1], 'N°'+track: a[2],'Intensityp': a[3],
    'Intensityf':a[4]}) 
            dg.append(df1)
    df=pd.concat(dg)
    #Previous expression
    df_g=df.groupby(['Intensityp', 'Database', 'Current_level_'+track]).size().reset_index()
    df_g.columns = ['Intensityp', 'Database', 'Current_level_'+track, 'Count']
    df_t=df_g.groupby(['Database', 'Current_level_'+track])['Count'].sum(numeric_only=True).reset_index()
    tot=[]
    for _, j in zip(list(df_g["Database"]), list(df_g['Current_level_'+track])):
        for i, k in zip(list(df_t['Database']), list(df_t['Current_level_'+track])):
            if _==i and j==k:
                tot.append(int(df_t[df_t.Database.eq(_) & df_t['Current_level_'+track].eq(j)]['Count']))
    df_g['tot']=tot
    df_g['Percentage']=round(((df_g["Count"]/df_g['tot'])*100), 2)
    df_g.columns=['Intensityp', 'Databasep', 'Current_level_'+track+'p', 'Countp', 'tot', 'Percentagep']
    #Following expression
    df1_g=df.groupby(['Intensityf', 'Database', 'Current_level_'+track]).size().reset_index()
    df1_g.columns=['Intensityf', 'Database', 'Current_level_'+track, 'Count']
    df_t1=df1_g.groupby(['Database', 'Current_level_'+track])['Count'].sum(numeric_only=True).reset_index()
    tot=[]
    for _, j in zip(list(df1_g["Database"]), list(df1_g['Current_level_'+track ])):
        for i, k in zip(list(df_t1['Database']), list(df_t1['Current_level_'+track ])):
            if _==i and j==k:
                tot.append(int(df_t1[df_t1.Database.eq(_) & df_t1['Current_level_'+track].eq(j)]['Count']))
    df1_g['tot']=tot
    df1_g['Percentage']=round(((df1_g["Count"]/df1_g['tot'])*100), 2)
    df1_g.columns=['Intensityf', 'Databasef', 'Current_level_'+track+'f', 'Countf', 'tot', 'Percentagef'] 
    return df_g, df1_g

#Probabilities mimicry _________________________________________________________________________________________________________________________
def give_mimicry(lA, lB, delta_t=0):
    """ The function calculate the mimicry between two lists.
    
    Args :
        lA (list): list of tuples (start, stop, label) of expressions mimicked
        lB (list): list of tuples (start, stop, label) of expressions mimicking
        delta_t (int, optional): Defaults to 0.
                                Time after which expression occuring still counts as mimicry.
                                Should be in the same unit as the times in lstA and lstB 
    Returns:
        int: number of times B mimicked A (=len(the list described below))
        float: probability of B mimick A
    """
    count_=count_mimicry(lA, lB, delta_t)
    return (count_[0], round((count_[0]/len(lB)), 3))

def give_mimicry_folder1(function, folder, filter=None, label=None):
    """ Calculate mimicry of interactions on a folder

    Args:
        function (function): It's a function giving the list of tuples (start, stop, label) of expressions mimicked and mimicking
        folder (list): List of the .eaf files path 
        filter (string, optional): It has to be 'Intensity'. Defaults to None
        label (string or list, optional): If it's a string, it represents the intensity we want and if it's a list, 
        it represents the intensities we want to keep. Defaults to None
    Returns:
        list: A list of tuples [(count, probability),....]
    """
    DIR, databases_pair_paths, databases_paths, tier_lists, databases, databases_pairs, tiers=get_parameters()
    if folder==databases_pair_paths["ccdb_pairs"]:
        string='ccdb'
    if folder==databases_pair_paths["ifadv_pairs"]:
        string='ifadv'
    if folder==databases_pair_paths["ndc_pairs"]:
        string='ndc'
    dt=apply_function1(function, folder, string)  
    dt2=keep_info(dt[0], 4)
    df=list_to_df(dt2, dt[1][0:4])
    LA=[]
    LB=[]
    count_proba=[]
    n=1
    for _ in range(int(len(folder)/2)):
        if filter is None:    
            LA=df_to_list(df[df.subject.eq(n)])
            LB=df_to_list(df[df.subject.eq(n+1)])
        else:
            if filter=='Intensity':
                if type(label) is list:
                    LA=keep_info_with_lab(df_to_list(df[df.subject.eq(n)]), label[0], 2)
                    LB=keep_info_with_lab(df_to_list(df[df.subject.eq(n+1)]), label[1], 2)
                else:
                    LA=keep_info_with_lab(df_to_list(df[df.subject.eq(n)]), label, 2)
                    LB=keep_info_with_lab(df_to_list(df[df.subject.eq(n+1)]), label, 2)
        if len(LA)==0:
            LA.append((0, 0, 0, 0))
        if len(LB)==0:
            LB.append((0, 0, 0, 0))
        count_proba.append(give_mimicry(LA, LB))
        n+=2
    M=[]
    for i in count_proba:
        i+=(string,)
        M.append(i)
    return M

def give_mimicry_folder2(folder, database_pairs, function1, function2, tierA, tierB, filter=None, label=None, delta_t=0, mimic_choice=None):
    """ The function calculate the mimicry between two lists.
    
    Args:
        folder (list): List of the .eaf files path 
        database_pairs (string): The dataset of the pairs
        function1 (function): It's a function giving the list of tuples (start, stop, label) of expressions mimicked
        function2 (function): It's a function giving the list of tuples (start, stop, label) of expressions mimicking
        filter (string, optional): It has to be 'Intensity'. Defaults to None.
        tierA (string): The tier of the person A
        tierB (string): The mimicked tier by the person B
        label (string or list, optional): If it's a string, it represents the intensity we want and if it's a list, 
        it represents the intensities we want to keep. Defaults to None.
        delta_t (int, optional): Defaults to 0.
                                Time after which expression occuring still counts as mimicry.
                                Should be in the same unit as the times in lstA and lstB
        mimic_choice (string, optional): It has to be B/A (A mimicking B) or A/B (B mimicking A). Defaults to None. 
    Returns:
        list: A list of tuples [(count, probability),....]
    """
    string=database_pairs
    dA=eval('function1')(folder, string, tierA)
    dB=eval('function2')(folder, string, tierB)
    dA2=keep_info(dA[0], 4)
    dB2=keep_info(dB[0], 4)
    dfA=list_to_df(dA2, dA[1][0:4])
    dfB=list_to_df(dB2, dB[1][0:4])
    LA=[]
    LB=[]
    count_proba=[]
    lst=list(np.unique(list(dfA['subject'])))
    del lst[-1]
    n=1
    for _ in range(int(len(folder)/2)):
        if filter is None:    
            LA=df_to_list(dfA[dfA.subject.eq(n)])
            LB=df_to_list(dfB[dfB.subject.eq(n+1)])
        else:
            if filter=='Intensity':
                if type(label) is list:
                    LA=keep_info_with_lab(df_to_list(dfA[dfA.subject.eq(n)]), label[0], 2)
                    LB=keep_info_with_lab(df_to_list(dfB[dfB.subject.eq(n+1)]), label[1], 2)
                else:
                    LA=keep_info_with_lab(df_to_list(dfA[dfA.subject.eq(n)]), label, 2)
                    LB=keep_info_with_lab(df_to_list(dfB[dfB.subject.eq(n+1)]), label, 2)      
        if len(LA)==0:
            LA.append((0, 0, 0, 0))
        if len(LB)==0:
            LB.append((0, 0, 0, 0))
        if mimic_choice=='A/B':
            count_proba.append(give_mimicry(LA, LB, delta_t))
        elif mimic_choice=='B/A':
            count_proba.append(give_mimicry(LB, LA, delta_t))
        n+=2
    M=[]
    for i in count_proba:
        i+=(string,)
        M.append(i)
    return M

def give_mimicry_folder3(folder, database_pairs, function1, function2, tierA, tierB, tier_filter, entity, filter=None, label=None, delta_t=0):
    """ The function calculate the mimicry between two lists with a filter.
    
    Args:
        folder (list): List of the .eaf files path 
        database_pairs (string): The dataset of the pairs
        function1 (function): It's a function giving the list of tuples (start, stop, label) of expressions mimicked
        function2 (function): It's a function giving the list of tuples (start, stop, label) of expressions mimicking
        tierA (string): The tier of the person A
        tierB (string): The mimicked tier by the person B
        tier_filter : The tier with which we want to filter the data
        entity : The entity of the tier with which we want to filter the data
        filter (string, optional): It has to be 'Intensity'. Defaults to None.
        label (string or list, optional): If it's a string, it represents the intensity we want and if it's a list, 
        it represents the intensities we want to keep. Defaults to None.
        delta_t (int, optional): Defaults to 0.
                                Time after which expression occuring still counts as mimicry.
                                Should be in the same unit as the times in lstA and lstB 
    Returns:
        list: A list of tuples [(count, probability),....]
    """
    string=database_pairs
    dA=eval('function1')(folder, string, tier_filter, tierA, entity)
    dB=eval('function2')(folder, string, tier_filter, tierB, entity)
    dA2=keep_info(dA[0], 4)
    dB2=keep_info(dB[0], 4)
    dfA=list_to_df(dA2, dA[1][0:4])
    dfB=list_to_df(dB2, dB[1][0:4])
    LA=[]
    LB=[]
    count_proba=[]
    lst=list(np.unique(list(dfA['subject'])))
    del lst[-1]
    n=1
    for _ in range(int(len(folder)/2)):
        if filter is None:    
            LA=df_to_list(dfA[dfA.subject.eq(n)])
            LB=df_to_list(dfB[dfB.subject.eq(n+1)])
        else:
            if filter=='Intensity':
                if type(label) is list:
                    LA=keep_info_with_lab(df_to_list(dfA[dfA.subject.eq(n)]), label[0], 2)
                    LB=keep_info_with_lab(df_to_list(dfB[dfB.subject.eq(n+1)]), label[1], 2)
                else:
                    LA=keep_info_with_lab(df_to_list(dfA[dfA.subject.eq(n)]), label, 2)
                    LB=keep_info_with_lab(df_to_list(dfB[dfB.subject.eq(n+1)]), label, 2)
        if len(LA)==0 :
            LA.append((0, 0, 0, 0))
        if len(LB)==0:
            LB.append((0, 0, 0, 0))
        count_proba.append(give_mimicry(LA, LB, delta_t))
        n+=2
    M=[]
    for i in count_proba:
        i+=(string,)
        M.append(i)
    return M

def give_mimicry_folder4(folder, database_pairs, function1, function2, tierA, tierB, tier_filter, entity1, entity2, filter=None, label=None, delta_t=0, mimic_choice=None):
    """ The function calculate the mimicry between two lists with a filter.
    
    Args:
        folder (list): List of the .eaf files path 
        database_pairs (string): The dataset of the pairs
        function1 (function): It's a function giving the list of tuples (start, stop, label) of expressions mimicked
        function2 (function): It's a function giving the list of tuples (start, stop, label) of expressions mimicking
        tierA (string): The tier of the person A
        tierB (string): The mimicked tier by the person B
        tier_filter : The tier with which we want to filter the data
        entity1 : The entity of the tier with which we want to filter the data for the person A
        entity2 : The entity of the tier with which we want to filter the data for the person B
        filter (string, optional): It has to be 'Intensity'. Defaults to None.
        label (string or list, optional): If it's a string, it represents the intensity we want and if it's a list, 
        it represents the intensities we want to keep. Defaults to None.
        delta_t (int, optional): Defaults to 0.
                                Time after which expression occuring still counts as mimicry.
                                Should be in the same unit as the times in lstA and lstB 
        mimic_choice (string, optional): It has to be B/A (A mimicking B) or A/B (B mimicking A). Defaults to None.
    Returns:
        list: A list of tuples [(count, probability),....]
    """
    string=database_pairs
    dA=eval('function1')(folder, string, tier_filter, tierA, entity1)
    dB=eval('function2')(folder, string, tier_filter, tierB, entity2)
    dA2=keep_info(dA[0], 4)
    dB2=keep_info(dB[0], 4)
    dfA=list_to_df(dA2, dA[1][0:4])
    dfB=list_to_df(dB2, dB[1][0:4])
    LA=[]
    LB=[]
    count_proba=[]
    lst=list(np.unique(list(dfA['subject'])))
    del lst[-1]
    n=1
    for _ in range(int(len(folder)/2)):
        if filter is None:    
            LA=df_to_list(dfA[dfA.subject.eq(n)])
            LB=df_to_list(dfB[dfB.subject.eq(n+1)])
        else:
            if filter=='Intensity':
                if type(label) is list:
                    LA=keep_info_with_lab(df_to_list(dfA[dfA.subject.eq(n)]), label[0], 2)
                    LB=keep_info_with_lab(df_to_list(dfB[dfB.subject.eq(n+1)]), label[1], 2)
                else:
                    LA=keep_info_with_lab(df_to_list(dfA[dfA.subject.eq(n)]), label, 2)
                    LB=keep_info_with_lab(df_to_list(dfB[dfB.subject.eq(n+1)]), label, 2)
        if len(LA)==0 :
            LA.append((0, 0, 0, 0))
        if len(LB)==0:
            LB.append((0, 0, 0, 0))
        if mimic_choice=='A/B':
            count_proba.append(give_mimicry(LA, LB, delta_t))
        elif mimic_choice=='B/A':
            count_proba.append(give_mimicry(LB, LA, delta_t))
        n+=2
    M=[]
    for i in count_proba:
        i+=(string,)
        M.append(i)
    return M

#Correlation _________________________________________________________________________________________________________________________
def get_correlation(lA, lB):
    """ This function calculates correlation between two lists.

    Args:
        lA (list): list of numeric elements
        lB (list): list of numeric elements
    Returns:
        numeric: the value is the correlation between the two lists
    """
    # Filter non-numeric elements
    lA=[x for x in lA if isinstance(x, (int, float))]
    lB=[x for x in lB if isinstance(x, (int, float))]
    if len(lA)==0 or len(lB)==0:
        corr=0
    else:
        # Adjust the size of the lists to match
        min_len=min(len(lA), len(lB))
        lA=lA[:min_len]
        lB=lB[:min_len]
        # Calculate correlation using numpy corrcoef
        corr_matrix=np.corrcoef(lA, lB)
        corr=corr_matrix[0, 1]
        # Round the correlation value to 3 decimal places
        corr=round(corr, 3)
    return corr

def get_correlation_folder(tier, folder, width, shift, tier2=None, role=None, which_role=None):
    """ This function calculates the correlation in an interaction. 

    Args:
        tier (string): tier we want to use
        folder (list): list of eaf paths in the dataset chosen
        width (numeric):  window width in ms
        shift (numeric):  window shift in ms
        tier2 (string, optional): second tier we want to use. Defaults to None.
        role (string, optional): To say if we want to dispatch by entity or not. Defaults to False.
        which_role (string, optional): To say if we want to dispatch by an entity. Defaults to None.

    Returns:
        list: List of values corresponding to the correlation of each interaction of the database
    """
    corr_l=[]
    for i in range(0, len(folder), 2):
        L=[folder[i], folder[i+1]]
        if role is not None:
            a=eval('get_tier_from_entity')(L[0], tier, role, which_role)[0]
            b=eval('get_tier_from_entity')(L[1], tier, role, which_role)[0]
        else:
            if tier2 is None:
                a=eval('get_tier_dict')(L[0], tier)
                b=eval('get_tier_dict')(L[1], tier)
            else:
                a=eval('get_tier_dict')(L[0], tier)
                b=eval('get_tier_dict')(L[1], tier2)
        lst=[tuple_to_int_sequence(a, width=width, shift=shift), tuple_to_int_sequence(b, width=width, shift=shift)]
        c=get_correlation(lst[0], lst[1])
        corr_l.append(c)
    return corr_l

def get_correlation_byI(tier1, entity1, folder, width, shift, tier2=None, entity2=None):
    """ This function calculates the correlation in an interaction filtered by entity. 

    Args:
        tier1 (str): tier we want to use
        entity1 (str): It's the entity of tier1 we want to use
        folder (list): list of eaf paths in the dataset chosen
        width (numeric):  window width in ms
        shift (numeric):  window shift in ms
        tier2 (str, optional): It's the second expression. Defaults to None.
        entity2 (str, optional): It's the second intensity. Defaults to None.
    Returns:
        list: List of values corresponding to the correlation of each interaction of the database
    """
    corr_l=[]
    for i in range(0, len(folder), 2):
        L=[folder[i], folder[i+1]]
        a=get_IR_list(L[0], tier1, entity1)  
        if tier2 is None:
            if entity2 is None:
                b=get_IR_list(L[1], tier1, entity1)
            else:
                b=get_IR_list(L[1], tier1, entity2)
        else:
            if entity2 is None:
                b=get_IR_list(L[1], tier2, entity1)
            else:
                b=get_IR_list(L[1], tier2, entity2)
        lst=[tuple_to_int_sequence(a, width=width, shift=shift), tuple_to_int_sequence(b, width=width, shift=shift)]
        c=get_correlation(lst[0], lst[1])
        corr_l.append(c)
    return corr_l

def get_correlation_by_entity(tier1, entity1, folder, width, shift, tier2, entity2=None):
    """ This function calculates the correlation in an interaction filtered by entity.

    Args:
        tier1 (str): tier we want to use of person 1
        entity1 (str): It's the entity of tier1 we want to use
        folder (list): list of eaf paths in the dataset chosen
        width (numeric):  window width in ms
        shift (numeric):  window shift in ms
        tier2 (str): tier we want to use of person 2
        entity2 (str, optional): It's the entity of tier2 we want to use. Defaults to None.
    Returns:
        list: List of values corresponding to the correlation of each interaction of the database
    """
    corr_l=[]
    for i in range(0, len(folder), 2):
        L=[folder[i], folder[i+1]]
        a=get_IR_list(L[0], tier1, entity1)  
        if entity2 is None:
            b=eval('get_tier_dict')(L[1], tier2)
        else:
            b=get_IR_list(L[1], tier2, entity2)
        lst=[tuple_to_int_sequence(a, width=width, shift=shift), tuple_to_int_sequence(b, width=width, shift=shift)]
        c=get_correlation(lst[0], lst[1])
        corr_l.append(c)
    return corr_l
   
#Others_______________________________________________________________________________________________________________________
def get_database_name(folder):
        """ This function give the name of the database corresponding to the folder.
        
        Args:
            folder (list): list of eaf paths
        Returns:
            str: name of the database
        """
        level=0
        for _ in reversed(list(enumerate(folder[0]))):
            if folder[0][_[0]]=='\\':
                level=_[0]
                break
        a=folder[0][:level]
        level=0
        for _ in reversed(list(enumerate(a))):
            if a[_[0]]=='\\':
                level=_[0]
                break
        return a[level+1:]
   
def expression_per_min(folder, expression, case=None):
    """ This function calculates the number of one tier we have per minute.   
    
    Args:
        folder (list) -> list of all files paths
        expression (str) -> tiers_0
        case (int, optional): Express if you want to look into conversations ; for that, you put 2. Defaults to None.
    Returns:
        A list containing the number of expression per minute for each file
    """
    L=[]
    M=[]
    tiers_=[]
    m=60000
    m_multiples=[m, m*2, m*3, m*4, m*5, m*6, m*7]
    threshold_value=20000
    if case is None:
        for j in range(0, len(folder), 1):
            n=0
            nb=0                            #variable which represent the number of smiles by minute
            to_dict=read_eaf_to_dict(folder[j] , mark=True, tiers=None)
            lst=None
            if expression in to_dict:
               lst=to_dict[expression]
            else:
                match=re.search(r'^([a-zA-Z]+)', expression)
                if match:
                    word=match.group(1)
                lst=to_dict[word]
            n=len(lst)  #number of expression in the file
            eaf=pympi.Elan.Eaf(folder[j])
            duration_annotated=check_duration(eaf)
            Default=False
            Pass=False
            #if the duration annotated is near one value of m_multiples, we divide n by the corresponding value (1 or 2 or 3 .... )
            for i in m_multiples:
                if (i-threshold_value < duration_annotated < i+threshold_value):
                    nb=n/(i/m)
                    L.append(nb) 
                    Default=True
                else: 
                    pass
            if Default==False:
                L.append(0)
            for i in range(0, len(lst), 1):
                M.append(lst[i])
            tiers_.append(M)
    else:
        for j in range(0, len(folder), 2):
            n, n2, nb, nb2=0, 0, 0, 0       # nb and nb2 are variables which represent the number of smiles by minute for person 1 and person 2
            to_dict=read_eaf_to_dict(folder[j] , mark=True, tiers=None)
            to_dict2=read_eaf_to_dict(folder[j+1] , mark=True, tiers=None)
            lst=to_dict.get(expression)
            lst2=to_dict2.get(expression)
            if lst is None:
                match=re.search(r'^([a-zA-Z]+)', expression)
                if match:
                    word=match.group(1)
                    lst=to_dict.get(word)
                    lst2=to_dict2.get(word)
            n=len(lst)
            n2=len(lst2)
            eaf1=pympi.Elan.Eaf(folder[j])
            duration_annotated=check_duration(eaf1)
            eaf2=pympi.Elan.Eaf(folder[j+1])
            duration_annotated=check_duration(eaf2)
            Default=False
            #If the duration annotated is near one value of m_multiples, we divide n by the corresponding value (1 or 2 or 3 .... )
            for i in m_multiples:
                if (i-threshold_value < duration_annotated < i+threshold_value):
                    nb=n/(i/m)
                    nb2=n2/(i/m)
                    L.append(nb+nb2) 
                    Default=True
                else:
                    pass
            if Default==False:
                L.append(0)
            for j in range(0, len(lst), 1):
                M.append(lst[j])
            for k in range(0, len(lst2), 1):
                M.append(lst2[k])
            tiers_.append(M)
    return L, tiers_

def expression_per_min_I(folder, expression, intensity):
    """ This function calculates the number of one tier we have per minute for one entity.  
    
    Args:
        folder (list): list of all files paths
        expression (str): tiers
        intensity (str): This is the entity we search for
    Returns:
        list, list : list of tuples ('start', 'end', 'intensity', 'person'), ['start', 'end', 'intensity', 'person']
    """
    m, n, nb=60000, 0, 0
    L=[]
    m_multiples=[m, m*2, m*3, m*4, m*5, m*6, m*7]
    threshold_value=30000
    count=[]
    for root in folder:
        lst=get_IR_list(root, expression, intensity)
        n=len(lst)

        eaf=pympi.Elan.Eaf(root)
        duration_annotated=check_duration(eaf)
        #if the duration annotated is near one value of m_multiples, we divide n by the corresponding value (1 or 2 or 3 .... )
        for i in m_multiples:
            if (i-threshold_value < duration_annotated < i+threshold_value):
                test = True
                nb=n/(i/m)
                count.append(nb)
            else:
                pass
    return count


