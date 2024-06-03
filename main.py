import math
import numpy as np
import requests
from bs4 import BeautifulSoup
import scipy
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import scipy.stats
from scipy.stats import norm
import matplotlib.pyplot as plt
import pandas as pd
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from pandas.plotting import table
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.pdfgen import canvas
import os, sys
from kivy.resources import resource_add_path, resource_find


class CurrencyApp(MDApp):

    def build(self):
        global formatted_date1
        formatted_date1 = '01/01/2004'
        global formatted_date2
        formatted_date2 = '30/01/2004'
        global value_curr
        value_curr = 'R01235'

        global H, q
        H = MDTextField(text='Среднее значение',
                        pos_hint={'x': .0, 'y': 0.3},
                        size_hint=(0.5, 0.5)
                        )
        q = MDTextField(text='Уровень значимости', pos_hint={'x': .0, 'y': 0.2}, size_hint=(0.5, 0.5))
        return Builder.load_file('currency.kv')

    def get_pdf(self):
        url = f'https://cbr.ru/scripts/XML_dynamic.asp?date_req1={formatted_date1}&date_req2={formatted_date2}&VAL_NM_RQ={value_curr}'
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
                + ((sum(two_n) / len(two_n) - x) ** 2) * len(two_n) + (
                        (sum(tree_n) / len(tree_n) - x) ** 2) * len(
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
        ranges = [f'{min_val} - {one_val}', f'{one_val} - {two_val}', f'{two_val} - {tree_val}',
                  f'{tree_val} - {four_val}', f'{four_val} - {max_val}']
        probabilities = [p1, p2, p3, p4, p5]
        ranges1 = [(min_val + one_val) / 2, (one_val + two_val) / 2, (two_val + tree_val) / 2,
                   (tree_val + four_val) / 2, (four_val + max_val) / 2]

        with PdfPages('chart.pdf') as pdf:
            plt.figure(figsize=(10, 6))
            plt.bar(ranges1, probabilities, color='skyblue', label="Вероятности", width=0.13)
            plt.xticks(ranges1, ranges)
            plt.xlabel('Диапазоны')
            plt.ylabel('Вероятности')
            plt.title('Вероятности относительно диапазонов')
            x_values = np.linspace(min(data), max(data), 100)
            y_values = norm.pdf(x_values, x, s)
            y_values = y_values * max(probabilities) / max(y_values)
            plt.plot(x_values, y_values, color='red', label='Нормальное распределение')
            pdf.savefig()
            plt.close()

    def wrap_text(self, text, max_width, c):
        lines = []
        words = text.split()
        current_line = ""
        for word in words:
            if c.stringWidth(current_line + ' ' + word if current_line else word, 'DejaVuSans', 14) <= max_width:
                current_line += ' ' + word if current_line else word
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
        return lines

    def get_pdf1(self):
        if self.root.ids.text_label.text or self.root.ids.text_student.text:
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
            c = canvas.Canvas('hypothesis.pdf', pagesize=letter)
            c.setFont('DejaVuSans', 14)

            max_width = 540
            title_label = "Критерий хи квадрат:"
            c.drawString(0, 770, title_label)

            text_label = self.root.ids.text_label.text if self.root.ids.text_label.text != "" else ""
            lines_label = self.wrap_text(text_label, max_width, c)
            y_position = 750
            for line in lines_label:
                c.drawString(0, y_position, line)
                y_position -= 16

            title_student = "Критерий Стьюдента:"
            y_position -= 10
            c.drawString(0, y_position, title_student)

            text_student = self.root.ids.text_student.text if self.root.ids.text_student.text != "" else ""
            lines_student = self.wrap_text(text_student, max_width, c)
            y_position -= 16
            for line in lines_student:
                c.drawString(0, y_position, line)
                y_position -= 16

            c.save()
        else:
            self.show_save_text_error()

    def get_student(self):
        if self.root.ids.text_H.text and self.root.ids.text_q.text:
            H = float(self.root.ids.text_H.text)
            q = float(self.root.ids.text_q.text)
            url = f'https://cbr.ru/scripts/XML_dynamic.asp?date_req1={formatted_date1}&date_req2={formatted_date2}&VAL_NM_RQ={value_curr}'
            xml = requests.get(url)

            soup = BeautifulSoup(xml.content, 'lxml')
            data = []
            for i in soup.find_all('value'):
                data.append(float(i.text.replace(',', '.')))
            data = [round(i, 2) for i in data]
            data = sorted(data)
            print('Данные:', data)
            intervals = 5
            n = len(data)
            min_val = min(data)
            max_val = max(data)
            interval_range = (max_val - min_val) / intervals
            bins = [round(min_val + i * interval_range, 2) for i in range(intervals + 1)]

            one_val = bins[1]
            two_val = bins[2]
            three_val = bins[3]
            four_val = bins[4]

            min_n = []
            one_n = []
            two_n = []
            tree_n = []
            max_n = []

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

            t = (x - H) / (s / math.sqrt(n))

            left_data = scipy.stats.t.ppf(q, n)

            if left_data < t:
                self.root.ids.text_student.text = f"Нулевая гипотеза  принимается, так как p-значение = {t} больше нашего уровня значимости a = {q} ({left_data})"
            else:
                self.root.ids.text_student.text = f"Нулевая гипотеза отвергается, так как p-значение = {t} меньше нашего уровня значимости a = {q} ({left_data})"
        else:
            self.show_value_error()

    dialog = None

    def show_value_error(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Введены не все данные",
                buttons=[
                    MDFlatButton(text="OK", text_color=self.theme_cls.primary_color, on_release=self.close_dialog)
                ],
            )
        self.dialog.open()

    dialog1 = None

    def show_save_text_error(self):
        if not self.dialog1:
            self.dialog1 = MDDialog(
                text="Не проверена не одна гипотеза",
                buttons=[
                    MDFlatButton(text="OK", text_color=self.theme_cls.primary_color, on_release=self.close_dialog1)
                ],
            )
        self.dialog1.open()

    def show_save_chart_error(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Не построен график",
                buttons=[
                    MDFlatButton(text="OK", text_color=self.theme_cls.primary_color, on_release=self.close_dialog)
                ],
            )
        self.dialog.open()

    def show_error(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Данных за выбранный временной период нет",
                buttons=[
                    MDFlatButton(text="OK", text_color=self.theme_cls.primary_color, on_release=self.close_dialog)
                ],
            )
        self.dialog.open()

    def close_dialog1(self, obj):
        self.dialog1.dismiss()

    def close_dialog(self, obj):
        self.dialog.dismiss()

    def on_save(self, instance, value, date_range):
        global formatted_date1
        formatted_date1 = value.strftime("%d/%m/%Y")
        self.root.ids.date_label1.text = formatted_date1

    def on_save1(self, instance, value, date_range):
        global formatted_date2
        formatted_date2 = value.strftime("%d/%m/%Y")
        self.root.ids.date_label2.text = formatted_date2

    def show_date_picker(self):
        date_dialog = MDDatePicker(min_year=2004, max_year=2025, year=2010, day=1, month=1)
        date_dialog.bind(on_save=self.on_save)
        date_dialog.open()

    def show_date_picker1(self):
        date_dialog = MDDatePicker(min_year=2004, max_year=2025, year=2010, day=30, month=1)
        date_dialog.bind(on_save=self.on_save1)
        date_dialog.open()

    def menu_open(self):
        global data
        data = {'USD': "R01235", "EUR": "R01239", "GBP": "R01035", "AED": "R01230", "KZT": "R01335", "CNY": 'R01375'}
        menu_items = [
            {
                "text": i,
                "on_release": lambda x=i: self.menu_callback(x),
            } for i in data
        ]
        self.menu = MDDropdownMenu(
            caller=self.root.ids.button, items=menu_items
        ).open()

    def menu_callback(self, text_item):
        global value_curr
        value_curr = data[text_item]
        self.root.ids.curr_label.text = text_item

    def get_chart(self):
        url = f'https://cbr.ru/scripts/XML_dynamic.asp?date_req1={formatted_date1}&date_req2={formatted_date2}&VAL_NM_RQ={value_curr}'
        global x, s

        xml = requests.get(url)

        soup = BeautifulSoup(xml.content, 'lxml')
        data = []
        for i in soup.find_all('value'):
            data.append(float(i.text.replace(',', '.')))
        data = [round(i, 2) for i in data]
        if not data:
            self.show_error()
        data = sorted(data)
        print('Данные:', data)
        intervals = 5
        n = len(data)
        min_val = min(data)
        max_val = max(data)
        interval_range = (max_val - min_val) / intervals
        bins = [round(min_val + i * interval_range, 2) for i in range(intervals + 1)]

        one_val = bins[1]
        two_val = bins[2]
        three_val = bins[3]
        four_val = bins[4]

        min_n = []
        one_n = []
        two_n = []
        tree_n = []
        max_n = []

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
            return round(abs((scipy.stats.norm.cdf((val1 - mean) / std) - scipy.stats.norm.cdf((val2 - mean) / std))),
                         4)

        p1 = calculate_p(min_val, one_val, x, s)
        p2 = calculate_p(one_val, two_val, x, s)
        p3 = calculate_p(two_val, three_val, x, s)
        p4 = calculate_p(three_val, four_val, x, s)
        p5 = calculate_p(four_val, max_val, x, s)

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
        y_values = scipy.stats.norm.pdf(x_values, x, s)
        y_values = y_values * max(probabilities) / max(y_values)
        plt.plot(x_values, y_values, color='red', label='Нормальное распределение')

        plt.show()

    def get_currency(self):
        url = f'https://cbr.ru/scripts/XML_dynamic.asp?date_req1={formatted_date1}&date_req2={formatted_date2}&VAL_NM_RQ={value_curr}'
        global x, s

        xml = requests.get(url)

        soup = BeautifulSoup(xml.content, 'lxml')
        data = []
        for i in soup.find_all('value'):
            data.append(float(i.text.replace(',', '.')))
        data = [round(i, 2) for i in data]
        if not data:
            self.show_error()
        data = sorted(data)
        print('Данные:', data)
        intervals = 5
        n = len(data)
        min_val = min(data)
        max_val = max(data)
        interval_range = (max_val - min_val) / intervals
        bins = [round(min_val + i * interval_range, 2) for i in range(intervals + 1)]

        one_val = bins[1]
        two_val = bins[2]
        three_val = bins[3]
        four_val = bins[4]

        min_n = []
        one_n = []
        two_n = []
        tree_n = []
        max_n = []

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
            return round(abs((scipy.stats.norm.cdf((val1 - mean) / std) - scipy.stats.norm.cdf((val2 - mean) / std))),
                         4)

        p1 = calculate_p(min_val, one_val, x, s)
        p2 = calculate_p(one_val, two_val, x, s)
        p3 = calculate_p(two_val, three_val, x, s)
        p4 = calculate_p(three_val, four_val, x, s)
        p5 = calculate_p(four_val, max_val, x, s)

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
        sum_n_np_np = n_np_np1 + n_np_np2 + n_np_np3 + n_np_np4 + n_np_np5
        k = 5.99
        if k > sum_n_np_np:
            self.root.ids.text_label.text = f'Нулевая гипотеза принимается, так как значение статистики (хи квадрат) равное {sum_n_np_np} меньше чем критическое знчение статистики равное {k}'
        else:
            self.root.ids.text_label.text = f'Нулевая гипотеза не принимается, так как значение статистики (хи квадрат) равное {sum_n_np_np} больше чем критическое знчение статистики равное {k}'

    def get_table_currency(self):
        url = f'https://cbr.ru/scripts/XML_dynamic.asp?date_req1={formatted_date1}&date_req2={formatted_date2}&VAL_NM_RQ={value_curr}'
        xml = requests.get(url)
        soup = BeautifulSoup(xml.content, 'lxml')

        data = []
        date = []

        for i in soup.find_all('valcurs'):
            for j in i('record'):
                date.append(j['date'])

        for i in soup.find_all('value'):
            data.append(float(i.text.replace(',', '.')))
        data = [round(i, 2) for i in data]

        data_dict = {date_val: data_val for date_val, data_val in zip(date, data)}
        df = pd.DataFrame(list(data_dict.items()), columns=['Дата', 'Курс валюты'])

        fig, ax = plt.subplots(figsize=(5, 6))
        ax.axis('tight')
        ax.axis('off')
        tbl = table(ax, df, loc='center', cellLoc='center', colWidths=[0.3] * len(df.columns))
        print(len(data_dict))
        plt.show()


if __name__ == "__main__":
    try:
        if hasattr(sys, '_MEIPASS'):
            resource_add_path(os.path.join(sys._MEIPASS))
        app = CurrencyApp()
        app.run()
    except Exception as e:
        print(e)
        input("Press enter.")
