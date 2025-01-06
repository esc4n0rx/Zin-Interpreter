# Projeto Zin: Interpretador e Compilador

## Sobre o Projeto
O **Zin** é uma linguagem de programação simples e em português, projetada para ensinar conceitos básicos de programação e lógica. O projeto inclui:

- **Lexer**: Para transformar o código-fonte em tokens.
- **Parser**: Para gerar a AST (Abstract Syntax Tree) a partir dos tokens.
- **Interpretador**: Para executar programas escritos em Zin.

## Funcionalidades Implementadas
### 1. Lexer
O Lexer é responsável por identificar e categorizar os elementos do código-fonte. Ele suporta:
- Palavras-chave como `INICIO`, `FIM`, `PROGAMA`, `PRINCIPAL`, `MODULO`, `EXECUTAR`.
- Operadores lógicos e aritméticos (`+`, `-`, `*`, `/`, `>=`, `<=`, `==`, `!=`, `>`, `<`).
- Identificadores, variáveis e tipos (`inteiro`, `texto`, `decimal`, etc.).
- Strings delimitadas por aspas (`"..."` ou `"..."`).
- Estruturas de controle como `SE`, `SENAO`, `ENQUANTO`.

### 2. Parser
O Parser transforma os tokens em uma AST, estruturando o programa. As principais funcionalidades são:

- **Declarações de Variáveis**:
  ```
  variavel nome tipo texto
  variavel idade tipo inteiro
  ```
- **Estruturas de Controle**:
  - `SE` e `SENAO`.
  - `ENQUANTO`.
- **Blocos de Implementação**:
  ```
  IMPLEMENTACAO PROGAMA TESTE.
  ```
- **Módulos e Funções**:
  ```
  MODULO EXEMPLO.
  funcao soma(a, b)
      retorne a + b.
  FIM MODULO.
  ```
- **Execução**:
  ```
  EXECUCAO PROGAMA TESTE.
  EXECUTAR MODULO EXEMPLO.
  ```

### 3. Interpretador
O Interpretador lê a AST gerada pelo Parser e executa o programa. Suporta:
- Declaração e atribuição de variáveis.
- Entrada e saída (`pergunte` e `escreva`).
- Avaliação de expressões matemáticas e lógicas.
- Execução de estruturas de controle (`SE`, `SENAO`, `ENQUANTO`).
- Execução de módulos e funções com suporte a parâmetros e retorno.

## Exemplo de Programa em Zin
```zin
INICIO PROGAMA TESTE.
variavel nome tipo texto
variavel idade tipo inteiro

IMPLEMENTACAO PROGAMA TESTE.
PRINCIPAL.
    pergunte("Qual o seu nome?" {nome}).
    pergunte("Qual a sua idade?" {idade}).
    EXECUTAR MODULO SAUDACAO.
FIM PRINCIPAL.

MODULO SAUDACAO.
funcao cumprimenta(nome)
    escreva("Olá {nome}, seja bem-vindo!").
retorne null.
FIM MODULO.

EXECUCAO PROGAMA TESTE.
EXECUTAR PRINCIPAL.
FIM PROGAMA TESTE.
```

### Comandos Suportados
- **`pergunte`**: Solicita entrada do usuário.
- **`escreva`**: Exibe mensagens no terminal.
- **Estruturas de Controle**:
  - `SE ... SENAO`.
  - `ENQUANTO ... FAÇA`.
- **Módulos e Funções**:
  - Declaração de módulos com funções.
  - Execução de módulos e funções com retorno de valores.

## Estrutura do Projeto

```
/
├── lexer.py          # Lexer para tokenização do código Zin
├── parser.py         # Parser para geração da AST
├── interpretador.py  # Interpretador para execução da AST
├── README.md         # Documentação do projeto
```

## Como Executar

### Pré-requisitos
- Python 3.10 ou superior.

### Executando o Interpretador
1. Crie um arquivo com extensão `.zin` contendo seu programa.
2. Rode o comando no terminal:
   ```
   python interpretador.py <nome_do_arquivo>.zin
   ```

Exemplo:
```bash
python interpretador.py TESTE.zin
```

## Próximos Passos
- Melhorar a documentação com mais exemplos práticos.
- Suporte a mais tipos de dados e operadores.
- Implementar um compilador para traduzir programas Zin para Python.

## Contribuições
Sinta-se à vontade para contribuir com melhorias! Faça um fork do repositório e envie suas sugestões.

## Licença
Este projeto é livre para uso e modificação sob a licença MIT.
