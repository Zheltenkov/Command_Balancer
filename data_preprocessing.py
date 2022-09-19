import pandas as pd
import numpy as np
import collections
from datetime import date
from datetime import datetime
from config.config import parse_args
from dateutil.relativedelta import relativedelta


pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 1000)

def calculate_age(born:str)-> int:
    """
    Get age of emploeyr in dataset.
    :param born: string of date in iso format
    :return: integer value of age
    """
    born, today = datetime.fromisoformat(str(born)).date(), date.today()
    return int(today.year - born.year - ((today.month, today.day) < (born.month, born.day)))


def get_employee_data(file_path_employees: str):
    """

    :param file_path:
    :return:
    """
    data = pd.read_excel(file_path_employees)
    #Get unique list of employees
    workers = list(data['Таб.№'].unique())
    last_updates = [data[data['Таб.№'] == worker].sort_values(by=['Дата конца периода'],
                    ascending=False).drop_duplicates(subset=['Таб.№'], keep='first') for worker in workers]

    # Get intermidiate dataset
    df = pd.concat(last_updates).reset_index(drop=True)
    df['Возраст сотрудника'] = [calculate_age(str(date)) for date in df['Дата рождения сотруд']]
    df['Адрес регистрации'] = [str(row).split(' ')[1] if str(row) != 'nan' else None for row in df['Адрес регистрации по']]
    df['Город рождения'] = [str(row).split(' ')[-1] for row in df['Место рождения сотру']]
    df['Город рождения'] = [row if len(row) > 3 else None for row in df['Город рождения']]
    df['Местный житель'] = [1 if row == 'Норильск' else 0 for row in df['Адрес регистрации']]

    df = df[['Таб.№', 'Дата рождения сотруд','Название категории п', 'ИД фактической штатн', 'Разряд (по фактическ',
             'Семейное положение с', 'Название фактическог', 'Пол сотрудника', 'Текущий рабочий стат',
             'Возраст сотрудника', 'Адрес регистрации', 'Город рождения', 'Местный житель']]

    df.columns = ['Табельный номер', 'Дата рождения сотруд', 'Категория рабочего', 'ИД должности', 'Разряд',
                  'Семейное положение', 'Название мс', 'Пол', 'Рабочий статус', 'Возраст', 'Регистрация',
                  'Город рождения', 'Местный житель']

    return df , workers


def get_education_data(file_path_education: str, path_educate_dict: str, workers: list):
    """

    :param file_path_education:
    :param path_educate_dict:
    :return:
    """
    data = pd.read_excel(file_path_education)

    edu = pd.read_excel(path_educate_dict)
    edu = edu.set_index('ОКИН')
    education_dict = edu.to_dict()['Текст ОКИН']

    attributes = []
    for worker in workers:
        dd = data[data['Табельный номер сотр'] == worker].sort_values(by=['Дата получения образ'], ascending=False)
        try:
            last_date = datetime.fromisoformat(str(pd.to_datetime(
                dd[dd['Код вида образования'] != 'Z1'].sort_values(by=['Дата получения образ'], ascending=True)[
                    'Дата получения образ'].values[0]))).date()
            num_of_dg = int(dd[dd['Код вида образования'] != 'Z1'].shape[0])
            codes_dg = list(
                dd[dd['Код вида образования'] != 'Z1'].sort_values(by=['Код вида образования'], ascending=False)[
                    'Код вида образования'].unique())[0]
        except:
            last_date, num_of_dg, codes_dg = None, None, None

        try:
            last_date_cr = datetime.fromisoformat(str(pd.to_datetime(
                dd[dd['Код вида образования'] == 'Z1'].sort_values(by=['Дата получения образ'],
                    ascending=True)['Дата получения образ'].values[0]))).date()
            num_of_cr = int(dd[dd['Код вида образования'] == 'Z1'].shape[0])
            codes_cr = list(dd['Специальность'].unique())
        except:
            last_date_cr, num_of_cr, codes_cr = None, None, None

        attributes.append([worker, last_date, num_of_dg, codes_dg, last_date_cr, num_of_cr, codes_cr])

    education = pd.DataFrame(attributes,
                             columns=['Табельный номер', 'Дата последнего образования', 'Коллиство образований',
                                      'Коды образований','Дата последнего курса', 'Кол-во курсов', 'Наименование'])

    education['Наименование образования'] = education['Коды образований'].replace(education_dict)
    education['Наличие высшего'] = [1 if 'Высшее' in str(row) else 0 for row in education['Наименование образования']]
    education['Не проходил курсов'] = [(date.today() - date).days if str(date) != 'None' else None for date in
                                       education['Дата последнего образования']]

    education = education[['Табельный номер', 'Дата последнего образования', 'Наименование образования',
                           'Наличие высшего']]

    return education


def get_courses_data(file_path_courses: str, workers: list):
    """

    :param file_path_courses:
    :param workers:
    :return:
    """
    data = pd.read_excel(file_path_courses)
    dtt = data[['Табельный номер сотр', 'Код программы обучен', 'Наименование програм', 'Начало обучения',
                'Окончание обучения', 'Код квалификации']]
    dtt['Год'] = [str(date).split('-')[0] for date in dtt['Окончание обучения']]

    courses = []
    today = datetime.today()
    for worker in workers:
        try:
            last_crs = datetime.fromisoformat(str(pd.to_datetime(
                dtt[dtt['Табельный номер сотр'] == worker].sort_values(by=['Окончание обучения'], ascending=False)[
                    'Окончание обучения'].values[0]))).date()
        except:
            last_crs = None
        try:
            stage = relativedelta(today, datetime.fromisoformat(str(pd.to_datetime(
                dtt[dtt['Табельный номер сотр'] == worker].sort_values(by=['Начало обучения'], ascending=True)[
                    'Начало обучения'].values[0]))).date()).years
        except:
            stage = None
        try:
            num_cr_22 = int(dtt[(dtt['Табельный номер сотр'] == worker) & (dtt['Год'] == '2022')].shape[0])
        except:
            num_cr_22 = None
        try:
            vsego_cr = int(dtt[dtt['Табельный номер сотр'] == worker].shape[0])
        except:
            vsego_cr = None
        courses.append([worker, last_crs, stage, num_cr_22, vsego_cr])

    course = pd.DataFrame(courses, columns=['Табельный номер', 'Дата последнего курса', 'Стаж в компании',
                                            'Курсов за 2022', 'Всего курсов пройдено'])

    return course


if __name__ == '__main__':
    args = parse_args()

    data, workers = get_employee_data(args.file_path_employees)
    data_education = get_education_data(args.file_path_education, args.path_educate_dict, workers)
    data = data.merge(data_education, on='Табельный номер', how='left')
    data_courses = get_courses_data(args.file_path_courses, workers)
    data = data.merge(data_courses, on='Табельный номер', how='left')

    data.to_excel('data/Сотрудники_итог.xlsx', engine='xlsxwriter', index=False)

