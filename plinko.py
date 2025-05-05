import pygame
import sys
import random
import math
import os

pygame.init()

WIDTH, HEIGHT = 1000, 800
BACKGROUND_COLOR = (25, 25, 40)
PEG_COLOR = (200, 200, 220)
SLOT_COLOR = (50, 50, 80)
TEXT_COLOR = (220, 220, 220)
BALL_COLORS = {
    "LOW": (255, 255, 0),
    "MEDIUM": (255, 165, 0),
    "HIGH": (255, 50, 50)
}
BUTTON_COLOR = (70, 70, 100)
BUTTON_HOVER_COLOR = (90, 90, 120)
BUTTON_TEXT_COLOR = (230, 230, 230)

# default
risk_level = "MEDIUM"
rows = 12
ball_radius = 10
peg_radius = 4
starting_money = 1000.00
current_money = starting_money
bet_amount = 1.00
gravity = 0.19
elasticity = 0.5
auto_play = False
auto_play_count = 0
auto_play_delay = 0
auto_play_timer = 0
balls_in_play = []
menu_collapsed = False

#all tables
multiplier_tables = {
    "LOW": {
        8:  [2.5, 2.0, 1.4, 0.7, 0.0, 0.7, 1.4, 2.0, 2.5],
        10: [2.8, 2.2, 1.6, 1.2, 1.0, 0.9, 1.0, 1.2, 1.6, 2.2, 2.8],
        12: [3.0, 2.4, 1.8, 1.4, 1.1, 1.0, 0.9, 1.0, 1.1, 1.4, 1.8, 2.4, 3.0],
        14: [3.2, 2.6, 2.0, 1.5, 1.2, 1.0, 0.9, 0.8, 0.9, 1.0, 1.2, 1.5, 2.0, 2.6, 3.2],
        16: [3.5, 2.8, 2.2, 1.6, 1.3, 1.1, 1.0, 0.9, 0.8, 0.9, 1.0, 1.1, 1.3, 1.6, 2.2, 2.8, 3.5]
    },
    "MEDIUM": {
        8:  [10.0, 6.0, 4.0, 2.0, 0.6, 2.0, 4.0, 6.0, 10.0],
        10: [12.0, 8.0, 5.0, 3.0, 1.2, 0.5, 1.2, 3.0, 5.0, 8.0, 12.0],
        12: [15.0, 10.0, 6.0, 3.5, 2.0, 1.2, 0.5, 1.2, 2.0, 3.5, 6.0, 10.0, 15.0],
        14: [18.0, 14.0, 8.0, 4.0, 2.4, 1.4, 0.8, 0.5, 0.8, 1.4, 2.4, 4.0, 8.0, 14.0, 18.0],
        16: [20.0, 16.0, 10.0, 5.0, 3.0, 1.8, 1.0, 0.6, 0.5, 0.6, 1.0, 1.8, 3.0, 5.0, 10.0, 16.0, 20.0]
    },
    "HIGH": {
        8:  [120.0, 60.0, 30.0, 6.0, 0.2, 6.0, 30.0, 60.0, 120.0],
        10: [150.0, 80.0, 40.0, 15.0, 5.0, 0.2, 5.0, 15.0, 40.0, 80.0, 150.0],
        12: [200.0, 120.0, 60.0, 25.0, 10.0, 3.0, 0.1, 3.0, 10.0, 25.0, 60.0, 120.0, 200.0],
        14: [250.0, 180.0, 100.0, 50.0, 20.0, 8.0, 3.0, 0.1, 0.1, 3.0, 8.0, 20.0, 50.0, 100.0, 180.0],
        16: [300.0, 220.0, 150.0, 80.0, 30.0, 10.0, 5.0, 1.5, 0.1, 1.5, 5.0, 10.0, 30.0, 80.0, 150.0, 220.0, 300.0]
    }
}



history = []
max_history_displayed = 10

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("plinko")

