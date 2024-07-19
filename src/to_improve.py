from snl_stats_extraction_data import *

#This function has to be improved so the second function can work.
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
    trackp, trackf, track_number, current_level, database=([] for _ in range(5))
    for root in folder:
        n=1
        sl_lst=get_TCdict(root, track, check)
        lst_check=eval('function_to_lst_check')(root, check)
        lst_track=eval('function_to_lst_track')(root, track)
        level_list=[]
        current_level=[]
        for entity in tier_lists[track]:
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

def SL_track_byRI_test(check, track, dir, role, case):
    """ This function is used to track the expression of laughs or smiles by entities in a tier for the database.
    
    Args:
        check (str): laughs or smiles. It's the expression which preced or follow
        track (str): laughs or smiles. It's the expression of which we want to know what is before and after
        dir (str) : path of the folder containing all datasets
        role (str) : entity 
        case (str): tier tracked 
    Returns:
        df_g (pandas dataframe): dataframe containing all the information about the tracking
        df1_g (pandas dataframe): dataframe containing all the information about the tracking
    """
    #Variables
    dg=[]
    n=0
    L=[]
    for path in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, path)):
            n+=1
            data=["ccdb", "ifadv", "ndc"]
            for i in data:
                if path==i:
                    L.append((get_all_filepaths((os.path.join(dir, path)), "eaf", None), path))
    for i in range(len(L)):
        a=fill_trackfp_byIR(L[i][0], L[i][1], eval('get_'+check+'_from_'+role), eval('get_'+track+'_from_'+role), case, True)
        print(len(a[0]), len(a[1]), len(a[2]), len(a[3]), len(a[4]))
        print(a[1])
        print(a[3])
        print(a[4])
        df1=pd.DataFrame({'Database': a[0],'Current_level_'+track[:-1]: a[1], 'N°'+track[:-1]: a[2],
        'Intensityp': a[3],'Intensityf': a[4]})
        dg.append(df1)
    df=pd.concat(dg)
    #Previous smiles
    df_g=df.groupby(['Intensityp', 'Database', 'Current_level_'+track[:-1] ]).size().reset_index()
    df_g.columns=['Intensityp', 'Database', 'Current_level_'+track[:-1], 'Count']
    df_t=df_g.groupby(['Database', 'Current_level_'+track[:-1] ])['Count'].sum().reset_index()
    tot=[]
    for _, j in zip(list(df_g["Database"]), list(df_g['Current_level_'+track[:-1] ])):
        for i, k in zip(list(df_t['Database']), list(df_t['Current_level_'+track[:-1] ])):
            if _==i and j==k:
                tot.append(int(df_t[df_t.Database.eq(_) & df_t['Current_level_'+track[:-1]].eq(j)]['Count']))
    df_g['tot']=tot
    df_g['Percentage']=round(((df_g["Count"]/df_g['tot'])*100), 2)
    df_g.columns=['Intensityp', 'Databasep', 'Current_level_'+track[:-1]+'p', 'Countp', 'tot', 'Percentagep']
    #Following smiles
    df1_g=df.groupby(['Intensityf', 'Database', 'Current_level_'+track[:-1]]).size().reset_index()
    df1_g.columns=['Intensityf', 'Database', 'Current_level_'+track[:-1], 'Count']
    df_t1=df1_g.groupby(['Database', 'Current_level_'+track[:-1]])['Count'].sum().reset_index()
    tot=[]
    for _, j in zip(list(df1_g["Database"]), list(df1_g['Current_level_'+track[:-1] ])):
        for i, k in zip(list(df_t1['Database']), list(df_t1['Current_level_'+track[:-1] ])):
            if _==i and j==k:
                tot.append(int(df_t1[df_t1.Database.eq(_) & df_t1['Current_level_'+track[:-1]].eq(j)]['Count']))
    df1_g['tot']=tot
    df1_g['Percentage']=round(((df1_g["Count"]/df1_g['tot'])*100), 2)
    df1_g.columns=['Intensityf', 'Databasef', 'Current_level_'+track[:-1]+'f', 'Countf', 'tot', 'Percentagef'] 
    return df_g, df1_g

#This function has to be improved so we can get correlation of two lists coming from roles.
def get_correlation_byRI_test(SL1,intensity1, folder, width, shift, SL2=None, intensity2=None, which_role=None):
    """ This function calculates the correlation in an interaction filtered by entity. 

    Args:
        SL1 (str): S for smiles or L for laughs
        intensity1 (str): low, subtle, medium or high
        folder (list): list of eaf paths in the dataset chosen
        width (numeric):  window width in ms
        shift (numeric):  window shift in ms
        SL2 (str, optional): S for smiles or L for laughs. It's the second expression. Defaults to None.
        intensity2 (str, optional): low, subtle, medium or high. Defaults to None.
        which_role (str, optional): "spk" for speaker and "lsn" for listener. Defaults to None.
    Returns:
        list: List of values corresponding to the correlation of each interaction of the database
    """
    corr_l=[]
    for i in range(0, len(folder), 2):
        L=[folder[i], folder[i+1]]
        #a=get_IR_list(L[0], SL1, intensity1) 
        if SL1=='S':
            a=keep_info_with_lab(eval('get_smiles_from_'+which_role)(L[0])[0], intensity1, 2)
            if SL2 is None:
                if intensity2 is None:
                    b=keep_info_with_lab(eval('get_smiles_from_'+which_role)(L[1])[0], intensity1, 2)
                else:
                    b=keep_info_with_lab(eval('get_smiles_from_'+which_role)(L[1])[0], intensity2, 2)
            else:
                if intensity2 is None:
                    b=keep_info_with_lab(eval('get_laughs_from_'+which_role)(L[1])[0], intensity1, 2)
                else:
                    b=keep_info_with_lab(eval('get_laughs_from_'+which_role)(L[1])[0], intensity2, 2)
        if SL1=='L':
            a=keep_info_with_lab(eval('get_laughs_from_'+which_role)(L[0])[0], intensity1, 2)
            if SL2 is None:
                if intensity2 is None:
                    b=keep_info_with_lab(eval('get_laughs_from_'+which_role)(L[1])[0], intensity1, 2)
                else:
                    b=keep_info_with_lab(eval('get_laughs_from_'+which_role)(L[1])[0], intensity2, 2)
            else:
                if intensity2 is None:
                    b=keep_info_with_lab(eval('get_smiles_from_'+which_role)(L[1])[0], intensity1, 2)
                else:
                    b=keep_info_with_lab(eval('get_smiles_from_'+which_role)(L[1])[0], intensity2, 2)                    
        a=keep_info(a, 3)
        b=keep_info(b, 3)
        print(a, "    |    ", b)
        lst=[tuple_to_int_sequence(a, width=width, shift=shift), tuple_to_int_sequence(b, width=width, shift=shift)]
        c=get_correlation(lst[0], lst[1])
        corr_l.append(c)
    return corr_l

