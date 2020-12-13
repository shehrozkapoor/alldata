__version__ = '0.0.2'


import fitz
from PIL import Image
from PyPDF2 import PdfFileReader, PdfFileWriter
from tabula import read_pdf
import tabula
import camelot
import nltk
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx

class Table:
    def __init__(self,address):
        self._address = address


    def extractTableCsv(self):
        try:
            tables = tabula.convert_into(self._address,"extractedCSVAll.csv",pages='all')
            if tables is None:
                print('[!] No table found an empty file created')
        except FileNotFoundError:
            print("[!] File not found Invalid address")
        except Exception as e:
            print(e)

    def extractTableJson(self):
        try:
            tables = tabula.convert_into(self._address,"extractedJsonAll.json",pages='all')
            if tables is None:
                print('[!] No table found an empty file created')
        except FileNotFoundError:
            print("[!] File not found Invalid address")
        except Exception as e:
            print(e)

    def extractTableHTML(self):
        try:
            tables = camelot.read_pdf(self._address,pages='all')
            if len(tables)<1:
                print("[!] No Table Found")
                return
            tables.export("tablesHTMLAll.html", f="html")
        except FileNotFoundError:
            print("[!] File not found Invalid address")
        except Exception as e:
            print(e)

    def extractSpecPageTableHTML(self,page):
        try:
            tables = camelot.read_pdf(self._address,pages=str(page))
            if len(tables)<1:
                print("[!] No Table Found")
                return
            tables.export(f"tablesHTML{page}.html", f="html")
        except FileNotFoundError:
            print("[!] File not found Invalid address")
        except IndexError:
            print("[!] Page Not Found")
        except Exception as e:
            print(e)

    def extractSpecPageTableCsv(self,page):
        try:
            tables = tabula.read_pdf(self._address,pages='all')
            if len(tables)<page:
                print('[!] Invalid Page Number')
                return
            tables = tabula.convert_into(self._address, f"OutputCsv{page}.csv", output_format="csv", pages=page)
            if tables is None:
                print('[!] No table found an empty file created')
        except FileNotFoundError:
            print("[!] File not found Invalid address")
        except Exception as e:
            print(e)
    def extractSpecPageTableJson(self,page):
        try:
            tables = tabula.read_pdf(self._address,pages='all')
            if len(tables)<page:
                print('[!] Invalid Page Number')
                return
            tables = tabula.convert_into(self._address, f"OutputJson{page}.json", output_format="json", pages=page)
            if tables is None:
                print('[!] No table found an empty file created')
        except FileNotFoundError:
            print("[!] File not found Invalid address")
        except Exception as e:
            print(e)

class Image:
    def __init__(self,address):
        self._address = address

    def extractImageAll(self):
        doc = fitz.open(self._address)
        for i in range(len(doc)):
            for img in doc.getPageImageList(i):
                if len(doc.getPageImageList(i))==0:
                    print(f'[!]No Image Found on {i}')
                xref = img[0] 
                pix = fitz.Pixmap(doc, xref)
                if pix.n < 5: 
                    pix.writePNG("p%s-%s.png" % (i, xref))
                else: 
                    pix1 = fitz.Pixmap(fitz.csRGB, pix)  
                    pix1.writePNG("p%s-%s.png" % (i, xref))
                    pix1 = None  
                pix = None  
    def extractImageAllJpeg(self):
        doc = fitz.open(self._address)
        for i in range(len(doc)):
            for img in doc.getPageImageList(i):
                if len(doc.getPageImageList(i))==0:
                    print(f'[!]No Image Found on {i}')
                xref = img[0]  
                pix = fitz.Pixmap(doc, xref)
                if pix.n < 5:  
                    pix.writeJpeg("p%s-%s.jpeg" % (i, xref))
                else:  
                    pix1 = fitz.Pixmap(fitz.csRGB, pix)  
                    pix1.writeJpeg("p%s-%s.jpeg" % (i, xref))
                    pix1 = None  
                pix = None 

    def extractImageSpecPage(self,page):
        doc = fitz.open(self._address)
        if len(doc)<page:
            print("[!]Page Not Found")
            return
        for i in range(len(doc)):
            if i==page:
                if len(doc.getPageImageList(i))==0:
                    print('[!]No Image Found')
                    return
                for img in doc.getPageImageList(i):
                    xref = img[0]  
                    pix = fitz.Pixmap(doc, xref)
                    if pix.n < 5:  
                        pix.writePNG("p%s-%s.png" % (i, xref))
                    else:  
                        pix1 = fitz.Pixmap(fitz.csRGB, pix)  
                        pix1.writePNG("p%s-%s.png" % (i, xref))
                        pix1 = None  
                    pix = None 


class Text:
    def __init__(self,address):
        self._address = address


    def extractTextAll(self):
        try:
            pdf = PdfFileReader(self._address)
        except FileNotFoundError:
            print("[!] No File Found ")
            return
        with open('extractText.txt','w') as f:
            for page_num in range(pdf.numPages):
                pageObj = pdf.getPage(page_num)
                f.write(pageObj.extractText())
            f.close()

    def extractTextSpecPage(self,page):
        try:
            pdf = PdfFileReader(self._address)
        except FileNotFoundError:
            print("[!] No File Found ")
            return
        with open(f'extractTextPage{page}.txt','w') as f:
            pageObj = pdf.getPage(page)
            f.write(pageObj.extractText())
            f.close()

class summarize:
    def __init__(self,address):
        self._address=address

    def read_article(self):
        file = open(self._address       , "r")
        filedata = file.readlines()
        article = filedata[0].split(". ")
        sentences = []

        for sentence in article:
            print(sentence)
            sentences.append(sentence.replace("[^a-zA-Z]", " ").split(" "))
        sentences.pop() 
    
        return sentences

    def sentence_similarity(sent1, sent2, stopwords=None):
        if stopwords is None:
            stopwords = []

        sent1 = [w.lower() for w in sent1]
        sent2 = [w.lower() for w in sent2]

        all_words = list(set(sent1 + sent2))

        vector1 = [0] * len(all_words)
        vector2 = [0] * len(all_words)

    # build the vector for the first sentence
        for w in sent1:
            if w in stopwords:
                continue
            vector1[all_words.index(w)] += 1

    # build the vector for the second sentence
        for w in sent2:
            if w in stopwords:
                continue
            vector2[all_words.index(w)] += 1

        return 1 - cosine_distance(vector1, vector2)
 
    def build_similarity_matrix(sentences, stop_words):
        # Create an empty similarity matrix
        similarity_matrix = np.zeros((len(sentences), len(sentences)))
    
        for idx1 in range(len(sentences)):
            for idx2 in range(len(sentences)):
                if idx1 == idx2: #ignore if both are same sentences
                    continue 
                similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

        return similarity_matrix


    def generate_summary(file_name, top_n=5):
        nltk.download("stopwords")
        stop_words = stopwords.words('english')
        summarize_text = []

        # Step 1 - Read text anc split it
        sentences =  read_article(file_name)

        # Step 2 - Generate Similary Martix across sentences
        sentence_similarity_martix = build_similarity_matrix(sentences, stop_words)

        # Step 3 - Rank sentences in similarity martix
        sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
        scores = nx.pagerank(sentence_similarity_graph)

        # Step 4 - Sort the rank and pick top sentences
        ranked_sentence = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)    
        print("Indexes of top ranked_sentence order are ", ranked_sentence)    

        for i in range(top_n):
            summarize_text.append(" ".join(ranked_sentence[i][1]))

        # Step 5 - Offcourse, output the summarize texr
        print("Summarize Text: \n", ". ".join(summarize_text))
