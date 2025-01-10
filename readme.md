# Zin - Linguagem de Programação Simples

Zin é uma linguagem de programação educacional criada para facilitar o aprendizado de lógica de programação e estrutura de código. Com sintaxe em português, Zin visa ser intuitiva e acessível para iniciantes.

## Funcionalidades

- **Variáveis e Tipos**: Suporte para variáveis de tipos como `inteiro`, `texto`, `decimal`, `lista` e `grupo`.
- **Estruturas Condicionais**: `SE`, `SENAO`.
- **Laços de Repetição**: `ENQUANTO`.
- **Funções**: Definição e execução de funções customizadas.
- **Modularidade**: Suporte a módulos e execução modular.
- **Interatividade**: Funções como `pergunte` para entrada do usuário.
- **Escreva**: Saída formatada com substituição dinâmica de variáveis.
- **Manipulação de Listas e Grupos**: Trabalhe com índices, campos e valores de estruturas complexas.
- **Importação de Módulos Externos**: Integre bibliotecas externas para expandir as funcionalidades. bibliotecas podem ser feitas em python.
- **Novo Sistema de Comandos**:
  - `zin -run main.zin`: Executa um arquivo Zin.
  - `zin -version`: Mostra a versão atual da linguagem.
  - `zin -create main.zin`: Cria um arquivo Zin com estrutura base.

## Instalação

### Requisitos
- **Python**: Certifique-se de que o Python está instalado em seu sistema.
- **Git**: Necessário para clonar o repositório.

### Passos de Instalação

1. **Baixe o Instalador**:
   Execute o comando abaixo no PowerShell:
   ```powershell
   Invoke-WebRequest -Uri https://raw.githubusercontent.com/esc4n0rx/Zin-Interpreter/refs/heads/master/install_zin.ps1 -OutFile install_zin.ps1
   ```
2. **Execute o Instalador**:
   No PowerShell, execute:
   ```powershell
   .\install_zin.ps1
   ```

3. **Siga as Instruções**:
   O instalador irá:
   - Verificar se o Python está instalado e oferecer para instalar caso não esteja.
   - Verificar se o Git está instalado.
   - Clonar o repositório do Zin.
   - Configurar o executável `zin` no PATH do sistema.

4. **Teste a Instalação**:
   Após concluir, verifique a instalação executando:
   ```powershell
   zin -version
   ```

## Exemplos de Uso

### Criar um Arquivo Base
Crie um novo arquivo `.zin` com a estrutura básica:
```bash
zin -create meu_programa.zin
```

### Executar um Programa Zin
Execute seu programa com:
```bash
zin -run meu_programa.zin
```

### Estrutura de um Programa
Um exemplo simples de programa em Zin:
```zin
INICIO PROGAMA MEU_TESTE.
variavel nome tipo texto

IMPLEMENTACAO PROGAMA MEU_TESTE.
PRINCIPAL.
    pergunte("Qual o seu nome?" {nome}).
    escreva("Olá, {nome}!").
FIM PRINCIPAL.

EXECUCAO PROGAMA MEU_TESTE.
EXECUTAR PRINCIPAL.

FIM PROGAMA MEU_TESTE.
```

## Contribuição

Contribuições são bem-vindas! Clone o repositório, faça alterações e envie um pull request.

## Licença

Este projeto é licenciado sob a [MIT License](LICENSE).