font = pygame.font.SysFont('Arial', 18)
medium_font = pygame.font.SysFont('Arial', 24)
large_font = pygame.font.SysFont('Arial', 32)

clock = pygame.time.Clock()

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        self.color = BUTTON_COLOR  
        self.hover_color = BUTTON_HOVER_COLOR  

    def draw(self):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 130), self.rect, 2, border_radius=5)
        
        text_surf = font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered

    def handle_event(self, event):
        # we retired hb
        pass

class Ball:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = ball_radius
        self.vel_x = 0
        self.vel_y = 0
        self.in_slot = False
        self.slot_index = -1
        self.multiplier = 0
        self.winnings = 0
        self.slot_animation = 0
        self.slot_animation_speed = 5
        
    def update(self, pegs, slots):
        if self.in_slot:

            self.slot_animation += self.slot_animation_speed
            if self.slot_animation >= 100:
                return True  
            return False
            

        self.vel_y += gravity
        
        
        self.x += self.vel_x
        self.y += self.vel_y
        
    
        board_width = WIDTH * 0.7
        board_left = (WIDTH - board_width) / 2
        board_right = board_left + board_width
        
        if self.x - self.radius < board_left:
            self.x = board_left + self.radius
            self.vel_x = -self.vel_x * elasticity
        elif self.x + self.radius > board_right:
            self.x = board_right - self.radius
            self.vel_x = -self.vel_x * elasticity
            
        for peg in pegs:
            dx = self.x - peg[0]
            dy = self.y - peg[1] # that one triangle dude x square + y squared but if we are below that we got collision
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < self.radius + peg_radius:
                nx = dx / distance
                ny = dy / distance
                
                # make sure they dont overlap and if they do move them apart
                overlap = (self.radius + peg_radius) - distance
                self.x += nx * overlap
                self.y += ny * overlap
                
                # create the bounce and velocity 
                dot_product = self.vel_x * nx + self.vel_y * ny
                self.vel_x = (self.vel_x - 2 * dot_product * nx) * elasticity
                self.vel_y = (self.vel_y - 2 * dot_product * ny) * elasticity
                
                # rigging
                self.vel_x += random.uniform(-0.1, 0.1)
        

        if self.y > slots[0][1] - self.radius:
            for i, slot in enumerate(slots):
                if abs(self.x - slot[0]) < slot[2] / 2:
                    self.in_slot = True
                    self.slot_index = i
                    self.multiplier = multiplier_tables[risk_level][rows][i]
                    self.winnings = bet_amount * self.multiplier
                    
                    global current_money, history
                    current_money += self.winnings
                    history.insert(0, {
                        "multiplier": self.multiplier,
                        "bet": bet_amount,
                        "win": self.winnings
                    })
                    if len(history) > 6: 
                        history.pop()
                    break
            
            # if we are below the slots give it a bounce
            if not self.in_slot and self.y > slots[0][1]:
                self.y = slots[0][1] - self.radius
                self.vel_y = -self.vel_y * elasticity
        
        return False  

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # draw winnings for balls in slots
        if self.in_slot:
            # draw a highlight effect
            pygame.draw.circle(screen, (255, 255, 255, 128), 
                              (int(self.x), int(self.y)), 
                              self.radius + 5)
            
            win_text = medium_font.render(f"x{self.multiplier:.1f}", True, (255, 255, 255))
            screen.blit(win_text, (self.x - win_text.get_width() / 2, self.y - 30))
            
            money_text = medium_font.render(f"${self.winnings:.2f}", True, (255, 255, 20))
            screen.blit(money_text, (self.x - money_text.get_width() / 2, self.y + 10))

