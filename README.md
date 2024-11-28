## Sistema de Detección y Seguimiento de Vehículos
Este proyecto implementa un sistema de detección y seguimiento de vehículos utilizando OpenCV. Detecta vehículos desde un video, los clasifica según su tamaño (automóvil, bus o camión), cuenta los vehículos en carriles específicos, identifica el color predominante de cada vehículo y permite hacer zoom en la zona de los carriles para inspección detallada. Además, el sistema muestra el conteo de vehículos por carril y cuenta con funciones para pausar, hacer zoom y alternar distintas ventanas de visualización.


### Instalación
Primero deberas instalar python, con el siguiente url lo puedeshacer:
    url "https://www.python.org/downloads/"


Seguidamente se deben instalar los paquetes necesarios 

  $ pip install opencv-python numpy

Coloca el archivo de video (Street.mp4 o el video de tu preferencia) en el directorio resources.


### Con el siguiente comando lograras correr el codigo 
   $ python main.py



## Aspectos importantes que debes considerar
Controles:
ESC: Salir del programa.
c: Alternar ventana de conteo de vehículos.
z: Alternar el modo de zoom en la zona de carriles.
+: Aumentar el nivel de zoom.
-: Disminuir el nivel de zoom.
d: Pausar o reanudar el video cuando el zoom está activo.

