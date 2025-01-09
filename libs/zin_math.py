import math

def raiz_quadrada(valor):
    """Retorna a raiz quadrada de um número."""
    return math.sqrt(valor)

def cosseno(angulo):
    """Retorna o cosseno de um ângulo em graus."""
    return math.cos(math.radians(angulo))

def porcentagem(parte, total):
    """Calcula a porcentagem de 'parte' em relação a 'total'."""
    return (parte / total) * 100

def potencia(base, expoente):
    """Calcula a potência de 'base' elevado a 'expoente'."""
    return math.pow(base, expoente)
