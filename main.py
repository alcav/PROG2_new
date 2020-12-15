from flask import Flask, render_template, request, flash
import funktionen
import plotly
import plotly.graph_objects as go
from datetime import datetime, timedelta


app = Flask("TimeTool")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' # Wird für flash benötigt

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
    if request.method == 'POST':  # Wenn User etwas im Formular (siehe index.html) eingibt
        datum = request.form['datum']  # Eingaben werden zu Variablen
        kategorie = request.form['kategorie']
        startzeit = request.form['startzeit']
        endzeit = request.form['endzeit']
        pause = request.form['pause']
        erfolgreich = funktionen.neue_eingabe_speichern(datum, kategorie, startzeit, endzeit, pause)  # Funktion gibt erfolgreich zurück
        if erfolgreich:   # erfolgreich ist True oder False
            flash('Ihre Eingabe wurde gespeichert.')
        else:
            flash('Ihre Eingabe konnte nicht gespeichert werden, da die Zeitsumme kleiner als 0 ist.')
    return render_template('index.html', kategorien=kategorien_farben.keys())


@app.route('/uebersicht', methods=['GET', 'POST'])
@app.route('/uebersicht/<key>', methods=['GET', 'POST'])
def uebersicht():
    zeiterfassung = funktionen.erfasste_zeit_laden()

    if request.method == 'POST':  # Wenn der User eine spezifische Kategorie im Filter gewählt hat
        gefilterte_kategorie = request.form['gefilterte_kategorie']
        gefilterte_zeit = funktionen.zeiterfassung_filtern(gefilterte_kategorie)
        summe = timedelta(0)
        for key, value in gefilterte_zeit.items():
            einzelne_zeit = value[1]  # Value[1] = zugehörige Zeit
            einzelne_zeit_obj = datetime.strptime(einzelne_zeit, '%H:%M:%S')  # Umwandlung des Strings nach datetime
            einzelne_zeit = timedelta(hours=einzelne_zeit_obj.hour, minutes=einzelne_zeit_obj.minute,
                                      seconds=einzelne_zeit_obj.second)  # Umwandlung von datetime nach timedelta (damit Zeiten zusammengerechnet werden können)
            summe += einzelne_zeit  # Die einzelne_zeit wird aktualisiert
        return render_template('uebersicht.html',
                           zeiterfassung=gefilterte_zeit,
                           farben=kategorien_farben,
                           kategorien=kategorien_farben.keys(),
                           gefilterte_kategorie=gefilterte_kategorie,
                           summe=summe)

    else:  # Wenn nichts gefiltert wurde
        summe = timedelta(0)
        for key, value in zeiterfassung.items():
            einzelne_zeit = value[1]  # Value[1] = zugehörige Zeit
            einzelne_zeit_obj = datetime.strptime(einzelne_zeit, '%H:%M:%S')  # Umwandlung des Strings nach datetime
            einzelne_zeit = timedelta(hours=einzelne_zeit_obj.hour, minutes=einzelne_zeit_obj.minute,
                                      seconds=einzelne_zeit_obj.second)  # Umwandlung von datetime nach timedelta (damit Zeiten zusammengerechnet werden können)
            summe += einzelne_zeit  # Die einzelne_zeit wird aktualisiert
        return render_template('uebersicht.html',
                           zeiterfassung=zeiterfassung,
                           farben=kategorien_farben,
                           kategorien=kategorien_farben.keys(),
                           summe=summe)


@app.route('/loeschen')
@app.route('/loeschen/<key>')
def loeschen(key=False):  # Default, wenn Key nicht vorhanden
    if key:
        zeiterfassung = funktionen.erfasste_zeit_laden()  # Die .json Einträge werden als Dict geladen
        del zeiterfassung[key]  # Der entsprechende Eintrag wird aus dem Dict gelöscht
        funktionen.zeiterfassung_abspeichern(zeiterfassung)  # Der Dict wird in .json abgespeichert
        return render_template('uebersicht.html',
                               zeiterfassung=zeiterfassung,
                               farben=kategorien_farben,
                               kategorien=kategorien_farben.keys())
    else:
        return render_template('uebersicht.html')


@app.route('/aendern', methods=['GET', 'POST'])
@app.route('/aendern/<key>', methods=['GET', 'POST'])
def aendern(key=False):  # Default, wenn Key nicht vorhanden
    if key:
        if request.method == 'POST':  # Wenn User etwas in Formular (siehe aenderbare_uebersicht.html) eingibt
            zeiterfassung = funktionen.erfasste_zeit_laden()
            neue_kategorie = request.form['neue_kategorie']  # Eingaben werden zu Variablen
            neue_zeit = request.form['neue_zeit']
            zeiterfassung[key] = str(neue_kategorie), str(neue_zeit)  # Der Eintrag im Dictionary wird aktualisiert
            funktionen.zeiterfassung_abspeichern(zeiterfassung)
            return render_template('uebersicht.html',
                                   zeiterfassung=zeiterfassung,
                                   farben=kategorien_farben,
                                   kategorien=kategorien_farben.keys())
        else:  # Wenn Formular noch nicht ausgefüllt wurde, also request.method nicht gleich POST
            zeiterfassung = funktionen.erfasste_zeit_laden()
            aenderbare_kategorie = zeiterfassung[key]  # Die Werte zum angewählten Schlüssel werden zur Variablen anderbare_kategorie
            return render_template('aenderbare_uebersicht.html',
                                   zeiterfassung=zeiterfassung,
                                   aenderbare_kategorie=aenderbare_kategorie,  # Diese Variable wird an das .html Format weitergegeben
                                   farben=kategorien_farben,
                                   key = key,
                                   kategorien=kategorien_farben.keys())
    else:
        return render_template('uebersicht.html')


@app.route('/grafik')
def grafik():
    labels, values = funktionen.zeiten_zusammenzaehlen()
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    div = plotly.io.to_html(fig, include_plotlyjs=True, full_html=False)
    return render_template('grafik.html', plotly_div=div)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
