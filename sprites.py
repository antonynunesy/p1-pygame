import pygame
import os
import constantes as cons

diretorio_img = os.path.join(os.getcwd(),"imagens")

class Agente(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        super().__init__()
        self.vel = cons.VEL_PLAYER
        self.gravidade = cons.GRAVIDADE
        self.forca_pulo = cons.FORCA_PULO #força de pulo como atributo individual do agente
        self.dx, self.dy = 0, 0
        self.direcao = 1
        self.virar = False
        self.lado = 1
        self.mundo = False
        spritesheet_parado = pygame.image.load(os.path.join(diretorio_img, "Agente_Glitch/agente_parado.png")).convert_alpha()
        spritesheet_correndo = pygame.image.load(os.path.join(diretorio_img, "Agente_Glitch/agente_correndo.png")).convert_alpha()
        spritesheet_pulando = pygame.image.load(os.path.join(diretorio_img, "Agente_Glitch/agente_pulando.png")).convert_alpha()
        spritesheet_gparado = pygame.image.load(os.path.join(diretorio_img, "Agente_Glitch/glitch_parado.png")).convert_alpha()
        spritesheet_gcorrendo = pygame.image.load(os.path.join(diretorio_img, "Agente_Glitch/glitch_correndo.png")).convert_alpha()
        spritesheet_gpulando = pygame.image.load(os.path.join(diretorio_img, "Agente_Glitch/glitch_pulando.png")).convert_alpha()
        self.bg = []
        for i in range(6):
            img = spritesheet_parado.subsurface((i*24+4, 8), (16, 32))
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.bg.append(img)
        for i in range(10):
            img = spritesheet_correndo.subsurface((i*24+2, 8), (18, 32))
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.bg.append(img)
        for i in range(1, 4):
            img = spritesheet_pulando.subsurface((i*24+2, 8), (18, 32))
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.bg.append(img)

        for i in range(6):
            img = spritesheet_gparado.subsurface((i*24+4, 8), (16, 32))
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.bg.append(img)
        for i in range(10):
            img = spritesheet_gcorrendo.subsurface((i*24+2, 8), (18, 32))
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.bg.append(img)
        for i in range(1, 4):
            img = spritesheet_gpulando.subsurface((i*24+2, 8), (18, 32))
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.bg.append(img)

        self.index = 0
        self.image = self.bg[self.index]    
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x,y)

    def update(self):
        if self.mundo:
            glitch = 19
        else:
            glitch = 0

        if self.dx == 0 and self.dy == 0:
            if self.index < glitch or self.index > 5+glitch:
                self.index = 0+glitch
            self.index += 0.25
            self.image = self.bg[int(self.index)]
        elif self.dx != 0 and self.dy == 0:
            if self.index < 6+glitch:
                self.index = 6+glitch
            elif self.index > 15+glitch:
                self.index = 6+glitch
            self.index += 0.4 * (self.vel/cons.VEL_PLAYER)
            self.image = self.bg[int(self.index)]
        else:
            if self.dy < 0:
                self.image = self.bg[16+glitch]
            elif self.dy > 0:
                self.image = self.bg[18+glitch]

        self.image = pygame.transform.flip(self.image, self.virar, self.mundo)

    def movimento(self, objetos, caixas, botoes):
        self.tecla = pygame.key.get_pressed()
        self.dx = 0

        #ESQUERDA E DIREITA
        if self.tecla[pygame.K_a]:
            self.dx = -self.vel
            self.virar = True
            self.direcao = -1

        if self.tecla[pygame.K_d]:
            self.dx = self.vel
            self.virar = False
            self.direcao = 1

        self.colisao_geral = pygame.sprite.Group(objetos, caixas)

        self.rect.x += self.dx
        self.colisao_x()

        #GRAVIDADE
        self.dy += self.gravidade
        self.rect.y += self.dy
        self.colisao_y(botoes)

    def colisao_x(self):
        self.colisao = pygame.sprite.spritecollide(self, self.colisao_geral, False)

        for bloco in self.colisao:
            if self.dx > 0:
                self.rect.right = bloco.rect.left

            elif self.dx < 0:
                self.rect.left = bloco.rect.right

    def colisao_y(self, botoes):
        self.colisao = pygame.sprite.spritecollide(self, self.colisao_geral, False)
        self.apertando = [b for b in botoes if self.rect.colliderect(b.hitbox)]

        for bloco in self.colisao:
            if self.dy > 0:
                self.rect.bottom = bloco.rect.top
                self.dy = 0
            elif self.dy < 0:
                self.rect.top = bloco.rect.bottom
                self.dy = 0

        for botao in self.apertando:
            if botao:
                self.rect.bottom = botao.hitbox.top
                self.dy = 0


    def pular(self, botoes):
        self.rect.y += self.lado
        self.colisao = pygame.sprite.spritecollide(self, self.colisao_geral, False)
        self.apertando = [b for b in botoes if self.rect.colliderect(b.hitbox)]
        self.rect.y -= self.lado
        
        if self.colisao or self.apertando:
            self.dy = self.forca_pulo


    def borda(self, paredes):
        self.rolar = pygame.sprite.spritecollide(self, paredes, False)
        if self.rolar:
            self.rect.x -= self.dx
            return -self.dx
        return 0


    def troca_mundo(self, objetos):
        self.rect.y += self.lado
        self.colisao = pygame.sprite.spritecollide(self, objetos, False)
        self.rect.y -= self.lado

        #MIGRAR SISTEMA DE TROCA PRO CÓDIGO PRINCIPAL        

        if self.colisao:
            #ADICIONAR ANIMAÇÃO DE TROCA E DELAY
            self.lado *= -1
            self.mundo = not self.mundo
            self.rect.bottom = cons.ALTURA - self.rect.top
            self.gravidade *= -1
            self.forca_pulo *= -1
            return True
        return False
    

    def morre(self, perigo):
        self.bateu = pygame.sprite.spritecollide(self, perigo, False)
        
        return self.bateu



