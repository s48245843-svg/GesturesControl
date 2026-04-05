import cv2
import mediapipe as mp
import pyautogui
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import time

# Инициализация
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Глобальные переменные
running = False
cap = None
hands = None
screen_width, screen_height = pyautogui.size()
prev_cursor_pos = None

def find_working_cameras():
    """Находит все работающие камеры"""
    working = []
    for i in range(5):
        try:
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    working.append(str(i))
                    print(f"✅ Камера {i} работает")
                else:
                    print(f"⚠️ Камера {i} открывается но нет кадра")
            else:
                print(f"❌ Камера {i} не открывается")
            cap.release()
        except:
            pass
    if not working:
        working = ["0"]
        print("⚠️ Камеры не найдены, использую 0")
    return working

class GestureControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GESTURES CONTROL - v2.1")
        self.root.geometry("800x750")
        self.root.configure(bg='#1a1a2e')
        self.root.resizable(False, False)
        
        # Настройки чувствительности
        self.sensitivity = 1.5
        
        # Находим камеры
        self.available_cameras = find_working_cameras()
        
        # Красивый заголовок
        title_text = """
╔══════════════════════════════════════════════════════════════════╗
║     ██████╗ ███████╗███████╗████████╗██╗   ██╗██████╗           ║
║    ██╔════╝ ██╔════╝██╔════╝╚══██╔══╝██║   ██║██╔══██╗          ║
║    ██║  ███╗█████╗  ███████╗   ██║   ██║   ██║██████╔╝          ║
║    ██║   ██║██╔══╝  ╚════██║   ██║   ██║   ██║██╔══██╗          ║
║    ╚██████╔╝███████╗███████║   ██║   ╚██████╔╝██║  ██║          ║
║     ╚═════╝ ╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝          ║
║                   GESTURES CONTROL - v2.1                        ║
╚══════════════════════════════════════════════════════════════════╝
        """
        
        title_label = tk.Label(root, text=title_text, 
                               font=('Courier', 8), bg='#1a1a2e', 
                               fg='#00ff00', justify=tk.LEFT)
        title_label.pack(pady=10)
        
        # Инструкция
        inst_frame = tk.LabelFrame(root, text=" 📖 ИНСТРУКЦИЯ ПО ЖЕСТАМ ", 
                                   font=('Arial', 12, 'bold'), 
                                   bg='#16213e', fg='#ffd700',
                                   relief=tk.RAISED, bd=2)
        inst_frame.pack(pady=10, padx=20, fill='both')
        
        instructions = """
  ☝️ ТОЛЬКО УКАЗАТЕЛЬНЫЙ палец    →  ПЕРЕМЕЩЕНИЕ КУРСОРА
  ✌️ УКАЗАТЕЛЬНЫЙ + СРЕДНИЙ      →  СКРОЛЛИНГ
  ✊ КУЛАК                       →  ЛЕВЫЙ КЛИК
  🤘 РОКЕР (указ. + мизинец)     →  ПРАВЫЙ КЛИК
  🖐️ ВСЕ ПАЛЬЦЫ РАСКРЫТЫ        →  ПАУЗА
        """
        
        inst_label = tk.Label(inst_frame, text=instructions, 
                              font=('Courier', 11), bg='#16213e', 
                              fg='white', justify=tk.LEFT)
        inst_label.pack(pady=10, padx=10)
        
        # Настройки чувствительности
        sens_frame = tk.LabelFrame(root, text=" 🎚️ ЧУВСТВИТЕЛЬНОСТЬ ", 
                                   font=('Arial', 12, 'bold'),
                                   bg='#1a1a2e', fg='#e74c3c',
                                   relief=tk.RAISED, bd=2)
        sens_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(sens_frame, text="Множитель скорости:", 
                font=('Arial', 11), bg='#1a1a2e', fg='white').pack(side=tk.LEFT, padx=10)
        
        self.sens_label = tk.Label(sens_frame, text=f"{self.sensitivity:.1f}x", 
                                   font=('Arial', 14, 'bold'), bg='#1a1a2e', fg='#ffd700')
        self.sens_label.pack(side=tk.LEFT, padx=10)
        
        tk.Button(sens_frame, text="➖", command=self.sens_minus,
                 bg='#e67e22', fg='white', font=('Arial', 12, 'bold'), width=3).pack(side=tk.LEFT, padx=5)
        tk.Button(sens_frame, text="➕", command=self.sens_plus,
                 bg='#e67e22', fg='white', font=('Arial', 12, 'bold'), width=3).pack(side=tk.LEFT, padx=5)
        tk.Button(sens_frame, text="СБРОС", command=self.sens_reset,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)
        
        # Выбор камеры
        camera_frame = tk.Frame(root, bg='#1a1a2e')
        camera_frame.pack(pady=10)
        
        tk.Label(camera_frame, text="Выберите камеру:", 
                font=('Arial', 11), bg='#1a1a2e', fg='white').pack(side=tk.LEFT, padx=10)
        
        self.camera_var = tk.StringVar(value=self.available_cameras[0] if self.available_cameras else "0")
        self.camera_combo = ttk.Combobox(camera_frame, textvariable=self.camera_var, 
                                         values=self.available_cameras, width=15, state='readonly')
        self.camera_combo.pack(side=tk.LEFT, padx=10)
        
        tk.Button(camera_frame, text="📷 ТЕСТ", command=self.test_camera,
                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)
        
        # Статус
        self.status_label = tk.Label(root, text="⚡ СТАТУС: Ожидание запуска", 
                                     font=('Arial', 11, 'bold'), 
                                     bg='#1a1a2e', fg='#ff6b6b')
        self.status_label.pack(pady=10)
        
        # Кнопки
        button_frame = tk.Frame(root, bg='#1a1a2e')
        button_frame.pack(pady=20)
        
        self.start_button = tk.Button(button_frame, text="▶ СТАРТ", 
                                      command=self.start_control,
                                      bg='#00b894', fg='white', 
                                      font=('Arial', 14, 'bold'), padx=30, pady=10)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = tk.Button(button_frame, text="⏹️ СТОП", 
                                    command=self.stop_control,
                                    bg='#e74c3c', fg='white', 
                                    font=('Arial', 14, 'bold'), padx=30, pady=10,
                                    state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        self.exit_button = tk.Button(button_frame, text="❌ ВЫХОД", 
                                    command=self.exit_app,
                                    bg='#95a5a6', fg='white', 
                                    font=('Arial', 14, 'bold'), padx=30, pady=10)
        self.exit_button.pack(side=tk.LEFT, padx=10)
        
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
    
    def sens_plus(self):
        if self.sensitivity < 3.0:
            self.sensitivity = round(self.sensitivity + 0.2, 1)
            self.sens_label.config(text=f"{self.sensitivity:.1f}x")
    
    def sens_minus(self):
        if self.sensitivity > 0.3:
            self.sensitivity = round(self.sensitivity - 0.2, 1)
            self.sens_label.config(text=f"{self.sensitivity:.1f}x")
    
    def sens_reset(self):
        self.sensitivity = 1.0
        self.sens_label.config(text="1.0x")
    
    def test_camera(self):
        cam_id = int(self.camera_var.get())
        cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                cv2.imshow(f"Camera {cam_id} - Press ESC", frame)
                cv2.waitKey(2000)
                cv2.destroyAllWindows()
                self.status_label.config(text="✅ Камера работает!", fg='#00ff00')
            else:
                self.status_label.config(text="❌ Кадр не идёт!", fg='#ff0000')
            cap.release()
        else:
            self.status_label.config(text="❌ Камера не открывается!", fg='#ff0000')
        self.root.after(2000, lambda: self.status_label.config(
            text="⚡ СТАТУС: Ожидание запуска", fg='#ff6b6b'))
    
    def start_control(self):
        global running, hands
        
        if running:
            return
        
        camera_id = int(self.camera_var.get())
        
        test_cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        if not test_cap.isOpened():
            messagebox.showerror("Ошибка", f"Камера {camera_id} не работает!")
            return
        test_cap.release()
        
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        running = True
        self.status_label.config(text="✅ РАБОТАЕТ!", fg='#00ff00')
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.thread = threading.Thread(target=self.control_loop, args=(camera_id,))
        self.thread.daemon = True
        self.thread.start()
    
    def count_fingers(self, hand):
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
        return fingers
    
    def get_gesture(self, fingers):
        if sum(fingers) == 0:
            return "FIST"
        if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            return "POINTER"
        if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
            return "TWO_FINGERS"
        if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 1:
            return "ROCK"
        return "UNKNOWN"
    
    def control_loop(self, camera_id):
        global running, cap, prev_cursor_pos
        
        cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        left_click = False
        right_click = False
        scroll_y = None
        
        while running:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)
            
            if results.multi_hand_landmarks:
                for hand in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
                    fingers = self.count_fingers(hand)
                    gesture = self.get_gesture(fingers)
                    
                    cv2.putText(frame, f"Gesture: {gesture}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    if gesture == "POINTER":
                        x = int(hand.landmark[8].x * screen_width)
                        y = int(hand.landmark[8].y * screen_height)
                        if prev_cursor_pos:
                            x = int(prev_cursor_pos[0] * 0.7 + x * 0.3)
                            y = int(prev_cursor_pos[1] * 0.7 + y * 0.3)
                        prev_cursor_pos = (x, y)
                        pyautogui.moveTo(x, y)
                        cv2.putText(frame, "MOVING", (10, 60),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                        left_click = False
                        right_click = False
                    
                    elif gesture == "TWO_FINGERS":
                        cy = hand.landmark[12].y * screen_height
                        if scroll_y:
                            delta = cy - scroll_y
                            if abs(delta) > 15:
                                pyautogui.scroll(-int(delta/15))
                        scroll_y = cy
                        cv2.putText(frame, "SCROLLING", (10, 60),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                    
                    elif gesture == "FIST" and not left_click:
                        pyautogui.click(button='left')
                        left_click = True
                        cv2.putText(frame, "LEFT CLICK", (10, 60),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    
                    elif gesture == "ROCK" and not right_click:
                        pyautogui.click(button='right')
                        right_click = True
                        cv2.putText(frame, "RIGHT CLICK", (10, 60),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                    
                    else:
                        left_click = False
                        right_click = False
                        scroll_y = None
            
            cv2.putText(frame, "ESC to stop", (10, frame.shape[0]-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
            cv2.imshow("GESTURES CONTROL", frame)
            
            if cv2.waitKey(1) & 0xFF == 27:
                break
        
        self.stop_control()
    
    def stop_control(self):
        global running, cap, hands
        running = False
        if cap:
            cap.release()
        if hands:
            hands.close()
        cv2.destroyAllWindows()
        self.status_label.config(text="⏹️ ОСТАНОВЛЕН", fg='#ff6b6b')
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def exit_app(self):
        self.stop_control()
        self.root.quit()
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    print("🔍 ПОИСК КАМЕР...")
    print("=" * 40)
    root = tk.Tk()
    app = GestureControlApp(root)
    root.mainloop()