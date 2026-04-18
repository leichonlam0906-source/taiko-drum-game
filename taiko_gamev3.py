import pygame
import sys
import os
import json

# ==================== 初始化 ====================
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512 * 2)
pygame.mixer.music.set_volume(1.0)
pygame.mixer.set_num_channels(16)

pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("Taiko Drum Game")
clock = pygame.time.Clock()

# ==================== 路徑設定 ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")
BGM_DIR = os.path.join(BASE_DIR, "bgm")
SONGS_DIR = os.path.join(BASE_DIR, "songs")
LEVELS_DIR = os.path.join(BASE_DIR, "levels")

# 鼓聲
don_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "Don.wav"))
ka_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "Katsu.wav"))

# 選單 BGM
BGM_MENU = os.path.join(BGM_DIR, "Nebulite - Breath (freetouse.com).mp3")
BGM_TITLE = os.path.join(BGM_DIR, "Walen - Nostalgia Gaming (freetouse.com).mp3")

# ==================== 顏色 ====================
WHITE = (255, 255, 255)
RED = (230, 26, 26)
BLUE = (51, 144, 232)
BLACK = (0, 0, 0)
DARK_RED = (180, 20, 20)
DARK_BLUE = (30, 100, 200)
GOLD = (255, 215, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
ORANGE = (255, 100, 0)
YELLOW = (255, 255, 0)

# ==================== 字體設定 ====================
font_title = pygame.font.SysFont("PMingLiU", 72)
font_large = pygame.font.SysFont("PMingLiU", 48)
font_medium = pygame.font.SysFont("PMingLiU", 36)
font_small = pygame.font.SysFont("PMingLiU", 28)

# ==================== 輔助函數 ====================
def draw_gradient_rect(surface, color1, color2, rect):
    x, y, w, h = rect
    for i in range(h):
        ratio = i / h
        r = color1[0] * (1 - ratio) + color2[0] * ratio
        g = color1[1] * (1 - ratio) + color2[1] * ratio
        b = color1[2] * (1 - ratio) + color2[2] * ratio
        pygame.draw.line(surface, (int(r), int(g), int(b)), (x, y + i), (x + w, y + i))

def draw_rounded_rect(surface, color, rect, radius=10):
    x, y, w, h = rect
    if w < radius * 2 or h < radius * 2:
        pygame.draw.rect(surface, color, rect)
        return
    pygame.draw.rect(surface, color, (x + radius, y, w - radius * 2, h))
    pygame.draw.rect(surface, color, (x, y + radius, w, h - radius * 2))
    pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + radius, y + h - radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius)

def draw_centered_text(surface, text, font, color, y, shadow=False):
    text_surf = font.render(text, True, color)
    x = (surface.get_width() - text_surf.get_width()) // 2
    if shadow:
        shadow_surf = font.render(text, True, GRAY)
        surface.blit(shadow_surf, (x + 2, y + 2))
    surface.blit(text_surf, (x, y))

def draw_centered_text_in_rect(surface, text, font, color, rect, shadow=False):
    text_surf = font.render(text, True, color)
    x = rect[0] + (rect[2] - text_surf.get_width()) // 2
    y = rect[1] + (rect[3] - text_surf.get_height()) // 2
    if shadow:
        shadow_surf = font.render(text, True, GRAY)
        surface.blit(shadow_surf, (x + 2, y + 2))
    surface.blit(text_surf, (x, y))

