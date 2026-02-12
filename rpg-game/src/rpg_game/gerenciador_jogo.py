from guerreiro import Guerreiro
from mago import Mago
from personagem import Personagem

# Criando os lutadores
heroi = Guerreiro("Arthur", 100, 15, 50)
vilao = Personagem("Orc Lider", 80, 12, 0)

print("⚔️ A BATALHA COMEÇOU! ⚔️")

while heroi.esta_vivo() and vilao.esta_vivo():
    heroi.status()
    vilao.status()
    
    # Turno do Herói
    heroi.atacar(vilao)
    
    if vilao.esta_vivo():
        # Turno do Vilão
        vilao.atacar(heroi)
    
    print("-" * 30)

print("FIM DE JOGO!")
