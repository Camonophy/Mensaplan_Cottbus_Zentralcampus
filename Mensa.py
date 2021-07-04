import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup

'''
    Klasse zum Auslesen des aktuellen Mensaplans, 
    welcher online zur Verfuegung gestellt wird.
'''
class Mensaplan:

    '''
        Konstruktor

        param self: Verweis auf die eigene Klasse, 
                    wird beim erstellen eines [Mensaplan] ausgefuehrt.
    '''
    def __init__(self):
        self.__URL = "https://www.swffo.de/2011/ClassPackage/swffo-2020/swffo-speiseplaene/4frame-Speiseplan.CottbusBTU.php"
        self.__speiseplan = {}
        

    '''
        Erstelle einen Mensaplan, basierend auf der definierten URL im Konstruktor

        param self: Verweis auf eigene Klasse, kann mit 
                    [Mensaplan-Objekt].erstelle_speiseplan() aufgerufen werden.
    '''
    def erstelle_speiseplan(self):
        response   = urllib.request.urlopen(self.__URL)
        webContent = response.read()
        fullPage   = BeautifulSoup(webContent , 'html.parser')
        tagesMenus = fullPage.findAll(class_="essenAll")

        for menu in tagesMenus:
            tag      = self.__get_Tag(str(menu.find(class_="speiseplanTag")))
            gerichte = self.__get_Essen(self.__entferne_spitze_klammern(str(menu.findAll(class_="essen"))).split(','))

            self.__speiseplan[tag] = gerichte



    
    '''
    Entferne alle HTML spezifischen Tags, wie <h1><\h1>.

    param text:  Verweis auf eigene Klasse
    param text:  Text mit zu entfernden Tags
    return:      Text, in dem Tags durch [+++] ersetzt wurden
    '''
    def __entferne_spitze_klammern(self, text):
        start = end = 0
        text_len = len(text)

        try:
            while start < text_len:
                if text[start] == '<':
                    end = start + 1
                    while end < text_len:
                        if text[end] == '>':
                            text = text.replace(text[start: end + 1], "+++")
                            start = end - start
                            break
                        end += 1
                start += 1
        except:
            pass

        return text


    '''
    Lese die zur Auswahl stehenden Essen
    eines Tages aus.

    param self:  Verweis auf eigene Klasse
    param essen: HTML [essen] - Sektion
    return:      Dictionary mit folgendem Format:
                 {<EssensNr>: [<Deutsch>, <Englisch>]} 
    
    issue: Manche [mensaSpezial] haben eine unbekannte Struktur
    ''' 
    def __get_Essen(self, essen):
        essen_dict = {}

        for auswahl in essen:
            split_essen = auswahl.split("+++")
            try:
                # Manche Essenplane unterscheiden sich in ihrer Struktur
                if len(split_essen[5]) <= 2:
                    essen_dict[split_essen[1]] = [split_essen[3], split_essen[4][1: len(split_essen[4]) + 1]]
                else:
                    essen_dict[split_essen[1]] = [split_essen[3], split_essen[5][2: len(split_essen[5]) + 1]]
            except:
                # [mensaSpezial] ohne bisher zu erkennendes Format
                continue

        return essen_dict


    '''
    Lese den Wochentag und das Datum aus.

    param tag: HTML [speiseplanTag] - Sektion
    return:    String in [<Tag> <Datum>] Format
    '''
    def __get_Tag(self, tag):
        return tag.split("<")[2].split(">")[1]


    '''
        Gib den Speiseplan aus.
        Sollte kein Plan erstellt worden sein, wir ein leeres
        Dictionary zurueckgegeben.

        param self: Verweis auf eigene Klasse, wordurch diese mit
                    [Mensaplan-Objekt].get_speiseplan() aufgerufen werden.
        return:     Privates Dictionary, welches den Mensaplan enthaelt
    '''
    def get_speiseplan(self):
        return self.__speiseplan

# Starte diese Datei als Main-File
if __name__ == "__main__":
    mensaplan = Mensaplan()
    mensaplan.erstelle_speiseplan()
    speiseplan = mensaplan.get_speiseplan()

    sprache = input("Ausgabe auf englisch? / Output in english? ") in ["y", "yes", "j", "ja"]

    for tag, essen in speiseplan.items():
        ausgabe = [ "Am " + tag + " gibt es folgendes zur Auswahl: ", \
                    "There is the following to eat on " + tag + ": " ] 
        print(ausgabe[sprache])
        for name, inhalt in essen.items():
            print(name + ": ", end="")
            print(inhalt[sprache])
        print()


