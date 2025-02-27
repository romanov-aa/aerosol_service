from flask import Flask, request, jsonify
import pandas as pd
import pickle
from scipy import stats
from scipy.special import inv_boxcox
import numpy as np
import psycopg2


def preprocessing_2(aod_870, aod440, aod675, aod1020, angstrom, lidar, depolar, latitude, longtitude):
  '''
  Функция сама предобрабатывает данные на основании коэфициентов,
  которые были мной получены при длительном анализе и проектировании моделей
  '''
  data = pd.DataFrame({'AOD_Extinction-Total[870nm]': [aod_870], 'AOD_Extinction-Total[440nm]': [aod440],
                       'AOD_Extinction-Total[675nm]' : [aod675], 'AOD_Extinction-Total[1020nm]' : [aod1020],
                       'Extinction_Angstrom_Exponent_440-870nm-Total' : [angstrom], 'Lidar_Ratio[870nm]' : [lidar],
                       'Depolarization_Ratio[870nm]' : [depolar], 'Latitude(Degrees)' : [latitude],
                       'Longitude(Degrees)' : [longtitude]})

  data['AOD_Extinction-Total[1020nm]'] = data['AOD_Extinction-Total[1020nm]'] / data['AOD_Extinction-Total[870nm]']
  data['AOD_Extinction-Total[440nm]'] = data['AOD_Extinction-Total[440nm]'] / data['AOD_Extinction-Total[870nm]']
  data['AOD_Extinction-Total[675nm]'] = data['AOD_Extinction-Total[675nm]'] / data['AOD_Extinction-Total[870nm]']
  data['AOD_Extinction-Total[870nm]'] = data['AOD_Extinction-Total[870nm]'] / data['AOD_Extinction-Total[870nm]']

  data['Latitude(Degrees)'] = data['Latitude(Degrees)'] / 90
  data['Longitude(Degrees)'] = data['Longitude(Degrees)'] / 180

  data.drop(columns=['AOD_Extinction-Total[870nm]'], inplace=True)

  parametr_boxcox = {'c_440': 0.6393241472032326,
                      'c_675': 1.1077175169476254,
                      'c_1020': -0.6086171804191233,
                      'c_exponent': 0.9667249405841073,
                      'c_lidar': -0.1474147956405095,
                      'c_depolar': -0.052488544793626996}

  data['AOD_Extinction-Total[440nm]'] = stats.boxcox(data['AOD_Extinction-Total[440nm]'], parametr_boxcox['c_440'])
  data['AOD_Extinction-Total[675nm]'] = stats.boxcox(data['AOD_Extinction-Total[675nm]'], parametr_boxcox['c_675'])
  data['AOD_Extinction-Total[1020nm]'] = stats.boxcox(data['AOD_Extinction-Total[1020nm]'], parametr_boxcox['c_1020'])
  data['Extinction_Angstrom_Exponent_440-870nm-Total'] = stats.boxcox(data['Extinction_Angstrom_Exponent_440-870nm-Total'],
                                                                      parametr_boxcox['c_exponent'])
  data['Lidar_Ratio[870nm]'] = stats.boxcox(data['Lidar_Ratio[870nm]'], parametr_boxcox['c_lidar'])
  data['Depolarization_Ratio[870nm]'] = stats.boxcox(data['Depolarization_Ratio[870nm]'], parametr_boxcox['c_depolar'])

  parametr_mean = {'c_440': 1.046746,
                      'c_675': 0.367553,
                      'c_1020': -0.194181,
                      'c_exponent': 0.097864,
                      'c_lidar': 2.903731,
                      'c_depolar': -3.348684,
                      'c_latitude' : 0.282108,
                      'c_longitude' : 0.204887
                   }

  parametr_std = {'c_440': 	0.620652,
                      'c_675': 0.227411,
                      'c_1020': 0.122237,
                      'c_exponent': 0.573719,
                      'c_lidar': 0.137506,
                      'c_depolar': 1.577932,
                      'c_latitude' : 0.189048,
                      'c_longitude' : 0.370660
                   }

  # df_model_scaler = (df_model_1 - mean) / std
  data['AOD_Extinction-Total[440nm]'] = (data['AOD_Extinction-Total[440nm]'] - parametr_mean['c_440']) / parametr_std['c_440']
  data['AOD_Extinction-Total[675nm]'] = (data['AOD_Extinction-Total[675nm]'] - parametr_mean['c_675']) / parametr_std['c_675']
  data['AOD_Extinction-Total[1020nm]'] = (data['AOD_Extinction-Total[1020nm]'] - parametr_mean['c_1020']) / parametr_std['c_1020']
  data['Extinction_Angstrom_Exponent_440-870nm-Total'] = (data['Extinction_Angstrom_Exponent_440-870nm-Total'] -
                                                          parametr_mean['c_exponent']) / parametr_std['c_exponent']
  data['Lidar_Ratio[870nm]'] = (data['Lidar_Ratio[870nm]'] - parametr_mean['c_lidar']) / parametr_std['c_lidar']
  data['Depolarization_Ratio[870nm]'] = (data['Depolarization_Ratio[870nm]'] - parametr_mean['c_depolar']) / parametr_std['c_depolar']
  data['Latitude(Degrees)'] = (data['Latitude(Degrees)'] - parametr_mean['c_latitude']) / parametr_std['c_latitude']
  data['Longitude(Degrees)'] = (data['Longitude(Degrees)'] - parametr_mean['c_longitude']) / parametr_std['c_longitude']

  return data


