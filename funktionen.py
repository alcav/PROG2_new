import json
from datetime import datetime, timedelta

# datetime = Das datetime-Modul bietet diverse Klassen, Methoden und Funktionen für die Arbeit mit Daten, Zeiten und Zeit-Intervallen
# timedelta = Die timedelta-Klasse wird verwendet zur Differenzbildung zwischen zwei Zeit- oder Datums-Objekten (Quelle: https://www.python-kurs.eu/python3_time_and_date.php)


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
    # Zeiterfassung.json wird im Schreibmodus geöffnet, d.h. überschrieben
    with open("zeiterfassung.json", "w") as open_file:
        # Json.dump() wandelt Python-Dictionarys bzw. Listen in Text in der JSON-Struktur um
        json.dump(zeiterfassung, open_file)


# Eine neue Eingabe wird gespeichert. Die Variablen aus main.py werden übernommen
def neue_eingabe_speichern(datum, kategorie, startzeit, endzeit, pause):
    # Die bereits erfassten Zeiten werden geladen (siehe Funktion oben)
    zeiterfassung = erfasste_zeit_laden()
    # Der Zeitstempel wird generiert (Std:Min:Sek)
    now = datetime.now()
    # Strftime wandelt den datetime object in einen string um
    current_time = now.strftime("%H:%M:%S")
    # Durch die Erweiterung des Datums mit der aktuellen Zeit wird sichergestellt, dass der spätere Key einzigartig ist
    datum = datum + ", " + current_time
    # Strptime wandelt den string in einen datetime object um
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
        # Ein neuer Eintrag wird im Dict abgespeichert. Die Gesamtzeit wird in einen string umgewandelt.
        zeiterfassung[datum] = kategorie, str(gesamtzeit)
        # Der Dict wird im json abgespeichert (siehe Funktion oben)
        zeiterfassung_abspeichern(zeiterfassung)
        # Eine Bestätigung wird ausgegeben (siehe main.py -> speichern)
        return True


# Die Zeitsummen aller Kategorien werden berechnet und in einem neuen Dict abgespeichert
def zeiten_zusammenzaehlen(kategorien):
    # Die bereits erfassten Zeiten werden geladen (siehe Funktion oben)
    zeiterfassung = erfasste_zeit_laden()
    # Ein leeres Dict wird erstellt
    kategorien_mit_zeit = {}

    for kategorie in kategorien:
        # Die Summe wird auf 0 gesetzt
        summe = timedelta(0)
        for key, value in zeiterfassung.items():
            # Wenn die Kategorie im Dict zeiterfassung vorhanden ist
            if kategorie in value:
                # Value[1] = Zeit
                einzelne_zeit = value[1]
                # Umwandlung des Strings nach datetime
                einzelne_zeit_obj = datetime.strptime(einzelne_zeit, '%H:%M:%S')
                # Umwandlung von datetime nach timedelta (damit Zeiten zusammengerechnet werden können)
                einzelne_zeit = timedelta(hours=einzelne_zeit_obj.hour, minutes=einzelne_zeit_obj.minute,
                                          seconds=einzelne_zeit_obj.second)
                # Die einzelne_zeit wird zur Summe addiert
                summe += einzelne_zeit
                # Wenn die Kategorie bereits im Dict kategorien_mit_zeit vorhanden ist...
                if kategorie in kategorien_mit_zeit:
                    # ... wird der Eintrag geöffnet ...
                    bisherige_zeit = kategorien_mit_zeit[kategorie]
                    # und aktualisiert (bisherige Zeit + neue Zeit in Sekunden)
                    kategorien_mit_zeit[kategorie] = summe.seconds + bisherige_zeit
                # Wenn die Kategorie noch nicht im Dict kategorien_mit_zeit ist ...
                else:
                    # ... werden die Kategorie als Key und die Anzahl Sekunden als Value in Dict gespeichert
                    kategorien_mit_zeit[kategorie] = summe.seconds
                # Die Summe wird wieder auf 0 gesetzt und die Schleife beginnt von vorne
                summe = timedelta(0)

    # Die Variablen für die grafische Darstellung werden erstellt (siehe main.py -> grafik) ...
    labels = list(kategorien_mit_zeit.keys())
    values = list(kategorien_mit_zeit.values())
    # ... und an main.py weitergegeben
    return labels, values


# Die Einträge zur gefilterten Kategorie werden in einem neuen Dict gespeichert und ausgegeben
def zeiterfassung_filtern(gefilterte_kategorie):
    # Die bereits erfassten Zeiten werden geladen (siehe Funktion oben)
    zeiterfassung = erfasste_zeit_laden()
    # Ein leeres Dict wird erstellt
    gefilterte_kategorie_dict = {}

    for key, value in zeiterfassung.items():
        # Wenn bereits Zeiten in der gefilterten Kategorie erfasst wurden
        if gefilterte_kategorie in value:
            # Der/die entsprechenden Einträge werden im neuen Dict abgespeichert
            gefilterte_kategorie_dict[key] = value
        # Wenn Filter = Alle ist
        elif gefilterte_kategorie == "Alle":
            # Alle Einträge werden im neuen Dict abgespeichert
            gefilterte_kategorie_dict = zeiterfassung
    return gefilterte_kategorie_dict


# Die Summe der gefilterten Kategorie wird berechnet
def summe_berechnen(gefilterte_kategorie_dict):
    summe = timedelta(0)
    for key, value in gefilterte_kategorie_dict.items():
        # Value[1] = Zeit
        einzelne_zeit = value[1]
        # Umwandlung des Strings nach datetime
        einzelne_zeit_obj = datetime.strptime(einzelne_zeit, '%H:%M:%S')
        # Umwandlung von datetime nach timedelta (damit Zeiten zusammengerechnet werden können)
        einzelne_zeit = timedelta(hours=einzelne_zeit_obj.hour, minutes=einzelne_zeit_obj.minute,
                                  seconds=einzelne_zeit_obj.second)
        # Die einzelne_zeit wird zur Summe addiert
        summe += einzelne_zeit
    return summe
