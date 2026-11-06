# LP-Schranke: was Brüche beweisen – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-lp-schranke-demo.streamlit.app/)** -->

Viertes Stück der Konzepte-Reihe **„Packen: Reihenfolge und Platzierungsregel“** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. [Stück 2](https://sebastianhanisch-schranken-beweis-demo.streamlit.app/) fragt, wann FFD (First Fit, größte zuerst) durch die Schranken L1 und L2 bewiesen optimal ist, und trennt bei den offenen Fällen mit dem exakten Optimum; [Stück 3](https://sebastianhanisch-ffd-versagt-demo.streamlit.app/) baut Instanzen, bei denen FFD das Optimum verfehlt. Dieses Stück setzt die stärkere **LP-Schranke** dazu und fragt, was sie über L1 und L2 hinaus beweist.

## Warum dieses Problem

L1 und L2 beweisen FFD in vielen Fällen nicht, obwohl es optimal ist. Die LP-Schranke lässt zu, dass eine Gruppe von Paketen, die in einen Container passt (ein Muster), auch zu einem Bruchteil benutzt wird. Die Demo zeigt an kleinen Beispielen, wie das rechnet, und misst an demselben Raster wie Stück 2, was sie zusätzlich beweist und ob sie das Optimum je verfehlt.

## Modell

Ganzzahlige Paketgrößen s₁ … sₙ mit 1 ≤ sᵢ ≤ C, Container der Kapazität C, alle Pakete vorab bekannt. **Muster:** eine Teilmenge der Pakete mit Summe höchstens C. **LP-Wert:** kleinste Summe der Mustergewichte (Gewichte dürfen Brüche sein), sodass jedes Paket mindestens einmal überdeckt ist (Gilmore und Gomory). Jede Packung ist eine Lösung mit ganzen Gewichten, also gilt L₁ ≤ LP ≤ OPT ≤ FFD und aufgerundet ⌈LP⌉ ≤ OPT. **Ausgänge je Instanz:** *durch L1 bewiesen* (FFD = L₁), *erst durch L2* (FFD = L₂ > L₁), *erst durch LP* (FFD = ⌈LP⌉ über L₂), *LP trifft das Optimum* (⌈LP⌉ = FFD − 1, und eine Packung mit FFD − 1 Containern existiert), *nicht entschieden* (⌈LP⌉ = FFD − 1, ob eine solche Packung existiert, ist offen), *Rundung verletzt* (⌈LP⌉ = FFD − 1, aber keine Packung mit FFD − 1 Containern: das Optimum liegt über dem aufgerundeten LP-Wert) und *LP mehr als 1 unter FFD*. Formeln im Expander 📐 der App.

## Methodik

- **Kern** (`lpb_algorithm.py`): `ffd`, `l1`, `l2`, `optimum` (Teilmengen-DP bis 12 Pakete), `alle_muster` und `lp_loesen` (LP mit allen Mustern, `scipy.optimize.linprog`, bis 14 Pakete; gibt den LP-Wert, eine optimale Lösung zusammengefasst nach den Größen der Pakete und die Dualpreise zurück), `lp_aufgerundet` (Toleranz 1e-6), `ausgang`, `container_pruefen` (unabhängiger Zulässigkeitsprüfer). `ffd`, `l1`, `l2` und `optimum` sind Kopien der Funktionen aus `schranken-beweis-demo` (Stück 2), hier noch einmal gegen die Orakel geprüft.
- **Beispiele** (live): das kleine Beispiel (4, 4, 4, 4, 3) mit Kapazität 10 (LP 2,5) und drei Beispiele aus Stück 2 (zwölf Pakete, Kapazität 100), dazu eine zufällige Instanz mit 6 bis 12 Paketen. Die App zeigt die FFD-Packung und die LP-Lösung als Balken, deren Breite das Gewicht des Musters ist.
- **Raster:** dasselbe wie in Stück 2: drei Größenbereiche (mittlere Teile 10 bis 50 %, große 20 bis 80 %, breite 1 bis 90 % der Kapazität) × drei Paketzahlen (12, 20, 30) × **100 feste Instanzen** je Zelle, Kapazität 1000, **dieselben Seeds**. Vorberechnet in `lpb_precomputed.json` (`generate_precomputed.py`). Den LP-Wert rechnet der Generator bis 12 Pakete mit allen Mustern und darüber per Spaltenerzeugung (`dev/cg.py`: beschränkter Rucksack als Preisproblem); bei FFD = L₁ entfällt er (dann ist ⌈LP⌉ nach L₁ ≤ ⌈LP⌉ ≤ FFD gleich FFD). Ob eine Packung mit FFD − 1 Containern existiert, entscheidet bei 12 Paketen die Teilmengen-DP, bei 20 und 30 ein ganzzahliges Programm (`dev/ilp.py`, **60 Sekunden Zeitlimit** je Instanz).
- **Suche nach Gegenbeispielen zur Rundung:** zufällige Instanzen mit 8, 9, 10 und 11 Paketen (1500, 1500, 1500 und 600; Kapazität 100, Größen 10 bis 60); Optimum per Teilmengen-DP, LP mit allen Mustern; vorberechnet.

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind Messungen an den Instanzen dieser Demo (feste Seeds), nachgerechnet in `tests/test_claims.py`, `tests/test_algorithm.py` und `tests/test_oracle_lp_schranke.py`.

**Raster** (je Zelle 100 Instanzen):

| Größen | n | durch L1 | erst durch L2 | erst durch LP | LP trifft das Optimum | nicht entschieden | Rundung verletzt | LP mehr als 1 unter FFD |
|---|---|---|---|---|---|---|---|---|
| mittel | 12 | 87 | 0 | 5 | 8 | 0 | 0 | 0 |
| mittel | 20 | 79 | 0 | 2 | 19 | 0 | 0 | 0 |
| mittel | 30 | 68 | 0 | 3 | 22 | 7 | 0 | 0 |
| groß | 12 | 38 | 58 | 4 | 0 | 0 | 0 | 0 |
| groß | 20 | 24 | 63 | 13 | 0 | 0 | 0 | 0 |
| groß | 30 | 17 | 65 | 17 | 1 | 0 | 0 | 0 |
| breit | 12 | 49 | 48 | 3 | 0 | 0 | 0 | 0 |
| breit | 20 | 45 | 43 | 9 | 3 | 0 | 0 | 0 |
| breit | 30 | 24 | 63 | 10 | 2 | 1 | 0 | 0 |

- Von den 900 Instanzen sind 431 durch L1 bewiesen, 340 erst durch L2; **129 bleiben offen** (FFD über L1 und L2). Die Aufteilung gleicht der in Stück 2.
- **Von den 129 offenen Instanzen beweist der aufgerundete LP-Wert bei 66 die Optimalität von FFD** (in jeder von ihnen liegt der aufgerundete LP-Wert über L2). Bei **55** ist der aufgerundete LP-Wert gleich dem Optimum und FFD braucht genau einen Container mehr. **8** sind nicht entschieden (7 bei mittleren Teilen mit n = 30, 1 bei breiten Teilen mit n = 30): dort liegt der aufgerundete LP-Wert einen Container unter FFD, und das ganzzahlige Programm hat in 60 Sekunden weder eine Packung mit einem Container weniger gefunden noch ihre Nichtexistenz bewiesen.
- **Die Rundung ist in keiner Instanz verletzt** (0 von 129), und in keiner liegt der aufgerundete LP-Wert mehr als einen Container unter FFD.
- **Dominanz über L2:** Der aufgerundete LP-Wert liegt in **0 von 900** Instanzen unter L2 und in 66 darüber. (Bei den 431 Instanzen mit FFD = L1 folgt das aus L₁ ≤ ⌈LP⌉ ≤ FFD ohne Rechnung.)
- **Mittlere Teile:** L2 beweist in 0 von 300 Instanzen mehr als L1, der LP-Wert in 10 von 300 zusätzlich.

**Suche nach Gegenbeispielen zur Rundung** (Optimum gegen aufgerundeten LP-Wert):

| n | Instanzen | Optimum gleich aufgerundetem LP-Wert | Optimum größer |
|---|---|---|---|
| 8 | 1500 | 1500 | 0 |
| 9 | 1500 | 1500 | 0 |
| 10 | 1500 | 1500 | 0 |
| 11 | 600 | 600 | 0 |

In **0 von 5100** zufälligen Instanzen mit 8 bis 11 Paketen liegt das Optimum über dem aufgerundeten LP-Wert. Das heißt nicht, dass es keine gibt: Aus der Literatur (Suchtreffer, Originale nicht gelesen) sind solche Instanzen ab etwa zehn Paketen bekannt.

**Beispiele** (LP aller Muster, Optimum per Teilmengen-DP):

| Beispiel | Summe | FFD | L1 | L2 | LP | aufgerundet | Optimum | Ausgang |
|---|---|---|---|---|---|---|---|---|
| Kleines Beispiel (4, 4, 4, 4, 3) | 19 | 3 | 2 | 2 | 2,5 | 3 | 3 | erst durch LP bewiesen |
| Beispiel 2 (bewiesen durch L2) | 834 | 11 | 9 | 11 | 11,0 | 11 | 11 | erst durch L2 bewiesen |
| Beispiel 3 (LP beweist FFD) | 498 | 6 | 5 | 5 | 5,1429 | 6 | 6 | erst durch LP bewiesen |
| Beispiel 4 (LP trifft das Optimum) | 496 | 6 | 5 | 5 | 5,0 | 5 | 5 | LP trifft das Optimum, FFD verliert |

Beim kleinen Beispiel von Hand: Muster {4, 4} (Summe 8), {4, 3} (7) und Einzelpakete; die 3 braucht ein Muster mit ihr (Gewicht mindestens 1 auf {4, 3}, das deckt eine Vier), die übrigen drei Vieren deckt {4, 4} mit Gewicht 1,5: LP = 1 + 1,5 = **2,5**, aufgerundet 3. Beim dritten Beispiel ist der LP-Wert 36/7 ≈ 5,1429 und beweist FFD, wo L1 und L2 (je 5) es nicht konnten.

## Ehrliche Grenzen

- Alle Aussagen gelten für gleichverteilte Paketgrößen in drei Bereichen, drei Paketzahlen (12, 20, 30) und nur FFD. Über 30 Pakete ist nichts gemessen.
- **„Die Rundung ist nie verletzt“ gilt für diese Instanzen,** nicht allgemein. Instanzen mit Optimum über dem aufgerundeten LP-Wert sind aus der Literatur bekannt (Suchtreffer; die kleinsten ab etwa zehn Paketen, die größte bekannte Lücke OPT − LP bei etwa 1,1); gezielt gebaute Instanzen können sich anders verhalten als die Zufallsinstanzen hier.
- Bei den 8 nicht entschiedenen Instanzen bleibt das Optimum offen; ihre Zahl hängt von der Rechenzeit ab. Ein erster Lauf mit 10 Sekunden Zeitlimit auf ausgelastetem Rechner ließ mehr Instanzen offen; die Datei ist mit 60 Sekunden bei ruhigem Rechner entschieden (`generate_precomputed.py --retry-u`).
- Stärkere Schranken als die LP-Schranke sind nicht gemessen; wie viele der 8 offenen Fälle sie entscheiden würden, ist unbekannt.
- Das Preisproblem der Spaltenerzeugung wird nicht erklärt (Verweis auf die Linie Exakte Suche).

### Annahmen, Grenzen und bekannte Probleme (Text wie in der App)

**Annahmen.** Ganzzahlige Paketgrößen; eine Sorte Container mit fester Kapazität; alle Pakete sind vor dem Packen bekannt; keine Geometrie, nur Größen. Die LP-Schranke ist die Relaxation, in der jede zulässige Teilmenge von Paketen ein Muster ist, die Gewichte der Muster Brüche sein dürfen und jedes Paket mindestens einmal überdeckt wird. Verglichen wird nur FFD (First Fit, größte zuerst).

**Grenzen.** Live rechnet die Demo den LP-Wert und das Optimum bis 12 Pakete. Das Raster hat drei Größenbereiche und drei Paketzahlen (12, 20, 30) mit je 100 Instanzen und dieselben Instanzen wie Stück 2 dieser Reihe; über 30 Pakete ist nichts gemessen. Die Suche nach Gegenbeispielen zur Rundung deckt 5100 zufällige Instanzen mit 8 bis 11 Paketen ab: Dass sie keines fand, heißt nicht, dass es keine gibt. Stärkere Schranken als die LP-Schranke sind nicht gemessen. Wie der LP-Wert bei vielen Paketen berechnet wird (Spaltenerzeugung), erklärt diese Demo nicht.

**Bekannte Probleme und Unsicherheiten.** Die Muster und Gewichte, die die Demo als LP-Lösung zeigt, sind eine optimale Lösung unter mehreren; der LP-Wert selbst ist eindeutig. Bei den Rasterinstanzen mit 20 und 30 Paketen kommt die Aussage „es gibt eine Packung mit einem Container weniger als FFD“ aus einem ganzzahligen Programm mit 60 Sekunden Zeitlimit; Instanzen, die es in dieser Zeit nicht entschieden hat, stehen in einer eigenen Spalte. 100 Instanzen je Zelle sind wenig, eine einzelne Zelle ist kein Gesetz. Dass kleinste Instanzen mit einem Optimum über dem aufgerundeten LP-Wert existieren (ab etwa zehn Paketen), steht nur aus Suchtreffern und Sekundärquellen, die Originale wurden nicht gelesen. Die App wurde im Browser bedient (Presets, Würfel-Button und Ausklapper auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät.

## Verifikation

- **Kern:** vier von Hand gerechnete Mini-Instanzen (Kapazität 10, eine je Ausgang außer „LP schwach“; Rechnung in `tests/conftest.py`), LP-Muster des kleinen Beispiels ({4, 4} mit 1,5 und {4, 3} mit 1), die Beispiele der App mit allen Werten (LP 36/7 beim dritten), Gültigkeit der angezeigten LP-Lösung, Aufrunden mit Toleranz, die Ordnung der Zweige von `ausgang`, Randfälle (leere Eingabe, ein Paket, gleiche Größen, Muster dürfen nicht mehr Exemplare enthalten, als es gibt).
- **Orakel** (`tests/test_oracle_lp_schranke.py`): LP mit allen Mustern gegen die Spaltenerzeugung (drei feste und zwölf zufällige Instanzen, darunter Gleichstände der Größen); **Dualzertifikat** an 60 Instanzen (Dualpreise nichtnegativ, jedes zulässige Muster hat höchstens den Preis 1, die Summe der Preise gleicht dem LP-Wert: der LP-Wert ist eine gültige untere Schranke); Optimum gegen Aufzählung aller Zerlegungen (n ≤ 8) und eine zweite DP über Untermengen (n ≤ 10); FFD gegen eine naive Zweitumsetzung (150 Instanzen); L2 gegen die Rechnung über alle ganzzahligen α (200 Instanzen); Dominanz L₂ ≤ ⌈LP⌉ ≤ OPT ≤ FFD und Ausgang gegen eine unabhängige Einordnung (80 Instanzen); Rundung an 150 Instanzen mit bis zu 9 Paketen.
- **Raster:** je Zelle die Aufteilung L1 / L2 / offen frisch gerechnet (alle neun Zellen), bei 12 Paketen die vollständigen Codes mit LP aller Muster und Teilmengen-DP, bei 20 und 30 Paketen je Zelle eine Stichprobe offener Instanzen mit Spaltenerzeugung (`tests/test_claims.py`); die Einordnung `instanz_code` mit Stub-Funktionen an von Hand gesetzten Fällen (alle sieben Codes, Flags, Aufrufargument für die Packbarkeit).
- **Suche:** die Größen 8 und 9 frisch gerechnet und exakt verglichen; die Zählungen der README gegen die Datei.
- **Verdikte:** alle Zweige an von Hand gesetzten Werten (`tests/test_verdicts.py`), je Preset der erwartete Ausgang und die Art.
- **Presets und Layout:** vollständig, Werte innerhalb der Reglergrenzen, Standard-Preset gleich Standardeinstellung; Schnellstart oben in der Seitenleiste, fester Kopf, genau das passende Preset hervorgehoben (`tests/test_layout.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jede Auswahl in jedem Wert, Regler und Startzahl an den Grenzen) und Footer-Test.
- **Tests gesamt:** 120, Laufzeit etwa anderthalb Minuten (ohne Parallelisierung).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `dev/cg.py` | LP-Wert per Spaltenerzeugung (nur Generator und Tests) |
| `dev/ilp.py` | ganzzahliges Programm: gibt es eine Packung mit m Containern? (nur Generator und Tests) |
| `generate_precomputed.py` | erzeugt `lpb_precomputed.json`; `--retry-u` entscheidet nicht entschiedene Instanzen neu, `--check` rechnet das Schnelle nach |
| `lpb_algorithm.py` | Kern: FFD, Schranken, LP-Schranke mit allen Mustern, Optimum, Ausgang |
| `lpb_constants.py` | Beispiele, Raster, Suche, Farben, Presets, Text der Annahmen |
| `lpb_evaluation.py` | Analyse, Verdikte, Einordnung der Rasterinstanzen, Raster und Suche |
| `lpb_layout.py` | Fester Kopf (Stylesheet) |
| `lpb_precomputed.json` | vorberechnete Codes des Rasters und Zählungen der Suche |
| `lpb_presets.py` | Permalink (Begrenzen), Presets (Schnellstart, aktives Preset hervorgehoben), Würfel-Button |
| `lpb_scenario.py` | Instanzen: Beispiele, zufällige, Raster (dieselben wie Stück 2) und Suche |
| `lpb_visualization.py` | Plotly-Abbildungen (Achsen gesperrt), LP-Lösung als Balken variabler Breite |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt; scipy und numpy für den LP bei höchstens 12 Paketen) |
| `tests/` | Mini-Instanzen und Handrechnung, Orakel, Randfälle, Verdikte, Presets, Layout, Raster und Zahlen der README, AppTest-Rauchtest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **PDF-Export:** die Demo zeigt zwölf Pakete; ein Export trüge nichts zur Frage bei.
- **Erklärung der Spaltenerzeugung:** Das Preisproblem erklärt die Linie Exakte Suche (Column Generation am Cutting-Stock-Problem).
- **Stärkere Schranken, Arc-Flow, Näherungsschemata:** spätere oder gelbe Stücke der Reihe.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, NumPy und SciPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
