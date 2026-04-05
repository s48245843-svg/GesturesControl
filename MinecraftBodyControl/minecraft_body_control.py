import cv2
import mediapipe as mp
import pyautogui
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import time
import numpy as np
from collections import deque

# Инициализация
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Глобальные переменные
running = False
cap = None
face_mesh = None
hands = None
pose = None
screen_width, screen_height = pyautogui.size()

# Настройки
head_speed_x = 3.0
head_speed_y = 2.5
smoothing = 0.1
deadzone = 0.015

# Для абсолютного позиционирования
calibrated = False
calib_nose_x = 0.5
calib_nose_y = 0.5
cursor_x, cursor_y = screen_width // 2, screen_height // 2

# Для FPS
fps_list = deque(maxlen=30)

def find_camera():
    for i in range(5):
        try:
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
                cap.set(cv2.CAP_PROP_FPS, 120)
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"✅ Найдена камера: {i}")
                    cap.release()
                    return str(i)
            cap.release()
        except:
            pass
    return "0"

class MinecraftBodyControl:
    def __init__(self, root):
        self.root = root
        self.root.title("MINECRAFT BODY CONTROL - 100+ FPS")
        self.root.geometry("750x800")
        self.root.configure(bg='#1a1a2e')
        self.root.resizable(False, False)
        
        self.camera_id = find_camera()
        
        # Заголовок
        title_text = """
╔══════════════════════════════════════════════════════════════════╗
║         🎮 MINECRAFT BODY CONTROL - 100+ FPS 🎮                 ║
║              АВТОМАТИЧЕСКАЯ КАЛИБРОВКА                          ║
║         ВСТАНЬ В ПОЛНЫЙ РОСТ - ПРОГРАММА ВСЁ СДЕЛАЕТ САМА       ║
╚══════════════════════════════════════════════════════════════════╝
        """
        
        title_label = tk.Label(root, text=title_text, 
                               font=('Courier', 8), bg='#1a1a2e', 
                               fg='#00ff00', justify=tk.LEFT)
        title_label.pack(pady=10)
        
        # Инструкция
        inst_frame = tk.LabelFrame(root, text=" 📖 ИНСТРУКЦИЯ ", 
                                   font=('Arial', 12, 'bold'), 
                                   bg='#16213e', fg='#ffd700',
                                   relief=tk.RAISED, bd=2)
        inst_frame.pack(pady=10, padx=20, fill='both')
        
        instructions = """
╔══════════════════════════════════════════════════════════════════╗
║  1. Нажми СТАРТ                                                 ║
║  2. ОТОЙДИ от компьютера на 2-3 метра (чтобы ты был в кадре)    ║
║  3. ВСТАНЬ В ПОЛНЫЙ РОСТ, смотри прямо в камеру                 ║
║  4. Программа САМА откалибруется через 5 секунд                 ║
║  5. ДВИГАЙ ГОЛОВОЙ - курсор двигается 1:1                       ║
║                                                              ║
║  🧠 ГОЛОВА            →  ПОВОРОТ КАМЕРЫ                         ║
║  ✊ КУЛАК             →  ЛЕВЫЙ КЛИК                              ║
║  🤘 РОКЕР             →  ПРАВЫЙ КЛИК                             ║
║  ✌️ ДВА ПАЛЬЦА        →  ИНВЕНТАРЬ (E)                          ║
║  👌 ЩИПОК             →  ПЕРЕТАСКИВАНИЕ                         ║
║  🦵 ШАГИ НА МЕСТЕ     →  ДВИЖЕНИЕ ВПЕРЁД                        ║
║  🦘 ПРЫЖОК            →  ПРОБЕЛ                                 ║
║  🔽 ПРИСЕДАНИЕ        →  SHIFT                                  ║
╚══════════════════════════════════════════════════════════════════╝
        """
        
        inst_label = tk.Label(inst_frame, text=instructions, 
                              font=('Courier', 9), bg='#16213e', 
                              fg='white', justify=tk.LEFT)
        inst_label.pack(pady=10, padx=10)
        
        # Настройки
        settings_frame = tk.LabelFrame(root, text=" ⚙️ НАСТРОЙКИ ", 
                                      font=('Arial', 12, 'bold'), 
                                      bg='#16213e', fg='#ffd700',
                                      relief=tk.RAISED, bd=2)
        settings_frame.pack(pady=10, padx=20, fill='x')
        
        # Чувствительность X
        tk.Label(settings_frame, text="Чувствительность X:", 
                font=('Arial', 10), bg='#16213e', fg='white').grid(row=0, column=0, padx=10, pady=5)
        self.speed_x_var = tk.DoubleVar(value=head_speed_x)
        self.speed_x_scale = tk.Scale(settings_frame, from_=0.5, to=8.0, resolution=0.1,
                                       orient=tk.HORIZONTAL, variable=self.speed_x_var,
                                       length=200, bg='#16213e', fg='white')
        self.speed_x_scale.grid(row=0, column=1, padx=10)
        self.speed_x_label = tk.Label(settings_frame, text=f"{head_speed_x:.1f}", 
                                      font=('Arial', 10), bg='#16213e', fg='#ffd700')
        self.speed_x_label.grid(row=0, column=2, padx=5)
        
        # Чувствительность Y
        tk.Label(settings_frame, text="Чувствительность Y:", 
                font=('Arial', 10), bg='#16213e', fg='white').grid(row=1, column=0, padx=10, pady=5)
        self.speed_y_var = tk.DoubleVar(value=head_speed_y)
        self.speed_y_scale = tk.Scale(settings_frame, from_=0.5, to=8.0, resolution=0.1,
                                       orient=tk.HORIZONTAL, variable=self.speed_y_var,
                                       length=200, bg='#16213e', fg='white')
        self.speed_y_scale.grid(row=1, column=1, padx=10)
        self.speed_y_label = tk.Label(settings_frame, text=f"{head_speed_y:.1f}", 
                                      font=('Arial', 10), bg='#16213e', fg='#ffd700')
        self.speed_y_label.grid(row=1, column=2, padx=5)
        
        def update_settings():
            global head_speed_x, head_speed_y
            head_speed_x = self.speed_x_var.get()
            head_speed_y = self.speed_y_var.get()
            self.speed_x_label.config(text=f"{head_speed_x:.1f}")
            self.speed_y_label.config(text=f"{head_speed_y:.1f}")
            self.status_label.config(text="✅ Настройки обновлены!", fg='#00ff00')
            self.root.after(2000, lambda: self.status_label.config(
                text="⚡ СТАТУС: Готов к работе", fg='#ffd700'))
        
        tk.Button(settings_frame, text="💾 ПРИМЕНИТЬ", command=update_settings,
                 bg='#00b894', fg='white', font=('Arial', 10, 'bold')).grid(row=0, column=3, rowspan=2, padx=20)
        
        # Статус
        self.status_label = tk.Label(root, text="⚡ СТАТУС: Нажми СТАРТ", 
                                     font=('Arial', 12, 'bold'), 
                                     bg='#1a1a2e', fg='#ffd700')
        self.status_label.pack(pady=10)
        
        # Таймер калибровки
        self.calib_timer_label = tk.Label(root, text="", 
                                          font=('Arial', 14, 'bold'), 
                                          bg='#1a1a2e', fg='#00ff00')
        self.calib_timer_label.pack(pady=5)
        
        # Кнопки
        button_frame = tk.Frame(root, bg='#1a1a2e')
        button_frame.pack(pady=20)
        
        self.start_button = tk.Button(button_frame, text="▶ СТАРТ", 
                                      command=self.start_control,
                                      bg='#00b894', fg='white', 
                                      font=('Arial', 16, 'bold'), padx=40, pady=15)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = tk.Button(button_frame, text="⏹️ СТОП", 
                                    command=self.stop_control,
                                    bg='#e74c3c', fg='white', 
                                    font=('Arial', 16, 'bold'), padx=40, pady=15,
                                    state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        self.exit_button = tk.Button(button_frame, text="❌ ВЫХОД", 
                                    command=self.exit_app,
                                    bg='#95a5a6', fg='white', 
                                    font=('Arial', 16, 'bold'), padx=40, pady=15)
        self.exit_button.pack(side=tk.LEFT, padx=10)
        
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
    
    def start_control(self):
        global running, face_mesh, hands, pose, calibrated
        
        if running:
            return
        
        camera_id = int(self.camera_id)
        
        test = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        if not test.isOpened():
            messagebox.showerror("Ошибка", "Камера не работает!")
            return
        test.release()
        
        # Инициализация
        face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3
        )
        
        hands = mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3,
            model_complexity=0
        )
        
        pose = mp_pose.Pose(
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3,
            model_complexity=0
        )
        
        running = True
        calibrated = False
        
        self.status_label.config(text="🟡 СТАТУС: КАЛИБРОВКА ЧЕРЕЗ 5 СЕКУНД...", fg='#ffd700')
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Запускаем поток
        self.thread = threading.Thread(target=self.control_loop, args=(camera_id,))
        self.thread.daemon = True
        self.thread.start()
        
        # Запускаем таймер калибровки в основном потоке
        self.start_calibration_timer()
    
    def start_calibration_timer(self):
        """Обратный отсчёт перед калибровкой"""
        def countdown(seconds):
            if seconds > 0 and running:
                self.calib_timer_label.config(text=f"⏰ ВСТАНЬ В ПОЛНЫЙ РОСТ! {seconds}...", fg='#ffd700')
                self.root.after(1000, lambda: countdown(seconds - 1))
            elif running:
                self.calib_timer_label.config(text="🎯 КАЛИБРОВКА... СМОТРИ ПРЯМО!", fg='#00ff00')
                self.root.after(1000, lambda: self.calib_timer_label.config(text="✅ КАЛИБРОВКА ГОТОВА! ДВИГАЙ ГОЛОВОЙ", fg='#00ff00'))
                self.root.after(3000, lambda: self.calib_timer_label.config(text=""))
        
        countdown(5)
    
    def auto_calibrate(self, nose_x, nose_y):
        """Автоматическая калибровка"""
        global calibrated, calib_nose_x, calib_nose_y
        
        if not calibrated:
            calib_nose_x = nose_x
            calib_nose_y = nose_y
            calibrated = True
            self.status_label.config(text="✅ СТАТУС: ОТКАЛИБРОВАНО! ДВИГАЙ ГОЛОВОЙ", fg='#00ff00')
            print(f"📏 Автокалибровка: нос в центре ({calib_nose_x:.3f}, {calib_nose_y:.3f})")
            return True
        return False
    
    def get_hand_gesture(self, hand):
        fingers = []
        # Большой палец
        if hand.landmark[4].x > hand.landmark[3].x:
            fingers.append(1)
        else:
            fingers.append(0)
        # Остальные
        for tip in [8, 12, 16, 20]:
            if hand.landmark[tip].y < hand.landmark[tip-2].y:
                fingers.append(1)
            else:
                fingers.append(0)
        
        thumb, index, middle, ring, pinky = fingers
        
        if sum(fingers) == 0:
            return "FIST"
        if index == 1 and middle == 1 and ring == 0 and pinky == 0:
            return "PEACE"
        if index == 1 and middle == 0 and ring == 0 and pinky == 1:
            return "ROCK"
        if thumb == 1 and index == 1 and middle == 0 and ring == 0 and pinky == 0:
            return "PINCH"
        if index == 1 and middle == 0 and ring == 0 and pinky == 0:
            return "POINTER"
        return "UNKNOWN"
    
    def control_loop(self, camera_id):
        global running, cap, cursor_x, cursor_y, calibrated, calib_nose_x, calib_nose_y, fps_list
        
        cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        cap.set(cv2.CAP_PROP_FPS, 120)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Для плавности
        smooth_x, smooth_y = screen_width // 2, screen_height // 2
        
        # Для кликов и действий
        left_click_sent = False
        right_click_sent = False
        inventory_sent = False
        drag_active = False
        w_pressed = False
        last_gesture = None
        last_action_time = 0
        
        # Для FPS
        fps_counter = 0
        fps_time = time.time()
        current_fps = 0
        
        # Флаг что калибровка была выполнена
        calibration_done = False
        
        while running:
            loop_start = time.time()
            
            ret, frame = cap.read()
            if not ret:
                continue
            
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # ========== ЛИЦО ==========
            face_results = face_mesh.process(rgb)
            
            if face_results.multi_face_landmarks:
                face = face_results.multi_face_landmarks[0]
                nose = face.landmark[1]
                nose_x = nose.x
                nose_y = nose.y
                
                # Рисуем лицо
                mp_drawing.draw_landmarks(
                    frame, face, mp_face_mesh.FACEMESH_CONTOURS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=1)
                )
                
                # АВТОМАТИЧЕСКАЯ КАЛИБРОВКА (первый кадр с лицом)
                if not calibration_done:
                    calibration_done = self.auto_calibrate(nose_x, nose_y)
                
                if calibrated:
                    # Вычисляем отклонение
                    offset_x = (nose_x - calib_nose_x) * head_speed_x
                    offset_y = (nose_y - calib_nose_y) * head_speed_y
                    
                    # Мёртвая зона
                    if abs(offset_x) < deadzone:
                        offset_x = 0
                    if abs(offset_y) < deadzone:
                        offset_y = 0
                    
                    # Новая позиция
                    center_x, center_y = screen_width // 2, screen_height // 2
                    new_x = center_x + offset_x * screen_width
                    new_y = center_y + offset_y * screen_height
                    
                    new_x = max(0, min(screen_width - 1, new_x))
                    new_y = max(0, min(screen_height - 1, new_y))
                    
                    # Сглаживание
                    smooth_x = int(smooth_x * (1 - smoothing) + new_x * smoothing)
                    smooth_y = int(smooth_y * (1 - smoothing) + new_y * smoothing)
                    cursor_x, cursor_y = smooth_x, smooth_y
                    
                    pyautogui.moveTo(cursor_x, cursor_y)
                    
                    cv2.putText(frame, f"POS: {cursor_x},{cursor_y}", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
                else:
                    cv2.putText(frame, "ЖДЁМ КАЛИБРОВКИ...", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                
                cv2.putText(frame, f"NOSE: {nose_x:.3f},{nose_y:.3f}", (10, 35),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            
            # ========== РУКИ ==========
            hand_results = hands.process(rgb)
            if hand_results.multi_hand_landmarks:
                for hand in hand_results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
                    gesture = self.get_hand_gesture(hand)
                    current_time = time.time()
                    
                    cv2.putText(frame, f"GESTURE: {gesture}", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                    
                    # Левый клик
                    if gesture == "FIST":
                        if not left_click_sent:
                            pyautogui.click(button='left')
                            left_click_sent = True
                            cv2.putText(frame, "✊ LEFT", (10, 120),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    else:
                        left_click_sent = False
                    
                    # Правый клик
                    if gesture == "ROCK" and current_time - last_action_time > 0.3:
                        pyautogui.click(button='right')
                        last_action_time = current_time
                        cv2.putText(frame, "🤘 RIGHT", (10, 150),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                    
                    # Инвентарь
                    if gesture == "PEACE" and gesture != last_gesture:
                        if current_time - last_action_time > 0.3:
                            pyautogui.press('e')
                            last_action_time = current_time
                            cv2.putText(frame, "🎒 INV", (10, 180),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 165, 0), 2)
                    
                    # Перетаскивание
                    if gesture == "PINCH":
                        if not drag_active:
                            pyautogui.mouseDown(button='left')
                            drag_active = True
                            cv2.putText(frame, "👌 DRAG", (10, 210),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                    else:
                        if drag_active:
                            pyautogui.mouseUp(button='left')
                            drag_active = False
                    
                    last_gesture = gesture
            
            # ========== ПОЗА ==========
            pose_results = pose.process(rgb)
            if pose_results.pose_landmarks:
                landmarks = pose_results.pose_landmarks.landmark
                
                # Ходьба
                left_ankle = landmarks[27].y
                right_ankle = landmarks[28].y
                
                if abs(left_ankle - right_ankle) > 0.05:
                    if not w_pressed:
                        pyautogui.keyDown('w')
                        w_pressed = True
                        cv2.putText(frame, "🚶 W", (10, 240),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
                else:
                    if w_pressed:
                        pyautogui.keyUp('w')
                        w_pressed = False
                
                # Прыжок
                if left_ankle < 0.3 and right_ankle < 0.3:
                    pyautogui.press('space')
                    cv2.putText(frame, "🦘 JUMP", (10, 270),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                    time.sleep(0.2)
                
                # Приседание
                knee = landmarks[25].y
                hip = landmarks[23].y
                if knee - hip > 0.12:
                    pyautogui.keyDown('shift')
                    cv2.putText(frame, "🔽 CROUCH", (10, 300),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 165, 0), 1)
                else:
                    pyautogui.keyUp('shift')
            
            # ========== FPS ==========
            fps_counter += 1
            if time.time() - fps_time >= 1.0:
                current_fps = fps_counter
                fps_counter = 0
                fps_time = time.time()
                fps_list.append(current_fps)
            
            avg_fps = sum(fps_list) // len(fps_list) if fps_list else 0
            
            cv2.putText(frame, f"FPS: {current_fps}", (10, frame.shape[0] - 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.putText(frame, "ESC STOP", (frame.shape[1] - 80, frame.shape[0] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            cv2.imshow("MINECRAFT BODY CONTROL", frame)
            
            if cv2.waitKey(1) & 0xFF == 27:
                break
            
            # Контроль для 100+ FPS
            elapsed = time.time() - loop_start
            if elapsed < 0.01:
                time.sleep(0.01 - elapsed)
        
        self.stop_control()
    
    def stop_control(self):
        global running, cap, face_mesh, hands, pose, calibrated
        running = False
        if cap:
            cap.release()
        if face_mesh:
            face_mesh.close()
        if hands:
            hands.close()
        if pose:
            pose.close()
        cv2.destroyAllWindows()
        pyautogui.keyUp('w')
        pyautogui.keyUp('shift')
        calibrated = False
        self.status_label.config(text="⚡ СТАТУС: ОСТАНОВЛЕН", fg='#ff6b6b')
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.calib_timer_label.config(text="")
    
    def exit_app(self):
        self.stop_control()
        self.root.quit()
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    print("=" * 50)
    print("MINECRAFT BODY CONTROL - 100+ FPS")
    print("АВТОМАТИЧЕСКАЯ КАЛИБРОВКА")
    print("=" * 50)
    print("\nИНСТРУКЦИЯ:")
    print("1. Нажми СТАРТ")
    print("2. ОТОЙДИ ОТ КОМПЬЮТЕРА (чтобы быть в кадре полностью)")
    print("3. ВСТАНЬ В ПОЛНЫЙ РОСТ, смотри прямо")
    print("4. Через 5 секунд программа САМА откалибруется")
    print("5. Двигай головой - камера поворачивается!")
    print("=" * 50)
    root = tk.Tk()
    app = MinecraftBodyControl(root)
    root.mainloop()