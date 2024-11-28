import math

class Tracker:
    def __init__(self):
        self.point_center = {}
        self.missing_count = {}  # Nuevo diccionario para contar fotogramas perdidos
        self.id_count = 1

    def Tracking(self, objects):
        object_id = []

        for rect in objects:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2

            object_det = False
            for id, pt in self.point_center.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])

                if dist < 150:  #Umbral de distancia
                    self.point_center[id] = (cx, cy)
                    self.missing_count[id] = 0  # Restablece el contador
                    object_id.append([x, y, w, h, id])
                    object_det = True
                    break

            if not object_det:
                self.point_center[self.id_count] = (cx, cy)
                self.missing_count[self.id_count] = 0
                object_id.append([x, y, w, h, self.id_count])
                self.id_count += 1

        # Incrementa el contador de objetos no detectados
        for id in list(self.point_center.keys()):
            if id not in [obj[-1] for obj in object_id]:  # Si no está en la lista de detecciones
                self.missing_count[id] += 1

            # Elimina el objeto si no ha sido detectado en 5 fotogramas consecutivos
            if self.missing_count[id] > 5:
                del self.point_center[id]
                del self.missing_count[id]

        return object_id