# ==================== 載入所有關卡 ====================
def load_levels():
    levels = {}
    if not os.path.exists(LEVELS_DIR):
        os.makedirs(LEVELS_DIR)
        return levels
    
    for folder_name in os.listdir(LEVELS_DIR):
        folder_path = os.path.join(LEVELS_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue
        
        config_path = os.path.join(folder_path, "config.json")
        if not os.path.exists(config_path):
            print(f"警告：{folder_name} 缺少 config.json")
            continue
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        title = config.get("title", folder_name)
        levels[title] = {
            "title": title,
            "offset": config.get("offset", 0.0),
            "bgm": config.get("bgm", ""),
            "tempo_changes": config.get("tempo_changes", [[1.0, 120]]),
            "difficulties": {}
        }
        
        difficulties = ["Easy", "Normal", "Hard", "Master", "Ultra"]
        for diff in difficulties:
            diff_path = os.path.join(folder_path, f"{diff}.json")
            if os.path.exists(diff_path):
                with open(diff_path, "r", encoding="utf-8") as f:
                    diff_data = json.load(f)
                    levels[title]["difficulties"][diff] = diff_data
                    print(f"✅ 成功載入 {diff}.json，notes 數量：{len(diff_data.get('notes', []))}")
            else:
                print(f"警告：{folder_name} 缺少 {diff}.json")
    
    return levels

# ==================== 音符類 ====================
class Note:
    def __init__(self, time, note_type, start_x=800, target_x=100, speed=300):
        self.time = time
        self.note_type = note_type
        self.start_x = start_x
        self.target_x = target_x
        self.speed = speed
        self.hit = False
        self.missed = False
        self.hit_effect = 0

    def get_x(self, current_time):
        time_left = self.time - current_time
        x = self.target_x + time_left * self.speed
        return x

class RollNote:
    def __init__(self, start_time, end_time, start_x=800, target_x=100, speed=300):
        self.start_time = start_time
        self.end_time = end_time
        self.start_x = start_x
        self.target_x = target_x
        self.speed = speed
        self.hit = False
        self.missed = False
        self.roll_hits = 0

    def get_x(self, current_time):
        time_left = self.start_time - current_time
        x = self.target_x + time_left * self.speed
        return x

    def get_width(self, current_time):
        if current_time < self.start_time:
            return 0
        elif current_time > self.end_time:
            return 60
        else:
            progress = (current_time - self.start_time) / (self.end_time - self.start_time)
            return int(20 + progress * 60)

    def is_active(self, current_time):
        return self.start_time <= current_time <= self.end_time

    def is_done(self, current_time):
        return current_time > self.end_time

# ==================== 拍子轉時間（支援 BPM 變化）====================
def create_beat_to_time_function(tempo_changes, offset=0.0):
    if tempo_changes[0][0] != 1.0:
        tempo_changes.insert(0, [1.0, tempo_changes[0][1]])
    
    cache = {}
    printed_changes = set()
    
    def beat_to_time(beat):
        nonlocal printed_changes
        if beat in cache:
            return cache[beat]
        
        time = offset
        current_beat = 1.0
        current_bpm = tempo_changes[0][1]
        next_change_idx = 1
        
        while current_beat < beat:
            next_change_beat = tempo_changes[next_change_idx][0] if next_change_idx < len(tempo_changes) else float('inf')
            
            if beat <= next_change_beat:
                duration = (beat - current_beat) * (60 / current_bpm)
                time += duration
                current_beat = beat
            else:
                duration = (next_change_beat - current_beat) * (60 / current_bpm)
                time += duration
                current_beat = next_change_beat
                current_bpm = tempo_changes[next_change_idx][1]
                next_change_idx += 1
                
                change_key = f"{current_beat:.2f}_{current_bpm:.2f}"
                if change_key not in printed_changes:
                    print(f"[BPM Change] 拍子 {current_beat:.2f} → BPM {current_bpm:.2f}")
                    printed_changes.add(change_key)
        
        cache[beat] = time
        return time
    
    return beat_to_time

# ==================== 初始化遊戲 ====================
def init_game(level_data, difficulty):
    diff_data = level_data["difficulties"][difficulty]
    offset = level_data.get("offset", 0.0)
    tempo_changes = level_data.get("tempo_changes", [[1.0, 120]])
    
    beat_to_time = create_beat_to_time_function(tempo_changes, offset)
    base_speed = 300 * (tempo_changes[0][1] / 120)
    
    notes = []
    i = 0
    while i < len(diff_data["notes"]):
        item = diff_data["notes"][i]
        
        if len(item) >= 2 and item[1] == "roll_start" and i + 2 < len(diff_data["notes"]):
            start_beat = item[0]
            end_beat = diff_data["notes"][i + 1][0]
            start_time = beat_to_time(start_beat)
            end_time = beat_to_time(end_beat)
            notes.append(RollNote(start_time, end_time, speed=base_speed))
            i += 2
        else:
            beat = item[0]
            note_type = item[1]
            time = beat_to_time(beat)
            notes.append(Note(time, note_type, speed=base_speed))
            i += 1
    
    if notes:
        last_note = notes[-1]
        if isinstance(last_note, Note):
            print(f"⏱️ 最後一個音符時間：{last_note.time:.2f} 秒")
        elif isinstance(last_note, RollNote):
            print(f"⏱️ 最後一個連打結束時間：{last_note.end_time:.2f} 秒")
    
    bgm_path = level_data["bgm"]
    if not os.path.isabs(bgm_path):
        bgm_path = os.path.join(BASE_DIR, bgm_path)
    return notes, bgm_path

# ==================== 開始畫面 ====================
def show_title_screen():
    pygame.mixer.music.load(BGM_TITLE)
    pygame.mixer.music.play(-1)
    background = pygame.Surface((800, 400))
    draw_gradient_rect(background, (50, 50, 100), (100, 80, 150), (0, 0, 800, 400))
    taiko_center = (400, 180)
    waiting = True
    alpha = 0
    alpha_direction = 5
    while waiting:
        alpha += alpha_direction
        if alpha > 255 or alpha < 100:
            alpha_direction = -alpha_direction
        screen.blit(background, (0, 0))
        pygame.draw.ellipse(screen, DARK_RED, (taiko_center[0] - 80, taiko_center[1] - 40, 160, 80))
        pygame.draw.ellipse(screen, RED, (taiko_center[0] - 75, taiko_center[1] - 35, 150, 70))
        pygame.draw.circle(screen, GOLD, (taiko_center[0], taiko_center[1]), 15)
        pygame.draw.circle(screen, GOLD, (taiko_center[0] - 50, taiko_center[1]), 8)
        pygame.draw.circle(screen, GOLD, (taiko_center[0] + 50, taiko_center[1]), 8)
        draw_centered_text(screen, "TAIKO DRUM", font_title, GOLD, 50, shadow=True)
        color = ORANGE if alpha > 200 else WHITE
        draw_centered_text(screen, "Press SPACE to Start", font_medium, color, 280)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
        clock.tick(60)

# ==================== 選曲畫面 ====================
def select_song(levels_dict):
    pygame.mixer.music.load(BGM_MENU)
    pygame.mixer.music.play(-1)
    song_list = list(levels_dict.keys())
    selected_index = 0
    background = pygame.Surface((800, 400))
    draw_gradient_rect(background, (30, 30, 50), (60, 60, 90), (0, 0, 800, 400))
    while True:
        screen.blit(background, (0, 0))
        title_rect = (200, 30, 400, 60)
        draw_rounded_rect(screen, DARK_RED, title_rect, 15)
        draw_centered_text_in_rect(screen, "SELECT SONG", font_large, GOLD, title_rect)
        for i, song_name in enumerate(song_list):
            y = 130 + i * 60
            item_rect = (200, y - 20, 400, 50)
            bg_color = (80, 50, 50) if i == selected_index else (50, 50, 70)
            draw_rounded_rect(screen, bg_color, item_rect, 10)
            if i == selected_index:
                pygame.draw.rect(screen, GOLD, item_rect, 2, border_radius=10)
            color = GOLD if i == selected_index else WHITE
            draw_centered_text_in_rect(screen, song_name, font_medium, color, item_rect)
        
        pygame.draw.polygon(screen, GOLD, [(180, 345), (195, 330), (210, 345)])
        pygame.draw.polygon(screen, LIGHT_GRAY, [(182, 345), (195, 330), (208, 345)], 1)
        pygame.draw.polygon(screen, GOLD, [(180, 355), (195, 370), (210, 355)])
        pygame.draw.polygon(screen, LIGHT_GRAY, [(182, 355), (195, 367), (208, 355)], 1)
        select_text = font_small.render("Select", True, LIGHT_GRAY)
        select_rect = select_text.get_rect(center=(195, 375))
        screen.blit(select_text, select_rect)

        space_rect = (560, 325, 80, 30)
        draw_rounded_rect(screen, DARK_BLUE, space_rect, 8)
        draw_rounded_rect(screen, LIGHT_GRAY, (space_rect[0]+1, space_rect[1]+1, space_rect[2]-2, space_rect[3]-2), 6)
        space_key_text = font_small.render("SPACE", True, BLACK)
        space_key_rect = space_key_text.get_rect(center=(space_rect[0] + space_rect[2]//2, space_rect[1] + space_rect[3]//2))
        screen.blit(space_key_text, space_key_rect)
        confirm_text = font_small.render("Confirm", True, LIGHT_GRAY)
        confirm_rect = confirm_text.get_rect(center=(space_rect[0] + space_rect[2]//2, space_rect[1] + space_rect[3] + 20))
        screen.blit(confirm_text, confirm_rect)
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(song_list)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(song_list)
                elif event.key == pygame.K_SPACE:
                    return song_list[selected_index]
        clock.tick(60)

# ==================== 難度選擇畫面 ====================
def select_difficulty():
    difficulties = ["Easy", "Normal", "Hard", "Master", "Ultra"]
    selected_index = 1
    background = pygame.Surface((800, 400))
    draw_gradient_rect(background, (30, 30, 50), (60, 60, 90), (0, 0, 800, 400))
    diff_colors = [(100, 200, 100), (224, 81, 54), (255, 200, 50), (255, 80, 80), (200, 50, 200)]
    
    while True:
        screen.blit(background, (0, 0))
        title_rect = (180, 30, 440, 60)
        draw_rounded_rect(screen, DARK_BLUE, title_rect, 15)
        draw_centered_text_in_rect(screen, "SELECT DIFFICULTY", font_large, GOLD, title_rect)
        
        start_y = 100
        for i, diff in enumerate(difficulties):
            y = start_y + i * 45
            item_rect = (250, y - 15, 300, 38)
            bg_color = (80, 50, 50) if i == selected_index else (50, 50, 70)
            draw_rounded_rect(screen, bg_color, item_rect, 10)
            if i == selected_index:
                pygame.draw.rect(screen, GOLD, item_rect, 2, border_radius=10)
            color = GOLD if i == selected_index else diff_colors[i]
            draw_centered_text_in_rect(screen, diff, font_medium, color, item_rect)
        
        pygame.draw.polygon(screen, GOLD, [(180, 345), (195, 330), (210, 345)])
        pygame.draw.polygon(screen, LIGHT_GRAY, [(182, 345), (195, 330), (208, 345)], 1)
        pygame.draw.polygon(screen, GOLD, [(180, 355), (195, 370), (210, 355)])
        pygame.draw.polygon(screen, LIGHT_GRAY, [(182, 355), (195, 367), (208, 355)], 1)
        select_text = font_small.render("Select", True, LIGHT_GRAY)
        select_rect = select_text.get_rect(center=(195, 375))
        screen.blit(select_text, select_rect)

        space_rect = (560, 325, 80, 30)
        draw_rounded_rect(screen, DARK_BLUE, space_rect, 8)
        draw_rounded_rect(screen, LIGHT_GRAY, (space_rect[0]+1, space_rect[1]+1, space_rect[2]-2, space_rect[3]-2), 6)
        space_key_text = font_small.render("SPACE", True, BLACK)
        space_key_rect = space_key_text.get_rect(center=(space_rect[0] + space_rect[2]//2, space_rect[1] + space_rect[3]//2))
        screen.blit(space_key_text, space_key_rect)
        confirm_text = font_small.render("Confirm", True, LIGHT_GRAY)
        confirm_rect = confirm_text.get_rect(center=(space_rect[0] + space_rect[2]//2, space_rect[1] + space_rect[3] + 20))
        screen.blit(confirm_text, confirm_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(difficulties)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(difficulties)
                elif event.key == pygame.K_SPACE:
                    return difficulties[selected_index]
        
        clock.tick(60)

# ==================== 開始遊戲倒數 ====================
def show_game_start_screen():
    waiting = True
    background = pygame.Surface((800, 400))
    draw_gradient_rect(background, (100, 50, 50), (60, 30, 30), (0, 0, 800, 400))
    counter = 3
    last_tick = pygame.time.get_ticks()
    while waiting:
        current_tick = pygame.time.get_ticks()
        if current_tick - last_tick > 1000:
            counter -= 1
            last_tick = current_tick
            if counter <= 0:
                waiting = False
        screen.blit(background, (0, 0))
        if counter > 0:
            draw_centered_text(screen, str(counter), font_title, GOLD, 180)
        draw_centered_text(screen, "Get Ready!", font_large, WHITE, 80)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        clock.tick(60)

# ==================== 暫停畫面 ====================
def show_pause_screen():
    """顯示暫停畫面，返回是否應該繼續遊戲"""
    paused = True
    while paused:
        screen.fill(BLACK)
        draw_centered_text(screen, "GAME PAUSED", font_title, GOLD, 120)
        draw_centered_text(screen, "Press P to Resume", font_medium, WHITE, 200)
        draw_centered_text(screen, "Press ESC to Quit", font_small, LIGHT_GRAY, 250)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return True  # 繼續遊戲
                if event.key == pygame.K_ESCAPE:
                    return False  # 退出遊戲
        clock.tick(60)

def show_resume_countdown():
    """顯示恢復遊戲的倒數"""
    countdown = 3
    last_tick = pygame.time.get_ticks()
    background = pygame.Surface((800, 400))
    draw_gradient_rect(background, (20, 20, 40), (50, 50, 70), (0, 0, 800, 400))
    
    while countdown > 0:
        current_tick = pygame.time.get_ticks()
        if current_tick - last_tick >= 1000:
            countdown -= 1
            last_tick = current_tick
        
        screen.blit(background, (0, 0))
        draw_centered_text(screen, "RESUMING", font_title, GOLD, 120)
        if countdown > 0:
            draw_centered_text(screen, str(countdown), font_large, WHITE, 200)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        clock.tick(60)

# ==================== 結算畫面 ====================
def show_result_screen(stats, score):
    exit_enabled = False
    exit_start_time = pygame.time.get_ticks()
    waiting = True
    while waiting:
        screen.fill(WHITE)
        title = font_large.render("RESULT", True, BLACK)
        screen.blit(title, (350, 50))
        y = 80
        lines = [
            f"PERFECT:  {stats['perfect']}",
            f"GOOD:     {stats['good']}",
            f"OK:       {stats['ok']}",
            f"MISS:     {stats['miss']}",
            f"MAX COMBO: {stats['max_combo']}",
            f"TOTAL SCORE: {score}"
        ]
        for line in lines:
            text = font_medium.render(line, True, BLACK)
            screen.blit(text, (250, y))
            y += 40
        
        elapsed = (pygame.time.get_ticks() - exit_start_time) // 1000
        if not exit_enabled and elapsed >= 5:
            exit_enabled = True
        
        btn_color = (100, 200, 100) if exit_enabled else (150, 150, 150)
        btn_rect = pygame.Rect(650, 340, 100, 40)
        draw_rounded_rect(screen, btn_color, btn_rect, 8)
        pygame.draw.rect(screen, BLACK, btn_rect, 2)
        btn_text = font_small.render("EXIT", True, BLACK)
        text_rect = btn_text.get_rect(center=(btn_rect.centerx, btn_rect.centery))
        screen.blit(btn_text, text_rect)
        
        if not exit_enabled:
            timer_text = font_small.render(f"Wait {5 - elapsed} sec", True, (200, 0, 0))
            timer_rect = timer_text.get_rect(center=(700, 320))
            screen.blit(timer_text, timer_rect)
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and exit_enabled:
                if btn_rect.collidepoint(event.pos):
                    return False
        clock.tick(60)
    return False

# ==================== 遊戲主循環 ====================
def run_game(notes, bgm_path, start_time):
    pygame.mixer.music.load(bgm_path)
    pygame.mixer.music.play(0)

    score = 0
    combo = 0
    max_combo = 0
    judge_text = ""
    judge_display_time = 0
    
    stats = {"perfect": 0, "good": 0, "ok": 0, "miss": 0, "max_combo": 0}

    game_bg = pygame.Surface((800, 400))
    draw_gradient_rect(game_bg, (20, 20, 40), (50, 50, 70), (0, 0, 800, 400))

    pause_offset = 0
    pause_start = 0
    is_paused = False
    was_focused = True

    running = True
    game_finished = False

    while running:
        # =========================
        # 檢查焦點丟失（自動暫停）
        # =========================
        current_focused = pygame.key.get_focused()
        if not game_finished and current_focused != was_focused and not current_focused:
            # 焦點丟失，自動暫停
            if not is_paused:
                is_paused = True
                pygame.mixer.music.pause()
                pause_start = pygame.time.get_ticks()
        was_focused = current_focused

        # =========================
        # ⏸ 暫停畫面（手動 P 或焦點丟失）
        # =========================
        if is_paused and not game_finished:
            # 顯示暫停畫面
            screen.blit(game_bg, (0, 0))
            draw_centered_text(screen, "GAME PAUSED", font_title, GOLD, 120)
            draw_centered_text(screen, "Press P to Resume", font_medium, WHITE, 200)
            draw_centered_text(screen, "Press ESC to Quit", font_small, LIGHT_GRAY, 250)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        # 恢復遊戲，顯示倒數
                        show_resume_countdown()
                        pygame.mixer.music.unpause()
                        pause_end = pygame.time.get_ticks()
                        pause_offset += (pause_end - pause_start) / 1000.0
                        is_paused = False
                    elif event.key == pygame.K_ESCAPE:
                        return stats, score

            clock.tick(60)
            continue

        # =========================
        # ⏱ 正確時間
        # =========================
        current_time = pygame.time.get_ticks() / 1000.0 - start_time - pause_offset

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # 手動暫停（只有在遊戲未結束時）
                if not game_finished and event.key == pygame.K_p:
                    if not is_paused:
                        is_paused = True
                        pygame.mixer.music.pause()
                        pause_start = pygame.time.get_ticks()
                    continue

                # 打擊（只在遊戲未結束且未暫停時）
                if not game_finished and not is_paused:
                    if event.key == pygame.K_f:
                        hit_type = "red"
                    elif event.key == pygame.K_j:
                        hit_type = "blue"
                    else:
                        hit_type = None

                    if hit_type:
                        # 檢查連打
                        active_roll = None
                        for note in notes:
                            if isinstance(note, RollNote) and not note.hit:
                                if note.is_active(current_time):
                                    active_roll = note
                                    break
                        
                        if active_roll:
                            active_roll.roll_hits += 1
                            don_sound.play()
                            score += 10 * (1 + combo // 10)
                            judge_text = "ROLL!"
                            judge_display_time = pygame.time.get_ticks()
                        else:
                            closest_note = None
                            closest_diff = 0.5
                            
                            for note in notes:
                                if isinstance(note, Note) and not note.hit and not note.missed and note.note_type == hit_type:
                                    diff = abs(current_time - note.time)
                                    if diff < closest_diff:
                                        closest_diff = diff
                                        closest_note = note
                            
                            if closest_note:
                                closest_note.hit = True
                                closest_note.hit_effect = 10
                                combo += 1
                                if combo > max_combo:
                                    max_combo = combo
                                
                                if closest_note.note_type == "red":
                                    don_sound.play()
                                else:
                                    ka_sound.play()
                                
                                if closest_diff < 0.15:
                                    score += 100 * (1 + combo // 10)
                                    judge_text = "PERFECT!"
                                    judge_display_time = pygame.time.get_ticks()
                                    stats["perfect"] += 1
                                elif closest_diff < 0.3:
                                    score += 50 * (1 + combo // 10)
                                    judge_text = "GOOD!"
                                    judge_display_time = pygame.time.get_ticks()
                                    stats["good"] += 1
                                else:
                                    score += 10 * (1 + combo // 10)
                                    judge_text = "OK"
                                    judge_display_time = pygame.time.get_ticks()
                                    stats["ok"] += 1
                            else:
                                stats["miss"] += 1
                                combo = 0

        # MISS 判定
        for note in notes:
            if isinstance(note, Note) and not note.hit and not note.missed:
                if current_time > note.time + 0.5:
                    note.missed = True
                    combo = 0
                    stats["miss"] += 1
        
        # 連打完成判定
        for note in notes:
            if isinstance(note, RollNote) and not note.hit:
                if note.is_done(current_time):
                    note.hit = True
                    if note.roll_hits > 0:
                        score += 50 * (1 + combo // 10)
                        stats["ok"] += 1

        # =========================
        # ⭐ 遊戲結束判定
        # =========================
        if not game_finished:
            all_notes_done = all(
                isinstance(note, (Note, RollNote)) and 
                (note.hit or note.missed or (isinstance(note, RollNote) and note.is_done(current_time)))
                for note in notes
            )
            music_ended = not pygame.mixer.music.get_busy()
            
            if all_notes_done and music_ended:
                game_finished = True
                stats["max_combo"] = max_combo
                pygame.time.delay(1000)
                running = False

        # =========================
        # 🎨 畫面繪製
        # =========================
        screen.blit(game_bg, (0, 0))

        # 繪製太鼓
        pygame.draw.circle(screen, DARK_RED, (100, 200), 40)
        pygame.draw.circle(screen, RED, (100, 200), 35)
        pygame.draw.circle(screen, GOLD, (100, 200), 35, 2)

        pygame.draw.circle(screen, DARK_BLUE, (100, 280), 40)
        pygame.draw.circle(screen, BLUE, (100, 280), 35)
        pygame.draw.circle(screen, GOLD, (100, 280), 35, 2)

        # 繪製音符
        for note in notes:
            if isinstance(note, RollNote) and not note.hit:
                x = note.get_x(current_time)
                width = note.get_width(current_time)
                if -100 < x < 900 and width > 0:
                    roll_rect = pygame.Rect(int(x), 220, width, 40)
                    pygame.draw.rect(screen, (255, 200, 0), roll_rect)
                    pygame.draw.rect(screen, GOLD, roll_rect, 3)
                    roll_text = font_small.render("ROLL", True, BLACK)
                    text_rect = roll_text.get_rect(center=(int(x) + width//2, 240))
                    screen.blit(roll_text, text_rect)
            elif isinstance(note, Note) and not note.hit and not note.missed:
                x = note.get_x(current_time)
                if -100 < x < 900:
                    if note.note_type == "red":
                        color = RED
                        y = 200
                    else:
                        color = BLUE
                        y = 280
                    pygame.draw.circle(screen, GOLD, (int(x), y), 33)
                    pygame.draw.circle(screen, color, (int(x), y), 30)
            
            if hasattr(note, 'hit_effect') and note.hit_effect > 0:
                x = note.get_x(current_time)
                if -100 < x < 900:
                    if note.note_type == "red":
                        y = 200
                    else:
                        y = 280
                    effect_size = 45 + (10 - note.hit_effect) * 2
                    pygame.draw.circle(screen, GOLD, (int(x), y), effect_size, 3)
                    note.hit_effect -= 1

        # 顯示分數和 Combo
        score_panel = pygame.Surface((180, 120))
        score_panel.set_alpha(200)
        score_panel.fill((0, 0, 0))
        screen.blit(score_panel, (5, 5))
        
        score_text = font_medium.render(f"Score: {score}", True, GOLD)
        screen.blit(score_text, (15, 15))
        combo_text = font_medium.render(f"Combo: {combo}", True, WHITE)
        screen.blit(combo_text, (15, 55))
        if max_combo > 0:
            max_combo_text = font_small.render(f"Max: {max_combo}", True, LIGHT_GRAY)
            screen.blit(max_combo_text, (15, 95))

        # 顯示判定文字
        if judge_display_time > 0:
            elapsed = pygame.time.get_ticks() - judge_display_time
            if elapsed < 500:
                judge_surface = font_large.render(judge_text, True, ORANGE)
                text_rect = judge_surface.get_rect(center=(100, 140))
                screen.blit(judge_surface, text_rect)
            else:
                judge_display_time = 0

        pygame.display.flip()
        clock.tick(60)

    stats["max_combo"] = max_combo
    return stats, score

# ==================== 主程式 ====================
def main():
    levels = load_levels()
    if not levels:
        print("Error: No charts found (no JSON file in the levels folder)")
        return
    
    show_title_screen()
    
    while True:
        song_title = select_song(levels)
        level_data = levels[song_title]
        difficulty = select_difficulty()
        notes, bgm_path = init_game(level_data, difficulty)
        show_game_start_screen()
        start_time = pygame.time.get_ticks() / 1000.0
        stats, final_score = run_game(notes, bgm_path, start_time)
        if not show_result_screen(stats, final_score):
            continue

if __name__ == "__main__":
    main()