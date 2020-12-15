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
        # Erfolgreich ist True oder False
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
    zeiterfassung = funktionen.erfasste_zeit_laden()

    # Wenn der User eine spezifische Kategorie im Filter gewählt hat
    if request.method == 'POST':
        gefilterte_kategorie = request.form['gefilterte_kategorie']
        gefilterte_zeit = funktionen.zeiterfassung_filtern(gefilterte_kategorie)
        summe = funktionen.summe_berechnen(gefilterte_zeit)
        return render_template('uebersicht.html',
                           zeiterfassung=gefilterte_zeit,
                           farben=kategorien_farben,
                           kategorien=kategorien_farben.keys(),
                           gefilterte_kategorie=gefilterte_kategorie,
                           summe=summe)

    # Wenn nichts gefiltert wurde
    else:
        summe = funktionen.summe_berechnen(zeiterfassung)
        return render_template('uebersicht.html',
                           zeiterfassung=zeiterfassung,
                           farben=kategorien_farben,
                           kategorien=kategorien_farben.keys(),
                           summe=summe)


@app.route('/loeschen', methods=['GET', 'POST'])
@app.route('/loeschen/<key>', methods=['GET', 'POST'])
# Default, wenn Key nicht vorhanden
def loeschen(key=False):
    if key:
        # Die .json Einträge werden als Dict geladen
        zeiterfassung = funktionen.erfasste_zeit_laden()
        # Der entsprechende Eintrag wird aus dem Dict gelöscht
        del zeiterfassung[key]
        # Der Dict wird in .json abgespeichert
        funktionen.zeiterfassung_abspeichern(zeiterfassung)
        summe = funktionen.summe_berechnen(zeiterfassung)
        return render_template('uebersicht.html',
                               zeiterfassung=zeiterfassung,
                               farben=kategorien_farben,
                               kategorien=kategorien_farben.keys(),
                               summe=summe)
    else:
        return render_template('uebersicht.html')


@app.route('/aendern', methods=['GET', 'POST'])
@app.route('/aendern/<key>', methods=['GET', 'POST'])
# Default, wenn Key nicht vorhanden
def aendern(key=False):
    if key:
        # Wenn User etwas in Formular (siehe aenderbare_uebersicht.html) eingibt
        if request.method == 'POST':
            zeiterfassung = funktionen.erfasste_zeit_laden()
            # Eingaben werden zu Variablen
            neue_kategorie = request.form['neue_kategorie']
            neue_zeit = request.form['neue_zeit']
            # Der Eintrag im Dictionary wird aktualisiert und abgespeichert
            zeiterfassung[key] = str(neue_kategorie), str(neue_zeit)
            funktionen.zeiterfassung_abspeichern(zeiterfassung)
            summe = funktionen.summe_berechnen(zeiterfassung)
            return render_template('uebersicht.html',
                                   zeiterfassung=zeiterfassung,
                                   farben=kategorien_farben,
                                   kategorien=kategorien_farben.keys(),
                                   summe=summe)

        # Wenn Formular noch nicht ausgefüllt wurde, also request.method nicht gleich POST
        else:
            zeiterfassung = funktionen.erfasste_zeit_laden()
            # Die Werte zum angewählten Schlüssel werden zur Variablen anderbare_kategorie
            aenderbare_kategorie = zeiterfassung[key]
            summe = funktionen.summe_berechnen(zeiterfassung)
            return render_template('aenderbare_uebersicht.html',
                                   zeiterfassung=zeiterfassung,
                                   aenderbare_kategorie=aenderbare_kategorie,
                                   farben=kategorien_farben,
                                   key = key,
                                   kategorien=kategorien_farben.keys(),
                                   summe=summe)
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
