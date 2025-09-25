import pygame
import constantes as cons
import sprites as spr
import os
import csv

class Game():
    def __init__(self):
        #criando a tela do jogo
        pygame.init()
        pygame.mixer.init()
        self.tela = pygame.display.set_mode((cons.LARGURA, cons.ALTURA))
        pygame.display.set_caption(cons.TITULO_JOGO)
        self.clock = pygame.time.Clock()
        self.rodando = True
        self.fonte = pygame.font.match_font(cons.FONTE)
        self.carregar_arquivos()

    def carregar_arquivos(self):
        #carregar os arquivos de audio e imagens
        self.diretorio_img = os.path.join(os.getcwd(),"imagens")
        self.diretorio_aud = os.path.join(os.getcwd(), "audios")
        self.spritesheet = pygame.image.load(os.path.join(self.diretorio_img, "spritesheet.png")).convert_alpha()
        #self.jogo_start_logo = os.path.join(self.diretorio_img, "")
        #self.jogo_start_logo = pygame.image.load(self.jogo_start_logo).convert()

        self.img_list = []
        for i in range(4):
            for j in range(4):
                img = self.spritesheet.subsurface((j*32, i*32), (32, 32))
                self.img_list.append(img)
        self.img_list.append(pygame.image.load(os.path.join(self.diretorio_img, "spritesheet.png")).convert_alpha())
        self.img_list.append(pygame.image.load(os.path.join(self.diretorio_img, "spritesheet.png")).convert_alpha())
    
    def start(self):
            self.mostrar_texto("Pressione uma tecla para jogar", 32, cons.AMARELO, cons.MEIO_X, cons.MEIO_Y)
            self.mostrar_texto("Desenvolvido por Victor Rafael e Antony Nunes", 19, cons.BRANCO, cons.MEIO_X, cons.ALTURA - 30)

            pygame.display.flip()
            self.esperar_jogador()


    #pausa o jogo
    def pausar_jogo(self):
        pausado = True
            
        frame_congelado = self.tela.copy()

        while pausado:
            self.clock.tick(cons.FPS)
            
            #redesenha o estado atual do game
            self.tela.blit(frame_congelado, (0,0))

            #fundo semi-transparente
            overlay = pygame.Surface((cons.LARGURA, cons.ALTURA), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            self.tela.blit(overlay, (0, 0))   


            self.mostrar_texto("Jogo Pausado", 48, cons.AMARELO, cons.MEIO_X, cons.MEIO_Y - 50)
            self.mostrar_texto("Pressione ESC para continuar", 28, cons.BRANCO, cons.MEIO_X, cons.MEIO_Y + 20)
            self.mostrar_texto("Pressione R para reiniciar", 28, cons.BRANCO, cons.MEIO_X, cons.MEIO_Y + 50)
            self.mostrar_texto("Pressione Q para sair", 28, cons.BRANCO, cons.MEIO_X, cons.MEIO_Y + 80)

            #opcoes de tecla
            pygame.display.flip()
            for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pausado = False
                        self.jogando = False
                        self.rodando = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pausado = False  #volta ao jogo
                        elif event.key == pygame.K_q:
                            pausado = False
                            self.jogando = False
                            self.rodando = False
                        elif event.key == pygame.K_r:
                            pausado = False
                            self.reiniciar_jogo()
           

    #reset jogo
    def reiniciar_jogo(self):
        self.jogando = False
        self.novo_jogo()
        
    

    def mostrar_texto(self, texto, tamanho, cor, x, y):
        #exibe um texto na tela do jogo
        fonte = pygame.font.Font(self.fonte, tamanho)
        texto = fonte.render(texto, True, cor)
        texto_rect = texto.get_rect()
        texto_rect.midtop = (x, y)
        self.tela.blit(texto, texto_rect)


    def mostrar_logo(self, x, y):
        #start_logo_rect = self.jogo_start_logo.get_rect()
        #start_logo_rect.midtop = (x, y)
        #self.tela.blit(self.jogo_start_logo, start_logo_rect)
        pass


    def esperar_jogador(self):
        esperando = True
        while esperando:
            self.clock.tick(cons.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    esperando = False
                    self.rodando = False
                if event.type == pygame.KEYUP:
                    esperando = False


#####################################################################################


    def novo_jogo(self):
        self.tela_rolar = 0
        self.back_gounds = pygame.sprite.Group()
        self.sprites_fixas = pygame.sprite.Group() 
        self.sprites_dinamicas = pygame.sprite.Group()

        self.colisao_cenario = pygame.sprite.Group()
        self.colisao_caixas = pygame.sprite.Group()
        self.colisao_botoes = pygame.sprite.Group()
        self.limites = pygame.sprite.Group()

        sensor_esq = spr.Plataforma_arbritaria(cons.LIXO-32, -160, 32, cons.ALTURA + 2*160)
        sensor_dir = spr.Plataforma_arbritaria(cons.LARGURA-cons.LIXO, -160, 32, cons.ALTURA + 2*160)
        self.tela_desligada = spr.Mundo_desligado()
        self.divisao = spr.BackGround(0, cons.MEIO_Y-8, "P")
        back_ground_invert = spr.BackGround(0, cons.MEIO_Y, "F")

        self.ler_layout()
        self.criar_mundo()


        self.back_gounds.add(back_ground_invert)
        self.sprites_fixas.add(self.tela_desligada, self.divisao)
        self.limites.add(sensor_esq,sensor_dir)


        self.rodar()
        self.game_over() #habilita o game over novamente

    def ler_layout(self):
        self.layout = []
        for linha in range(cons.LINHAS):
            l = [-1]*cons.COLUNAS
            self.layout.append(l)
        
        with open("nivel.csv", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")

            for x, linha in enumerate(reader):
                for y, bloco in enumerate(linha):
                    self.layout[x][y] = int(bloco)


    def criar_mundo(self):
        for y, linha in enumerate(self.layout):
            for x, celula in enumerate(linha):
                if celula >= 0:
                    img = self.img_list[celula]
                    img_rect = img.get_rect()

                    if celula <= 9:
                        img_rect.topleft = (x*cons.TAMANHO_BLOCO, y*cons.TAMANHO_BLOCO)
                        bloco = spr.Plataforma(img, img_rect)
                        self.colisao_cenario.add(bloco)
                        self.sprites_dinamicas.add(bloco)
                    
                    elif celula == 10:
                        img_rect.topleft = (x*cons.TAMANHO_BLOCO, y*cons.TAMANHO_BLOCO)
                        caixa = spr.Caixa(img, img_rect, cons.VEL_PLAYER)
                        self.colisao_caixas.add(caixa)
                        self.sprites_dinamicas.add(caixa)

                    elif celula == 12:
                        img_rect.topleft = (x*cons.TAMANHO_BLOCO, y*cons.TAMANHO_BLOCO)
                        botao = spr.Botao([self.img_list[celula], self.img_list[celula+2]], img_rect)
                        self.colisao_botoes.add(botao)
                        self.sprites_dinamicas.add(botao)

                    elif celula == 16:
                        self.agente = spr.Agente(x*cons.TAMANHO_BLOCO, y*cons.TAMANHO_BLOCO, 2)
                        self.sprites_fixas.add(self.agente)

                    elif celula == 17:
                        bloco = spr.Plataforma_arbritaria(x*cons.TAMANHO_BLOCO, y*cons.TAMANHO_BLOCO, cons.TAMANHO_BLOCO, cons.TAMANHO_BLOCO)
                        self.colisao_cenario.add(bloco)
                        self.sprites_dinamicas.add(bloco)


    def rodar(self):
        #loop do jogo
        self.jogando = True
        while self.jogando:
            self.clock.tick(cons.FPS)
            self.eventos()
            self.atualizar()
            self.desenhar_sprites()


    def eventos(self):
        #define os eventos do jogo
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.jogando:
                    self.jogando = False
                self.rodando = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.agente.pular(self.colisao_botoes)
                if event.key == pygame.K_SPACE:
                    if self.agente.troca_mundo(self.colisao_cenario):
                        self.tela_desligada.rect.y = (self.tela_desligada.rect.y + cons.MEIO_Y) % cons.ALTURA
                if event.key == pygame.K_ESCAPE:
                    self.pausar_jogo()

                #MIGRARAR TROCA DE MUNDO PARA O ARQUIVO PRINCIPAL!!

        
    def atualizar(self):
        #atualizar sprites
        self.back_gounds.update()
        self.sprites_fixas.update()
        self.sprites_dinamicas.update()
        self.colisao_cenario.update()
        self.divisao.update()

        #atualizar ações
        self.agente.movimento(self.colisao_cenario, self.colisao_caixas, self.colisao_botoes)
        self.tela_rolar = self.agente.borda(self.limites)

        for bloco in self.sprites_dinamicas:
            bloco.rect.x += self.tela_rolar

        for caixa in self.colisao_caixas:
            caixas_temp = self.colisao_caixas.copy()
            caixas_temp.remove(caixa)
            caixa.movimento(self.colisao_cenario, caixas_temp, [self.agente], self.colisao_botoes)
            if caixa.morre([self.divisao]):
                caixa.kill()

        for botao in self.colisao_botoes:
            botao.apertou(self.colisao_caixas, self.agente)

        if self.agente.morre([self.divisao]):
            self.jogando = False

    def desenhar_sprites(self):
        #desenhar sprites
        self.tela.fill(cons.BRANCO) #limpando a tela
        self.back_gounds.draw(self.tela)
        self.sprites_dinamicas.draw(self.tela)
        self.sprites_fixas.draw(self.tela)
        
        pygame.display.flip()


    def game_over(self):
        esperando = True
        while esperando and self.rodando:
            self.clock.tick(cons.FPS)

            # fundo escuro
            self.tela.fill(cons.PRETO)

            # mensagens
            self.mostrar_texto("GAME OVER", 64, cons.VERMELHO, cons.MEIO_X, cons.MEIO_Y - 100)
            self.mostrar_texto("Pressione R para Reiniciar", 32, cons.BRANCO, cons.MEIO_X, cons.MEIO_Y)
            self.mostrar_texto("Pressione Q para Sair", 32, cons.BRANCO, cons.MEIO_X, cons.MEIO_Y + 60)

            pygame.display.flip()

            # capturar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    esperando = False
                    self.rodando = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        esperando = False
                        self.reiniciar_jogo()   # começa de novo
                    elif event.key == pygame.K_q:
                        esperando = False
                        self.rodando = False    # encerra tudo



g = Game()
g.start()

while g.rodando:
    g.novo_jogo()
    #g.game_over()
