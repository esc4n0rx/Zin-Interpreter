import json
import os
from lexer_gerador import Lexer
from parser_gerador import Parser
import sys

# Meu Deus, pra que tanta importação? Eu só queria um café...
# Mas ok, vamos fingir que somos profissionais.

class Interpretador:
    def __init__(self, arquivo_zin):
        # Esperando que esse arquivo_zin não seja o barulho que o motor do meu pc faz
        self.arquivo_zin = arquivo_zin
        self.contexto = {}  # Onde guardo as variáveis, ou seja, bagunça organizada
        self.modulos = {}   # Módulos, tipo um DLC do jogo
        self.pilha_contexto = []  # Porque empilhar contexto me faz sentir jogador de Tetris

    def processar_arquivo(self):
        # Aqui eu tento ler o arquivo. Espero que ele exista... se não, tchau.
        if not os.path.exists(self.arquivo_zin):
            raise FileNotFoundError(f"Arquivo {self.arquivo_zin} não encontrado.")

        # Pegar nome base sem extensão, igual quando a gente corta a borda do pão
        nome_programa = os.path.splitext(os.path.basename(self.arquivo_zin))[0]
        arquivo_json = f"{nome_programa}.json"

        # Se não tiver json, bora gerar na marra... #TeamGeradorDeAST
        if not os.path.exists(arquivo_json):
            print("Gerando AST...")
            with open(self.arquivo_zin, "r", encoding="utf-8") as arquivo:
                codigo = arquivo.read()

            lexer = Lexer()
            lexer.build()  # Isso aqui faz magia negra? Nem sei, mas deixa rolar
            tokens = lexer.tokenize(codigo)

            parser = Parser(tokens)
            ast = parser.parse()

            with open(arquivo_json, "w", encoding="utf-8") as arquivo_json_out:
                json.dump(ast, arquivo_json_out, indent=4, ensure_ascii=False)
            print(f"AST salva no arquivo: {arquivo_json}")

        # Senão, bora pular essa parte. A gente não gosta de trabalho repetido.
        with open(arquivo_json, "r", encoding="utf-8") as arquivo_json_in:
            self.ast = json.load(arquivo_json_in)
            # Carregamos a AST e temos um lindo dicionário gigante. Felicidade ou caos?

    def executar(self):
        # Esperamos que a AST tenha "programa". Senão, boa sorte, fiasco total.
        if "programa" not in self.ast:
            raise ValueError("AST inválida: estrutura do programa não encontrada.")

        programa = self.ast["programa"]
        print(f"Executando programa: {programa['nome']}")

        # Inicializa variáveis com None, tipo um teste cego
        for variavel in programa["variaveis"]:
            self.contexto[variavel["nome"]] = None

        self.modulos = programa["implementacao"].get("modulos", {})

        # Tem um campo de execução, então bora processar
        if "execucao" in programa:
            for modulo in programa["execucao"]["modulos"]:
                if modulo.lower() == "principal":
                    self.executar_principal(programa["implementacao"]["principal"])
                elif modulo in self.modulos:
                    self.executar_modulo(modulo)
                # Se não existir, a gente ignora... ou faz drama

    def executar_principal(self, comandos):
        # Meu playground de comandos
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
            # Fim do if. E a gente reza pra nada dar erro

    def interpretar_atribuicao(self, comando):
        # Hora de enfiar valores nas variáveis, do jeito que a gente acha certo
        variavel = comando["atribuir"]["variavel"]
        valor = comando["atribuir"]["valor"]

        # Se for dicionário com left e right, é sinal de que tem operação, viva
        if isinstance(valor, dict) and "left" in valor:
            left = self.contexto.get(valor["left"], valor["left"])
            right = self.contexto.get(valor["right"], valor["right"])
            operator = valor["operator"]
            # Nada como ver sinal de +, -, * e /...
            if operator == "+":
                self.contexto[variavel] = int(left) + int(right)
            elif operator == "-":
                self.contexto[variavel] = int(left) - int(right)
            elif operator == "*":
                self.contexto[variavel] = int(left) * int(right)
            elif operator == "/":
                self.contexto[variavel] = int(left) // int(right)
            # Se for outro operador, estamos perdidos
        else:
            # Valor direto, sem emoção
            self.contexto[variavel] = valor

    def interpretar_escreva(self, comando):
        # Mostrar coisas na tela, tipo "Hello World", mas dinamicamente
        texto = comando["escreva"]
        for variavel, valor in self.contexto.items():
            # Troca os placeholders {variavel} pelo valor. #MacGyverDev
            texto = texto.replace(f"{{{variavel}}}", str(valor) if valor is not None else "null")
        print(texto)

    def interpretar_pergunte(self, comando):
        # Este aqui é pra fazer input, porque a vida já não é complicada o bastante
        texto = comando["pergunte"]["texto"]
        variavel = comando["pergunte"]["variavel"]
        resposta = input(f"{texto} ")
        # Vou fingir que o usuário não digita nada absurdo
        if variavel in self.contexto:
            if isinstance(self.contexto[variavel], int):
                # Tentar converter pra int, se der ruim, paciência
                self.contexto[variavel] = int(resposta)
            else:
                self.contexto[variavel] = resposta

    def interpretar_se(self, comando):
        # O famoso if (ou "se"): se isso, faz aquilo, senão, faz banana
        condicao = comando["condicao"]
        bloco_se = comando["bloco_se"]
        bloco_senao = comando.get("bloco_senao", [])

        resultado = self.avaliar_condicao(condicao)

        if resultado:
            self.executar_principal(bloco_se)
        elif bloco_senao:
            self.executar_principal(bloco_senao)

    def interpretar_enquanto(self, comando):
        # Laço while, cuidado pra não virar loop infinito e travar tudo
        condicao = comando["condicao"]
        bloco = comando["bloco"]

        while self.avaliar_condicao(condicao):
            self.executar_principal(bloco)

    def avaliar_condicao(self, condicao):
        # Verificar se left e right estão no contexto ou se são literais
        left = self.contexto.get(condicao["left"], condicao["left"])
        right = self.contexto.get(condicao["right"], condicao["right"])

        # Tentar converter se for dígito. Se não for, paciência
        if isinstance(left, str) and left.isdigit():
            left = int(left)
        if isinstance(right, str) and right.isdigit():
            right = int(right)

        operator = condicao["operator"]

        # Comparações básicas: ==, !=, >, < etc. Tomara que a gente não quebre nada
        if operator == "==":
            return left == right
        elif operator == "!=":
            return left != right
        elif operator == ">":
            return left > right
        elif operator == "<":
            return left < right
        elif operator == ">=":
            return left >= right
        elif operator == "<=":
            return left <= right
        # Se não for nenhum desses, me deixa em paz
        raise ValueError(f"Operador inválido: {operator}")

    def executar_modulo(self, nome_modulo):
        # Hora de rodar o(s) módulo(s). Tipo DLC do jogo, lembrei de novo
        if nome_modulo not in self.modulos:
            raise ValueError(f"Módulo {nome_modulo} não encontrado.")

        funcoes = self.modulos[nome_modulo]
        for funcao in funcoes:
            self.executar_funcao(funcao)

    def executar_funcao(self, funcao):
        # Função com nome, parâmetros, corpo e retorno. Basicamente um mini-sistema solar
        nome_funcao = funcao["nome"]
        parametros = funcao["parametros"]
        corpo = funcao["corpo"]
        retorno = funcao["retorno"]

        # Clona contexto atual (tipo ctrl+c ctrl+v)
        contexto_local = dict(self.contexto)

        self.pilha_contexto.append(self.contexto)
        # Pilha de contextos, só pra complicar a vida

        self.contexto = contexto_local

        # Se não tiver valor pros params, bota None, que é pra ficar confuso
        for param in parametros:
            if param not in self.contexto:
                self.contexto[param] = None

        print(f"Executando função: {nome_funcao} com contexto: {self.contexto}")
        # #DomingãoDoDev

        self.executar_principal(corpo)

        resultado = self.avaliar_expressao(retorno)

        self.contexto = self.pilha_contexto.pop()

        return resultado

    def avaliar_expressao(self, expressao):
        # Faz a conta com base no dicionário mágico
        if isinstance(expressao, dict):
            left = self.contexto.get(expressao["left"], expressao["left"])
            right = self.contexto.get(expressao["right"], expressao["right"])
            operator = expressao["operator"]
            if operator == "+":
                return int(left) + int(right)
            elif operator == "-":
                return int(left) - int(right)
            elif operator == "*":
                return int(left) * int(right)
            elif operator == "/":
                return int(left) // int(right)
        elif isinstance(expressao, str):
            return self.contexto.get(expressao, expressao)
        elif isinstance(expressao, int):
            return expressao
        # Se não entrou nos casos, a gente desiste
        raise ValueError(f"Expressão inválida: {expressao}")


if __name__ == "__main__":
    # Ponto de partida do script, onde a magia começa (ou não)
    if len(sys.argv) < 2:
        print("Uso: python interpretador.py <arquivo_zin>")
        sys.exit(1)

    arquivo_zin = sys.argv[1]
    interpretador = Interpretador(arquivo_zin)
    interpretador.processar_arquivo()
    interpretador.executar()
    # E no final do dia, só queremos que tudo funcione sem levantar exceções
