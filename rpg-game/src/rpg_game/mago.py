from personagem import Personagem

class Mago(Personagem):

    def lancar_bola_de_fogo(self, oponente):
        custo_mana = 2
        if (self.mana - custo_mana) < 0:
            print(f"Ataque falhou, seu mana acabou. O oponente riu!")
            self.mana = 0
        else:
            dano_fogo = self.forca * 2
            print(f"🔥 {self.nome} lançou uma BOLA DE FOGO em {oponente.nome}!")
            oponente.receber_dano(dano_fogo)
            self.mana -= custo_mana