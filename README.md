<h1 align="left">Aerosol service</h1>

###

<h2 align="left">О проекте</h2>

###

<p align="left">Данный проект был создан для предсказания показателя преломления аэрозолей, используя методы машинного обучения.<br><br>Перед непосредсвенно обучением было проанализированно и обработанно свыше 100 тысяч записей, взятых с https://aeronet.gsfc.nasa.gov/<br>Данные распространялись бесплатно и были использованы в обучающих целях, так как участники проекта являются студентами и работа выполнялась для получения практики.<br><br>Итогой моделью обучения стала CatBoostRegressor<br>CatBosst опередил всех своих конкурентов, которые использовались для тестов.<br>Данная модель на обучающей выборке показала R2 = 0.8813<br><br>R2 - коэфициент детерминации, то есть доля дисперсии зависимой переменной, объясняемая рассматриваемой моделью зависимости, то есть объясняющими переменными. Более точно — это единица минус доля необъяснённой дисперсии (дисперсии случайной ошибки модели, или условной по факторам дисперсии зависимой переменной) в дисперсии зависимой переменной.<br>Если очень грубо, то чем ближе R2 к 1, тем лучше модель</p>

###

<h2 align="left">Как пользоваться тем, что есть сейчас</h2>

###

<p align="left">Файл api.py является апишкой, написанной на Flask, содержит POST-запрос, который получает данные от пользователя, обрабатывает их и отправляет ответ.<br><br>Файл test.py содержит тестовый запрос к API.<br><br>requirements.txt содержит используемые в проекте библиотеки<br><br>Чтобы всё заработало нужно сделать следующее:<br><br>1.  Открыть проетк в среде программирвоания и подкачать библиотеки при помощи<br> pip install -r requirements.txt<br><br>2. Запустить api.py<br><br>3. Дальше нужно создать новый терминал и запустить файл test.py через него. <br>Пример: python C:\aerosol_service\test.py<br><br>Готово, смотрим результат.<br><br>На данном этапе разработки данные вносятся в файле test.py, но в скоре будет это будет внедрено в Telegram-бота.<br><br>Рекомендованные диапазоны значений <br>:AOD_Extinction-Total[870nm] - (0.02736  /  3.1059)<br>    :AOD_Extinction-Total[440nm] - (0.10944  /  4.3218)<br>    :AOD_Extinction-Total[675nm] - (0.04654  /  3.3907)<br>    :AOD_Extinction-Total[1020nm] - (0.01898  /  3.0162)<br>    :Extinction_Angstrom_Exponent_440-870nm-Total - (-0.058907  /  2.36181)<br>    :Lidar_Ratio[870nm] - (7.3482  /  190.0)<br>    :Depolarization_Ratio[870nm] - (0.007074  /  0.35326)<br>    :Latitude(Degrees) - (-51.600503  /  80.053611)<br>    :Longitude(Degrees) - (-177.378333  /  153.013611)</p>

###