class Plataforma_arbritaria(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        self.image.set_alpha(0)
        self.rect = self.image.get_rect()   
        self.rect.topleft = (x, y)


class Plataforma(pygame.sprite.Sprite):
    def __init__(self, image, coord):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()   
        self.rect.topleft = (coord[0], coord[1])


class BackGround(pygame.sprite.Sprite):
    def __init__(self, x, y, tipo):
        super().__init__()
        self.bg = []        
        if tipo == "F":
            spritesheet_bg = pygame.image.load(os.path.join(diretorio_img, "BackGrounds/fundo_invert.png")).convert_alpha()

            for i in range(3):
                img = spritesheet_bg.subsurface((i*960, 0), (cons.LARGURA, cons.MEIO_Y))
                self.bg.append(img)
        elif tipo == "P":
            spritesheet_bg = pygame.image.load(os.path.join(diretorio_img, "divisao_central.png")).convert_alpha()

            for i in range(2):
                img = spritesheet_bg.subsurface((0, i*16), (cons.LARGURA, 16))
                self.bg.append(img)


        self.index = 0
        self.image = self.bg[self.index]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        if self.index > len(self.bg)-1:
            self.index = 0
        self.index += 0.25
        self.image = self.bg[int(self.index)]


class Mundo_desligado(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((cons.LARGURA, cons.ALTURA//2))
        self.image.fill(cons.PRETO)
        self.image.set_alpha(100)
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, cons.MEIO_Y)


class Caixa(pygame.sprite.Sprite):
    def __init__(self, img, coord, vel_player):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (coord[0], coord[1])
        self.vel = vel_player
        self.dx, self.dy = 0, 0


    def movimento(self, objetos, caixas, agente, botoes):
        self.tecla = pygame.key.get_pressed()
        self.dx = 0
        
        self.rect.x += 1
        self.empurrado = pygame.sprite.spritecollide(self, agente, False)
        self.rect.x -= 1

        #ESQUERDA E DIREITA
        if self.tecla[pygame.K_a] and self.empurrado:
            self.dx = -self.vel

        self.rect.x -= 1
        self.empurrado = pygame.sprite.spritecollide(self, agente, False)
        self.rect.x += 1

        if self.tecla[pygame.K_d] and self.empurrado:
            self.dx = self.vel

        self.colisao_geral = pygame.sprite.Group(objetos, caixas, agente)

        self.rect.x += self.dx
        self.colisao_x()

        #GRAVIDADE
        self.dy += cons.GRAVIDADE
        self.rect.y += self.dy
        self.colisao_y(botoes)

    def colisao_x(self):

        self.colisao = pygame.sprite.spritecollide(self, self.colisao_geral, False)

        for bloco in self.colisao:
            if self.dx > 0:
                self.rect.right = bloco.rect.left

            elif self.dx < 0:
                self.rect.left = bloco.rect.right

    def colisao_y(self, botoes):
        self.colisao = pygame.sprite.spritecollide(self, self.colisao_geral, False)
        self.apertando = [b for b in botoes if self.rect.colliderect(b.hitbox)]

        for bloco in self.colisao:
            if self.dy > 0:
                self.rect.bottom = bloco.rect.top
                self.dy = 0
            elif self.dy < 0:
                self.rect.top = bloco.rect.bottom
                self.dy = 0

        for botao in self.apertando:
            if botao:
                self.rect.bottom = botao.hitbox.top
                self.dy = 0


    def morre(self, perigo):
        self.bateu = pygame.sprite.spritecollide(self, perigo, False)
        
        return self.bateu


class Botao(pygame.sprite.Sprite):
    def __init__(self, imgs, coord):
        super().__init__()
        self.imgs = imgs
        self.index = 0
        self.image = self.imgs[self.index]
        self.rect = self.image.get_rect()
        self.rect.topleft = (coord[0], coord[1])
        self.hitbox = pygame.Rect(self.rect.x, self.rect.y, cons.TAMANHO_BLOCO, 10)
        self.hitbox.topleft = (coord[0], coord[1] + 22)


    def apertou(self, caixas, agente):
        self.hitbox.y -= 1
        self.apertado = [a for a in pygame.sprite.Group(caixas, agente) if self.hitbox.colliderect(a.rect)]
        self.hitbox.y += 1
            
        if self.apertado:
            self.index = 1
        else:
            self.index = 0

        self.image = self.imgs[self.index]

        self.hitbox.x = self.rect.x