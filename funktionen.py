import json
from datetime import datetime, timedelta

# datetime = Kombination aus Datum und Zeit
# timedelta = Dauer der Differenz zwischen zwei Daten, Zeiten oder Datetime Objekten


# Die .json Datei wird geöffnet (read) oder neu erstellt
def erfasste_zeit_laden():
    # Wenn die Datei "zeiterfassung.json" vorhanden ist, wird sie geöffnet
    try:
        with open("zeiterfassung.json", "r") as open_file:
            # Json.load wandelt den Text in der JSON-Struktur in Python-Dictionarys bzw. Listen um
            zeiterfassung = json.load(open_file)
    # Fehlermeldung wenn noch keine Datei "zeiterfassung.json" vorhanden ist
    except FileNotFoundError:
        print("Es sind noch keine Zeiten erfasst.")
        # Neues, leeres Dict wird erstellt
        zeiterfassung = {}
    # Fehlermeldung wenn .json Datei ungültig sein sollte
    except json.decoder.JSONDecodeError:
        print("Die Datei scheint leer oder ungültig zu sein.")
        # Neues, leeres Dict wird erstellt
        zeiterfassung = {}
    return zeiterfassung


# Die Daten werden neu abgespeichert
def zeiterfassung_abspeichern(zeiterfassung):
    # "Zeiterfassung.json" wird im Schreibmodus geöffnet, d.h. überschrieben
    with open("zeiterfassung.json", "w") as open_file:
        # Json.dump() wandelt Python-Dictionarys bzw. Listen in Text in der JSON-Struktur um
        json.dump(zeiterfassung, open_file)


# Die Variablen aus main.py werden übernommen
def neue_eingabe_speichern(datum, kategorie, startzeit, endzeit, pause):
    # Die bereits erfassten Zeiten werden geladen (siehe Funktion oben)
    zeiterfassung = erfasste_zeit_laden()

    now = datetime.now()
    # Strftime wandelt datetime object in string um
    current_time = now.strftime("%H:%M:%S")
    # Durch die Erweiterung mit der aktuellen Zeit wird sichergestellt, dass der spätere Key einzigartig ist
    datum = datum + ", " + current_time
    # Strptime wandelt string in datetime object um
    startzeit_obj = datetime.strptime(startzeit, '%H:%M')
    endzeit_obj = datetime.strptime(endzeit, '%H:%M')
    # Die Pause wird in Minuten umgewandelt
    pause = timedelta(minutes=int(pause))
    # Die Gesamtzeit wird berechnet
    gesamtzeit = endzeit_obj - startzeit_obj - pause
    # Wenn die Gesamtzeit kleiner als 0 ist, wird eine Fehlermeldung ausgegeben (siehe main.py -> speichern)
    if gesamtzeit < timedelta(0):
        return False
    else:
        # Ein neuer Eintrag wird im Dict abgespeichert
        zeiterfassung[datum] = kategorie, str(gesamtzeit)
        # Der Dict wird im json abgespeichert (siehe Funktion oben)
        zeiterfassung_abspeichern(zeiterfassung)
        # Eine Bestätigung wird ausgegeben (siehe main.py)
        return True


