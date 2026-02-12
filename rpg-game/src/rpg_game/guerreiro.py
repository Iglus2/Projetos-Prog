from personagem import Personagem

class Guerreiro(Personagem):

    def usar_escudo(self):
        print(f"🛡️ {self.nome} usou o escudo e recuperou 10 de vida!")
        self.vida += 10