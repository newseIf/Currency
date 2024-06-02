import math
import numpy as np
import requests
from bs4 import BeautifulSoup
import scipy
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
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



KV = '''
MDFloatLayout:

    MDRaisedButton:
        text: "Начало диапазона"
        pos_hint: {'x':0,'y':.9}
        on_release: app.show_date_picker()
    MDRaisedButton:
        text: "Конец диапазона"
        pos_hint: {'x':.0,'y':0.8}
        on_release: app.show_date_picker1()
    MDRaisedButton:
        id: button
        text: "Валюта"
        pos_hint: {'x':.0,'y':0.7}
        on_release: app.menu_open()
    MDRaisedButton:
        text: "Критерий хи квадрат"
        on_release: app.get_currency()
        pos_hint: {'x':.0,'y':0.6}
    MDRaisedButton:
        text: "Построение графика"
        on_release: app.get_chart()
        pos_hint: {'x':.25,'y':0.6}
    MDRaisedButton:
        text: "Критерий Стьюдента"
        on_release: app.get_student()
        pos_hint: {'x':0,'y':0.2}
    MDRaisedButton:
        text: "Выбранные данные"
        on_release: app.get_table_currency()
        pos_hint: {'x':0.81,'y':0.9}
    MDRaisedButton:
        text: "Сохранить график"
        on_release: app.get_pdf()
        pos_hint: {'x':0.805,'y':0.8}
    MDRaisedButton:
        text: "Сохранить гипотезы"
        on_release: app.get_pdf1()
        pos_hint: {'x':0.785,'y':0.7}
    FloatLayout:
        MDBoxLayout:
            size_hint: None, None
            size: '1920px', '5px'
            pos_hint: {'x':.0,'y':0.67}
            md_bg_color: app.theme_cls.primary_color

            canvas.before:
                Color:
                    rgba: app.theme_cls.accent_color
                Line:
                    points: self.x, self.center_y, self.x + self.width, self.center_y
                    width: 1.5
        MDBoxLayout:
            size_hint: None, None
            size: '1920px', '5px'
            pos_hint: {'x':.0,'y':0.5}
            md_bg_color: app.theme_cls.primary_color

            canvas.before:
                Color:
                    rgba: app.theme_cls.accent_color
                Line:
                    points: self.x, self.center_y, self.x + self.width, self.center_y
                    width: 1.5

    MDLabel:
        id: date_label1
        pos_hint: {'x':.2,'y':0.43}
        text: "01/01/2004"
    MDLabel:
        id: date_label2
        pos_hint: {'x':.2,'y':0.33}
        text: "30/01/2004"
    MDLabel:
        id: curr_label
        pos_hint: {'x':.2,'y':0.23}
        text: "USD"
    MDLabel:
        id: text_label
        pos_hint: {'x':.0,'y':0.05}
        text: ""
    MDLabel:
        id: text_student
        size_hint_y: None
        pos_hint: {'x':.0,'y':0.05}
        text: ""
    MDTextField:
        id: text_H
        font_size: '20px'
        size_hint_x: None
        width: 300
        pos_hint: {"x":.0, "y":.4}
        hint_text: "Средний значение"
    MDTextField:
        id: text_q
        font_size: '20px'
        pos_hint: {"x": .0, "y": .3}
        hint_text: "Уровень значимости"
        size_hint_x: None
        width: 300

    '''
class CurrencyApp(MDApp):

    def build(self):
        global formatted_date1
        formatted_date1= '01/01/2004'
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
        return Builder.load_string(KV)

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
            H = int(self.root.ids.text_H.text)
            q = float(self.root.ids.text_q.text)
            url = f'https://cbr.ru/scripts/XML_dynamic.asp?date_req1={formatted_date1}&date_req2={formatted_date2}&VAL_NM_RQ={value_curr}'
            print(H, q)
            xml = requests.get(url)

            soup = BeautifulSoup(xml.content, 'lxml')
            data = []
            for i in soup.find_all('value'):
                data.append(float(i.text.replace(',', '.')))
            data = [round(i, 2) for i in data]
            min_val = min(data)
            max_val = max(data)
            if len(data) <= 20:
                avg_val = round((max_val - min_val) / 7, 2)
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

            n = len(data)
            print(n)
            sum_data = [i for i in data]
            x = 1 / len(data) * (sum(sum_data))
            print(x)
            print(data)
            s_sqrt = 1 / len(data) * (
                    ((sum(min_n) / len(min_n) - x) ** 2) * len(min_n) + ((sum(one_n) / len(one_n) - x) ** 2) * len(one_n)
                    + ((sum(two_n) / len(two_n) - x) ** 2) * len(two_n) + ((sum(tree_n) / len(tree_n) - x) ** 2) * len(
                tree_n) + ((sum(max_n) / len(max_n) - x) ** 2) * len(max_n))
            s = s_sqrt ** 0.5
            print(s)

            t = (x - H) / (s / math.sqrt(n))
            print(t)

            left_data = scipy.stats.t.ppf(q, n)
            right_data = scipy.stats.t.ppf(q=1 - q, df=22)

            if t < left_data:
                self.root.ids.text_student.text = f"Нулевая гипотеза отвергается, так как p-значение = {t} меньше нашего уровня значимости a = {q} ({left_data})"
            else:
                self.root.ids.text_student.text = f"Нулевая гипотеза принимается, так как p-значение = {t} больше нашего уровня значимости a = {q} ({left_data})"
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
        global x,s
        xml = requests.get(url)

        soup = BeautifulSoup(xml.content, 'lxml')
        data = []
        for i in soup.find_all('value'):
            data.append(float(i.text.replace(',', '.')))
        data = [round(i, 2) for i in data]
        if not data:
            self.show_error()
        else:
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

            global ranges1
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

    def get_currency(self):
        url = f'https://cbr.ru/scripts/XML_dynamic.asp?date_req1={formatted_date1}&date_req2={formatted_date2}&VAL_NM_RQ={value_curr}'

        xml = requests.get(url)

        soup = BeautifulSoup(xml.content, 'lxml')
        data = []
        for i in soup.find_all('value'):
            data.append(float(i.text.replace(',', '.')))
        data = [round(i, 2) for i in data]
        if not data:
            self.show_error()
        else:
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
    CurrencyApp().run()
