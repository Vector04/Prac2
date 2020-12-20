from setuptools import setup, find_packages

setup(
    name="pythonlab",
    author="V.N. Vreede",
    version="0.3",
    packages=find_packages(),
    entry_points={"console_scripts": ["test_app = ch4.smallangle:cli",
                                      "diode = pythonlab.views.views:cli",
                                      "interface = pythonlab.views.interface:cli", 
                                      "power = pythonlab.views.max_power:cli"]},
    package_data={"pythonlab.views":["plotter.ui", "currentplotter.ui", "powertracker.ui"]}
)
