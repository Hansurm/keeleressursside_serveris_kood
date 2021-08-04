#!/usr/bin/env/python3
# -*- coding: utf-8 -*-

#Järgmised 2 rida serveris kasutamiseks sisse kommenteerida.
#import nltk
#nltk.data.path.append("/home/urm97/nltk_data")
from estnltk.wordnet import wn
import json
import sys
import requests
import pandas as pd
import re

def algoritm(sona):
    #Vastavat algoritmi kasutati ka eeltöötluseks lokaalselt, hiljem kommenteeriti välja read, mida polnud vaja enam korrata iga päringu puhul.
    #Välja kommenteeritud read jäeti alles, et näha, kuidas midagi tehti, ning on juures ka kirjeldus, miks on välja kommenteeritud või mida vastava koodiplokiga tehti.

    dict = importDict()


    #leian synsetid
    word_synsets = wn.synsets(sona)
    #Kui vastus pole tühi list, saan alustada tööga, ehk leida vastavat infot ja seda sorteerida.
    if(len(word_synsets)>0):
        #print(word_synsets)
        synonyms = []
        synsetfound = False
        #print("Koik synsetid:",word_synsets)
        #otsin synsetide seast enda sõna (võtan alati esimese hetkel), Juhul kui leian sünohulga, mis sisaldab enda nimes otsitavat sõna, valin selle.
        for w in word_synsets:
            #print(w.name.partition('.')[0])
            if (w.name.partition('.')[0] == sona and not synsetfound):
                synset = w
                synsetfound = True
                #print("Synset mida kasutan: ", synset)
            else:
                if (w.name.partition('.')[0] != sona):
                    synonyms.append(w.name.partition('.')[0])


        #Kui on synsetiga varem töö ära tehtud ja salvestatud json file-i, siis loen sealt, kuid tekkis erindeid kogu synseti hulga läbitöötlemisel
        # nii et mõned synsetid jäid välja, juhul kui sünseti pole dictionarys, siis teostan kogu töö uuesti ühe sünsetiga. See tuleb ka kasuks, kui Eesti Wordneti peaks lisanduma sünohulki.
        if synset.name in dict:
            return json.dumps(dict.get(synset.name), ensure_ascii=False)
        else:
            #print(examples)
            definition = synset.definition()
            #print(definition)
            hyponyms = []
            hypernyms = []
            similarwords = []
            if (len(word_synsets)>0):
                #synset = word_synsets[0]
                #leian alammoisted - hyponym
                hyponym = synset.hyponyms()
                #leian ülemmõisted - hüpernüüm
                hypernym = synset.hypernyms()
                if (len(hyponym)>0):
                    #print("Alammõisted (Hüponüümid) :",hyponym)
                    for hypo in hyponym:
                        hyponyms.append(hypo.name.partition('.')[0])
                if (len(hypernym)>0):
                    #print("Ülemmõiste: (Hüpernüümid) :", hypernym)
                    for hypo in hypernym:
                        hypernyms.append(hypo.name.partition('.')[0])
                    if (len(hypernym)>0):
                        #print("Ülemmõiste (",hypernym[0].name.partition('.')[0], ") alammõisted v.a algne sõna (sarnased sõnad):")
                        for hypo in hypernym[0].hyponyms():
                            if (hypo.name.partition('.')[0] != sona):
                                #print(hypo.name.partition('.')[0])
                                similarwords.append(hypo.name.partition('.')[0])


            examples = synset.examples()

            ##Sorteerin välja sagenenumalt esinenud sõnad, jätan need alles(juhul kui on piisavalt sõnu üldse).
            filepathSagedus = "table1.txt"
            dfSagedus = pd.read_csv(filepathSagedus, delimiter="\t", index_col=['Word'])

            hyponymsSagedus = {}
            for hypo in hyponyms:
                if(hypo in dfSagedus.index):
                    hyponymsSagedus[hypo] = dfSagedus.loc[hypo].Total
                    hyponyms.remove(hypo)
            hyponymsSagedus = sorted(hyponymsSagedus.items(), key=lambda x: x[1], reverse=True)

            #Teen nii, et oleks vähemalt 5 näidet igaksjuhuks, võtan alati kindlasti need mille esinemised on teada, alustan kõige levinumast.
            #kordan igat sorti sõnade jaoks sama tehnikat.
            hyponymsSorted = []
            for pair in hyponymsSagedus:
                if (len(hyponymsSorted) < 5):
                    hyponymsSorted.append(pair[0])
            if (len(hyponymsSorted) < 5):
                vahe = 5 - len(hyponymsSorted)
                for x in range(vahe):
                    if (len(hyponyms) > x):
                        hyponymsSorted.append(hyponyms[x])

            hypernymsSagedus = {}
            for hyper in hypernyms:
                if (hyper in dfSagedus.index):
                    hypernymsSagedus[hyper] = dfSagedus.loc[hyper].Total
                    hypernyms.remove(hyper)
            hypernymsSagedus = sorted(hypernymsSagedus.items(), key=lambda x: x[1], reverse=True)

            hypernymsSorted = []
            for pair in hypernymsSagedus:
                if (len(hypernymsSorted) < 5):
                    hypernymsSorted.append(pair[0])
            if (len(hypernymsSorted) < 5):
                vahe = 5 - len(hypernymsSorted)
                for x in range(vahe):
                    if (len(hypernyms) > x):
                        hypernymsSorted.append(hypernyms[x])

            simWordsSagedus = {}
            for simWord in similarwords:
                if (simWord in dfSagedus.index):
                    simWordsSagedus[simWord] = dfSagedus.loc[simWord].Total
                    similarwords.remove(simWord)
            simWordsSagedus = sorted(simWordsSagedus.items(), key=lambda x: x[1], reverse=True)

            simWordsSorted = []
            for pair in simWordsSagedus:
                if (len(simWordsSorted) < 5):
                    simWordsSorted.append(pair[0])
            if (len(simWordsSorted) < 5):
                vahe = 5 - len(simWordsSorted)
                for x in range(vahe):
                    if (len(similarwords) > x):
                        simWordsSorted.append(similarwords[x])

            teSaurusAnto = ""
            teSaurusSynod = []

            ##SEDA EI SAA SERVERIS KASUTADA, POLE BEAUTIFULSOUP-i
            #Et järgnevat koodi lokaalselt proovida, siis tuleb kommentaari märgid eemaldada nii järgnevalt 7 realt, kui ka allpool leiduv funktsioon "scrapeWord()"
            #infoFromTesaurus = scrapeWord(synset.name.partition('.')[0])
            #teSaurusAnto = ""
            #teSaurusSynod = []
            #if(infoFromTesaurus[0] != ''):
            #    teSaurusAnto = infoFromTesaurus[0]
            #    if(len(infoFromTesaurus[1])>0):
            #        teSaurusSynod = infoFromTesaurus[1]


            jsondata = {
                "examples": examples,
                "definition": definition,
                "hyponyms": hyponymsSorted,
                "hypernyms": hypernymsSorted,
                "similarwords": simWordsSorted,
                "tsantonyym": teSaurusAnto,
                "tsSynod": teSaurusSynod
            }
            return json.dumps(jsondata, ensure_ascii=False)
    else:
        #kui sõnale ei leita sünseti tagastan tyhja sõnastiku
        return json.dumps({}, ensure_ascii=False)

