import pygame


class Enemy(pygame.sprite.Sprite):
    def __init__(self, health: int, enemy_img: pygame.image):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.center = (500, 275)
        self.health = health
        self.max_health = health


class EnemySpawner:
    def __init__(self, basic_health: int):
        self.health = basic_health
        self.image = pygame.image.load("img/enemy.png")

    def spawn(self) -> Enemy:
        return Enemy(self.health, self.image)


class Hero(pygame.sprite.Sprite):
    def __init__(self, img: pygame.image, damage: int, coordinates: (int, int), hero_type: str, cost: int):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.basic_damage = damage
        self.damage = damage
        self.hero_type = hero_type
        self.rect = self.image.get_rect()
        self.rect.center = coordinates
        self.level = 1
        self.cost = cost

    def upgrade_hero(self) -> int:
        inc = 0
        global balance
        if balance >= self.cost:
            balance -= self.cost
            if self.hero_type == "knight":
                self.damage += self.level * self.basic_damage
            else:
                inc = self.level * self.basic_damage
                self.level += 1
            self.cost *= 2
        return inc


class HeroFactory:
    types = ["knight", "archer", "wizard"]

    def __init__(self):
        self.coordinates = {"knight": (300, 325), "archer": (200, 300), "wizard": (100, 325)}
        self.basic_damages = {"knight": 1, "archer": 10, "wizard": 50}
        self.filenames = {"knight": "knight.png", "archer": "archer.png", "wizard": "wizard.png"}
        self.costs = {"knight": 1, "archer": 5, "wizard": 10}
        self.images = {}
        for hero_type in self.types:
            self.images[hero_type] = pygame.image.load("img/" + self.filenames[hero_type])

    def create(self, hero_type: str) -> Hero:
        return Hero(self.images[hero_type], self.basic_damages[hero_type], self.coordinates[hero_type], hero_type, self.costs[hero_type])


class Button:
    def __init__(self, color: (int, int, int), x: int, y: int, width: int, height: int, text: str, this_hero: Hero, hero_type: str, face_img: pygame.image):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.hero = this_hero
        self.hero_type = hero_type
        self.face_img = face_img

    def draw(self, window: pygame.display):
        text = game_font.render(self.text, False, (0, 0, 0))
        hero_cost = hero_factory.costs[self.hero_type]
        if self.hero is not None:
            hero_cost = self.hero.cost
        cost = game_font.render(str(hero_cost), False, (0, 0, 0))
        pygame.draw.rect(window, (255, 255, 0), (self.x, self.y, self.width, self.height))
        window.blit(text, (self.x, self.y))
        window.blit(cost, (self.x + self.width, self.y))
        window.blit(self.face_img, (self.x - 40, self.y - 5))

    def check_click(self, mouse_pos: (int, int)) -> bool:
        return self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height


class UpgradeShop:
    def __init__(self, window: pygame.display):
        self.buttons_list = []
        self.window = window
        x = 50
        y = 100
        width = 100
        height = 30
        for hero_type in HeroFactory.types:
            face_img = pygame.image.load("img/" + hero_type + "_face.png")
            button = Button((255, 255, 255), x, y, width, height, "Upgrade", heroes.get(hero_type), hero_type, face_img)
            self.buttons_list.append(button)
            y += height + 10

    def draw_shop(self):
        for button in self.buttons_list:
            button.draw(self.window)

    def upgrade(self, mouse_pos: (int, int)) -> int:
        inc = 0
        for button in self.buttons_list:
            if button.check_click(mouse_pos):
                if button.hero is not None:
                    inc = button.hero.upgrade_hero()
                else:
                    button.hero = hero_factory.create(button.hero_type)
                    heroes[button.hero_type] = button.hero
                    inc = button.hero.basic_damage
        return inc


def draw_enemy_health(window: pygame.display, enemy: Enemy):
    pygame.draw.rect(window, (0, 0, 0), (425, 90, 150, 30))
    pygame.draw.rect(window, (0, 255, 0), (425, 90, 150 * (enemy.health / enemy.max_health), 30))


def attack(enemy: Enemy, damage: int):
    balance_inc = 0
    enemy.health -= damage
    if enemy.health <= 0:
        balance_inc = 1
        pygame.event.post(pygame.event.Event(SPAWN_EVENT))
    return balance_inc


def main():
    pygame.init()
    pygame.font.init()
    global game_font
    game_font = pygame.font.SysFont('Century Gothic', 20)
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Click Saga")
    clock = pygame.time.Clock()
    bg = pygame.image.load("img/bg.png")
    delta = 1000
    pygame.time.set_timer(INC_EVENT, delta)
    is_running = True
    auto_inc = 0
    main_hero = hero_factory.create("knight")
    heroes["knight"] = main_hero
    upgrade_shop = UpgradeShop(screen)
    enemy_basic_health = 10
    enemy_spawner = EnemySpawner(enemy_basic_health)
    cur_enemy = enemy_spawner.spawn()
    global balance
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    balance += attack(cur_enemy, main_hero.damage)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                auto_inc += upgrade_shop.upgrade(event.pos)
            elif event.type == INC_EVENT:
                balance += attack(cur_enemy, auto_inc)
            elif event.type == SPAWN_EVENT:
                enemy_spawner.health += enemy_basic_health
                cur_enemy = enemy_spawner.spawn()
        screen.blit(bg, (0, 0))
        upgrade_shop.draw_shop()
        balance_field = game_font.render("Balance: " + str(balance), False, (0, 0, 0))
        damage_field = game_font.render("Auto damage: " + str(auto_inc), False, (0, 0, 0))
        screen.blit(balance_field, (10, 10))
        screen.blit(damage_field, (10, 30))
        for hero in heroes.values():
            screen.blit(hero.image, hero.rect)
        screen.blit(cur_enemy.image, cur_enemy.rect)
        draw_enemy_health(screen, cur_enemy)
        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()


screen_width = 720
screen_height = 480
fps = 60
INC_EVENT = pygame.USEREVENT + 1
SPAWN_EVENT = pygame.USEREVENT + 2
balance = 0
game_font = None
hero_factory = HeroFactory()
heroes = dict()

if __name__ == '__main__':
    main()