def predict_reff_carboost_2(aod_870, aod440, aod675, aod1020, angstrom, lidar, depolar, latitude, longtitude):
  '''
  Фунция предсказывает эффективный радиус
  Модель представляет из себя CatBoostRegressor
  ----------------
  Для предсказания нужно внести в функцию следующие данные:
    :AOD_Extinction-Total[870nm] (0.02736  /  3.1059)
    :AOD_Extinction-Total[440nm] (0.10944  /  4.3218)
    :AOD_Extinction-Total[675nm] (0.04654  /  3.3907)
    :AOD_Extinction-Total[1020nm] (0.01898  /  3.0162)
    :Extinction_Angstrom_Exponent_440-870nm-Total (-0.058907  /  2.36181)
    :Lidar_Ratio[870nm] (7.3482  /  190.0)
    :Depolarization_Ratio[870nm] (0.007074  /  0.35326)
    :Latitude(Degrees) (-51.600503  /  80.053611)
    :Longitude(Degrees) (-177.378333  /  153.013611)
    -----------------
    В скобках указан диапазон значений, с которыми модель работает правильно
    -----------------
    На обучающей выборке модель показала R2 = 0.8813
     
  '''
  data = preprocessing_2(aod_870, aod440, aod675, aod1020, angstrom, lidar, depolar, latitude, longtitude)
  pred = model_catboost_all.predict(data)

  predictions = pred * 0.752990 + -1.297311
  result = inv_boxcox(predictions, -0.5221520921344286)
  return result

conn =psycopg2.connect(dbname='aerosol_service', user='user',
                        password='user', host='127.0.0.1',
                        port='5432')
cursor = conn.cursor()

app = Flask(__name__)

# Загрузка модели
with open('model_cat_boost_all.pkl', 'rb') as file:
    model_catboost_all = pickle.load(file)

@app.route('/predict', methods=['POST'])
def predict():
    # Получение данных из запроса
    data = request.get_json()

    # Извлечение переменных
    aod_870 = data['aot']['870nm']
    aod440 = data['aot']['440nm']
    aod675 = data['aot']['675nm']
    aod1020 = data['aot']['1020nm']
    angstrom = data['ang']
    lidar = data['lr']
    depolar = data['dpr']
    latitude = data['coord']['lat']
    longtitude = data['coord']['lon']

    # Вызов вашей функции с переменными
    result = predict_reff_carboost_2(aod_870, aod440, aod675, aod1020, angstrom, lidar, depolar, latitude, longtitude)

    if isinstance(result, np.ndarray):
        result = result.tolist()  # Преобразование в список
    
    query = f"""
    INSERT INTO statistic VALUES(Default, {aod_870}, {aod440}, {aod675}, {aod1020}, {angstrom}, 
    {lidar}, {depolar}, {latitude}, {longtitude});

"""
    cursor.execute(query)
    conn.commit()

    # Возврат результата в формате JSON
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)