def generate_pegs():
    pegs = []
    board_width = WIDTH * 0.7
    board_height = HEIGHT * 0.7
    board_left = (WIDTH - board_width) / 2
    board_top = HEIGHT * 0.18
    
    horizontal_spacing = board_width / (rows + 1)
    vertical_spacing = board_height / (rows)
    
    for row in range(rows):

        if row == 0: continue
        pegs_in_row = row + 1
        
        row_width = pegs_in_row * horizontal_spacing
        
        row_left_offset = (board_width - row_width) / 2
        
        for col in range(pegs_in_row):
            x = board_left + row_left_offset + col * horizontal_spacing + horizontal_spacing/2
            y = board_top + row * vertical_spacing
            pegs.append((x, y))
    
    return pegs

def generate_slots():
    slots = []
    board_width = WIDTH * 0.7
    board_left = (WIDTH - board_width) / 2
    slot_top = HEIGHT * 0.85
    
    num_slots = rows + 1
    
    horizontal_spacing = board_width / (rows + 1)
    
    slots_width = num_slots * horizontal_spacing

    slots_left_offset = (board_width - slots_width) / 2
    
    slot_width = horizontal_spacing
    
    for i in range(num_slots):
        x = board_left + slots_left_offset + i * slot_width + slot_width/2
        slots.append((x, slot_top, slot_width))
    
    return slots

def draw_board(pegs, slots):
    screen.fill(BACKGROUND_COLOR)
    
    board_width = WIDTH * 0.7
    board_height = HEIGHT * 0.7
    board_left = (WIDTH - board_width) / 2
    board_top = HEIGHT * 0.18
    
    pygame.draw.rect(screen, (40, 40, 60), 
                    (board_left, board_top, board_width, board_height), 
                    border_radius=10)
    
    for peg in pegs:
        pygame.draw.circle(screen, PEG_COLOR, (int(peg[0]), int(peg[1])), peg_radius)
    
    for i, slot in enumerate(slots):
        rect = pygame.Rect(slot[0] - slot[2]/2, slot[1] - 30, slot[2], 60)
        pygame.draw.rect(screen, SLOT_COLOR, rect, border_radius=10)
        
        multiplier = multiplier_tables[risk_level][rows][i]
        color = (150, 255, 150) if multiplier > 1 else (255, 150, 150)
        multiplier_text = font.render(f"x{multiplier:.1f}", True, color)
        screen.blit(multiplier_text, (slot[0] - multiplier_text.get_width()/2, slot[1] - 15))
        
    # title
    title_text = large_font.render("plinkoooooo", True, TEXT_COLOR)
    screen.blit(title_text, (WIDTH/2 - title_text.get_width()/2, 20))
    
    # always show money
    money_bg = pygame.Rect(10, 10, 215, 40)
    pygame.draw.rect(screen, (40, 40, 60), money_bg, border_radius=5)
    money_text = medium_font.render(f"balance: ${current_money:.2f}", True, TEXT_COLOR)
    screen.blit(money_text, (20, 20))
    
    if not menu_collapsed:
        menu_bg = pygame.Rect(10, HEIGHT - 180, WIDTH - 20, 170)
        pygame.draw.rect(screen, (30, 30, 50), menu_bg, border_radius=8)
        
        bet_text = font.render(f"amount{bet_amount:.2f}", True, TEXT_COLOR)
        screen.blit(bet_text, (20, HEIGHT - 140))
        
        risk_text = font.render(f"difficulty: {risk_level}", True, TEXT_COLOR)
        screen.blit(risk_text, (20, HEIGHT - 110))
        
        rows_text = font.render(f"rows: {rows}", True, TEXT_COLOR)
        screen.blit(rows_text, (20, HEIGHT - 80))
        
        auto_text = font.render(f"auto: {'ON' if auto_play else 'OFF'} ({auto_play_count})", True, TEXT_COLOR)
        screen.blit(auto_text, (20, HEIGHT - 50))
    else:
        toggle_bg = pygame.Rect(10, HEIGHT - 45, 40, 35)
        pygame.draw.rect(screen, (30, 30, 50), toggle_bg, border_radius=8)
        
        settings_text = f"${bet_amount:.2f} | {risk_level} | {rows} rows | Auto: {'ON' if auto_play else 'OFF'}"
        settings_font = font.render(settings_text, True, TEXT_COLOR)
        settings_width = settings_font.get_width() + 20
        
        pill_x = (WIDTH / 2) - (settings_width / 2)
        settings_pill = pygame.Rect(pill_x, HEIGHT - 45, settings_width, 35)
        pygame.draw.rect(screen, (30, 30, 50), settings_pill, border_radius=8)
    
        screen.blit(settings_font, (pill_x + 10, HEIGHT - 35))
    
    # history
    history_panel_x = WIDTH - 200
    history_panel_y = 60
    pygame.draw.rect(screen, (40, 40, 60), (history_panel_x, history_panel_y, 200, 160), border_radius=5)
    
    history_title = font.render("Recent Results", True, TEXT_COLOR)
    screen.blit(history_title, (history_panel_x + 10, history_panel_y + 10))
    
    for i, result in enumerate(history[:max_history_displayed]):
        if i >= max_history_displayed:
            break
            
        color = (150, 255, 150) if result["multiplier"] > 1 else (255, 150, 150)
        history_text = font.render(f"${result['bet']:.2f} x{result['multiplier']:.1f} = ${result['win']:.2f}", True, color)
        screen.blit(history_text, (history_panel_x + 10, history_panel_y + 35 + i * 20))

