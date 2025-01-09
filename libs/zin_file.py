def ler_arquivo(caminho):
    """Lê o conteúdo de um arquivo de texto e retorna como string."""
    try:
        with open(caminho, 'r', encoding='utf-8') as arquivo:
            return arquivo.read()
    except FileNotFoundError:
        return f"Erro: Arquivo '{caminho}' não encontrado."

def escrever_arquivo(caminho, conteudo):
    """Escreve o conteúdo em um arquivo de texto."""
    try:
        with open(caminho, 'w', encoding='utf-8') as arquivo:
            arquivo.write(conteudo)
        return f"Arquivo '{caminho}' salvo com sucesso."
    except Exception as e:
        return f"Erro ao escrever no arquivo: {str(e)}"
