'''
Created on 2 окт. 2022 г.

@author: Alex
'''

import numpy as np
import pandas as pd
import pickle
from sklearn import metrics
from sklearn import preprocessing



info_columns = ['ФИО', 'Дата рождения', 'Пол', 'Номер', 'Объект' ]

model_requirements = ['Глицин', 'Аспаргиновая кислота', 'Лизин', 'АДМА', 'АДМА/Аргинин', 'Холин (свободный)', 'Карнитин (С0)',
         'Acetylcarnitine (С2)', 'Propionylcarnitine (С3)',
         'Tiglylcarnitine (C5:1)', 'Isovalerylcarnitine (iC5)', 'Hydroxyisovalerylcarnitine (iC5-OH)',
         'Octenoylcarnitine (C8)', 'Octanoylcarnitine (C8)', 'Adipoylcarnitine (С6DC)',
         'Dodecanoylcarnitine (С12)', 'Tetradecadienoylcarnitine (C14:2)', 'Hydroxytetradecanoylcarnitine (C14:2-OH)',
         'Hexadecenoylcarnitine (C16:1)', 'Palmitoylcarnitine (C16)',
         'Hydroxyhexadecenoylcarnitine (C16:1-OH)', 'Linoleylcarnitine (C18:2)', 'Stearoylcarnitine (C18)',
         '5-Hydroxytryptophan', 'Tryptophan', 'Kynurenine/Tryptophan',
         'Quinolinic acid', 'HIAA', 'Antranillic acid', 'Xanturenic acid', 'Indole-3-lactate', 'Indole-3-acrylate',
         'Kynurenic acid']

model_requirements2 = ['Пролин',
 'Лейцин',
 'Изолейцин',
 'Орнитин',
 'Фенилаланин',
 'Метионин',
 'СДМА',
 'Карнитин (С0)',
 'Glutarylcarnitine (С5DC)',
 'Octenoylcarnitine (C8)',
 'Adipoylcarnitine (С6DC)',
 'Dodecenoylcarnitine (C12:1)',
 'Dodecanoylcarnitine (С12)',
 'Kynurenine',
 'Tryptophan',
 'Kynurenine/Tryptophan',
 'Serotonin',
 'HIAA',
 'Indole-3-carboxaldehyde',
 'Indole-3-acrylate',
 'Indole-3-propionate',
 'Kynurenic acid']

groups = {'Аминокислоты' : r'aminoacids_range.xlsx',
          'Ацилкарнитины' : r'acillcarnitine_range.xlsx',
          'Триптофаны' : r'triptofanes_range.xlsx',
          'Свободный холин и СДМА' : r'holin_range.xlsx'}

groups_content = {'Аминокислоты' : [],
          'Ацилкарнитины' : [],
          'Триптофаны' : [],
          'Свободный холин и СДМА' : []}


def extract_info(df):
    info_df = df[info_columns].copy()
    return info_df


def add_range(df, group_name):
    ranges_fname = groups[group_name]
    range_df = pd.read_excel(ranges_fname, index_col = 'Метаболит')
    range_df.index = range_df.index.str.strip()
    
    existing = [x for x in range_df.index if (x in df.index)]
    
    groups_content[group_name] = existing
    
    df['Нижняя граница'][existing] = range_df['Нижняя граница']
    df['Верхняя граница'][existing] = range_df['Верхняя граница']
    
    return df


def add_all_ranges(df):
    df['Нижняя граница'] = np.nan
    df['Верхняя граница'] = np.nan
    
    for grp in groups:
        df = add_range(df, grp)
    
    return df



def make_result_column(x):
    if x[0] < x[2] < x[1]:
        return 'Норма'
    if x[2] / 5 < x[1] < x[2]:
        return 'Риск повышения'
    if x[2] * 5 > x[0] > x[2]:
        return 'Риск понижения'
    if x[2] / 5 > x[1]:
        return 'Повышено'
    else:
        return 'Понижено'


def add_analyse(df):
    existed_cols = df.columns.to_list()
    df['Вывод'] = df[['Нижняя граница', 'Верхняя граница','Результат']].apply(make_result_column, axis=1)
    
    rel_up = df['Результат'] / df['Верхняя граница']
    df['Риск повышения'] = rel_up.loc[rel_up.between(1, 5)]
    df['Повышено'] = rel_up.loc[rel_up.between(5, np.inf)]
    df['Норма'] = rel_up.loc[rel_up.between(0, 1)]
    rel_down = df['Нижняя граница'] / df['Результат']
    df['Риск понижения'] = rel_down.loc[rel_down.between(1, 5)]
    df['Понижено'] = rel_down.loc[rel_down.between(5, np.inf)]
    
    new_cols = ['Вывод', 'Понижено', 'Риск понижения', 'Норма', 'Риск повышения', 'Повышено']  
    
    df = df[existed_cols + new_cols]
    
    return df