def create_buttons():
    buttons = []
    
    if not menu_collapsed:
        # collpase and expand
        menu_btn_text = "▲ Hide"
        menu_btn = Button(20, HEIGHT - 170, 80, 25, menu_btn_text, toggle_menu)
        menu_btn.color = (60, 60, 90)  
        buttons.append(menu_btn)
        
        buttons.append(Button(150+300, HEIGHT - 140, 60, 25, "- 0.1", lambda: change_bet(-0.1)))
        buttons.append(Button(220+300, HEIGHT - 140, 60, 25, "+ 0.1", lambda: change_bet(0.1)))
        buttons.append(Button(290+300, HEIGHT - 140, 60, 25, "- 1.0", lambda: change_bet(-1.0)))
        buttons.append(Button(360+300, HEIGHT - 140, 60, 25, "+ 1.0", lambda: change_bet(1.0)))
        buttons.append(Button(430+300, HEIGHT - 140, 60, 25, "× 2", lambda: change_bet_multiply(2)))
        buttons.append(Button(500+300, HEIGHT - 140, 60, 25, "÷ 2", lambda: change_bet_multiply(0.5)))
        
        buttons.append(Button(150+300, HEIGHT - 110, 70, 25, "LOW", lambda: change_risk("LOW")))
        buttons.append(Button(230+300, HEIGHT - 110, 70, 25, "MEDIUM", lambda: change_risk("MEDIUM")))
        buttons.append(Button(310+300, HEIGHT - 110, 70, 25, "HIGH", lambda: change_risk("HIGH")))
        
        # yeah
        buttons.append(Button(150+300, HEIGHT - 80, 50, 25, "8", lambda: change_rows(8)))
        buttons.append(Button(210+300, HEIGHT - 80, 50, 25, "10", lambda: change_rows(10)))
        buttons.append(Button(270+300, HEIGHT - 80, 50, 25, "12", lambda: change_rows(12)))
        buttons.append(Button(330+300, HEIGHT - 80, 50, 25, "14", lambda: change_rows(14)))
        buttons.append(Button(390+300, HEIGHT - 80, 50, 25, "16", lambda: change_rows(16)))
        
        # autoplay buttons 
        buttons.append(Button(150+300, HEIGHT - 50, 80, 25, "Toggle Auto", toggle_auto_play))
        buttons.append(Button(240+300, HEIGHT - 50, 50, 25, "10", lambda: set_auto_count(10)))
        buttons.append(Button(300+300, HEIGHT - 50, 50, 25, "25", lambda: set_auto_count(25)))
        buttons.append(Button(360+300, HEIGHT - 50, 50, 25, "50", lambda: set_auto_count(50)))
        buttons.append(Button(420+300, HEIGHT - 50, 50, 25, "100", lambda: set_auto_count(100)))
        
        # play
        play_btn = Button(WIDTH - 150, HEIGHT - 80, 120, 50, "PLAY", drop_ball)
        play_btn.color = (80, 120, 80)
        play_btn.hover_color = (100, 150, 100)
        buttons.append(play_btn)
    else:
        menu_btn = Button(15, HEIGHT - 40, 30, 25, "▼", toggle_menu)
        menu_btn.color = (60, 60, 90)
        buttons.append(menu_btn)
        
        # play 
        play_btn = Button(WIDTH - 90, HEIGHT - 40, 80, 30, "PLAY", drop_ball)
        play_btn.color = (80, 120, 80)
        play_btn.hover_color = (100, 150, 100)
        buttons.append(play_btn)
    
    return buttons

