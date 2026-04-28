import sqlite3

conn = sqlite3.connect("ptaci.db")
cursor = conn.cursor()

# vytvoření tabulky
cursor.execute("""
CREATE TABLE IF NOT EXISTS ptaci (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nazev TEXT,
    vedecky_nazev TEXT,
    rad TEXT,
    celed TEXT,
    delka_cm INTEGER,
    rozpeti_cm INTEGER,
    hmotnost_g INTEGER,
    status_ohrozeni TEXT,
    typ_potravy TEXT,
    migrace INTEGER,
    vyskyt_kontinent TEXT,
    snuska_ks REAL
)
""")

# data (ukázka – můžeš rozšířit)
data = [
    ("Kos černý", "Turdus merula", "Pěvci", "Drozdovití", 25, 38, 100, "Málo dotčený", "všežravec", 1, "Evropa", 4.5),
    ("Vrabec domácí", "Passer domesticus", "Pěvci", "Vrabčovití", 16, 24, 30, "Málo dotčený", "všežravec", 0, "Evropa", 5),
    ("Orel skalní", "Aquila chrysaetos", "Dravci", "Jestřábovití", 85, 220, 4500, "Téměř ohrožený", "masožravec", 0, "Evropa", 2),
    ("Sýkora koňadra", "Parus major", "Pěvci", "Sýkorovití", 14, 22, 20, "Málo dotčený", "hmyzožravec", 1, "Evropa", 8),
]

cursor.executemany("""
INSERT INTO ptaci (
    nazev, vedecky_nazev, rad, celed,
    delka_cm, rozpeti_cm, hmotnost_g,
    status_ohrozeni, typ_potravy, migrace,
    vyskyt_kontinent, snuska_ks
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", data)

conn.commit()
conn.close()

print("Hotovo – databáze vytvořena bez CSV.")