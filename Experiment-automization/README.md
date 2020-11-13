# Experiment Automatisering
## Door Victor Vreede
Al mijn code geschreven voor de module experimtent automatisering.
Hierbij een overzicht van alle modules en requirements.

## File structure:
```
Experiment-automatization
│   README.md
│   setup.py   
│   __init__.py   
│
└───ch2
│       solutions.py
└───ch3
│       first_measurement.py
│       experiment.py
│       ...
└───ch4
│       __init__.py
│       smallangle.py
└───pythonlab
    │   __init__.py
    └───controllers
            __init__.py
            arduino_device.py
```
### Opmerkingen:
 - `experiment.py` gebruikt de `pythonlab` module, de import werkt alleen als deze geïnstalleerd is. Gebruik hiervoor ```pip install --editable .``` in `Experiment-automatization/`, zoals beschreven in hoofdstuk 4 van de handleiding. Merk op dat `first_measurement.py` dezelfde taken verricht, maar dan zonder deze benodigheid.
 - De uitwerking van Opdracht 3.7 is te vinden in `experiment.py`, de uitwerking is te zien in de functie `save_csv()` functie.
 - De uitwerkingen van hoofdstuk 4 zijn op dit moment nog niet af.
 - Alle code is verder te vinden op [github](https://github.com/Vector04/Prac2.git).