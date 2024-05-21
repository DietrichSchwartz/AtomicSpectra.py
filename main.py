import pandas as pd
import plotly.express as px
from NIST_ASD import NISTASD
import pandas
import numpy as np
from scipy.signal import find_peaks

if __name__ == '__main__':
    parameters = {}
    Elements = list(input('Введите элементы через пробел:').split())
    try:
        parameters['low_w'], parameters['upper_w'] = map(int, input('Введите диапазон длин волн:').split())
    except:
        parameters['low_w'], parameters['upper_w'] = 200, 1200
    parameters['sp_num'] = list(map(str, input('Введите порядок ионизации:').split())) or None

    for el in Elements:
        Elements[Elements.index(el)] = NISTASD(element=str(el), low_w=parameters['low_w'],
                        upper_w=parameters['upper_w'], sp_num=parameters['sp_num'])

    # Считывание экспериментальных данных
    experimental_data = pandas.read_csv('experimental_data_05.txt', sep="\t", decimal=',',
                                         names=['lambda', 'I'], dtype=np.float64)
    minimum = min(experimental_data['lambda'])
    maximum = max(experimental_data['lambda'])
    I = experimental_data['I'].values
    lambda_Exp = experimental_data['lambda'].values
    result_std = I[-150:].std()
    print('Standard deviation of baseline = ', result_std)
    fig = px.line(experimental_data, x='lambda', y='I', title="Experimental spectra")

    # Нахождение пиков в спектре экспериментальных данных
    peaks, properties = find_peaks(I, prominence=3*result_std, height=3*result_std)
    properties["prominences"]

    Found_lines = pd.DataFrame({'exp_wl': [list() for i in range(len(Elements))],
                                'exp_intens': [list() for i in range(len(Elements))],
                                'wl': [list() for i in range(len(Elements))],
                                'intens': [list() for i in range(len(Elements))]})
    Found_lines.index = [e.element for e in Elements]

    for el in Elements:
        # Порог интенсивности:
        el.data_frame = el.data_frame[el.data_frame['intens'] > 10 ]
        #Погрешность измерения спектрометром:
        stand = 0.5

        for i in peaks:
            wl = el.data_frame.keys()[2]
            for index, row in el.data_frame.iterrows():
                if row[f'{wl}'] > lambda_Exp[i] - stand and row[f'{wl}'] < lambda_Exp[i] + stand:
                    Found_lines.loc[f'{el.element}']['exp_wl'].append(lambda_Exp[i])
                    Found_lines.loc[f'{el.element}']['exp_intens'].append(I[i])
                    Found_lines.loc[f'{el.element}']['wl'].append(row[f'{wl}'])
                    Found_lines.loc[f'{el.element}']['intens'].append(row['intens'])

    for el in Elements:
        fig.add_scatter(x=Found_lines.loc[f'{el.element}']['wl'], y=Found_lines.loc[f'{el.element}']['exp_intens'],
                        name=f'{el.element}',  mode='markers',
                        hovertemplate='Wavelength(exp)=%{x}<br>Intense(exp)=%{y}<br>%{text}',
                        text=['Intense*={II}'.format(II=Found_lines.loc[f'{el.element}']['intens'][i]) for i in range(len(Found_lines.loc[f'{el.element}']['intens']))])

    fig.update_layout(hovermode='closest')
    fig.show()

