# Experiment Automatisering
## Door Victor Vreede
Al mijn code geschreven voor de module experimtent automatisering.
Hierbij een overzicht van alle modules en requirements.

## File structure:
```
Experiment-automatization
│   README.md
│   setup.py
│       
├───ch3
│       3.2-grafiek.png
│       experiment.py
│       first_measurement.py
│       ...
│       
├───ch4
│       smallangle.py
│       __init__.py
│           
├───ch5
│       first_design.py
│       first_design.ui
│       gui_prog_test.py
│       plotter.py
│       plotter.ui
│       plot_test.py
│       ...
│           
└───pythonlab
    │   __init__.py
    │   
    ├───controllers
    │       arduino_device.py
    │       __init__.py
    │           
    ├───models
    │       models.py
    │       __init__.py    
    │           
    └───views
           currentplotter.ui
           helpers.py
           interface.py
           interface_backup.py
           plotter.py
           plotter.ui
           views.py
           __init__.py       
```
### Opmerkingen:
 - `experiment.py` gebruikt de `pythonlab` module, de import werkt alleen als deze geïnstalleerd is. Gebruik hiervoor ```pip install --editable .``` in `Experiment-automatization/`, zoals beschreven in hoofdstuk 4 van de handleiding. Merk op dat `first_measurement.py` dezelfde taken verricht, maar dan zonder deze benodigheid.
 - De uitwerking van Opdracht 3.7 is te vinden in `experiment.py`, de uitwerking is te zien in de functie `save_csv()` functie.
 - De uitwerkingen van hoofdstuk 4 zijn te vinden in `pythonlab/models/models.py` en `pythonlab/views/views.py`. De command-line functionaliteit werkt alleen als de `pythonlab` module is geïnstalleerd, zie hiervoor de bovenste opmerking.
 - De uitwerkingen van hoofdstuk 5 zijn te vinden in `pythonlab/views/`. De voornaamste code staat in `pythonlab/views/interface.py`. De command-line functionaliteit werkt alleen als de `pythonlab` module is geïstalleerd.
 - Het autodetecteren van de juiste usb port is gebeurt iets anders and voorgeschreven, de gebruiker kan namelijk de juiste poort kiezen en de identificatiestring opvragen. Dit heeft 2 voordelen. Niet alleen runt de code veel sneller, mochten er toevallig 2 visa-devices aangesloten zijn dan kan de gebruiker het juiste device kiezen. 
 - De threading functionaliteit heb ik iets anders geïmplementeerd dan normaal, dit omdat ik wat problemen had met de blokkering van `QtCore.Timer()` zodra de thread bezig was. Nu gebruik ik een subclass van `QtCore.QThread` in combinatie met een `qtCore.pyqtSignal`. De functionaliteit is hetzelfde, de implementatie is verschillend. Een versie van de code zonder `QThread` (Deze functionalitiet is niet volledig!!) is te vinden in `interface_backup.py`, mocht er intresse daarin zin.
 - Alle code is verder te vinden op [github](https://github.com/Vector04/Prac2.git).