def prepare_data(raw_dataframe):
    df = raw_dataframe
    
    info = extract_info(df)
    
    # prepare df for the next stage
    df = df.drop(info_columns, axis = 1)
    df = df.T
    df.columns = ['Результат']
    df.index = df.index.str.strip()
    
    df = add_all_ranges(df)
    
    df = add_analyse(df)
    
    return info, df, groups_content

def desease_prediction_cvd(profile):
    res_cvd = dict()
    cvd_proba = 78
    res_cvd['ССЗ'] = cvd_proba
    return res_cvd

def desease_prediction(profile):
    """
    profile - 2nd result of prepare_data() function
    """
    # loaded_model = pickle.load(open('RF_model_1711.pkl', 'rb'))
    # scaler_sv1 = pickle.load(open('first_scaler1911.pkl', 'rb')) 

    # data1 = pd.DataFrame(profile['Результат'].T[model_requirements]).T
    
    # data1 = scaler_sv1.transform(data1)
    # data1= preprocessing.normalize(data1, norm='l2')
    # a = loaded_model.predict_proba(data1)
    # heart_des_proba = float(a[:,1])*100
    heart_des_proba=78

    res = dict()
    # res['ССЗ'] = heart_des_proba
    
    if heart_des_proba >= 70:
        # loaded_model2 = pickle.load(open('RF_second_model_1911.pkl', 'rb'))
        # scaler_sv2 = pickle.load(open('scaler1911.pkl', 'rb'))
        
        # data2 =  pd.DataFrame(profile['Результат'].T[model_requirements2]).T
        # data2 = scaler_sv2.transform(data2)
        # data2 = preprocessing.normalize(data2, norm='l2')
        # c = loaded_model2.predict_proba(data2)
        # GB_proba = float(c[:,1])*100
        # IBS_proba = float(c[:,0])*100
        GB_proba=68
        IBS_proba=22
        HSN_proba=10
        if GB_proba > 60:
            res['ГБ'] = GB_proba
            res['ИБС']  = IBS_proba
            res['ХСН'] = HSN_proba
        else:
            res['ИБС'] = IBS_proba
            res['ГБ'] = GB_proba
            res['ХСН'] = HSN_proba

    return res
    

def desease_prediction_lc(profile):
    """
    profile - 2nd result of prepare_data() function
    """
    # loaded_model = pickle.load(open('RF_model_1711.pkl', 'rb'))
    # scaler_sv1 = pickle.load(open('first_scaler1911.pkl', 'rb')) 

    # data1 = pd.DataFrame(profile['Результат'].T[model_requirements]).T
    
    # data1 = scaler_sv1.transform(data1)
    # data1= preprocessing.normalize(data1, norm='l2')
    # a = loaded_model.predict_proba(data1)
    # heart_des_proba = float(a[:,1])*100
    lc_des_proba=6
    kc_des_proba=5
    crc_des_proba=2
    pc_des_proba=0

    res_cancer = dict()
    
    
    res_cancer['Рак легкого'] = lc_des_proba
    res_cancer['Рак почки'] = kc_des_proba
    res_cancer['Колоректальный\nрак'] = crc_des_proba
    res_cancer['Рак простаты'] = pc_des_proba
    return res_cancer





if __name__ == '__main__':
    test_fname = r'TEST_test.xlsx'    
    df = pd.read_excel(test_fname)
    
    info, profile, groups_content = prepare_data(df)
    print(groups_content)
    print(info)
    
    pd.set_option('display.max_columns', None)
    print(profile.head(10))
    
    desease_cvd = desease_prediction_cvd(profile)
    print(desease_cvd)
    
    categories = deseases.keys()
    proba = deseases.values()
    print(list(categories), list(proba))
    
    deseases = desease_prediction(profile)
    print(deseases)
    
    categories = deseases.keys()
    proba = deseases.values()
    print(list(categories), list(proba))
    
    deseases_lc = desease_prediction_lc(profile)
    print(deseases_lc)
    
    categories_lc = deseases_lc.keys()
    proba_lc = deseases_lc.values()

    print(list(categories_lc), list(proba_lc))

    
    print('done')