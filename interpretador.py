import json
import os
import sys
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lexer_gerador import Lexer
from parser_gerador import Parser

class Interpretador:
    def __init__(self, arquivo_zin):
        self.arquivo_zin = arquivo_zin
        self.contexto = {}       # Dicionário geral onde guardamos variáveis
        self.modulos = {}        # Dicionário com módulos (chaves = nome do módulo, valor = AST do módulo)
        self.pilha_contexto = [] # Pilha para contextos de função, se necessário

    def processar_arquivo(self):
        """Gera (se necessário) a AST em JSON e carrega para self.ast."""
        if not os.path.exists(self.arquivo_zin):
            raise FileNotFoundError(f"Arquivo {self.arquivo_zin} não encontrado.")

        nome_programa = os.path.splitext(os.path.basename(self.arquivo_zin))[0]
        arquivo_json = f"{nome_programa}.json"

        if not os.path.exists(arquivo_json):
            print("Gerando AST...")
            with open(self.arquivo_zin, "r", encoding="utf-8") as arquivo:
                codigo = arquivo.read()

            lexer = Lexer()
            lexer.build()
            tokens = lexer.tokenize(codigo)

            parser = Parser(tokens)
            ast = parser.parse()

            with open(arquivo_json, "w", encoding="utf-8") as arquivo_json_out:
                json.dump(ast, arquivo_json_out, indent=4, ensure_ascii=False)
            print(f"AST salva no arquivo: {arquivo_json}")

        with open(arquivo_json, "r", encoding="utf-8") as arquivo_json_in:
            self.ast = json.load(arquivo_json_in)

    def executar(self):
        """Ponto de entrada da execução do programa."""
        if "programa" not in self.ast:
            raise ValueError("AST inválida: não tem chave 'programa'.")

        programa = self.ast["programa"]
        print(f"Executando programa: {programa['nome']}")

        # Inicializa as variáveis definidas em 'variaveis' , simples e direto
        for var_info in programa["variaveis"]:
            var_nome = var_info["nome"]
            var_tipo = var_info["tipo"]

            # Se for lista, convertemos os valores para uma lista Python
            if var_tipo == "lista":
                lista_python = []
                for item in var_info.get("valores", []):
                    # Se for string só de dígitos, convertemos para int
                    if isinstance(item, str) and item.isdigit():
                        lista_python.append(int(item))
                    else:
                        lista_python.append(item)
                self.contexto[var_nome] = lista_python

            # Se for grupo, guardamos como dict com {campos, dados}
            elif var_tipo == "grupo":
                self.contexto[var_nome] = var_info.get("valores", {})

            # Variáveis simples = None de início
            else:
                self.contexto[var_nome] = None

        # Carrega módulos da AST (se existirem),se nao existir ferrou
        implementacao = programa.get("implementacao", {})
        self.modulos = implementacao.get("modulos", {})


        if "importes" in programa:
            for imp_item in programa["importes"]:
                # Cada imp_item = {"importe": "zin_math"}
                self.interpretar_importe(imp_item)

        # Executa o que estiver em 'execucao'
        if "execucao" in programa:
            for modulo in programa["execucao"]["modulos"]:
                if modulo.lower() == "principal":
                    # Executar bloco principal
                    principal = implementacao["principal"]
                    self.executar_principal(principal)
                elif modulo in self.modulos:
                    # Executar módulo
                    self.executar_modulo(modulo)
                # Caso contrário, ignora ou avisa.

    def executar_principal(self, comandos):
        """Executa os comandos de um bloco (por exemplo, principal)."""
        for comando in comandos:
            if "atribuir" in comando:
                self.interpretar_atribuicao(comando)
            elif "escreva" in comando:
                self.interpretar_escreva(comando)
            elif "pergunte" in comando:
                self.interpretar_pergunte(comando)
            elif comando.get("tipo") == "SE":
                self.interpretar_se(comando)
            elif comando.get("tipo") == "ENQUANTO":
                self.interpretar_enquanto(comando)
            elif "executar_modulo" in comando:
                self.executar_modulo(comando["executar_modulo"])
            elif "acesso_lista" in comando:
                valor = self.avaliar_expressao(comando)  
                print(valor)
            elif "acesso_grupo" in comando:
                valor = self.avaliar_expressao(comando)  
                print(valor)
            elif "importe" in comando:
                self.interpretar_importe(comando)

    # -------------------------------------------------
    # Atribuição
    # -------------------------------------------------
    def interpretar_atribuicao(self, comando):
        """
        Exemplo de comando:
        {
          "atribuir": {
            "variavel": "resultado_raiz",
            "valor": { ... AST de expressão ... }
          }
        }
        """
        var_nome = comando["atribuir"]["variavel"]
        expr_ast = comando["atribuir"]["valor"]

        valor_calculado = self.avaliar_expressao(expr_ast)
        self.contexto[var_nome] = valor_calculado

    # -------------------------------------------------
    # Escreva
    # -------------------------------------------------
    def interpretar_escreva(self, comando):
        """
        comando = {"escreva": "Mensagem com {variavel} etc."}
        Substitui placeholders por valores do self.contexto ou faz parsing se precisar.
        """
        texto = comando["escreva"]

        # Substitui {variavel} simples (se for igual ao nome no contexto)
        for variavel, valor in self.contexto.items():
            texto = texto.replace(f"{{{variavel}}}", str(valor) if valor is not None else "null")

        # Se ainda restam placeholders complexos (ex.: {lista[0].campo}), 
        padrao = r"\{([^{}]+)\}"
        # Encontra todos { ... }
        matches = re.findall(padrao, texto)

        for m in matches:
            # m = "algo" dentro de {algo}
            # Verifica se tem '.' ou '[ ]'
            if "." in m or "[" in m:
                # Tenta acessar via AST:
                valor_dinamico = self.avaliar_placeholder_dinamico(m)
                placeholder_str = f"{{{m}}}"
                texto = texto.replace(placeholder_str, str(valor_dinamico))
            else:
                # Se não tiver '.', assume que é uma var normal
                placeholder_str = f"{{{m}}}"
                texto = texto.replace(placeholder_str, str(self.contexto.get(m, "null")))

        print(texto)

    def avaliar_placeholder_dinamico(self, expressao_str):
        """
        Exemplo:
         - "lista_numeros[0]"
         - "grupo_pessoas[1].NOME"
        Vamos criar um dict de AST rápido e chamar avaliar_expressao.
        """
        # Simplificado: suponde que a sintaxe seja algo como "nome[índice].campo"
        # Precisaríamos de um parser real, mas aqui vou fazer parsing manual básico.

        # 1) Se tiver '.', dividimos a parte da lista e do campo
        if "." in expressao_str:
            parte_lista, campo = expressao_str.split(".", 1)  # ex: "grupo_pessoas[1]" e "NOME"
            nome_lista, indice = self.extrair_lista(parte_lista)  # ex: "grupo_pessoas", "1"
            ast_grupo = {
                "acesso_grupo": {
                    "nome": nome_lista,
                    "indice": int(indice),
                    "campo": campo
                }
            }
            return self.avaliar_expressao(ast_grupo)
        else:
            # Sem '.', então deve ser só "lista[0]"
            nome_lista, indice = self.extrair_lista(expressao_str)
            ast_lista = {
                "acesso_lista": {
                    "nome": nome_lista,
                    "indice": int(indice)
                }
            }
            return self.avaliar_expressao(ast_lista)

    def extrair_lista(self, texto):
        """
        Recebe algo tipo "lista_numeros[0]" e retorna ("lista_numeros", "0").
        Simples parse manual: tudo antes do '[' e tudo dentro do '[]'
        """
        if "[" not in texto or "]" not in texto:
            return (texto, 0)  # fallback

        nome, resto = texto.split("[", 1)
        indice_str = resto.split("]", 1)[0]
        return (nome, indice_str)

    # -------------------------------------------------
    # Pergunte
    # -------------------------------------------------
    def interpretar_pergunte(self, comando):
        texto = comando["pergunte"]["texto"]
        variavel = comando["pergunte"]["variavel"]
        resposta = input(f"{texto} ")
        if variavel in self.contexto:
            # Se variável já for int, tenta converter
            if isinstance(self.contexto[variavel], int):
                try:
                    self.contexto[variavel] = int(resposta)
                except ValueError:
                    self.contexto[variavel] = resposta
            else:
                self.contexto[variavel] = resposta

    # -------------------------------------------------
    # SE
    # -------------------------------------------------
    def interpretar_se(self, comando):
        condicao = comando["condicao"]
        bloco_se = comando["bloco_se"]
        bloco_senao = comando.get("bloco_senao", [])

        resultado = self.avaliar_condicao(condicao)

        if resultado:
            self.executar_principal(bloco_se)
        else:
            self.executar_principal(bloco_senao)

    def avaliar_condicao(self, condicao_ast):
        """
        Normalmente, condicao_ast poderia ser algo como:
        {"left": "idade", "operator": ">=", "right": 18}
        """
        # Podemos reutilizar avaliar_expressao se quisermos suportar expressões mais complexas.
        # A diferença é que condicao_ast tem 'operator' que seja de comparação.
        val = self.avaliar_expressao(condicao_ast)
        # Se a expressão binária retornar True/False, ótimo. Se retornar um valor numérico,deu ruim 
        return bool(val)

    # -------------------------------------------------
    # ENQUANTO
    # -------------------------------------------------
    def interpretar_enquanto(self, comando):
        condicao = comando["condicao"]
        bloco = comando["bloco"]

        while True:
            teste = self.avaliar_condicao(condicao)
            if not teste:
                break
            self.executar_principal(bloco)

    # -------------------------------------------------
    # IMPORTAR MÓDULOS
    # -------------------------------------------------
    def interpretar_importe(self, comando):
        nome_modulo = comando["importe"]
        try:
            modulo = __import__(f"libs.{nome_modulo}", fromlist=["*"])
            self.contexto[nome_modulo] = modulo
            print(f"Módulo '{nome_modulo}' importado com sucesso.")
        except ImportError:
            raise ImportError(f"Erro ao importar o módulo '{nome_modulo}'. Verifique se existe em 'libs'.")

    # -------------------------------------------------
    # Execução de módulos
    # -------------------------------------------------
    def executar_modulo(self, nome_modulo):
        if nome_modulo not in self.modulos:
            raise ValueError(f"Módulo '{nome_modulo}' não encontrado na AST.")
        funcoes = self.modulos[nome_modulo]
        for func in funcoes:
            self.executar_funcao(func)

    def executar_funcao(self, funcao):
        """
        funcao = {
          "nome": "...",
          "parametros": [...],
          "corpo": [...],
          "retorno": ...
        }
        """
        nome_funcao = funcao["nome"]
        parametros = funcao["parametros"]
        corpo = funcao["corpo"]
        retorno_ast = funcao["retorno"]

        # Cria um contexto local copiando do global
        contexto_local = dict(self.contexto)
        self.pilha_contexto.append(self.contexto)
        self.contexto = contexto_local

        # Inicializa parâmetros com None se não existirem
        for p in parametros:
            if p not in self.contexto:
                self.contexto[p] = None

        print(f"Executando função: {nome_funcao}")

        self.executar_principal(corpo)
        resultado = self.avaliar_expressao(retorno_ast)

        # Restaura contexto anterior
        self.contexto = self.pilha_contexto.pop()

        return resultado

    # -------------------------------------------------
    # Avaliação de Expressões (coração do interpretador)
    # -------------------------------------------------
    def avaliar_expressao(self, expr):
        """
        Avalia recursivamente o nó da AST de 'expr' e retorna o valor real (int, float, str etc.).
        """

        # 1) Se for literal numérico
        if isinstance(expr, (int, float)):
            return expr

        # 2) Se for string, pode ser uma variável no contexto
        if isinstance(expr, str):
            return self.contexto.get(expr, expr)

        # 3) Se for dicionário, analisamos cada tipo possível
        if isinstance(expr, dict):
            # a) chamada_modulo
            if "chamada_modulo" in expr:
                return self.executar_chamada_modulo(expr["chamada_modulo"])

            # b) acesso_lista
            if "acesso_lista" in expr:
                return self.avaliar_acesso_lista(expr["acesso_lista"])

            # c) acesso_grupo
            if "acesso_grupo" in expr:
                return self.avaliar_acesso_grupo(expr["acesso_grupo"])

            # d) expressão binária (left, operator, right)
            if "left" in expr and "operator" in expr and "right" in expr:
                left_val = self.avaliar_expressao(expr["left"])
                right_val = self.avaliar_expressao(expr["right"])
                op = expr["operator"]

                # Converte se for string numérica
                if isinstance(left_val, str) and left_val.isdigit():
                    left_val = int(left_val)
                if isinstance(right_val, str) and right_val.isdigit():
                    right_val = int(right_val)

                if op == "+": return left_val + right_val
                if op == "-": return left_val - right_val
                if op == "*": return left_val * right_val
                if op == "/": return left_val // right_val
                if op == "==": return left_val == right_val
                if op == "!=": return left_val != right_val
                if op == ">": return left_val > right_val
                if op == "<": return left_val < right_val
                if op == ">=": return left_val >= right_val
                if op == "<=": return left_val <= right_val
                raise ValueError(f"Operador não suportado: {op}")

        # 4) Se nada se encaixa, erro
        raise ValueError(f"Expressão inválida: {expr}")

    def executar_chamada_modulo(self, info):
        """
        info = {
          "modulo": "zin_math",
          "funcao": "raiz_quadrada",
          "argumentos": [ ... AST ... ]
        }
        """
        nome_modulo = info["modulo"]
        nome_funcao = info["funcao"]
        args_ast = info["argumentos"]

        # Avalia cada argumento
        args_val = [self.avaliar_expressao(a) for a in args_ast]

        if nome_modulo not in self.contexto:
            raise ValueError(f"Módulo '{nome_modulo}' não foi importado ou não está no contexto.")

        modulo_obj = self.contexto[nome_modulo]

        if not hasattr(modulo_obj, nome_funcao):
            raise ValueError(f"Função '{nome_funcao}' não encontrada no módulo '{nome_modulo}'.")

        func = getattr(modulo_obj, nome_funcao)
        resultado = func(*args_val)
        return resultado

    def avaliar_acesso_lista(self, acesso):
        """
        acesso = {
          "nome": "lista_numeros",
          "indice": expr (pode ser int ou AST)
        }
        """
        nome_lista = acesso["nome"]
        indice_ast = acesso["indice"]
        indice_val = self.avaliar_expressao(indice_ast) if isinstance(indice_ast, dict) else indice_ast

        if nome_lista not in self.contexto or not isinstance(self.contexto[nome_lista], list):
            raise ValueError(f"'{nome_lista}' não é uma lista válida.")

        if not isinstance(indice_val, int):
            raise ValueError(f"Índice '{indice_val}' não é inteiro para a lista '{nome_lista}'.")

        lista = self.contexto[nome_lista]
        if indice_val < 0 or indice_val >= len(lista):
            raise IndexError(f"Índice '{indice_val}' fora do intervalo para a lista '{nome_lista}'.")

        return lista[indice_val]

    def avaliar_acesso_grupo(self, acesso):
        """
        acesso = {
          "nome": "grupo_pessoas",
          "indice": expr (pode ser int ou AST),
          "campo": "FUNCAO"  (por exemplo)
        }
        """
        nome_grupo = acesso["nome"]
        indice_ast = acesso["indice"]
        campo = acesso["campo"]

        indice_val = self.avaliar_expressao(indice_ast) if isinstance(indice_ast, dict) else indice_ast

        if nome_grupo not in self.contexto or not isinstance(self.contexto[nome_grupo], dict):
            raise ValueError(f"'{nome_grupo}' não é um grupo válido.")

        grupo = self.contexto[nome_grupo]
        campos = grupo.get("campos", [])
        dados = grupo.get("dados", [])

        if not isinstance(indice_val, int) or indice_val < 0 or indice_val >= len(dados):
            raise IndexError(f"Índice '{indice_val}' fora do intervalo para o grupo '{nome_grupo}'.")

        if campo not in campos:
            raise ValueError(f"Campo '{campo}' não encontrado no grupo '{nome_grupo}'.")

        campo_index = campos.index(campo)
        return dados[indice_val][campo_index]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python interpretador.py <arquivo_zin>")
        sys.exit(1)

    arquivo_zin = sys.argv[1]
    interpretador = Interpretador(arquivo_zin)
    interpretador.processar_arquivo()
    interpretador.executar()
