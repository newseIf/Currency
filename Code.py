import numpy as np
import scipy
import scipy.stats as stats
from matplotlib import pyplot as plt
from bs4 import BeautifulSoup
import requests

# Данные
url = f'https://cbr.ru/scripts/XML_dynamic.asp?date_req1=01/02/2020&date_req2=28/02/2020&VAL_NM_RQ=R01235'
# url = f'https://cbr.ru/scripts/XML_dynamic.asp?date_req1=01/01/2006&date_req2=30/01/2006&VAL_NM_RQ=R01235'

xml = requests.get(url)

soup = BeautifulSoup(xml.content, 'lxml')
data = []
for i in soup.find_all('value'):
    data.append(float(i.text.replace(',', '.')))
data = [round(i, 2) for i in data]

data = sorted(data)
print('Данные:',data)
print(len(data))
intervals = 5
n = len(data)
min_val = min(data)
max_val = max(data)
interval_range = (max_val - min_val) / intervals
bins = [round(min_val + i * interval_range,2) for i in range(intervals + 1)]
# Границы интервалов
one_val = bins[1]
two_val = bins[2]
three_val = bins[3]
four_val = bins[4]

# Массивы для интервалов
min_n = []
one_n = []
two_n = []
tree_n = []
max_n = []

# Заполнение массивов для интервалов
for value in data:
    if value <= one_val:
        min_n.append(value)
    elif one_val < value <= two_val:
        one_n.append(value)
    elif two_val < value <= three_val:
        two_n.append(value)
    elif three_val < value <= four_val:
        tree_n.append(value)
    else:
        max_n.append(value)

print("Интервалы:", bins)
print("min_n:", min_n)
print("one_n:", one_n)
print("two_n:", two_n)
print("tree_n:", tree_n)
print("max_n:", max_n)

sum_data = [i for i in data]
x = 1 / len(data) * (sum(sum_data))

def calculate_term(subset, mean):
    if len(subset) == 0:
        return 0
    return ((sum(subset) / len(subset) - mean) ** 2) * len(subset)


s_sqrt = 1 / len(data) * (
        calculate_term(min_n, x) +
        calculate_term(one_n, x) +
        calculate_term(two_n, x) +
        calculate_term(tree_n, x) +
        calculate_term(max_n, x)
)
s = s_sqrt ** 0.5


def calculate_p(val1, val2, mean, std):
    return round(abs((stats.norm.cdf((val1 - mean) / std) - stats.norm.cdf((val2 - mean) / std))), 4)


p1 = calculate_p(min_val, one_val, x, s)
p2 = calculate_p(one_val, two_val, x, s)
p3 = calculate_p(two_val, three_val, x, s)
p4 = calculate_p(three_val, four_val, x, s)
p5 = calculate_p(four_val, max_val, x, s)

print(p1,p2,p3,p4,p5)
print(p1+p2+p3+p4+p5)
np1 = round(len(data) * p1, 4)
np2 = round(len(data) * p2, 4)
np3 = round(len(data) * p3, 4)
np4 = round(len(data) * p4, 4)
np5 = round(len(data) * p5, 4)

n_np1 = round((len(min_n) - abs(np1)) ** 2, 4)
n_np2 = round((len(one_n) - abs(np2)) ** 2, 4)
n_np3 = round((len(two_n) - abs(np3)) ** 2, 4)
n_np4 = round((len(tree_n) - abs(np4)) ** 2, 4)
n_np5 = round((len(max_n) - abs(np5)) ** 2, 4)

n_np_np1 = round(n_np1 / np1, 4)
n_np_np2 = round(n_np2 / np2, 4)
n_np_np3 = round(n_np3 / np3, 4)
n_np_np4 = round(n_np4 / np4, 4)
n_np_np5 = round(n_np5 / np5, 4)
print("критерий:")
print(n_np_np1 + n_np_np2 + n_np_np3 + n_np_np4 + n_np_np5)

ranges = [f'{min_val} - {one_val}', f'{one_val} - {two_val}', f'{two_val} - {three_val}',
          f'{three_val} - {four_val}', f'{four_val} - {max_val}']
probabilities = [p1, p2, p3, p4, p5]
ranges1 = [(min_val + one_val) / 2, (one_val + two_val) / 2, (two_val + three_val) / 2,
           (three_val + four_val) / 2, (four_val + max_val) / 2]

plt.figure(figsize=(10, 6))
plt.bar(ranges1, probabilities, color='skyblue', label="Вероятности", width=0.13)
plt.xticks(ranges1, ranges)
plt.xlabel('Диапазоны')
plt.ylabel('Вероятности')
plt.title('Гистограмма нормального распределния и соответствующая нормальная кривая')

x_values = np.linspace(min(data), max(data), 100)
y_values = stats.norm.pdf(x_values, x, s)
y_values = y_values * max(probabilities) / max(y_values)
plt.plot(x_values, y_values, color='red', label='Нормальное распределение')

plt.show()