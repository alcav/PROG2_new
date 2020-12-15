import json
from datetime import datetime, timedelta

# datetime = Kombination aus Datum und Zeit
# timedelta = Dauer der Differenz zwischen zwei Daten, Zeiten oder Datetime Objekten

def erfasste_zeit_laden(): # Die .json Datei wird geöffnet (read) oder neu erstellt
    try:
        with open("zeiterfassung.json", "r") as open_file:  # Wenn die Datei "zeiterfassung.json" vorhanden ist, wird sie geöffnet
            zeiterfassung = json.load(open_file)  # Json.load wandelt den Text in der JSON-Struktur in Python-Dictionarys bzw. Listen um
    except FileNotFoundError:  # Fehlermeldung wenn noch keine Datei "zeiterfassung.json" vorhanden ist
        zeiterfassung = {}  # Neues, leeres Dict wird erstellt
    except json.decoder.JSONDecodeError:  # Fehlermeldung wenn .json Datei ungültig sein sollte
        print("Die Datei scheint leer oder ungültig zu sein.")
        zeiterfassung = {}
    return zeiterfassung  # Der geöffnete Dict heisst zeiterfassung


def zeiterfassung_abspeichern(zeiterfassung): # Die Daten werden neu abgespeichert
    with open("zeiterfassung.json", "w") as open_file:  # "Zeiterfassung.json" wird im Schreibmodus geöffnet, d.h. überschrieben
        json.dump(zeiterfassung, open_file)  # Json.dump() wandelt Python-Dictionarys bzw. Listen in Text in der JSON-Struktur um


def neue_eingabe_speichern(datum, kategorie, startzeit, endzeit, pause):  # Die Variablen aus main.py werden übernommen
    zeiterfassung = erfasste_zeit_laden()  # Die bereits erfassten Zeiten werden geladen (siehe Funktion oben)

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")  # Strftime wandelt datetime object in string um
    datum = datum + ", " + current_time  # Durch die Erweiterung mit der aktuellen Zeit wird sichergestellt, dass der spätere Key einzigartig ist

    startzeit_obj = datetime.strptime(startzeit, '%H:%M') # Strptime wandelt string in datetime object um
    endzeit_obj = datetime.strptime(endzeit, '%H:%M')
    pause = timedelta(minutes=int(pause)) # Die Pause wird in Minuten umgewandelt

    gesamtzeit = endzeit_obj - startzeit_obj - pause

    if gesamtzeit < timedelta(0):
        return False  # Wenn die Gesamtzeit kleiner als 0 ist, wird eine Fehlermeldung ausgegeben (siehe main.py)
    else:
        zeiterfassung[datum] = kategorie, str(gesamtzeit)  # Ein neuer Eintrag wird im Dict abgespeichert
        zeiterfassung_abspeichern(zeiterfassung)  # Der Dict wird im json abgespeichert (siehe Funktion oben)
        return True  # Eine Bestätigung wird ausgegeben (siehe main.py)


def zeiten_zusammenzaehlen():
    zeiterfassung = erfasste_zeit_laden()  # Die bereits erfassten Zeiten werden geladen (siehe Funktion oben)

    kategorien = ["Sonstiges", "Isolation", "Wandtäferung", "Fenster", "Möbelbau", "Küche"]
    kategorien_mit_zeit = {}  # Ein leeres Dict wird erstellt

    for kategorie in kategorien:
        summe = timedelta(0)  # Die Summe wird auf 0 gesetzt
        for key, value in zeiterfassung.items():
            if kategorie in value:  # Wenn die Kategorie im Dict zeiterfassung vorhanden ist
                einzelne_zeit = value[1]  # Value[1] = zugehörige Zeit
                einzelne_zeit_obj = datetime.strptime(einzelne_zeit, '%H:%M:%S')  # Umwandlung des Strings nach datetime
                einzelne_zeit = timedelta(hours=einzelne_zeit_obj.hour, minutes=einzelne_zeit_obj.minute,
                                          seconds=einzelne_zeit_obj.second)  # Umwandlung von datetime nach timedelta (damit Zeiten zusammengerechnet werden können)
                summe += einzelne_zeit  # Die einzelne_zeit wird aktualisiert
                if kategorie in kategorien_mit_zeit:  # Wenn die Kategorie bereits im Dict kategorien_mit_zeit vorhanden ist...
                    bisherige_zeit = kategorien_mit_zeit[kategorie]  # ... wird der Eintrag geöffnet ...
                    kategorien_mit_zeit[kategorie] = summe.seconds + bisherige_zeit  # und aktualisiert (bisherige Zeit + neue Zeit in Sekunden)
                else:
                    kategorien_mit_zeit[kategorie] = summe.seconds  # Wenn die Kategorie noch nicht im Dict ist: Kategorie wird als Key, Anzahl Sekunden als Value in Dict gespeichert
                summe = timedelta(0)  # Die Summe wird wieder auf 0 gesetzt und die Schleife beginnt von vorne

    labels = list(kategorien_mit_zeit.keys())  # Variablen für die grafische Darstellung (siehe main.py)
    values = list(kategorien_mit_zeit.values())

    print(kategorien_mit_zeit)

    return labels, values # Variablen werden an main.py weitergegeben


def zeiterfassung_filtern(gefilterte_kategorie):
    zeiterfassung = erfasste_zeit_laden()  # Die bereits erfassten Zeiten werden geladen (siehe Funktion oben)

    dict_gefiltert = {}  # Ein leeres Dict wird erstellt

    for key, value in zeiterfassung.items():
        if gefilterte_kategorie in value:
            dict_gefiltert[key] = value
        elif gefilterte_kategorie == "Alle":
            dict_gefiltert = zeiterfassung
    return dict_gefiltert


def einzelne_zeit(dict):
    for key, value in gefilterte_zeit.items(dict):
        einzelne_zeit = value[1]  # Value[1] = zugehörige Zeit
        einzelne_zeit_obj = datetime.strptime(einzelne_zeit, '%H:%M:%S')  # Umwandlung des Strings nach datetime
        einzelne_zeit = timedelta(hours=einzelne_zeit_obj.hour, minutes=einzelne_zeit_obj.minute,
                                  seconds=einzelne_zeit_obj.second)  # Umwandlung von datetime nach timedelta (damit Zeiten zusammengerechnet werden können)
        summe += einzelne_zeit  # Die einzelne_zeit wird aktualisiert
        return summe