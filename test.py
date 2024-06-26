import numpy as np
import requests
import scipy
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
from scipy.stats import norm

url = f'https://cbr.ru/scripts/XML_dynamic.asp?date_req1=01/03/2016&date_req2=30/03/2016&VAL_NM_RQ=R01239'

xml = requests.get(url)

soup = BeautifulSoup(xml.content, 'lxml')
data = []
for i in soup.find_all('value'):
    data.append(float(i.text.replace(',', '.')))
data = [round(i, 2) for i in data]
min_val = min(data)
max_val = max(data)
if len(data) <= 20:
    avg_val = round((max_val - min_val) / 6, 2)
elif len(data) <= 42:
    avg_val = round((max_val - min_val) / 5, 2)
else:
    avg_val = round((max_val - min_val) / 4, 2)
one_val = round(min_val + avg_val, 2)
two_val = round(one_val + avg_val, 2)
tree_val = round(two_val + avg_val, 2)
four_val = round(tree_val + avg_val, 2)

min_n = []
one_n = []
two_n = []
tree_n = []
max_n = []
for i in data:
    if i >= min_val and i < one_val:
        min_n.append(i)
    if i >= one_val and i <= two_val:
        one_n.append(i)
    if i >= two_val and i <= tree_val:
        two_n.append(i)
    if i >= tree_val and i <= four_val:
        tree_n.append(i)
    if i > four_val and i <= max_val:
        max_n.append(i)

sum_data = [i for i in data]
x = 1 / len(data) * (sum(sum_data))

s_sqrt = 1 / len(data) * (
        ((sum(min_n) / len(min_n) - x) ** 2) * len(min_n) + ((sum(one_n) / len(one_n) - x) ** 2) * len(
    one_n)
        + ((sum(two_n) / len(two_n) - x) ** 2) * len(two_n) + ((sum(tree_n) / len(tree_n) - x) ** 2) * len(
    tree_n) + ((sum(max_n) / len(max_n) - x) ** 2) * len(max_n))
s = s_sqrt ** 0.5

p1 = round(abs((1 / 2 * (2 * ((scipy.stats.norm.cdf((min_val - x) / s) - 0.5)) - 2 * (
        scipy.stats.norm.cdf((one_val - x) / s) - 0.5)))), 4)
p2 = round(abs(1 / 2 * (2 * ((scipy.stats.norm.cdf((one_val - x) / s) - 0.5)) - 2 * (
        scipy.stats.norm.cdf((two_val - x) / s) - 0.5))), 4)
p3 = round(abs(1 / 2 * (2 * ((scipy.stats.norm.cdf((two_val - x) / s) - 0.5)) - 2 * (
        scipy.stats.norm.cdf((tree_val - x) / s) - 0.5))), 4)
p4 = round(abs(1 / 2 * (2 * ((scipy.stats.norm.cdf((tree_val - x) / s) - 0.5)) - 2 * (
        scipy.stats.norm.cdf((four_val - x) / s) - 0.5))), 4)
p5 = round(abs(1 / 2 * (2 * ((scipy.stats.norm.cdf((four_val - x) / s) - 0.5)) - 2 * (
        scipy.stats.norm.cdf((max_val - x) / s) - 0.5))), 4)

np1 = len(data) * p1
np2 = len(data) * p2
np3 = len(data) * p3
np4 = len(data) * p4
np5 = len(data) * p5

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
print(n_np_np1 + n_np_np2 + n_np_np3 + n_np_np4 + n_np_np5)

ranges = [f'{min_val} - {one_val}', f'{one_val} - {two_val}', f'{two_val} - {tree_val}',
          f'{tree_val} - {four_val}', f'{four_val} - {max_val}']
probabilities = [p1, p2, p3, p4, p5]
ranges1 = [(min_val + one_val) / 2, (one_val + two_val) / 2, (two_val + tree_val) / 2,
           (tree_val + four_val) / 2, (four_val + max_val) / 2]
plt.figure(figsize=(10, 6))
plt.bar(ranges1, probabilities, color='skyblue', label="Вероятности", width=0.13)
plt.xticks(ranges1, ranges)
plt.xlabel('Диапазоны')
plt.ylabel('Вероятности')
plt.title('Гистограмма нормального распределния и соответствующая нормальная кривая')

x_values = np.linspace(min(data), max(data), 100)
y_values = norm.pdf(x_values, x, s)
y_values = y_values * max(probabilities) / max(y_values)
plt.plot(x_values, y_values, color='red', label='Нормальное распределение')

plt.show()