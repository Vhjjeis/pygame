import pygame, random, os, random

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('game')
    size = width, height = 480, 640
    screen = pygame.display.set_mode(size)


    def reload():
        global blocks_i, is_game, best_points, bird
        blocks_i = 1
        for i in range(len(blocks)):
            blocks[0].kill()
            del blocks[0]
        for i in range(3):
            blocks.append(Block(580 + i * 240, blocks_i))
            blocks_i += 1
        is_game = 0
        if bird.points > best_points:
            best_points = bird.points
        bird.kill()
        bird = AnimatedSprite(load_image("spr_b2_strip4.png"), 4, 1, 200, 300)


    def load_image(name, colorkey=None):
        fullname = os.path.join('data', name)
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)
        if colorkey is not None:
            image = image.convert()
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
        return image


    class Bg(pygame.sprite.Sprite):
        image = load_image("bg.png")

        def __init__(self):
            super().__init__(bg_group)
            self.image = Bg.image
            self.rect = self.image.get_rect()


    class Earth(pygame.sprite.Sprite):
        image = load_image("earth.png")

        def __init__(self, x):
            super().__init__(earths_sprites)
            self.image = Earth.image
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = 560
            self.mask = pygame.mask.from_surface(self.image)

        def update(self, *args):
            if is_game == 1:
                self.rect.x -= v
                if self.rect.x + self.rect.width < 0:
                    self.kill()


    class Block(pygame.sprite.Sprite):
        image = load_image("block.png", 'white')

        def __init__(self, x, blocks_i):
            super().__init__(blocks_group)
            self.name = blocks_i
            self.image = Block.image
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = random.randint(-400, -150)
            self.mask = pygame.mask.from_surface(self.image)

        def update(self, event):
            if is_game == 1:
                self.rect.x -= v
                if self.rect.x + self.rect.width < 0:
                    self.kill()


    class Cursor(pygame.sprite.Sprite):
        image = load_image("cursor.png")

        def __init__(self, *group):
            super().__init__(*group)
            self.image = Cursor.image
            self.rect = self.image.get_rect()
            self.rect.x = -100

        def update(self, *args):
            if args and args[0].type == pygame.MOUSEMOTION:
                self.rect.x = args[0].pos[0]
                self.rect.y = args[0].pos[1]


    class AnimatedSprite(pygame.sprite.Sprite):
        def __init__(self, sheet, columns, rows, x, y):
            super().__init__(all_sprites)
            self.frames1 = []
            self.frames2 = []
            self.frames3 = []
            self.cut_sheet(sheet, columns, rows)
            self.cur_frame = 0
            self.image = self.frames1[self.cur_frame]
            self.rect = self.rect.move(x, y)

            self.tick = 0
            self.up = False
            self.up_tick = 35

            self.points = 0
            self.get_points = False
            self.game_over = 0

        def cut_sheet(self, sheet, columns, rows):
            self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                    sheet.get_height() // rows)
            for j in range(rows):
                for i in range(columns):
                    frame_location = (self.rect.w * i, self.rect.h * j)
                    self.frames1.append(sheet.subsurface(pygame.Rect(
                        frame_location, self.rect.size)))
                    self.frames2.append(pygame.transform.rotate(sheet.subsurface(pygame.Rect(
                        frame_location, self.rect.size)), 45))
                    self.frames3.append(pygame.transform.rotate(sheet.subsurface(pygame.Rect(
                        frame_location, self.rect.size)), -65))

        def update(self, *args):
            global is_game
            if is_game == 0:
                self.tick += 1
                if self.tick == 5:
                    self.cur_frame = (self.cur_frame + 1) % len(self.frames1)
                    self.image = self.frames1[self.cur_frame]
                    self.tick = 0
                self.rect.y = 301 if self.rect.y == 300 else 300
                if args and args[0].type == pygame.MOUSEBUTTONDOWN and args[0].button == 1:
                    is_game = 1
            if is_game == 1:
                self.tick += 1
                if self.tick == 5:
                    self.cur_frame = (self.cur_frame + 1) % len(self.frames1)
                    if -10 < self.up_tick < -5:
                        self.image = self.frames1[self.cur_frame]
                    elif -5 < self.up_tick:
                        self.image = self.frames2[self.cur_frame]
                    elif self.up_tick < -10:
                        self.image = self.frames3[self.cur_frame]
                    self.tick = 0
                if args and args[0].type == pygame.MOUSEBUTTONDOWN and args[0].button == 1:
                    self.up = True

                if args and args[0].type == pygame.MOUSEBUTTONUP and args[0].button == 1 and self.up:
                    self.up = False
                    music_wing.play()
                    self.rect.y -= 44
                    self.up_tick = 0 if self.up_tick < 0 else self.up_tick
                    self.up_tick += 15 if self.up_tick < self.up_tick + 1 else 0
                else:
                    self.up_tick -= 1

                if self.up_tick < 0:
                    self.rect.y += 4
                else:
                    self.rect.y += 1

                for i in blocks:
                    if pygame.sprite.collide_mask(self, i) or self.rect.x < 0:
                        music_die.play()
                        is_game = 2
                    if i.rect.x < self.rect.x and self.points < i.name:
                        self.points = i.name
                        music_point.play(0)
                if self.rect.y + self.rect.height > 560:
                    music_die.play()
                    is_game = 2
            if is_game == 2:
                self.game_over += 1
                if self.game_over == 20:
                    reload()


    running = True
    fps = 50
    clock = pygame.time.Clock()
    v = 3
    earths = []
    blocks = []
    blocks_i = 1
    blocks_group = pygame.sprite.Group()
    cursor_group = pygame.sprite.Group()
    bg_group = pygame.sprite.Group()
    earths_sprites = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    bg = Bg()
    bird = AnimatedSprite(load_image("spr_b2_strip4.png"), 4, 1, 200, 300)
    music_point = pygame.mixer.Sound("data/point.wav")
    music_wing = pygame.mixer.Sound("data/wing.wav")
    music_die = pygame.mixer.Sound("data/die.wav")
    best_points = 0
    is_game = 0

    for i in range(21):
        earths.append(Earth(i * 24))
    Cursor(cursor_group)
    for i in range(3):
        blocks.append(Block(580 + i * 240, blocks_i))
        blocks_i += 1
    pygame.mouse.set_visible(False)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        bg_group.draw(screen)
        earths_sprites.draw(screen)
        earths_sprites.update(event)
        if is_game in [1, 2]:
            blocks_group.draw(screen)
            blocks_group.update(event)
        if is_game == 0:
            font = pygame.font.Font(None, 30)
            text_points = font.render("Best score: " + str(best_points), True, 'black')
            screen.blit(text_points, [190, 50])
            font = pygame.font.Font(None, 30)
            text_points = font.render("Press start ", True, 'black')
            screen.blit(text_points, [160, 350])
        font = pygame.font.Font(None, 30)
        text_points = font.render("Score: " + str(bird.points), True, 'black')
        screen.blit(text_points, [200, 10])
        all_sprites.draw(screen)
        all_sprites.update(event)
        cursor_group.draw(screen)
        cursor_group.update(event)
        if earths[0].rect.x < 0:
            earths.append(Earth(earths[-1].rect.x + 24))
            del(earths[0])
        if blocks[0].rect.x < 0:
            blocks.append(Block(blocks[-1].rect.x + 240, blocks_i))
            blocks_i += 1
            del(blocks[0])

        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()