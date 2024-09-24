# Chmura Salami
<img src="chmura_salami.jpeg" width="600" style="margin:0 10px 10px 0" />

## Skrypty dla Szkoły w Chmurze

### Wymagania
    
    git
    python 3.x

### Instalacja

    pip install git+https://github.com/bohdanbobrowski/mdmc2exif

### Środowisko deweloperskie

    git clone git@github.com:bohdanbobrowski/chmura_salami.git
    cd chmura_salami
    python -m venv venv

...na Linuxie/macOS:

    source venv/bin/activate

...na Windows:

    venv\Scripts\activate

...i wreszcie:

    pip install -e .

### Skrypt `chmura_salami`

#### Sposób użycia:

    chmura_salami [nazwa pliku xlsx] [opcjonalnie: nazwa arkusza, domyślnie "Sheet1"]

Nie jest to zawsze konieczne, ale gdy nazwa pliku bądź arkusza zawiera spacje należy je podać w cudzysłowiu. 

#### Przykłady:

    chmura_salami grafik_nauczycieli.xlsx
    chmura_salami grafik_nauczycieli.xlsx Sheet1   
    chmura_salami "Grafik nauczycieli.xlsx"
    chmura_salami "Grafik nauczycieli.xlsx" "Sheet1"
