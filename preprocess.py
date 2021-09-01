import nltk, os, math, pickle
from nltk import text
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import *
from collections import defaultdict


file = {} #file adalah dictionary yang menampung semua dokumen. Indeksnya adalah docID
fileopen = {} #Menyimpan semua file yang terbuka
file_content = {}   #untuk menyimpan konten setiap file
file_tokenize = {}  #untuk menyimpan kata-kata tokenized
file_stop = {}  #set kata-kata setelah penghapusan kata-kata berhenti
file_stem = {}  #kumpulan kata setelah stemming
file_count = 0  #untuk menghitung jumlah dokumen dalam direktori

term_freq = {}  # frekuensi setiap kata muncul dalam setiap dokumen
term_pos = {} #posisi kemunculan istilah dalam setiap dokumen

posting_list = defaultdict(list) # nama kata dan ID dokumen
word_unique = []    #kata-kata unik dalam daftar posting
query_tokenize = [] #persyaratan tokenized dari kueri
query_stop = []
query_stem = []

match_list = [] #daftar posting untuk semua kata.dirancang untuk menjadi daftar
final_list = [] #daftar akhir docID's

word_full_unique = []   #semua kata unik(Tidak stemmin)
final_wildcard_list = [] #daftar wildcard terakhir

punctuation = ['.', ',', '(', ')', ":", ";"] #Daftar semua tanda baca
stray_chars = ['..', '==', '++', '--', '//', '``' ,' ','~', '/'] #Daftar karakter yang harus dihilangkan
stemmer = PorterStemmer()

def defaultLists(get_flag):
    flag = get_flag
    flag = 0
    path_object = os.getcwd()
    path_object += "\f_file"
    if (os.path.exists(path_object)):
        flag = 1
        return flag
    else:
        file_name = "f_file"
        fileObject = open(file_name, 'wb')
        pickle.dump(file, fileObject)
        fileObject.close()

        file_name = "f_stop"
        fileObject = open(file_name, 'wb')
        pickle.dump(file_stop, fileObject)
        fileObject.close()

        file_name = "f_word_unique"
        fileObject = open(file_name, 'wb')
        pickle.dump(word_unique, fileObject)
        fileObject.close()

        file_name = "f_word_full_unique"
        fileObject = open(file_name, 'wb')
        pickle.dump(word_full_unique, fileObject)
        fileObject.close()

        file_name = "t_freq"
        fileObject = open(file_name, 'wb')
        pickle.dump(term_freq, fileObject)
        fileObject.close()

        file_name = "t_pos"
        fileObject = open(file_name, 'wb')
        pickle.dump(term_pos, fileObject)
        fileObject.close()

        file_name = "p_list"
        fileObject = open(file_name, 'wb')
        pickle.dump(posting_list, fileObject)
        fileObject.close()
        
        return flag
    
