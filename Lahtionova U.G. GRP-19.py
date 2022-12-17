#подлючение необходимых библиотек
from tkinter import *
from tkinter.ttk import Treeview
from tkinter.messagebox import showerror, showwarning
from numpy import *
from matplotlib import rcParams
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

#создание графического окна
window = Tk()
window.title('Расчёт длинной балки на упругом основании')
window.geometry('1920x1080')

#создание рамки с подписью внутри графического окна
frm = LabelFrame(window, text='Данные для расчёта')
#размещение рамки в window
frm.place(relx=0, rely=0)

#создание холста для рисунка
canvas = Canvas(window, width=350, height=410)
img = PhotoImage(file="Lahtionova.png")
canvas.create_image(0, 0, anchor=NW, image=img)
canvas.place(relx=0.21, rely=0) #размещение холста в window

#размещение текстовых меток во frm
data = ['Длина балки, м',
        'Ширина постели, м',
        f'Коэффициент постели, Н/м\N{superscript three}',
        'Сосредоточенная сила 1, Н',
        'Сосредоточенная сила 2, Н',
        'Точка приложения силы 1, м',
        'Точка приложение силы 2, м',
        f'Модуль деформации, Н/м\N{superscript two}',
        f'Момент инерции, м\N{superscript four}',
        ]
for d in range(len(data)):
    lbl = Label(frm, text=data[d], width=25, pady=7, anchor='w')
    lbl.grid(row=d, column=0)

#создание текстовых полей ввода
ent1 = Entry(frm)
ent2 = Entry(frm)
ent3 = Entry(frm)
ent4 = Entry(frm)
ent5 = Entry(frm)
ent6 = Entry(frm)
ent7 = Entry(frm)
ent8 = Entry(frm)
ent9 = Entry(frm)
#размещение текстовых полей ввода во frm
Ent = [ent1, ent2, ent3, ent4, ent5, ent6, ent7, ent8, ent9]
for j in Ent:
    j.grid(row=Ent.index(j), column=1)

#функция для очистки полей ввода
def clear():
    for c in Ent:
        c.delete(0, END)

#функция ввода исходных значений
def enter():
    clear() #очищение полей ввода для избежания повторений
    ent1.insert(0, 113)
    ent2.insert(0, 0.12)
    ent3.insert(0, 500000000)
    ent4.insert(0, 19200)
    ent5.insert(0, 74500)
    ent6.insert(0, 14)
    ent7.insert(0, 19)
    ent8.insert(0, 20000000)
    ent9.insert(0, 0.346)

