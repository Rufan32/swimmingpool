import tkinter as tk
import random
import math
import numpy as np
from collections import deque
import pyaudio

class VoiceControlledPool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎤 声音交互海豹泳池")
        self.root.geometry("800x600")
        self.root.configure(bg='#e0f7fa')
        
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg='#e0f7fa', highlightthickness=0)
        self.canvas.pack()
        
        self.waves = []
        self.seals = []
        self.fishes = []
        self.volume = 0
        self.volume_history = deque(maxlen=10)
        self.is_listening = False
        
        self.pool_blue = '#87ceeb'
        
        self.create_pool()
        self.create_seals()
        self.create_fishes()
        
        self.setup_audio()
        
        self.animate()
    
    def create_pool(self):
        self.canvas.create_rectangle(100, 100, 700, 500, fill=self.pool_blue, outline='#78909c', width=3)
        
        self.canvas.create_rectangle(90, 90, 710, 100, fill='#78909c', outline='')
        self.canvas.create_rectangle(90, 500, 710, 510, fill='#78909c', outline='')
        self.canvas.create_rectangle(90, 100, 100, 500, fill='#78909c', outline='')
        self.canvas.create_rectangle(700, 100, 710, 500, fill='#78909c', outline='')
        
        self.create_pool_grid()

    def create_pool_grid(self):
        grid_spacing = 30
        grid_color = "#ffffff"
        
        for y in range(100, 501, grid_spacing):
            self.canvas.create_line(100, y, 700, y, fill=grid_color, width=1)
        
        for x in range(100, 701, grid_spacing):
            self.canvas.create_line(x, 100, x, 500, fill=grid_color, width=1)

    def create_fishes(self):
        salmon_color = '#FF8C69'
        
        positions = [
            (200, 95), (350, 95), (500, 95),
            (200, 505), (350, 505), (500, 505),
            (95, 200), (95, 350), (95, 400),
            (705, 200), (705, 350), (705, 400)
        ]
        
        for x, y in positions:
            fish = {
                'x': x,
                'y': y,
                'size': random.randint(15, 25),
                'color': salmon_color,
                'direction': random.choice([0, 1]),
                'eaten': False,
                'ids': []
            }
            self.fishes.append(fish)
            self.draw_fish(fish)
    
    def draw_fish(self, fish):
        for item_id in fish['ids']:
            self.canvas.delete(item_id)
        fish['ids'] = []
        
        size = fish['size']
        x, y = fish['x'], fish['y']
        
        if fish['direction'] == 0:
            body = self.canvas.create_oval(
                x - size, y - size/2,
                x + size, y + size/2,
                fill=fish['color'], outline='#D2691E', width=1
            )
            tail_points = [
                x + size, y,
                x + size * 1.5, y - size/2,
                x + size * 1.5, y + size/2
            ]
        else:
            body = self.canvas.create_oval(
                x - size/2, y - size,
                x + size/2, y + size,
                fill=fish['color'], outline='#D2691E', width=1
            )
            tail_points = [
                x, y + size,
                x - size/2, y + size * 1.5,
                x + size/2, y + size * 1.5
            ]
        
        fish['ids'].append(body)
        
        tail = self.canvas.create_polygon(tail_points, fill=fish['color'], 
                                        outline='#D2691E', width=1)
        fish['ids'].append(tail)
        
        eye_size = size * 0.15
        if fish['direction'] == 0:
            eye = self.canvas.create_oval(
                x - size/2, y - eye_size/2,
                x - size/2 + eye_size, y + eye_size/2,
                fill='black', outline=''
            )
        else:
            eye = self.canvas.create_oval(
                x - eye_size/2, y - size/2,
                x + eye_size/2, y - size/2 + eye_size,
                fill='black', outline=''
            )
        fish['ids'].append(eye)

    def create_seals(self):
        for _ in range(6):
            seal = {
                'x': random.randint(150, 650),
                'y': random.randint(150, 450),
                'size': random.randint(35, 45),
                'speed_x': random.uniform(-0.8, 0.8),
                'speed_y': random.uniform(-0.3, 0.3),
                'oscillation': random.uniform(0, 2 * math.pi),
                'amplitude': 0,
                'target_amplitude': 0,
                'direction': random.randint(0, 3),
                'has_salmon': False,
                'salmon_timer': 0,
                'ids': []
            }
            self.seals.append(seal)
        
        for i in range(5):
            wave = {
                'x': random.randint(120, 680),
                'y': random.randint(120, 480),
                'radius': 0,
                'max_radius': random.randint(30, 60),
                'speed': random.uniform(0.5, 1.0),
                'alpha': 1.0,
                'ids': []
            }
            self.waves.append(wave)
    
    def check_fish_collision(self, seal):
        for fish in self.fishes:
            if fish['eaten']:
                continue
                
            distance = math.sqrt((seal['x'] - fish['x'])**2 + (seal['y'] - fish['y'])**2)
            
            if distance < seal['size'] + fish['size']:
                fish['eaten'] = True
                for item_id in fish['ids']:
                    self.canvas.delete(item_id)
                fish['ids'] = []
                
                seal['has_salmon'] = True
                seal['salmon_timer'] = 300
                
                self.create_new_fish()
                break
    
    def create_new_fish(self):
        salmon_color = '#FF8C69'
        
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top':
            x, y = random.randint(120, 680), 95
            direction = 0
        elif edge == 'bottom':
            x, y = random.randint(120, 680), 505
            direction = 0
        elif edge == 'left':
            x, y = 95, random.randint(120, 480)
            direction = 1
        else:
            x, y = 705, random.randint(120, 480)
            direction = 1
        
        fish = {
            'x': x,
            'y': y,
            'size': random.randint(15, 25),
            'color': salmon_color,
            'direction': direction,
            'eaten': False,
            'ids': []
        }
        self.fishes.append(fish)
        self.draw_fish(fish)
    
    def draw_salmon_in_hand(self, seal, hand_x, hand_y, direction):
        salmon_size = seal['size'] * 0.4
        
        if direction == 0:
            salmon_x, salmon_y = hand_x, hand_y - salmon_size/2
            salmon_direction = 1
        elif direction == 1:
            salmon_x, salmon_y = hand_x + salmon_size/2, hand_y
            salmon_direction = 0
        elif direction == 2:
            salmon_x, salmon_y = hand_x, hand_y + salmon_size/2
            salmon_direction = 1
        else:
            salmon_x, salmon_y = hand_x - salmon_size/2, hand_y
            salmon_direction = 0
        
        if salmon_direction == 0:
            body = self.canvas.create_oval(
                salmon_x - salmon_size, salmon_y - salmon_size/2,
                salmon_x + salmon_size, salmon_y + salmon_size/2,
                fill='#FF8C69', outline='#D2691E', width=1
            )
            tail_points = [
                salmon_x + salmon_size, salmon_y,
                salmon_x + salmon_size * 1.5, salmon_y - salmon_size/2,
                salmon_x + salmon_size * 1.5, salmon_y + salmon_size/2
            ]
        else:
            body = self.canvas.create_oval(
                salmon_x - salmon_size/2, salmon_y - salmon_size,
                salmon_x + salmon_size/2, salmon_y + salmon_size,
                fill='#FF8C69', outline='#D2691E', width=1
            )
            tail_points = [
                salmon_x, salmon_y + salmon_size,
                salmon_x - salmon_size/2, salmon_y + salmon_size * 1.5,
                salmon_x + salmon_size/2, salmon_y + salmon_size * 1.5
            ]
        
        seal['ids'].append(body)
        
        tail = self.canvas.create_polygon(tail_points, fill='#FF8C69', 
                                        outline='#D2691E', width=1)
        seal['ids'].append(tail)
        
        eye_size = salmon_size * 0.15
        if salmon_direction == 0:
            eye = self.canvas.create_oval(
                salmon_x - salmon_size/2, salmon_y - eye_size/2,
                salmon_x - salmon_size/2 + eye_size, salmon_y + eye_size/2,
                fill='black', outline=''
            )
        else:
            eye = self.canvas.create_oval(
                salmon_x - eye_size/2, salmon_y - salmon_size/2,
                salmon_x + eye_size/2, salmon_y - salmon_size/2 + eye_size,
                fill='black', outline=''
            )
        seal['ids'].append(eye)
    
    def draw_seal(self, seal):
        for item_id in seal['ids']:
            self.canvas.delete(item_id)
        seal['ids'] = []
        
        size = seal['size']
        x, y = seal['x'], seal['y']
        direction = seal['direction']
        
        swing = math.sin(seal['oscillation']) * seal['amplitude']
        current_y = y + swing
        
        if direction == 0:
            body_x, body_y = x, current_y
            head_x, head_y = x, current_y - size * 0.5
            tail_x, tail_y = x, current_y + size * 0.6
            hand1_x, hand1_y = x - size * 0.4, current_y
            hand2_x, hand2_y = x + size * 0.4, current_y
            eye1_x, eye1_y = x - size * 0.15, current_y - size * 0.45
            eye2_x, eye2_y = x + size * 0.15, current_y - size * 0.45
            mouth_x, mouth_y = x, current_y - size * 0.3
            blush1_x, blush1_y = x - size * 0.25, current_y - size * 0.35
            blush2_x, blush2_y = x + size * 0.25, current_y - size * 0.35
            
        elif direction == 1:
            body_x, body_y = x, current_y
            head_x, head_y = x + size * 0.5, current_y
            tail_x, tail_y = x - size * 0.6, current_y
            hand1_x, hand1_y = x, current_y - size * 0.4
            hand2_x, hand2_y = x, current_y + size * 0.4
            eye1_x, eye1_y = x + size * 0.45, current_y - size * 0.15
            eye2_x, eye2_y = x + size * 0.45, current_y + size * 0.15
            mouth_x, mouth_y = x + size * 0.3, current_y
            blush1_x, blush1_y = x + size * 0.35, current_y - size * 0.25
            blush2_x, blush2_y = x + size * 0.35, current_y + size * 0.25
            
        elif direction == 2:
            body_x, body_y = x, current_y
            head_x, head_y = x, current_y + size * 0.5
            tail_x, tail_y = x, current_y - size * 0.6
            hand1_x, hand1_y = x - size * 0.4, current_y
            hand2_x, hand2_y = x + size * 0.4, current_y
            eye1_x, eye1_y = x - size * 0.15, current_y + size * 0.45
            eye2_x, eye2_y = x + size * 0.15, current_y + size * 0.45
            mouth_x, mouth_y = x, current_y + size * 0.3
            blush1_x, blush1_y = x - size * 0.25, current_y + size * 0.35
            blush2_x, blush2_y = x + size * 0.25, current_y + size * 0.35
            
        else:
            body_x, body_y = x, current_y
            head_x, head_y = x - size * 0.5, current_y
            tail_x, tail_y = x + size * 0.6, current_y
            hand1_x, hand1_y = x, current_y - size * 0.4
            hand2_x, hand2_y = x, current_y + size * 0.4
            eye1_x, eye1_y = x - size * 0.45, current_y - size * 0.15
            eye2_x, eye2_y = x - size * 0.45, current_y + size * 0.15
            mouth_x, mouth_y = x - size * 0.3, current_y
            blush1_x, blush1_y = x - size * 0.35, current_y - size * 0.25
            blush2_x, blush2_y = x - size * 0.35, current_y + size * 0.25
        
        body = self.canvas.create_oval(
            body_x - size * 0.6, body_y - size * 0.6,
            body_x + size * 0.6, body_y + size * 0.6,
            fill='white', outline='#DDDDDD', width=2
        )
        seal['ids'].append(body)
        
        head = self.canvas.create_oval(
            head_x - size * 0.3, head_y - size * 0.3,
            head_x + size * 0.3, head_y + size * 0.3,
            fill='white', outline='#DDDDDD', width=2
        )
        seal['ids'].append(head)
        
        eye_size = size * 0.08
        left_eye = self.canvas.create_oval(
            eye1_x - eye_size/2, eye1_y - eye_size/2,
            eye1_x + eye_size/2, eye1_y + eye_size/2,
            fill='black', outline=''
        )
        seal['ids'].append(left_eye)
        
        right_eye = self.canvas.create_oval(
            eye2_x - eye_size/2, eye2_y - eye_size/2,
            eye2_x + eye_size/2, eye2_y + eye_size/2,
            fill='black', outline=''
        )
        seal['ids'].append(right_eye)
        
        if direction == 0 or direction == 2:
            mouth_center = self.canvas.create_line(
                mouth_x, mouth_y,
                mouth_x, mouth_y + (size * 0.1 if direction == 0 else -size * 0.1),
                width=2, fill='black'
            )
            mouth_left = self.canvas.create_line(
                mouth_x, mouth_y + (size * 0.05 if direction == 0 else -size * 0.05),
                mouth_x - size * 0.08, mouth_y + (size * 0.08 if direction == 0 else -size * 0.08),
                width=2, fill='black'
            )
            mouth_right = self.canvas.create_line(
                mouth_x, mouth_y + (size * 0.05 if direction == 0 else -size * 0.05),
                mouth_x + size * 0.08, mouth_y + (size * 0.08 if direction == 0 else -size * 0.08),
                width=2, fill='black'
            )
        else:
            mouth_center = self.canvas.create_line(
                mouth_x, mouth_y,
                mouth_x + (size * 0.1 if direction == 1 else -size * 0.1), mouth_y,
                width=2, fill='black'
            )
            mouth_top = self.canvas.create_line(
                mouth_x + (size * 0.05 if direction == 1 else -size * 0.05), mouth_y,
                mouth_x + (size * 0.08 if direction == 1 else -size * 0.08), mouth_y - size * 0.08,
                width=2, fill='black'
            )
            mouth_bottom = self.canvas.create_line(
                mouth_x + (size * 0.05 if direction == 1 else -size * 0.05), mouth_y,
                mouth_x + (size * 0.08 if direction == 1 else -size * 0.08), mouth_y + size * 0.08,
                width=2, fill='black'
            )
            seal['ids'].append(mouth_top)
            seal['ids'].append(mouth_bottom)
        
        seal['ids'].append(mouth_center)
        if direction == 0 or direction == 2:
            seal['ids'].append(mouth_left)
            seal['ids'].append(mouth_right)
        
        if direction == 0:
            tail_points = [
                tail_x, tail_y,
                tail_x - size * 0.2, tail_y + size * 0.3,
                tail_x + size * 0.2, tail_y + size * 0.3
            ]
        elif direction == 1:
            tail_points = [
                tail_x, tail_y,
                tail_x - size * 0.3, tail_y - size * 0.2,
                tail_x - size * 0.3, tail_y + size * 0.2
            ]
        elif direction == 2:
            tail_points = [
                tail_x, tail_y,
                tail_x - size * 0.2, tail_y - size * 0.3,
                tail_x + size * 0.2, tail_y - size * 0.3
            ]
        else:
            tail_points = [
                tail_x, tail_y,
                tail_x + size * 0.3, tail_y - size * 0.2,
                tail_x + size * 0.3, tail_y + size * 0.2
            ]
            
        tail = self.canvas.create_polygon(tail_points, fill='white', 
                                        outline='#DDDDDD', width=1)
        seal['ids'].append(tail)
        
        hand_size = size * 0.12
        left_hand = self.canvas.create_oval(
            hand1_x - hand_size/2, hand1_y - hand_size/2,
            hand1_x + hand_size/2, hand1_y + hand_size/2,
            fill='white', outline='#DDDDDD', width=1
        )
        seal['ids'].append(left_hand)
        
        right_hand = self.canvas.create_oval(
            hand2_x - hand_size/2, hand2_y - hand_size/2,
            hand2_x + hand_size/2, hand2_y + hand_size/2,
            fill='white', outline='#DDDDDD', width=1
        )
        seal['ids'].append(right_hand)
        
        if seal['has_salmon']:
            if direction == 0:
                self.draw_salmon_in_hand(seal, hand2_x, hand2_y, direction)
            elif direction == 1:
                self.draw_salmon_in_hand(seal, hand2_x, hand2_y, direction)
            elif direction == 2:
                self.draw_salmon_in_hand(seal, hand1_x, hand1_y, direction)
            else:
                self.draw_salmon_in_hand(seal, hand1_x, hand1_y, direction)
        
        blush_size = size * 0.06
        left_blush = self.canvas.create_oval(
            blush1_x - blush_size/2, blush1_y - blush_size/2,
            blush1_x + blush_size/2, blush1_y + blush_size/2,
            fill='#FFB6C1', outline=''
        )
        seal['ids'].append(left_blush)
        
        right_blush = self.canvas.create_oval(
            blush2_x - blush_size/2, blush2_y - blush_size/2,
            blush2_x + blush_size/2, blush2_y + blush_size/2,
            fill='#FFB6C1', outline=''
        )
        seal['ids'].append(right_blush)
    
    def setup_audio(self):
        try:
            self.audio = pyaudio.PyAudio()
            self.CHUNK = 1024
            self.FORMAT = pyaudio.paInt16
            self.CHANNELS = 1
            self.RATE = 44100
            
            self.stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK,
                stream_callback=self.audio_callback
            )
            self.is_listening = True
            self.stream.start_stream()
            print("麦克风已启用，开始检测声音...")
            
        except Exception as e:
            print(f"无法访问麦克风: {e}")
            self.is_listening = False
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        if self.is_listening:
            try:
                audio_data = np.frombuffer(in_data, dtype=np.int16)
                volume = np.sqrt(np.mean(audio_data**2)) / 32768.0
                self.volume_history.append(volume)
                self.volume = min(1.0, np.mean(self.volume_history) * 5)
            except Exception as e:
                print(f"音频处理错误: {e}")
        
        return (in_data, pyaudio.paContinue)
    
    def update_waves(self):
        if self.volume > 0.05 and random.random() < self.volume * 0.5:
            new_wave = {
                'x': random.randint(120, 680),
                'y': random.randint(120, 480),
                'radius': 0,
                'max_radius': 15 + int(self.volume * 50),
                'speed': 0.3 + self.volume * 1.5,
                'alpha': 1.0,
                'ids': []
            }
            self.waves.append(new_wave)
        
        for wave in self.waves[:]:
            wave['radius'] += wave['speed']
            wave['alpha'] = 1.0 - (wave['radius'] / wave['max_radius'])
            
            if wave['alpha'] <= 0:
                self.waves.remove(wave)
                if wave['ids']:
                    for wave_id in wave['ids']:
                        self.canvas.delete(wave_id)
                continue
            
            if wave['ids']:
                for wave_id in wave['ids']:
                    self.canvas.delete(wave_id)
                wave['ids'] = []
            
            num_layers = 3
            base_radius = wave['radius']
            
            for i in range(num_layers):
                layer_radius = base_radius - i * 6
                if layer_radius > 0:
                    layer_alpha = wave['alpha'] * (1.0 - i * 0.3)
                    if layer_alpha > 0:
                        brightness = int(200 + 55 * layer_alpha)
                        color = f'#{brightness:02x}{brightness:02x}{brightness:02x}'
                        wave_id = self.canvas.create_oval(
                            wave['x'] - layer_radius, wave['y'] - layer_radius,
                            wave['x'] + layer_radius, wave['y'] + layer_radius,
                            outline=color, width=1
                        )
                        wave['ids'].append(wave_id)
    
    def animate(self):
        self.update_waves()
        
        for seal in self.seals:
            seal['target_amplitude'] = self.volume * 8
            seal['amplitude'] += (seal['target_amplitude'] - seal['amplitude']) * 0.2
            
            seal['x'] += seal['speed_x']
            seal['y'] += seal['speed_y'] + math.sin(seal['oscillation']) * seal['amplitude'] * 0.3
            seal['oscillation'] += 0.15
            
            if seal['x'] < 120:
                seal['speed_x'] = abs(seal['speed_x'])
                seal['direction'] = 1
            elif seal['x'] > 680:
                seal['speed_x'] = -abs(seal['speed_x'])
                seal['direction'] = 3
                
            if seal['y'] < 120:
                seal['speed_y'] = abs(seal['speed_y'])
                seal['direction'] = 2
            elif seal['y'] > 480:
                seal['speed_y'] = -abs(seal['speed_y'])
                seal['direction'] = 0
            
            self.check_fish_collision(seal)
            
            if seal['has_salmon']:
                seal['salmon_timer'] -= 1
                if seal['salmon_timer'] <= 0:
                    seal['has_salmon'] = False
            
            self.draw_seal(seal)
        
        self.canvas.delete("info")
        
        # 计算海豹抓到鱼的数量
        fish_caught = sum(1 for seal in self.seals if seal['has_salmon'])
        
        # 只显示海豹抓到鱼的数量
        self.canvas.create_text(400, 30, text=f"seal got {fish_caught} fish", 
                               fill="darkblue", font=("Arial", 16), tags="info")
        
        self.root.after(30, self.animate)
    
    def run(self):
        try:
            self.root.mainloop()
        finally:
            if self.is_listening:
                self.stream.stop_stream()
                self.stream.close()
            self.audio.terminate()

if __name__ == "__main__":
    try:
        pool = VoiceControlledPool()
        pool.run()
    except ImportError:
        print("错误: 需要安装pyaudio库")
        print("请运行: pip install pyaudio")
    except Exception as e:
        print(f"程序错误: {e}")