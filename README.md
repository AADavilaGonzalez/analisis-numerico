# Analisis Numerico
Coleccion de varios algoritmos numericos comunmente utilizados implementados en
python con numpy.

---

## Como Correr los Algoritmos
Los algoritmos fueron implementados como scripts interactivos de un solo archivo.
Para poder reutilizar codigo entre scripts se necesito desarrollar una pequeña
herramienta 'glue' para poder generar los scripts finales a partir de los archivos
principales y las utilidades compartidas.

### Los scripts se pueden ejecutar de dos formas:

1. Utilizando la carpeta de proyecto como modulo de python:
    >desde fuera de la carpeta del proyecto, ejectutar el script como submodulo:  
    >python -m analisis-numerico.[algoritmo].main
    
2. Generando el script final mediante la herramienta glue:
    >invocar la herramienta sobre el archivo principal para generar el script final:  
    >./glue [algorimto]/main.py [algoritmo]/out.py
