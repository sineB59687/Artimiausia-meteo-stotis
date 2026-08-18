# Meteorologijos stočių paieška

Ši programa skirta Lietuvos meteorologijos stočių paieškai pagal pasirinktą vietovę arba tašką žemėlapyje. Programa leidžia rasti artimiausias meteorologijos stotis, parodyti tris artimiausias stotis bei, pasirinkus filtrą, ieškoti tik stočių, kurios teikia vėjo duomenis.

## Pagrindinės funkcijos

Programa leidžia:

- įvesti miesto pavadinimą arba adresą;
- pasirinkti vietovę iš automatiškai pateikiamų paieškos rezultatų;
- paspausti bet kurią vietą žemėlapyje ir pagal ją rasti artimiausias stotis;
- rasti tris artimiausias meteorologijos stotis;
- matyti atstumą iki kiekvienos rastos stoties;
- įjungti filtrą **„Tik vėjo duomenys“**;
- žemėlapyje matyti stotis, kurios teikia vėjo duomenis;
- paspausti ant stoties ir pamatyti jos informaciją;
- naudoti mygtuką **„Priartinti“**, kad žemėlapis būtų priartintas prie pasirinktos vietos ir rastų stočių;
- naudoti interaktyvų žemėlapį vietovės pasirinkimui.

---

## Projekto struktūra

```text
MeteorologijosStociuPaieska/
│
├── app.py
├── requirements.txt
│
├── templates/
│   └── index.html
│
└── static/
    ├── style.css
    └── app.js
```

### `app.py`

Pagrindinis programos failas.

Jame yra:

- Flask serveris;
- meteorologijos stočių duomenų įkėlimas;
- stočių koordinatės;
- artimiausių stočių skaičiavimas;
- vėjo duomenis teikiančių stočių filtras;
- vietovių paieškos API;
- Geoapify geokodavimo API naudojimas;
- programos API maršrutai.

### `templates/index.html`

Pagrindinis svetainės puslapis.

Jame aprašoma:

- paieškos laukelis;
- mygtukas **„Ieškoti“**;
- vėjo duomenų filtras;
- žemėlapis;
- artimiausių trijų stočių informacija;
- legenda;
- mygtukas **„Priartinti“**;
- automatinio vietovių pasiūlymo langas.

### `static/style.css`

Šiame faile aprašoma programos išvaizda.

Čia nustatomi:

- spalvos;
- šriftai;
- paieškos laukelio išvaizda;
- mygtukų išvaizda;
- stočių informacijos langeliai;
- žemėlapio legenda;
- meteorologijos stočių žymekliai;
- išdėstymas mažesniuose ekranuose.

### `static/app.js`

Šis failas valdo interaktyvią svetainės dalį.

Jame yra funkcijos, atsakingos už:

- žemėlapio sukūrimą;
- stočių žymeklių sukūrimą;
- paiešką;
- vietovių pasiūlymus;
- stočių paiešką pagal koordinates;
- rezultatų atvaizdavimą;
- vėjo stočių filtravimą;
- žemėlapio priartinimą;
- vartotojo pasirinktos vietos atvaizdavimą.

Funkcijų pavadinimai palikti **anglų kalba**, kad kodą būtų lengviau prižiūrėti ir plėsti.

---

# Naudojamos technologijos

## Python

Programa naudoja Python kaip pagrindinę serverio programavimo kalbą.

## Flask

Flask naudojamas kaip interneto serverio karkasas.

Jis:

1. paleidžia svetainę;
2. pateikia HTML, CSS ir JavaScript failus;
3. priima užklausas iš naršyklės;
4. apdoroja stočių paiešką;
5. grąžina rezultatus naršyklei.

## JavaScript

JavaScript naudojamas svetainės interaktyvumui.

Jis komunikuoja su Flask serveriu naudodamas API užklausas.

## Leaflet

Žemėlapiui naudojama **Leaflet** biblioteka.

Žemėlapyje rodomi:

- vartotojo pasirinkta vieta;
- artimiausia stotis;
- antra artimiausia stotis;
- trečia artimiausia stotis;
- vėjo duomenis teikiančios stotys.

## OpenStreetMap

Žemėlapio pagrindui naudojami OpenStreetMap žemėlapio duomenys.

## Geoapify

Geoapify naudojamas vietovės pavadinimui arba adresui paversti į geografines koordinates.


# API maršrutai

Programa naudoja Flask API maršrutus.

### Vietovės paieška

```text
/api/location
```

Naudojama įvestam miestui arba adresui surasti.

### Automatiniai pasiūlymai

```text
/api/autocomplete
```

Naudojama vietovių pasiūlymams paieškos laukelyje.

### Meteorologijos stočių paieška

```text
/api/stations
```

Naudojama artimiausioms stotims pagal geografines koordinates rasti.

### Sveikatos patikrinimas

```text
/health
```

Naudojamas patikrinti, ar serveris veikia.

---

# Geoapify API raktas

Vietovių paieškai naudojamas Geoapify API raktas.


---

# Paleidimas lokaliai

Pirmiausia reikia įdiegti Python.

Tada projekto aplanke įdiegti reikalingas bibliotekas:

```bash
pip install -r requirements.txt
```

Serveris paleidžiamas:

```bash
python app.py
```

arba Windows sistemoje:

```bash
py app.py
```

Tada naršyklėje atidaromas Flask pateiktas vietinis adresas, dažniausiai:

```text
http://127.0.0.1:5000
```

---

# Paleidimas per Render

Projektą galima talpinti Render platformoje.

GitHub saugykloje turi būti visas projektas:

```text
app.py
requirements.txt
templates/
static/
```

Render įdiegia bibliotekas pagal:

```text
requirements.txt
```

ir paleidžia Flask programą pagal nustatytą paleidimo komandą.

Geoapify API raktas turi būti įrašytas Render **Environment Variables** skiltyje, o ne GitHub kode.

---

# `requirements.txt`

Projekte naudojamos Python bibliotekos turi būti nurodytos `requirements.txt` faile.

Pavyzdžiui:

```text
Flask
pandas
requests
```

Jeigu `app.py` naudoja papildomas bibliotekas, jos taip pat turi būti įtrauktos į šį failą.

---

# Stočių duomenys

Meteorologijos stočių informaciją programa gali gauti iš naudojamo stočių duomenų šaltinio.

Papildomos rankiniu būdu įtrauktos stotys turi būti pateiktos su jų:

```text
pavadinimu
kodu
platuma
ilguma
```

Pavyzdžiui:

```python
{
    "name": "Vilniaus AS",
    "code": "vilniaus-ams",
    "latitude": 54.64095,
    "longitude": 25.29250
}
```

Vėjo stočių sąraše naudojami stočių kodai, todėl pakeitus stoties kodą reikia atitinkamai pakeisti ir vėjo stočių sąrašą.

---

# Svarbu keičiant kodą

Keičiant programą rekomenduojama:

1. **Nekeisti API maršrutų pavadinimų**, jei jų neatnaujina ir `app.js`.
2. **Nekeisti HTML elementų `id`**, jei jie naudojami JavaScript faile.
3. Geoapify API rakto nelaikyti viešame GitHub kode.
4. Prieš siunčiant pakeitimus į GitHub patikrinti, ar programa veikia lokaliai.
5. Keičiant stočių sąrašą patikrinti, ar jų koordinatės yra teisingos.
6. Jei keičiami `app.py` atsakymo JSON laukų pavadinimai, juos reikia atitinkamai pakeisti ir `app.js`.