def preprocessing(get_path):
    
    global word_full_unique
    global word_unique
    global file_count
    global file_tokenize
    path= get_path
    
    docID = 1 #docID memberikan ID ke dokumen
    for filename in os.listdir(path):
        file[docID] = filename
        docID = docID+1

    file_count = len(file) #untuk mendapatkan hitungan jumlah file dalam folder

    for i in range(1, file_count+1):
        print(i)
        if (file[i].endswith(".txt")): #membuka file
            fileopen[i] = open(path + file[i], encoding = "ISO-8859-1")
            file_content = fileopen[i].read()

        file_content = file_content.lower() #menjadikan dokumen menjadi huruf kecil
        file_tokenize[i] = word_tokenize(file_content) #melakukan tokenisasi setiap file

        file_stem = [stemmer.stem(word) for word in file_tokenize[i]] #Porter Stemmer
        file_stop[i] = [word for word in file_stem if (word not in stopwords.words('english') and word not in punctuation)] #menhapus stopword dan tanda baca

        #menghapus tanda baca multicharacter
        for word in file_stop[i]:
            for stray in stray_chars:
                if stray in word:
                    while word in file_stop[i]:
                        file_stop[i].remove(word)
        
        #menyimpan indeks setiap kata
        term_pos_temp = {}
        term_freq_temp = {}
        for term in file_stop[i]:
            index_list = []
            for index, k in enumerate(file_stop[i]):
                if k == term:
                    index_list.append(index)
            term_pos_temp[term] = index_list
            term_freq_temp[term] = len(index_list)
            
        term_pos[i] = term_pos_temp #menyimpan indeks setiap kata per dokumen
        term_freq[i] = term_freq_temp   

    for i in range(1, file_count+1):
        for term in file_tokenize[i]:
            word_full_unique.append(term)

    word_full_unique = list(set(word_full_unique))

    file_tokenize = {} #menghapus file_tokenize dari dictionary

    for i in range(1, file_count+1): #membuat daftar posting
        unique = list(set(file_stop[i]))
        for word in unique:
            posting_list[word].append(i)
            
    for i in range(1, file_count+1): #mengurutkan daftar postingan
        unique = list(set(file_stop[i]))
        for word in unique:
            word_unique.insert(0, word)
            posting_list[word].sort()

    word_unique = list(set(word_unique))
    
