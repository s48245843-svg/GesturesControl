import cv2
import numpy as np

print("=" * 50)
print("ПОИСК КАМЕРЫ")
print("=" * 50)

# Пробуем разные методы открытия камеры
methods = [
    (0, cv2.CAP_DSHOW),
    (0, cv2.CAP_ANY),
    (1, cv2.CAP_DSHOW),
    (1, cv2.CAP_ANY),
    (0, cv2.CAP_V4L2),  # для Linux
    (1, cv2.CAP_V4L2),
]

for cam_id, api in methods:
    try:
        print(f"\nПробуем камера {cam_id} с API {api}...")
        cap = cv2.VideoCapture(cam_id, api)
        
        if cap.isOpened():
            # Устанавливаем параметры
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Пытаемся прочитать 5 кадров
            for i in range(5):
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"✅ УСПЕХ! Камера {cam_id} работает!")
                    cv2.imshow("Camera Test", frame)
                    cv2.waitKey(2000)
                    cv2.destroyAllWindows()
                    cap.release()
                    exit(0)
                else:
                    print(f"   Попытка {i+1}: кадр не получен")
            
            cap.release()
        else:
            print(f"   Камера {cam_id} не открывается")
    except Exception as e:
        print(f"   Ошибка: {e}")

print("\n❌ НЕ УДАЛОСЬ НАЙТИ РАБОТАЮЩУЮ КАМЕРУ")
print("\nВозможные решения:")
print("1. Перезагрузи компьютер")
print("2. Проверь что камера работает в приложении 'Камера' Windows")
print("3. Закрой все программы которые используют камеру (Discord, Zoom, браузеры)")
print("4. Попробуй другой USB-порт")