#функция для расчета таблицы значений и построения эпюр
def calculate():
    global L, h, k0, P1, P2, b1, b2, E, I
    #проверка введенных данных
    try:
        #прием данных из полей ввода
        L = int(ent1.get())
        h = float(ent2.get())
        k0 = int(ent3.get())
        P1 = float(ent4.get())
        P2 = float(ent5.get())
        b1 = int(ent6.get())
        b2 = int(ent7.get())
        E = float(ent8.get())
        I = float(ent9.get())
    except ValueError: #исключение ошибки ввода данных
        showerror('Error', 'Данные введены некорректно')

    beta = (k0 * h / (4 * E * I)) ** (1 / 4)

    #исключение ошибок ввода данных
    if (b1 > b2) ^ (b1 > L) ^ (b2 > L):
        showwarning('Warning', 'Введите корректные данные')
        return
    elif L * beta < 2 * pi:
        showerror('Error', 'Короткая балка - расчёт невозможен')
        return
        #создание массива аргументов с учетом разрывов в точках приложения сил
    x1 = arange(0, b1 + 1, 1)
    x2 = arange(b1, b2 + 1, 1)
    x3 = arange(b2, L + 1)
    x = concatenate((x1, x2, x3))

    #объявление массивов
    y = []
    fi = []
    M = []
    Q = []

    #цикл заполнения массивов
    for i in x:
        y.append((-P1 * exp(-beta * abs(b1 - i)) * (sin(beta * abs(b1 - i)) - cos(beta * abs(b1 - i)))
                  - P2 * exp(-beta * abs(b2 - i)) * (sin(beta * abs(b2 - i)) - cos(beta * (b2 - i)))) /
                 (8 * E * I * beta ** 3))
        fi.append((P1 * exp(-beta * abs(b1 - i)) * sin(beta * abs(b1 - i))
                   + P2 * exp(-beta * abs(b2 - i)) * sin(beta * abs(b2 - i))) / (4 * E * I * beta ** 2))
        M.append((-P1 * exp(-beta * abs(b1 - i)) * (cos(beta * (b1 - i)) - sin(beta * abs(b1 - i)))
                  - P2 * exp(-beta * abs(b2 - i)) * (cos(beta * (b2 - i)) - sin(beta * abs(b2 - i)))) / (4 * beta))
        Q.append(sign(i - b1 - 0.01) * P1 * exp(-beta * abs(b1 - i)) * cos(beta * (b1 - i)) / 2
                 + sign(i - b2 - 0.01) * P2 * exp(-beta * abs(b2 - i)) * cos(beta * (b2 - i)) / 2)

    #замена элементов массива из-за разрыва в точках приложения сил
    Q[b1 + 1] = P1 / 2 - P2 * exp(-beta * (b2 - b1)) / 2 * cos(beta * (b2 - b1))
    Q[b2 + 2] = P1 * exp(-beta * (b2 - b1)) / 2 * cos(beta * (b2 - b1)) + P2 / 2

    #создание таблицы значений
    table = Treeview(window, columns=('x', 'y', 'fi', 'M', 'Q'), show='headings', height=18)

    table.column('x', width=35, anchor='center')
    table.column('y', width=170, anchor='center')
    table.column('fi', width=170, anchor='center')
    table.column('M', width=170, anchor='center')
    table.column('Q', width=170, anchor='center')
    #шапка таблиццы
    table.heading('x', text='x, м')
    table.heading('y', text='y(x), м')
    table.heading('fi', text='fi(x), рад')
    table.heading('M', text='M(x), Н*м')
    table.heading('Q', text='Q(x), Н')
    #заполнение таблицы значений
    for i in range(len(x)):
        table.insert("", END, values=(str(x[i]), str(y[i]), str(fi[i]), str(M[i]), str(Q[i])))

    #размещение таблицы в window
    table.place(relx=0, rely=0.49)

    #редактирование границ figure
    rcParams['figure.subplot.left'] = 0.12
    rcParams['figure.subplot.bottom'] = 0.06
    rcParams['figure.subplot.right'] = 0.945
    rcParams['figure.subplot.top'] = 0.967
    rcParams['figure.subplot.hspace'] = 0.45

    #создание окна для эпюр
    fig = plt.figure(figsize=(8, 8))
    #создание эпюры прогиба в figure
    ax1 = fig.add_subplot(4, 1, 1)
    ax1.set(xticks=arange(0, L + 2, 5),
            xlim=(0, L + 2),
            xlabel=('x,м'),
            ylabel=('y(x), м')
            )
    ax1.set_title('Эпюра прогиба балки', fontsize=10)
    ax1.plot(x, y, '-og', markersize=3)
    ax1.vlines(b1, 0, y[b1], color='r', linestyle='--')
    ax1.vlines(b2, 0, y[b2 + 2], color='r', linestyle='--')
    ax1.scatter([b1, b2], [y[b1], y[b2 + 2]], zorder=5, color='r', marker='o')
    ax1.grid()
    # создание эпюры угла поворота оси в figure
    ax2 = fig.add_subplot(4, 1, 2)
    ax2.set(xticks=(arange(0, L + 2, 5)),
            xlim=(0, L + 2),
            xlabel=('x,м'),
            ylabel=('fi(x), рад')
            )
    ax2.set_title('Эпюра угла поворота оси балки', fontsize=10)
    ax2.plot(x, fi, '-og', markersize=3)
    ax2.scatter([b1, b2], [fi[b1], fi[b2 + 2]], zorder=5, color='r', marker='o')
    ax2.grid(True)
    # создание эпюры изгибающего момента в figure
    ax3 = fig.add_subplot(4, 1, 3)
    ax3.set(xticks=(arange(0, L + 2, 5)),
            xlim=(0, L + 2),
            xlabel=('x,м'),
            ylabel=('M(x), Н*м')
            )
    ax3.set_title('Эпюра изгибающего момента', fontsize=10)
    ax3.plot(x, M, '-og', markersize=3)
    ax3.vlines(b1, 0, M[b1], color='r', linestyle='--')
    ax3.vlines(b2, 0, M[b2 + 2], color='r', linestyle='--')
    ax3.scatter([b1, b2], [M[b1], M[b2 + 2]], zorder=5, color='r', marker='o')
    ax3.grid()
    # создание эпюры перерезывающей силы в figure
    ax4 = fig.add_subplot(4, 1, 4)
    ax4.set(xticks=(arange(0, L + 2, 5)),
            xlim=(0, L + 2),
            xlabel=('x,м'),
            ylabel=('Q(x), Н')
            )
    ax4.set_title('Эпюра перерезывающей силы', fontsize=10)
    ax4.plot(x1, Q[:b1 + 1], '-og', markersize=3)
    ax4.plot(x2, Q[b1 + 1:b2 + 2], '-og', markersize=3)
    ax4.plot(x3, Q[b2 + 2:], '-og', markersize=3)
    ax4.vlines(b1, Q[b1], Q[b1 + 1], color='r', linestyle='--')
    ax4.vlines(b2, Q[b2 + 1], Q[b2 + 2], color='r', linestyle='--')
    ax4.scatter([b1, b1, b2, b2], [Q[b1], Q[b1 + 1], Q[b2 + 1], Q[b2 + 2]], zorder=5, color='r', marker='o')
    ax4.grid()

    # размещение figure в window
    canvas2 = FigureCanvasTkAgg(fig, window)
    canvas2.get_tk_widget().place(relx=0.48, rely=0)

#создание кнопок для ввода исходных данных, расчеты и очистки
btn1 = Button(frm, text='Вставить исходные данные', command=enter)
btn1.grid(row=9, column=0, columnspan=2, pady=3)

btn2 = Button(frm, text='Рассчитать', command=calculate)
btn2.grid(row=10, column=0, columnspan=2, pady=3)

btn3 = Button(frm, text='Очистить', command=clear)
btn3.grid(row=11, column=0, columnspan=2, pady=3)

window.mainloop()