def querying(get_query):

    global posting_list
    global final_list
    global file_count

    result_count = -1
    query = get_query
    query_tokenize = [] #variable terms tokenisasi dari query
    query_stop = []     #kata-kata berhenti dari kueri
    query_stem = []     #variable untuk menyimmpan kata-kata kueri
    final_list = []     
    tf_idf = {}

    query_tokenize = word_tokenize(query)   #Tokenisasi queri
    query_stop = [word for word in query_tokenize if (word not in stopwords.words('english') and word not in punctuation)]  #Remove stop words from query	
		
    #menerapkan porter Stemmer jika kata tersebut bukan kueri wildcard
    for word in query_stop:
        if '*' in word:
            query_stem.append(word)
        else:
            word = stemmer.stem(word) #Porter Stemmer untuk kata-kata dalam kueri yang tidak memiliki karakter wildcard
            query_stem.append(word)

    print("Query")
    print(query_stem)

    flag = 0    #0 artinya AND(default), 1 artinya OR, -1 artnya NOT
    flag_prox = False
    flag_prox_check = False
    diff = -1

    for index, word in enumerate(query_stem):
        if(word in word_unique):
            temp = posting_list[word] #menyimpan daftar posting untuk kata tertentu
                    
            if not final_list and flag != -1: #memeriksa apakah daftarnya kosong
                final_list = temp #masukkan daftar posting ke list

            elif not final_list and flag == -1 and not flag_prox_check: #Jika ~ adalah token pertama dalam kueri (yaitu final_list kosong dan Anda mendapatkan ~)
                for i in range(1, file_count+1):
                    final_list.append(i)
                final_list.sort()
                for doc_id in temp:
                    print(final_list)
                    if doc_id in final_list:
                        final_list.remove(doc_id)
                flag = 0    #Menyetel ulang flag ke 0
                        
            else:
                if(flag == 0 and not flag_prox):  #' ' operasi AND
                    temp1 = []
                    for doc_id in temp: #AND daftar posting yang diperoleh sampai saat itu dan daftar posting kata
                        if doc_id in final_list:
                            temp1.append(doc_id)
                    final_list = temp1  #Mengganti final_list lama dengan daftar AND baru

                elif(flag == 1 and not flag_prox): #/ operasi OR
                    temp1 = []
                    for doc_id in temp: #memasukkan semua docID yang ada di temp tetapi tidak di final_list
                        if doc_id not in final_list:
                            temp1.append(doc_id)
                    for doc_id in final_list: #Masukkan semua docID dari final_list
                        temp1.append(doc_id)
                    final_list = temp1                      
                    flag = 0    #Menyetel ulang flag ke 0

                elif(flag == -1 and not flag_prox and not flag_prox_check):   #~ operasi NOT
                    temp1 = final_list
                    for doc_id in temp:
                        if doc_id in final_list:
                            temp1.remove(doc_id)
                    final_list = temp1
                    flag = 0

                elif(flag_prox):    #menghandel proximity queries
                    prox_list = []
                    for doc_id in range(1, file_count+1):
                        if(query_stem[index-2] in term_pos[doc_id] and query_stem[index] in term_pos[doc_id]):
                            pos_prev_word = term_pos[doc_id][query_stem[index-2]]
                            pos_curr_word = term_pos[doc_id][query_stem[index]]

                            #print(pos_prev_word)
                            #print(pos_curr_word)
                            
                            i=0
                            j=0                    
                            
                            while (j<len(pos_prev_word) and i<len(pos_curr_word)):
                                if((pos_curr_word[i]-pos_prev_word[j]) == diff): #pastikan count ditambahkan jika ranking diberikan
                                    i+=1
                                    j+=1
                                    prox_list.append(doc_id)
                                    break
                                elif((pos_curr_word[i] - pos_prev_word[j]) < diff):
                                    i+=1
                                elif((pos_curr_word[i] - pos_prev_word[j]) > diff):
                                    j+=1
                    print("PROXIMITY")
                    print(prox_list)

                    print("FINAL")
                    print(final_list)
                    if not final_list and flag != -1:  #Jika final list dan flag tidak -1, daftar terakhir adalah daftar proximity
                        final_list = prox_list

                    elif not final_list and flag == -1: #Jika final list kosong dan flag adalah -1
                        for i in range(1, file_count+1):
                            final_list.append(i)
                            final_list.sort()
                        for doc_id in prox_list:
                            if doc_id in final_list:
                                final_list.remove(doc_id)
                        flag = 0    #menyetel ulang flag to 0
                        flag_prox_check = False
                
                    elif(flag == 0):  #' ' operasi AND
                        temp1 = []
                        for doc_id in prox_list: #daftar posting yang diperoleh dan daftar posting kata
                            if doc_id in final_list:
                                temp1.append(doc_id)
                        final_list = temp1  #mengganti final_list yang lama dengan list yang baru

                    elif(flag == 1): #/ operasi OR
                        temp1 = []
                        for doc_id in prox_list: #Masukkan semua docID yang ada di temp tetapi tidak di final_list
                            if doc_id not in final_list:
                                temp1.append(doc_id)
                        for doc_id in final_list: #Masukkan semua docID dari final_list
                            temp1.append(doc_id)
                        final_list = temp1                      
                        flag = 0    #menyetel ulang flag to 0
                    
                    elif(flag == -1):   #~ operasi not
                        temp1 = final_list
                        for doc_id in prox_list:
                            if doc_id in final_list:
                                temp1.remove(doc_id)
                        final_list = temp1
                        flag = 0
                        flag_prox_check = False
                    flag_prox = False
            
        elif(word == " "): #jika terdapat " ", set flag to 0
            flag = 0
            continue
        elif(word == "~"): #jika terdapat ~, set flag to -1. Jadi pada iterasi berikutnya melakukan operasi NOT
            flag = -1
            if index+2 < len(query_stem):
                if (query_stem[index+2].startswith('^^') and query_stem[index+2].split('^^')[1].isdigit()):
                    flag_prox_check = True
            
        elif(word == "/"): #jika terdapat /, set flag to 1. Di iter berikutnya, ia melakukan operasi OR
            flag = 1
        elif(word.startswith('^^') and word.split('^^')[1].isdigit()):
            flag_prox = True
            diff = int(word.split('^^')[1])+1

        elif(word.startswith('..') and word.split('..')[1].isdigit()):
            result_count = int(word.split('..')[1])
        
        #WILDCARD QUERI    
        elif('*' in word):
            fore_word = word.split('*')[0]
            back_word = word.split('*')[1]

            wildcard_list = []
            wildcard_list_full = []
            final_wildcard_list = []
            first = True

            for term in word_full_unique:
                if term.startswith(fore_word) and term.endswith(back_word):
                    wildcard_list_full.append(term)
                    term = stemmer.stem(term)
                    wildcard_list.append(term)

            print("WILDCARD LIST")
            print(wildcard_list)

            print("UNSTEMMED WILDCARD LIST")
            print(wildcard_list_full)
                    
            for term in wildcard_list:
                temp = posting_list[term]

                #print(posting_list[term])
                
                if not final_wildcard_list: #cek apakah listnya kosong
                    final_wildcard_list = temp #measukkan ke daftar posting
                    
                else:
                    temp1 = []
                    for doc_id in temp:
                        if doc_id not in final_wildcard_list:
                            temp1.append(doc_id)
                    for doc_id in final_wildcard_list:
                        temp1.append(doc_id)
                    final_wildcard_list = temp1

            print("FINAL WILDCARD LIST")
            print(final_wildcard_list)
            
            if not final_list and flag != -1:  #Jika final list kosong dan flag bukan -1, final list adalah daftar_wildcard_final
                final_list = final_wildcard_list

            elif not final_list and flag == -1:
                for i in range(1, file_count+1):
                    final_list.append(i)
                final_list.sort()
                for doc_id in final_wildcard_list:
                    if doc_id in final_list:
                        final_list.remove(doc_id)
                flag = 0    #reset flag to 0 
                
            elif(flag == 0):  #' ' operasi AND
                    temp1 = []
                    for doc_id in final_wildcard_list: #daftar posting yang diperoleh dan daftar posting kata
                        if doc_id in final_list:
                            temp1.append(doc_id)
                    final_list = temp1  #mengganti final_list yang lama dengan list yang baru

            elif(flag == 1): #/ operasi OR
                    temp1 = []
                    for doc_id in final_wildcard_list: #Masukkan semua docID yang ada di temp tetapi tidak di final_list
                        if doc_id not in final_list:
                            temp1.append(doc_id)
                    for doc_id in final_list: #Masukkan semua docID dari final_list
                        temp1.append(doc_id)
                    final_list = temp1                      
                    flag = 0    #Reset flag to 0
                    
            elif(flag == -1):   #~ operasi NOT
                    temp1 = final_list
                    for doc_id in final_wildcard_list:
                        if doc_id in final_list:
                            temp1.remove(doc_id)
                    final_list = temp1
                    flag = 0

    #print(final_list)
    
    #tf-idf setiap istilah kueri atas setiap dokumen daftar_final
    for doc_id in final_list:
        doc_score = 0
        for term in query_stem:
            if term in term_freq[doc_id]:
                term_tf = term_freq[doc_id][term]
            else:
                term_tf = 0
            term_df = len(posting_list[term])
            N = file_count

            if(term_df != 0):
                doc_score = doc_score + (term_tf * math.log10(N/term_df))
                
        tf_idf[doc_id] = doc_score

    """print("FINAL LIST")
    print(final_list)"""
    print("RANKED FINAL LIST")
    ranked_final_list = []
    ranked_final_list = sorted(tf_idf, key = tf_idf.get, reverse = True) #Cetak daftar akhir yang diurutkan (Berdasarkan peringkat)rint the sorted final list (Based on rank)

    result = "Doc_ID:     Nama_Dokumen\n"
    
    if(result_count == -1):
        for doc_id in ranked_final_list:
            if doc_id < 10:
                result += (str(doc_id) + "           " + file[doc_id] + "\n")
            else:
                result += (str(doc_id) + "         " + file[doc_id] + "\n")
            print(str(doc_id) + " " + file[doc_id])
            
    else:
        for doc_id in ranked_final_list:
            if(result_count <= 0):
                break
            else:
                print(str(doc_id) + " " + file[doc_id])
                if doc_id < 10:
                    result += (str(doc_id) + "          " + file[doc_id] + "\n")
                else:
                    result += (str(doc_id) + "        " + file[doc_id] + "\n")
                result_count = result_count - 1
    return result

     
