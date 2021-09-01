from sys import path
import tkinter as tk 
from tkinter import *
from tkinter import font
from PIL import ImageTk, Image
from nltk import text
import preprocess
from tkinter import ttk, filedialog
from tkinter.filedialog import askopenfile

app_window = Tk()
app_window.title('Sistem Information Retrieval')
app_window.iconbitmap('favicon.ico')

w, h = app_window.winfo_screenwidth(), app_window.winfo_screenheight()
app_window.geometry("%dx%d+0+0" % (w, h))

doc = ""

repo = Frame(app_window, width = 200, height = 50)
space = LabelFrame(app_window, width = 200, height = 50, bd = 0)
search = Frame(app_window)
result = LabelFrame(app_window)
flag = 0

def defaultRepo():
    global flag
    flag = preprocess.defaultLists(flag)
    if flag == 0 :
        setRepo()
        
def setRepo():
    repo_path = repo_entry.get()
    preprocess.preprocessing(repo_path)

def getFolderPath():
   folder_selected = filedialog.askdirectory()
   folderPath.set(folder_selected +'/')

folderPath = StringVar()

img = ImageTk.PhotoImage(Image.open("UISI.png"))
logo = Label(app_window, image = img)
logo.pack(side=LEFT)

judul_label = Label(repo, text= "SISTEM TEMU KEMBALI INFORMASI UNTUK PENCARIAN JUDUL TUGAS AKHIR BERBASIS KATA KUNCI", font=('Calibry bold',15))
judul_label.pack(side= TOP)

des_label = Label(repo, text= "PENCARIAN JUDUL\nKombinasi Kata kunci dengan fungsi Boolean AND(' ') dan OR('/') (contoh : Sistem absensi, sistem / absensi)",
                  font=('Calibry bold', 12),
                  justify="left")
des_label.pack(pady=20, ipady=10, ipadx=10)

repo_label = Label(repo, text = "                           Masukkan Direktori Repositori:  ",font=('Calibry bold',10))
repo_entry = Entry(repo, width = 50, textvariable=folderPath)
repo_browse = Button(repo, text = "browse", command = getFolderPath, width = 10, height = 1)
repo_button = Button(repo, text = "Load data", command = defaultRepo, width = 10, height = 1)

repo_label.pack(side= LEFT)
repo_entry.pack(side = LEFT)
repo_browse.pack(side = LEFT, padx=5, pady=5)
repo_button.pack(side = LEFT)

def searchQuery():
    query = query_entry.get()
    global doc
    doc = preprocess.querying(query)
    result_doc.config(text = doc)

query_label = Label(search, text = "Kata Kunci:  ", font=('Calibry bold',10))
query_entry = Entry(search, width = 50)
query_button = Button(search, text = "Cari", command = searchQuery, width = 10, height = 1)
query_label.pack(side = LEFT)
query_entry.pack(side = LEFT)
query_button.pack(side= LEFT, padx=5, pady=5)

result_doc = Message(result, text = doc, width = 1000, relief = RAISED)
result_label = Label(result, text="Hasil Pencarian:")
result_label.pack(side = TOP)
result_doc.pack(fill = BOTH, expand = YES)

repo.pack()
space.pack()
search.pack()
result.pack(fill = "both", expand = "yes")


app_window.mainloop()
