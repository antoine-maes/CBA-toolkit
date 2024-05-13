import subprocess
import streamlit as st
import os, sys
import Affichage_pattern

Affichage_pattern.affichage()
script_path=os.path.realpath(os.path.dirname("src"))
os.chdir(script_path)
sys.path.append("..")

from src.page3.snl_stats_visualization_page3 import *
from src.page3.snl_stats_visualization_page3_express import *
from src.page3.snl_stats_visualization_database import *
DIR, databases_pair_paths, databases_paths, tier_lists, databases, databases_pairs, tiers=get_parameters()
real_tier_lists , real_tiers = get_parameters_tag()

def page1():
    st.sidebar.markdown("Descriptive analysis")
    st.title('Descriptive analysis of the database')

    def page1_1() :
        st.sidebar.markdown("Database Information")
        st.header('Database Information')
        name_databases=[key.replace('_paths','').upper() for key in databases.keys()]
        databases_=[value for value in databases_pair_paths.values()]
        databases_choice=st.selectbox("Dataset choice: ", name_databases)

        lst_tiers_choice = []
        for tier in real_tier_lists.keys() :
            if real_tier_lists[tier]['Intensities'] != None or real_tier_lists[tier]['Replace_Value'] != "" :
                lst_tiers_choice.append(tier)
        name_tiers=lst_tiers_choice+["GENERAL"]
        tiers_choice=st.selectbox("Expression choice:", name_tiers, index=name_tiers.index("GENERAL"))

        for i in range(len(name_databases)):
            if databases_choice==name_databases[i]:
                database=databases_choice
                databases_choice=databases_[i]
        if tiers_choice=='GENERAL':
            data=display_general_informations_files(databases_choice)
            columns_names=["Filename", "Duration"]+list(real_tier_lists.keys())
            df=pd.DataFrame(data, columns=columns_names)
            if df is not None:
                st.table(df)
                # Export CSV
                csv = df.to_csv(index=False)
                st.download_button(label='Download CSV', data=csv, file_name=f'{database}_information.csv', mime='text/csv')
            else:
                st.write("No data available")
        else:
            if real_tier_lists[tiers_choice]['Replace_Value'] != "":
                data=display_specific_informations(databases_choice, tiers_choice, [real_tier_lists[tiers_choice]['Replace_Value'], str("No_" + real_tier_lists[tiers_choice]['Replace_Value'])], 'Replace_Value')
                columns_names=["Filename", "Min duration", "Max duration"]+[real_tier_lists[tiers_choice]['Replace_Value'], str("No_" + real_tier_lists[tiers_choice]['Replace_Value'])]
                df1=pd.DataFrame(data, columns=columns_names)
                if df1 is not None:
                    st.write(df1)
                    # Export CSV
                    csv = df1.to_csv(index=False)
                    st.download_button(label='Download CSV', data=csv, file_name=f'{database}_information_{tiers_choice.lower()}.csv', mime='text/csv')
                else:
                    st.write("No data available")
            else:
                data=display_specific_informations(databases_choice, tiers_choice, real_tier_lists[tiers_choice]['Intensities'], 'Intensities')
                columns_names=["Filename", "Min duration", "Max duration"]+real_tier_lists[tiers_choice]['Intensities']
                df2=pd.DataFrame(data, columns=columns_names)
                if df2 is not None:
                    st.write(df2)
                    # Export CSV
                    csv = df2.to_csv(index=False)
                    st.download_button(label='Download CSV', data=csv, file_name=f'{database}_information_{tiers_choice.lower()}.csv', mime='text/csv')
                else:
                    st.write("No data available")
    def page1_2():
        st.sidebar.markdown("Expression Per Minute")
        # # #Barplots ______________________________________________________
        st.header('Expression Per Minute')
        st.markdown('''We count the number of expressions/tiers we have in one minute in each dataset.''')
        st.write("<style>body { font-size: 18px; }</style><i>Reminder : </i>", unsafe_allow_html=True)
        st.write("<style>body { font-size: 14px; }</style><i>- Intra (per file/individual) : we count the number of expressions/tiers we have in one minute in each file/individual.</i>", unsafe_allow_html=True)
        st.write("<style>body { font-size: 14px; }</style><i>- Inter (per interaction) : we count the number of expressions/tiers we have in one minute in each interaction.</i>", unsafe_allow_html=True)
        st.markdown(''' ''')
        name_databases=[key.replace('_paths','').upper() for key in databases.keys()]
        databases_=[value for value in databases_pair_paths.values()]
        databases_choice=st.selectbox("Dataset choice: ", name_databases)
        for i in range(len(name_databases)):
            if databases_choice==name_databases[i]:
                database=databases_choice
                databases_choice=databases_[i]
        if st.checkbox("All entities"):
            lst_tiers_choice = []
            for tier in real_tier_lists.keys() :
                if real_tier_lists[tier]['Intensities'] != None or real_tier_lists[tier]['Replace_Value'] != "" :
                    lst_tiers_choice.append(tier)
            expression_choice=st.radio("Expression to see: ", lst_tiers_choice, key="E1")
            st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
            expression_choice=expression_choice
            choices_case=["Intra","Inter"]
            case_choice=st.radio("Choice: ", choices_case)
            case_list=[None, 2]
            st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
            for _ in range(len(case_list)):
                if case_choice==choices_case[_]:
                    case=case_choice
                    case_choice=case_list[_]
            if (plot_expression_per_min(databases_choice, expression_choice, case_choice)==None):
                st.write("No data available")
            else:
                fig, df3 = plot_expression_per_min(databases_choice, expression_choice, case_choice)
                st.plotly_chart(fig)
                if df3 is not None:
                    # Export CSV
                    csv = df3.to_csv(index=False)
                    st.download_button(label='Download CSV', data=csv, file_name=f'{database}_{expression_choice.lower()}_per_min_{case.lower()}.csv', mime='text/csv')
        if st.checkbox("By entity"):
            lst_tiers_choice = []
            for tier in real_tier_lists.keys() :
                if real_tier_lists[tier]['Intensities'] != None or real_tier_lists[tier]['Replace_Value'] != "" :
                    lst_tiers_choice.append(tier)
            expression_choice=st.radio("Expression to see: ", lst_tiers_choice, key="E2")
            st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
            if real_tier_lists[expression_choice]['Replace_Value'] != "" :
                 entity_choice=st.radio("Entity of the chosen expression: ", [real_tier_lists[expression_choice]['Replace_Value'], str("No_" + real_tier_lists[expression_choice]['Replace_Value'])])
            else :
                entity_choice = st.radio("Entity of the chosen expression: ", real_tier_lists[expression_choice]['Intensities'])
            if entity_choice is not None:
                if (plot_expression_per_min_I(databases_choice, expression_choice, entity_choice)==None) :
                    st.write("No data available")
                else:
                    fig, df4 = plot_expression_per_min_I(databases_choice, expression_choice, entity_choice)
                    st.write(fig)
                    if df4 is not None:
                        # Export CSV
                        csv = df4.to_csv(index=False)
                        st.download_button(label='Download CSV', data=csv, file_name=f'{database}_{entity_choice.lower()}_{expression_choice.lower()}_per_min.csv', mime='text/csv')
            else:
                st.write("No data available")
    def page1_3():
        st.header('Basic statistics on non verbal expressions')
        st.markdown('''We look at the maximum, minimum, mean, median and standard deviation on the database.''')
        st.markdown(''' ''')
        st.markdown('''Explanation of the statistics:''')
        st.write("<style>body { font-size: 14px; }</style><i>Absolute duration -> It means the sum of all difference of time over the entire video.</i>", unsafe_allow_html=True)
        st.write("<style>body { font-size: 14px; }</style><i>Relative duration -> It represents the percentage of the absolute duration compared to the total duration of the video.</i>", unsafe_allow_html=True)
        st.markdown(''' ''')
        st.markdown(''' ''')
        st.subheader('Statistics by dataset')
        name_list=["Absolute duration", "Relative duration"]
        lst_tiers_choice = []
        for tier in real_tier_lists.keys() :
            if real_tier_lists[tier]['Intensities'] != None or real_tier_lists[tier]['Replace_Value'] != "" :
                lst_tiers_choice.append(tier)
        expression_choices=lst_tiers_choice
        expression_choices.append('all')
        expression_choice=st.radio("Expression choice:", expression_choices)
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
        name_databases=[key.replace('_paths','').upper() for key in databases.keys()]
        figs=st.selectbox("Figures: ", name_list) 
        choice_list=["Standard deviation", "Mean", "Median", "Max", "Min", "All"]
        choice=st.radio("Which feature do you want see?  ", choice_list)
        if expression_choice!='all':
            if real_tier_lists[expression_choice]:
                if figs=='Absolute duration':
                    fig1_0, df1_0=plot_absolute_duration(expression_choice, choice, name_databases)
                    if fig1_0!=None:    
                        st.write(fig1_0)
                        # Export CSV
                        if not df1_0.empty:
                            csv = df1_0.to_csv(index=False)
                            st.download_button(label='Download CSV', data=csv, file_name=f'{expression_choice.lower()}_{choice.lower()}_abs.csv', mime='text/csv')
                    else:
                        st.write(f"No Data available for {expression_choice}")
                else:
                    fig2_0, df2_0=plot_relative_duration(expression_choice, choice, name_databases)
                    if fig2_0!=None:
                        st.write(fig2_0)
                        # Export CSV
                        if not df2_0.empty:
                            csv = df2_0.to_csv(index=False)
                            st.download_button(label='Download CSV', data=csv, file_name=f'{expression_choice.lower()}_{choice.lower()}_rel.csv', mime='text/csv')
                    else:
                        st.write(f"No Data available for {expression_choice}")
            else:
                st.write(f"No Data available for {expression_choice}")
        elif expression_choice=='all': 
            figures1=[]
            if figs=='Absolute duration':
                fig1_1=plot_absolute_duration(expression_choice, choice, name_databases)
                figures1.extend(fig1_1)
            else: 
                fig2_1=plot_relative_duration(expression_choice, choice, name_databases)
                figures1.extend(fig2_1)
            for fig in figures1:
                if fig!=None:
                    st.write(fig)
                else:
                    st.write("No Data available")
        st.markdown(''' ''')
        st.markdown('''-----------------------------------------------------------------------------------------------------------------''')
        st.markdown(''' ''')
        st.subheader('Statistics divided by expressions:')  
        expression_choices_1=expression_choices.copy()
        expression_choices_1.remove('all')
        expression_choice_1=st.radio("Divided by expression: ", expression_choices_1)
        if real_tier_lists[expression_choice_1]['Replace_Value'] != "" :
            expression_values = [real_tier_lists[expression_choice_1]['Replace_Value'], str("No_"+real_tier_lists[expression_choice_1]['Replace_Value'])]
        else :
            expression_values=real_tier_lists[expression_choice_1]['Intensities']
        if expression_values:
            name_list_by_expression_kind1=[f"Absolute duration from {expression_choice_1.lower()}"]
            name_list_by_expression_kind2=[f"Relative duration from {expression_choice_1.lower()}"]
            name_list_by_expression=name_list_by_expression_kind1+name_list_by_expression_kind2
            expression_choices_copy=expression_choices.copy()
            expression_choices_copy.remove(expression_choice_1) 
            expression_choice_copy=st.radio("Expression to analyse: ", expression_choices_copy)
            st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
            count=0
            figs1=st.selectbox("Figures: ", name_list_by_expression) 
            choice_list1=["Standard deviation", "Mean", "Median", "Max", "Min", "All"]
            choice1=st.radio("Which feature do you want see?  ", choice_list1, key = count)
            if expression_choice_copy!='all':
                if real_tier_lists[expression_choice_copy]:
                    if "Absolute" in figs1:
                        count+=1
                        for entity in expression_values:
                            try :
                                fig1_temp, df1_temp=plot_absolute_duration_from_tier(expression_choice_1, entity, expression_choice_copy, choice1, name_databases)
                                if fig1_temp!=None:
                                    st.write(fig1_temp)   
                                    # Export CSV
                                    if not df1_temp.empty:
                                        csv = df1_temp.to_csv(index=False)
                                        st.download_button(label='Download CSV', data=csv, file_name=f'{expression_choice_copy.lower()}_vs_{entity}_{expression_choice_1.lower()}_{choice1.lower()}_abs.csv', mime='text/csv') 
                                else:
                                    st.write(f"No data available for: {entity} {expression_choice_1}")
                            except :
                                st.write(f"No data available for: {entity} {expression_choice_1}")
                    elif "Relative" in figs1:
                        count+=1
                        for entity in expression_values:
                            fig1_temp, df1_temp=plot_relative_duration_from_tier(expression_choice_1, entity, expression_choice_copy, choice1, name_databases)
                            if fig1_temp!=None:
                                st.write(fig1_temp)
                                # Export CSV
                                if not df1_temp.empty:
                                    csv = df1_temp.to_csv(index=False)
                                    st.download_button(label='Download CSV', data=csv, file_name=f'{expression_choice_copy.lower()}_vs_{entity}{expression_choice_1.lower()}_{choice1.lower()}_rel.csv', mime='text/csv')
                            else: 
                                st.write(f"No data available for: {entity} {expression_choice_1}")
                else:
                    st.write(f"No data available for {expression_choice_copy} with {expression_choice_1}")
            elif expression_choice_copy=='all': 
                figures=[]
                if "Absolute" in figs1:
                    count+=1
                    for entity in expression_values:
                        fig1_temp=plot_absolute_duration_from_tier(expression_choice_1, entity, expression_choice_copy, choice1, name_databases)
                        figures.extend(fig1_temp)
                elif "Relative" in figs1:
                    count+=1
                    for entity in expression_values:
                        fig1_temp=plot_relative_duration_from_tier(expression_choice_1, entity, expression_choice_copy, choice1, name_databases)
                        figures.extend(fig1_temp)
                for fig_R in figures: 
                    if fig_R!=None:
                        st.write(fig_R)
                    else:
                        st.write("No Data available")
        else:
            st.write(f"No data available for {expression_choice_1}")
    
    page1_names_to_funcs={
    "Database Information": page1_1,
    "Expression Per Minute": page1_2,
    "Stats On Non Verbal Expressions": page1_3,}

    selected_page=st.sidebar.selectbox("Select a page", page1_names_to_funcs.keys())
    page1_names_to_funcs[selected_page]()

if os.path.isfile('base_data.json') and os.path.getsize('base_data.json') > 26:
    subprocess.run(["python", "../src/snl_stats_extraction_data.py"])
    page1()
else :
    st.error("You didn't choose tiers to analyze. Go on Modify Tiers")