def zeiten_zusammenzaehlen():
    # Die bereits erfassten Zeiten werden geladen (siehe Funktion oben)
    zeiterfassung = erfasste_zeit_laden()

    kategorien = ["Sonstiges", "Isolation", "Wandtäferung", "Fenster", "Möbelbau", "Küche"]
    # Ein leeres Dict wird erstellt
    kategorien_mit_zeit = {}

    for kategorie in kategorien:
        # Die Summe wird auf 0 gesetzt
        summe = timedelta(0)
        for key, value in zeiterfassung.items():
            # Wenn die Kategorie im Dict zeiterfassung vorhanden ist
            if kategorie in value:
                # Value[1] = zugehörige Zeit
                einzelne_zeit = value[1]
                # Umwandlung des Strings nach datetime
                einzelne_zeit_obj = datetime.strptime(einzelne_zeit, '%H:%M:%S')
                # Umwandlung von datetime nach timedelta (damit Zeiten zusammengerechnet werden können)
                einzelne_zeit = timedelta(hours=einzelne_zeit_obj.hour, minutes=einzelne_zeit_obj.minute,
                                          seconds=einzelne_zeit_obj.second)
                # Die einzelne_zeit wird aktualisiert
                summe += einzelne_zeit
                # Wenn die Kategorie bereits im Dict kategorien_mit_zeit vorhanden ist...
                if kategorie in kategorien_mit_zeit:
                    # ... wird der Eintrag geöffnet ...
                    bisherige_zeit = kategorien_mit_zeit[kategorie]
                    # und aktualisiert (bisherige Zeit + neue Zeit in Sekunden)
                    kategorien_mit_zeit[kategorie] = summe.seconds + bisherige_zeit
                else:
                    # Wenn die Kategorie noch nicht im Dict ist: Kategorie wird als Key, Anzahl Sekunden als Value in Dict gespeichert
                    kategorien_mit_zeit[kategorie] = summe.seconds
                # Die Summe wird wieder auf 0 gesetzt und die Schleife beginnt von vorne
                summe = timedelta(0)

    # Variablen für die grafische Darstellung (siehe main.py -> grafik)
    labels = list(kategorien_mit_zeit.keys())
    values = list(kategorien_mit_zeit.values())

    print(kategorien_mit_zeit)

    # Variablen werden an main.py weitergegeben
    return labels, values


def zeiterfassung_filtern(gefilterte_kategorie):
    # Die bereits erfassten Zeiten werden geladen (siehe Funktion oben)
    zeiterfassung = erfasste_zeit_laden()
    # Ein leeres Dict wird erstellt
    gefilterte_zeit = {}

    for key, value in zeiterfassung.items():
        # Wenn bereits Zeiten in der gefilterten Kategorie erfasst werden
        if gefilterte_kategorie in value:
            # Der/die entsprechenden Einträge werden im neuen Dict abgespeichert
            gefilterte_zeit[key] = value
        # Wenn Filter = Alle ist
        elif gefilterte_kategorie == "Alle":
            # Alle Einträge werden im neuen Dict abgespeichert
            gefilterte_zeit = zeiterfassung
    return gefilterte_zeit

"""
def zeiterfassung_filtern(gefilterte_kategorie):
    # Die bereits erfassten Zeiten werden geladen (siehe Funktion oben)
    zeiterfassung = erfasste_zeit_laden()
    # Ein leeres Dict wird erstellt
    dict_gefiltert = {}

    for key, value in zeiterfassung.items():
        # Wenn bereits Zeiten in der gefilterten Kategorie erfasst werden
        if gefilterte_kategorie in value:
            # Der/die entsprechenden Einträge werden im neuen Dict abgespeichert
            dict_gefiltert[key] = value
        # Wenn Filter = Alle ist
        elif gefilterte_kategorie == "Alle":
            # Alle Einträge werden im neuen Dict abgespeichert
            dict_gefiltert = zeiterfassung
    return dict_gefiltert
    """


def summe_berechnen(gefilterte_zeit):
    summe = timedelta(0)
    for key, value in gefilterte_zeit.items():
        # Value[1] = zugehörige Zeit
        einzelne_zeit = value[1]
        # Umwandlung des Strings nach datetime
        einzelne_zeit_obj = datetime.strptime(einzelne_zeit, '%H:%M:%S')
        # Umwandlung von datetime nach timedelta (damit Zeiten zusammengerechnet werden können)
        einzelne_zeit = timedelta(hours=einzelne_zeit_obj.hour, minutes=einzelne_zeit_obj.minute,
                                  seconds=einzelne_zeit_obj.second)
        # Die einzelne_zeit wird aktualisiert
        summe += einzelne_zeit
    # Die Variable wird weitergegeben
    return summe