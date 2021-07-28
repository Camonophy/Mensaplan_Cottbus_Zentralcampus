import urllib.request, urllib.error, urllib.parse
import datetime

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
        Entferne alle HTML spezifischen Tags, wie <h1><\h1>.

        param text:  Verweis auf eigene Klasse
        param text:  Text mit zu entfernden Tags
        return:      Text, in dem Tags durch [+++] ersetzt wurden
    '''
    def __entferne_Tags(self, text):
        start = end = 0
        text_len = len(text)

        try:
            while start < text_len:
                if text[start] == '<':
                    end = start + 1
                    while end < text_len:
                        if text[end] == '>':
                            text = text.replace(text[start: end + 1], "+++")
                            break
                        end += 1
                start += 1
        except:
            pass

        return text

    
    '''
        Ersetze die Kommas im Text, da diese nur zum trennen
        der Essen vorbehalten sind.

        param self:         Verweis auf eigene Klasse
        param essens_liste  Liste an HTML-Eintraegen
        return:             Gefilterte HTML-Eintraegen als String 
    '''
    def __ersetze_Kommas(self, essens_liste):
        neue_essensliste = ""

        for essen in essens_liste:
            neue_essensliste += str(essen).replace(","," | ") + ","
        return neue_essensliste


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

            # Filter Eintraege, welche keine Bedeutung haben, raus
            split_essen = [ eintrag for eintrag in split_essen if len(eintrag) > 3 ]
            
            try:
                essen_dict[split_essen[0]] = [split_essen[1], 
                                              split_essen[2].replace("\r", "")[1: len(split_essen[2]) + 1]]
            except:
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
        Liefert das Datum des heutigen tages zurück.

        return: "[Wochentag] [Tag].[Monat]" 
    '''
    def __get_tag_heute(self):
        heute = datetime.datetime.now()
        heute = datetime.datetime.strftime(heute, '%d.%m')
        tage  = self.__speiseplan.keys()
        try:
            return [ tag for tag in tage if tag[len(tag)-6: len(tag)-1] == heute ][0]
        except:
            return  []


    '''
        Erstelle einen Mensaplan, basierend auf der definierten URL im Konstruktor

        param self: Verweis auf eigene Klasse, kann mit 
                    [Mensaplan-Objekt].erstelle_speiseplan() 
                    aufgerufen werden.
    '''
    def erstelle_speiseplan(self):
        response   = urllib.request.urlopen(self.__URL)
        webContent = response.read()
        fullPage   = BeautifulSoup(webContent , 'html.parser')
        tagesMenus = fullPage.findAll(class_="essenAll")

        for menu in tagesMenus:
            essen_string = self.__ersetze_Kommas(menu.findAll(class_="essen"))
            essen_string = self.__entferne_Tags(essen_string).split(',')
            tag          = self.__get_Tag(str(menu.find(class_="speiseplanTag")))
            gerichte     = self.__get_Essen(essen_string)

            self.__speiseplan[tag] = gerichte

    
    '''
        Gib den Speiseplan aus.
        Sollte kein Plan erstellt worden sein, wird ein leeres
        Dictionary zurueckgegeben.

        param self:  Verweis auf eigene Klasse, wordurch diese mit
                     [Mensaplan-Objekt].get_speiseplan() aufgerufen werden.
        param heute: Nur die Liste des Speisen des heutigen Tages
        return:      Privates Dictionary, welches den Mensaplan enthaelt
    '''
    def get_speiseplan(self, heute=1):
        try:
            return self.__speiseplan[self.__get_tag_heute()] if heute else self.__speiseplan 
        except:
            return 0

    
    '''
        Gib den Speiseplan aus in einem lesbaren Format aus.

        param self:    Verweis auf eigene Klasse, wordurch diese mit
                       [Mensaplan-Objekt].print_speiseplan() aufgerufen werden.
        param sprache: 0 = Deutsch ; 1 = Englisch
        param heute:   Nur das Essen des heutigen tages anzeigen
    '''
    def print_speiseplan(self, sprache=0, heute=0):
        if heute:
            tag = self.__get_tag_heute()
            try:
                plan = self.__speiseplan[tag]
                ausgabe = [ "Am " + tag + " gibt es folgendes zur Auswahl: ", \
                            "There is the following to eat on " + tag + ": " ]
                print(ausgabe[sprache])
                for name, inhalt in plan.items():
                    print(name + ": ", end="")
                    print(inhalt[sprache])
                print()
            except:
                print("Heute gibt es leider nichts zur Auswahl.")
        else:
            for tag, essen in self.__speiseplan.items():
                ausgabe = [ "Am " + tag + " gibt es folgendes zur Auswahl: ", \
                            "There is the following to eat on " + tag + ": " ] 
                print(ausgabe[sprache])
                for name, inhalt in essen.items():
                    print(name + ": ", end="")
                    print(inhalt[sprache])
                print()


# Starte diese Datei als Main-File
if __name__ == "__main__":
    mensaplan = Mensaplan()
    mensaplan.erstelle_speiseplan()
    
    sprache = input("Ausgabe auf englisch? / Output in english? ") in ["y", "yes", "j", "ja"]
    heute = input("Nur das Essen von heute? / Just today's food list? ") in ["y", "yes", "j", "ja"]
    print()

    mensaplan.print_speiseplan(sprache, heute)

