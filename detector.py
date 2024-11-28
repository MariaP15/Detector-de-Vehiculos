import cv2
import numpy as np
from tracker import *

following = Tracker()
cap = cv2.VideoCapture("resources/Street.mp4")
detection = cv2.createBackgroundSubtractorMOG2(history=10000, varThreshold=12)

# Función para detectar el color predominante
def get_dominant_color(roi):
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    colors = {
        "blanco": ([0, 0, 200], [180, 25, 255]),
        "gris": ([0, 0, 100], [180, 25, 200]),
        "rojo": ([0, 100, 100], [10, 255, 255]),
        "rojo_brillante": ([170, 100, 100], [180, 255, 255]),
        "amarillo": ([10, 100, 100], [25, 255, 255]),
        "verde": ([25, 100, 100], [85, 255, 255]),
        "azul": ([85, 100, 100], [130, 255, 255]),
        "purpura": ([130, 100, 100], [170, 255, 255]),
        "negro": ([0, 0, 0], [180, 255, 50]),
    }
    color_counts = {color: 0 for color in colors}

    for color, (lower, upper) in colors.items():
        lower_np = np.array(lower)
        upper_np = np.array(upper)
        mask = cv2.inRange(hsv_roi, lower_np, upper_np)
        color_counts[color] = cv2.countNonZero(mask)

    dominant_color = max(color_counts, key=color_counts.get)
    color_map = {
        "blanco": (255, 255, 255),
        "gris": (128, 128, 128),
        "rojo": (0, 0, 255),
        "rojo_brillante": (0, 0, 255),
        "amarillo": (0, 255, 255),
        "verde": (0, 255, 0),
        "azul": (255, 0, 0),
        "purpura": (255, 0, 255),
        "negro": (0, 0, 0),
    }
    return color_map.get(dominant_color, (128, 128, 128))

# Diccionario para almacenar el conteo de vehículos por cada carril
lane_count_dict = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
vehicle_ids_per_lane = {1: set(), 2: set(), 3: set(), 4: set(), 5: set()}

# Función para contar vehículos por carril
def count_vehicles_by_lane(current_ids):
    for id, (x, y, lane_num) in text_position_dict.items():
        if id not in vehicle_ids_per_lane[lane_num]:
            vehicle_ids_per_lane[lane_num].add(id)
            lane_count_dict[lane_num] += 1

# Función para hacer zoom en toda la zona de los carriles
def zoom_in_on_zone(zone, zoom_factor=2):
    # Cambiar el tamaño de la zona completa para hacer el zoom
    zoomed_zone = cv2.resize(zone, (zone.shape[1] * zoom_factor, zone.shape[0] * zoom_factor), interpolation=cv2.INTER_LINEAR)
    return zoomed_zone

frame_count = 0
process_interval = 5
color_dict = {}
text_position_dict = {}  # Diccionario para almacenar la posición del texto y el carril por ID
show_lane_count_window = False  # Variable para controlar la ventana de conteo
zoom_enabled = False  # Control para activar/desactivar el zoom
zoom_factor = 2  # Nivel inicial de zoom
zoom_step = 20  # Desplazamiento de zoom por tecla de dirección
video_paused = False  # Control para pausar/reanudar el video

while True:
    if not video_paused or not zoom_enabled:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (1280, 720))
        zone = frame[220:1076, 200:1910]  # Zona de los carriles
        zone_width = zone.shape[1]
        lane_width = zone_width // 5

        # Aplicar detección de fondo
        mask = detection.apply(zone)
        _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        detections = []

        for count in contours:
            area = cv2.contourArea(count)
            if area > 800:
                x, y, width, height = cv2.boundingRect(count)
                cv2.rectangle(zone, (x, y), (x + width, y + height), (0, 0, 255), 3)
                detections.append([x, y, width, height])

        if frame_count % process_interval == 0:
            info_id = following.Tracking(detections)
            current_ids = set()

            for inf in info_id:
                x, y, width, height, id = inf
                lane_num = x // lane_width + 1
                center_x, center_y = x + width // 2, y + height // 2
                small_roi = zone[center_y - height // 4:center_y + height // 4,
                                 center_x - width // 4:center_x + width // 4]
                blurred_roi = cv2.GaussianBlur(small_roi, (15, 15), 0)
                color_bgr = get_dominant_color(blurred_roi)
                color_dict[id] = color_bgr

                text_position_dict[id] = (x, y, lane_num)
                current_ids.add(id)
            
            for id in list(color_dict.keys()):
                if id not in current_ids:
                    del color_dict[id]
                    del text_position_dict[id]
            
            # Llamar a la función para contar vehículos por carril
            count_vehicles_by_lane(current_ids)

        # Dibujar información sobre los vehículos detectados
        for id, (x, y, lane_num) in text_position_dict.items():
            color_bgr = color_dict.get(id, (128, 128, 128))
            cv2.putText(zone, f"ID:{id} C:{lane_num}", (x, y - 15), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)
            text_width = 80
            circle_x = x + text_width + 5
            circle_y = y - 15
            cv2.circle(zone, (circle_x, circle_y), 10, color_bgr, -1) #Color del vehiculo

    # Mostrar zoom si está activado
    if zoom_enabled:
        zoomed_zone = zoom_in_on_zone(zone, zoom_factor)
        cv2.imshow("Zoom", zoomed_zone)

    # Mostrar la ventana de conteo de vehículos si está activada
    if show_lane_count_window:
        count_window = np.zeros((200, 300, 3), dtype=np.uint8) * 255
        for i, lane in enumerate(lane_count_dict, start=1):
            count = lane_count_dict[lane]
            cv2.putText(count_window, f"Carril {lane}: {count}", (10, i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow("Vehiculos", count_window)

    cv2.imshow("Camara de seguridad", frame) #Ventana Principal 

    frame_count += 1
    key = cv2.waitKey(5)
    if key == 27:  # Presionar ESC para salir
        break
    elif key == ord('c'):  # Alternar la ventana de conteo con la tecla 'c'
        show_lane_count_window = not show_lane_count_window
    elif key == ord('z'):  # Alternar el zoom con la tecla 'z'
        zoom_enabled = not zoom_enabled
    elif key == ord('+'):  # Incrementar el factor de zoom con la tecla '+'
        zoom_factor += 1
    elif key == ord('-') and zoom_factor > 1:  # Disminuir el factor de zoom con la tecla '-'
        zoom_factor -= 1
    elif key == ord('d') and zoom_enabled:  # Pausar/reanudar video con la tecla 'd' si el zoom está activado
        video_paused = not video_paused

cap.release()
cv2.destroyAllWindows()