from flask import Flask, render_template, request, flash
import funktionen
import plotly
import plotly.graph_objects as go

app = Flask("TimeTool")

# Wird für Flash benötigt
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

kategorien_farben = {
    "Isolation": "#F5F6CE",
    "Wandtäferung": "#CEF6E3",
    "Fenster": "#CEECF5",
    "Möbelbau": "#F6CEF5",
    "Küche": "#F6CED8",
    "Sonstiges": "#F6D8CE"
}


@app.route('/', methods=['GET', 'POST'])
def speichern():
    # Wenn User etwas im Formular (siehe index.html) eingibt
    if request.method == 'POST':
        # Eingaben werden zu Variablen
        datum = request.form['datum']
        kategorie = request.form['kategorie']
        startzeit = request.form['startzeit']
        endzeit = request.form['endzeit']
        pause = request.form['pause']
        # Funktion gibt erfolgreich zurück
        erfolgreich = funktionen.neue_eingabe_speichern(datum, kategorie, startzeit, endzeit, pause)
        # Erfolgreich ist True oder False. False ist es, wenn die Zeitsumme kleiner als 0 ist.
        # Wenn erfolgreich wird eine Bestätigung ausgegeben
        if erfolgreich:
            flash('Ihre Eingabe wurde gespeichert.')
        # Wenn nicht erfolgreich wird eine entsprechende Meldung ausgegeben
        else:
            flash('Ihre Eingabe konnte nicht gespeichert werden, da die Zeitsumme kleiner als 0 ist.')
    return render_template('index.html', kategorien=kategorien_farben.keys())


@app.route('/uebersicht', methods=['GET', 'POST'])
@app.route('/uebersicht/<key>', methods=['GET', 'POST'])
def uebersicht():
    # Die .json Einträge werden als Dict geladen
    zeiterfassung = funktionen.erfasste_zeit_laden()
    # Wenn der User eine spezifische Kategorie im Filter gewählt hat
    if request.method == 'POST':
        # Eingabe wird zur Variable
        gefilterte_kategorie = request.form['gefilterte_kategorie']
        # Die Einträge der gewählten Kategorie werden in einem neuen Dict abgespeichert und die Zeiten zusammengezählt
        gefilterte_kategorie_dict = funktionen.zeiterfassung_filtern(gefilterte_kategorie)
        summe = funktionen.summe_berechnen(gefilterte_kategorie_dict)
        return render_template('uebersicht.html',
                           # Der Dict mit der gefilterten Kategorie wird als zeiterfassung an übersicht.html weitergegeben
                           zeiterfassung=gefilterte_kategorie_dict,
                           gefilterte_kategorie=gefilterte_kategorie,
                           farben=kategorien_farben,
                           kategorien=kategorien_farben.keys(),
                           # Die Summe ist die Summe der gefilterten Kategorie
                           summe=summe)
    # Wenn nichts gefiltert wurde
    else:
        # Die Zeiten werden zusammengezählt
        summe = funktionen.summe_berechnen(zeiterfassung)
        return render_template('uebersicht.html',
                           # Alle erfassten Kategorien und Zeiten werden an übersicht.html weitergegeben
                           zeiterfassung=zeiterfassung,
                           farben=kategorien_farben,
                           kategorien=kategorien_farben.keys(),
                           # Die Summe ist die Summe aller erfassten Zeiten
                           summe=summe)


@app.route('/loeschen', methods=['GET', 'POST'])
@app.route('/loeschen/<key>', methods=['GET', 'POST'])
# Default, wenn Key nicht vorhanden
def loeschen(key=False):
    if key:
        # Wenn ein Key in der URL vorhanden ist, hat der User auf Löschen geklickt
        # Die .json Einträge werden als Dict geladen
        zeiterfassung = funktionen.erfasste_zeit_laden()
        # Der gewählte Eintrag wird aus dem Dict gelöscht
        del zeiterfassung[key]
        # Der Dict wird in .json abgespeichert
        funktionen.zeiterfassung_abspeichern(zeiterfassung)
        # Die neue Zeitsumme wird berechnet
        summe = funktionen.summe_berechnen(zeiterfassung)
        return render_template('uebersicht.html',
                               zeiterfassung=zeiterfassung,
                               farben=kategorien_farben,
                               kategorien=kategorien_farben.keys(),
                               summe=summe)
    # In diesem Fall wurde nicht auf Löschen geklickt
    else:
        return render_template('uebersicht.html')


@app.route('/aendern', methods=['GET', 'POST'])
@app.route('/aendern/<key>', methods=['GET', 'POST'])
# Default, wenn Key nicht vorhanden
def aendern(key=False):
    # Wenn ein Key in der URL vorhanden ist, hat der User auf Ändern geklickt
    if key:
        # Wenn User etwas in Formular (siehe aenderbare_uebersicht.html) eingegeben hat, d.h. eine neue Kategorie und/oder Zeit gewählt hat und gespeichert hat
        if request.method == 'POST':
            # Die .json Einträge werden als Dict geladen
            zeiterfassung = funktionen.erfasste_zeit_laden()
            # Eingaben werden zu Variablen
            neue_kategorie = request.form['neue_kategorie']
            neue_zeit = request.form['neue_zeit']
            # Der Eintrag im Dictionary wird aktualisiert und abgespeichert
            zeiterfassung[key] = str(neue_kategorie), str(neue_zeit)
            funktionen.zeiterfassung_abspeichern(zeiterfassung)
            # Die neue Zeitsumme wird berechnet
            summe = funktionen.summe_berechnen(zeiterfassung)
            # Die aktualisierte Übersicht wird ausgegeben
            return render_template('uebersicht.html',
                                   zeiterfassung=zeiterfassung,
                                   farben=kategorien_farben,
                                   kategorien=kategorien_farben.keys(),
                                   summe=summe)
        # Wenn der User auf Ändern geklickt hat, die Eingaben jedoch noch nicht gespeichert hat, also request.method nicht gleich POST
        else:
            # Die .json Einträge werden als Dict geladen
            zeiterfassung = funktionen.erfasste_zeit_laden()
            # Die Values (Kategorie + Zeit) zum angewählten Key (Datum + Erfassungszeit) werden zur Variablen anderbare_kategorie
            aenderbare_kategorie = zeiterfassung[key]
            # Die änderbare Übersicht wird ausgegeben
            return render_template('aenderbare_uebersicht.html',
                                   zeiterfassung=zeiterfassung,
                                   aenderbare_kategorie=aenderbare_kategorie,
                                   farben=kategorien_farben,
                                   key=key,
                                   kategorien=kategorien_farben.keys())
    else:
        return render_template('uebersicht.html')


@app.route('/grafik')
def grafik():
    kategorien = kategorien_farben.keys()
    # Die für die Grafik benötigten Daten werden ausgerechnet/zusammengezählt
    labels, values = funktionen.zeiten_zusammenzaehlen(kategorien)
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    div = plotly.io.to_html(fig, include_plotlyjs=True, full_html=False)
    return render_template('grafik.html', plotly_div=div)


# Wenn die Datei ausgeführt wird, soll Debugging eingeschalten werden und die App soll auf dem Rechner Port 5000 laufen
if __name__ == "__main__":
    app.run(debug=True, port=5000)
