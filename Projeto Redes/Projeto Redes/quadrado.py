"""
Classe Quadrado - Representa um quadrado do tabuleiro
"""

class Quadrado:
    """Representa um quadrado do tabuleiro de damas"""
    
    def __init__(self, cor, ocupante=None):
        """
        Cria um quadrado do tabuleiro
        
        Args:
            cor: Cor visual do quadrado (constantes BRANCO ou PRETO)
            ocupante: Peça presente no quadrado (None = vazio)
        """
        self.cor = cor
        self.ocupante = ocupante  # Referência para objeto Peca ou None
    
    def esta_ocupado(self):
        """Verifica presença de peça no quadrado"""
        return self.ocupante is not None
    
    def esta_vazio(self):
        """Verifica ausência de peça no quadrado"""
        return self.ocupante is None
    
    def colocar_peca(self, peca):
        """Posiciona peça no quadrado"""
        self.ocupante = peca
    
    def remover_peca(self):
        """Remove e retorna peça do quadrado"""
        peca_removida = self.ocupante
        self.ocupante = None
        return peca_removida