def remove_html_tags(text):
    #html-tagide eemaldamine tekstist, kasutati funktsioonis "scrapeWord"
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

#Tesaurusest antonyymide (lisaks moned sünonüümid) leidmine.
# Keeleressursside serveris puudub beautifulsoup, nii et kommenteerin välja, et ülejäänud kood töötaks.
# def scrapeWord(word):
#     URL = 'https://www.filosoft.ee/thes_et/thes.cgi?word='+word
#     page = requests.get(URL)
#
#     soup = BeautifulSoup(page.content, 'html.parser')
#     alltables = soup.find_all('table')
#     if(len(alltables)>0):
#         #print(len(alltables))
#         table = alltables[0]
#         rows = list()
#         for row in table.findAll("td"):
#            rows.append(row)
#
#         synoJaAntonyymid = []
#         antonyym = ""
#         if(len(rows)>1):
#             antonymFound = False
#             for row in rows:
#                 if not (antonymFound):
#                     #print(type(row))
#                     #print(row)
#                     #kasutan ainult neid ridu, kus on antonyym, sest see on selle koodiploki eesmärk.
#                     #kui rida sisaldab antonyymi, tähistatud punase värviga (kood = #ff0000)
#                     if(str(row).find("#ff0000")!=-1):
#                         #print("Sain antonyymi")
#                         antonymFound = True
#                     rida = remove_html_tags(str(row)).split("\n")
#                     #eemaldan tühjad väärtused
#                     result = [x for x in rida if x]
#                     synoJaAntonyymid = result
#                     #print(result)
#                     #for i in range(len(rida)):
#                         #if(i==0 and rida[i]==argument):
#
#         synonyymid = []
#         if(len(synoJaAntonyymid)>0):
#             antonyym = synoJaAntonyymid[len(synoJaAntonyymid)-1]
#             for sona in synoJaAntonyymid:
#                 if(sona!=antonyym):
#                     synonyymid.append(sona)
#     else:
#         antonyym = ''
#         synonyymid = []
#
#     return [antonyym, synonyymid]

#Kasutati synsetide sõnastiku loomiseks. Võtab kaua aega sest käiakse läbi kogu eesti wordnetis leiduv sünonüümide hulk, lühemaks testimiseks võib välja kommenteerida read "if i == 10:" ning sellele järgnev rida "break".
#Kui teha seda kirjutatakse fail üle ja kaovad eelmised kirjed, kuid saate repositooriumist need uuesti alla laadida.
def writeToFile():
    mydict = {}
    for i, synset in enumerate(wn.all_synsets()):
        try:
            print(i, synset)
            print(synset.name.partition('.')[0])
            vastus = algoritm(synset.name.partition('.')[0])
            #vastus = algoritm(synset.name)
            mydict[synset.name] = vastus
        except:
            pass
        #if i == 10:
        #    break
    with open('synsetDict.json', 'w', encoding='utf8') as f:
        json.dump(mydict, f, ensure_ascii=False)

#loodud synsetide sõnastiku sisse lugemine.
def importDict():
    with open('synsetDict.json', 'r', encoding='utf8') as fp:
        data = json.load(fp)
    return data
print(algoritm(sys.argv[1]))
#writeToFile()