def change_bet(amount):
    global bet_amount
    bet_amount = max(0.1, min(current_money, bet_amount + amount))

def change_bet_multiply(factor):
    global bet_amount
    bet_amount = max(0.1, min(current_money, bet_amount * factor))

def change_risk(new_risk):
    global risk_level
    risk_level = new_risk

def change_rows(new_rows):
    global rows, pegs, slots
    if new_rows in [8, 10, 12, 14, 16]:
        rows = new_rows
        pegs = generate_pegs()
        slots = generate_slots()

def toggle_auto_play():
    global auto_play
    auto_play = not auto_play

def set_auto_count(count):
    global auto_play_count
    auto_play_count = count

def drop_ball():
    global current_money, auto_play_count
    
    if current_money < bet_amount or bet_amount <= 0:
        return
    
    current_money -= bet_amount
    
    # new ball lets gooo and we randomizing where it spawns x locaton
    board_width = WIDTH * 0.7
    board_left = (WIDTH - board_width) / 2
    ball_x = board_left + board_width / 2 + random.uniform(-10, 10)
    ball_y = HEIGHT * 0.12
    
    balls_in_play.append(Ball(ball_x, ball_y, BALL_COLORS[risk_level]))
    
    # if we are autoplaying decement it 
    if auto_play and auto_play_count > 0:
        auto_play_count -= 1

def toggle_menu():
    global menu_collapsed
    # toggle the menu state
    menu_collapsed = not menu_collapsed

def main():
    global pegs, slots, auto_play_timer, buttons
    
    # make the actual elements
    pegs = generate_pegs()
    slots = generate_slots()
    
    # buttons
    buttons = create_buttons()
    
    # basically the update() of unity in this world
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    if button.rect.collidepoint(event.pos) and button.action:
                        # if its toggle menu give it special treatment
                        if button.text == "▲ Hide" or button.text == "▼":
                            button.action() 
                            buttons = create_buttons()
                            break
                        else:
                            button.action()
                
        # if autoplay is on and there is balls to play drop some balls baby
        if auto_play and auto_play_count > 0 and len(balls_in_play) < 5:
            if current_time > auto_play_timer:
                drop_ball()
                auto_play_timer = current_time + auto_play_delay
        
        # checks if ur hovering so if you click it works
        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            button.check_hover(mouse_pos)
        
        # ball updater like it makes sure the gravity is applied and they dont collide
        for i in range(len(balls_in_play) - 1, -1, -1):
            if balls_in_play[i].update(pegs, slots):
                balls_in_play.pop(i)
        
        draw_board(pegs, slots)
        
        for ball in balls_in_play:
            ball.draw()

        for button in buttons:
            button.draw()
        
        pygame.display.flip()
        
        #framerate
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 