"""
Classe Peca - Representa uma peça do jogo de damas
"""

class Peca:
    """Representa uma peça no jogo de damas"""
    
    def __init__(self, cor, rei=False):
        """
        Cria uma nova peça de damas
        
        Args:
            cor: Cor da peça (constantes VERDE ou AMARELO)
            rei: Status de promoção (False = peça comum, True = dama)
        """
        self.cor = cor
        self.rei = rei  # Determina capacidades de movimento
        self.e_dama = rei  # Alias para compatibilidade com código do servidor
    
    def tornar_rei(self):
        """Promove peça comum para dama (rei)"""
        self.rei = True
        self.e_dama = True
    
    def promover_dama(self):
        """Alias para tornar_rei() - usado pelo servidor"""
        self.tornar_rei()
