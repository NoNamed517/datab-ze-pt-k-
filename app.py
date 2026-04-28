from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)
DB_NAME = "ptaci.db"

ALLOWED_SORT_COLUMNS = {
    "nazev", "vedecky_nazev", "rad", "celed",
    "delka_cm", "rozpeti_cm", "hmotnost_g",
    "status_ohrozeni", "typ_potravy", "migrace",
    "vyskyt_kontinent", "snuska_ks",
}


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def build_query(params):
    conditions = []
    values = []

    if params.get("rad"):
        conditions.append("rad = ?")
        values.append(params["rad"])

    if params.get("typ_potravy"):
        conditions.append("typ_potravy = ?")
        values.append(params["typ_potravy"])

    if params.get("kontinent"):
        conditions.append("vyskyt_kontinent = ?")
        values.append(params["kontinent"])

    if params.get("migrace"):
        conditions.append("migrace = ?")
        values.append(params["migrace"])

    if params.get("status"):
        conditions.append("status_ohrozeni = ?")
        values.append(params["status"])

    if params.get("hmotnost_min"):
        conditions.append("hmotnost_g >= ?")
        values.append(params["hmotnost_min"])

    if params.get("hmotnost_max"):
        conditions.append("hmotnost_g <= ?")
        values.append(params["hmotnost_max"])

    where = ""
    if conditions:
        where = "WHERE " + " AND ".join(conditions)

    return where, values


def get_filter_options(conn):
    cursor = conn.cursor()

    def get_values(column):
        cursor.execute(f"SELECT DISTINCT {column} FROM ptaci ORDER BY {column}")
        return [row[0] for row in cursor.fetchall()]

    return {
        "rad": get_values("rad"),
        "typ_potravy": get_values("typ_potravy"),
        "kontinent": get_values("vyskyt_kontinent"),
        "status": get_values("status_ohrozeni"),
    }


@app.route("/")
def dashboard():
    conn = get_db()
    cursor = conn.cursor()

    params = request.args.to_dict()

    where, values = build_query(params)

    # řazení
    razeni = params.get("razeni", "nazev")
    smer = params.get("smer", "ASC")

    if razeni not in ALLOWED_SORT_COLUMNS:
        razeni = "nazev"

    if smer not in ["ASC", "DESC"]:
        smer = "ASC"

    # data
    cursor.execute(f"SELECT * FROM ptaci {where} ORDER BY {razeni} {smer}", values)
    ptaci = cursor.fetchall()

    # statistiky
    cursor.execute(f"""
        SELECT
            COUNT(*) as pocet,
            ROUND(AVG(delka_cm), 1) as prum_delka,
            MAX(hmotnost_g) as max_hmotnost,
            ROUND(AVG(hmotnost_g), 1) as prum_hmotnost
        FROM ptaci {where}
    """, values)
    stats = cursor.fetchone()

    # grafy
    def fetch_chart(query):
        cursor.execute(query.format(where=where), values)
        rows = cursor.fetchall()
        return [r[0] for r in rows], [r[1] for r in rows]

    graf_rad_labels, graf_rad_data = fetch_chart(
        "SELECT rad, COUNT(*) FROM ptaci {where} GROUP BY rad"
    )

    graf_migrace_labels, graf_migrace_data = fetch_chart(
        "SELECT migrace, COUNT(*) FROM ptaci {where} GROUP BY migrace"
    )
    graf_migrace_labels = ["Netažní" if x == 0 else "Tažní" for x in graf_migrace_labels]

    graf_potrava_labels, graf_potrava_data = fetch_chart(
        "SELECT typ_potravy, ROUND(AVG(hmotnost_g),0) FROM ptaci {where} GROUP BY typ_potravy"
    )

    graf_kontinent_labels, graf_kontinent_data = fetch_chart(
        "SELECT vyskyt_kontinent, COUNT(*) FROM ptaci {where} GROUP BY vyskyt_kontinent"
    )

    filter_options = get_filter_options(conn)
    conn.close()

    return render_template(
        "dashboard.html",
        ptaci=ptaci,
        stats=stats,
        params=params,
        filter_options=filter_options,
        graf_rad_labels=graf_rad_labels,
        graf_rad_data=graf_rad_data,
        graf_migrace_labels=graf_migrace_labels,
        graf_migrace_data=graf_migrace_data,
        graf_potrava_labels=graf_potrava_labels,
        graf_potrava_data=graf_potrava_data,
        graf_kontinent_labels=graf_kontinent_labels,
        graf_kontinent_data=graf_kontinent_data,
    )


if __name__ == "__main__":
    app.run(debug=True)