# RELEASE.md

Este arquivo conta a história do repositório A-Maze-ing commit por commit, para entender o que mudou, por que mudou, e qual
problema cada mudança resolve. Ele não repete o `README.md` nem o
`subject`; cita os dois por path quando precisa.

## O que o subject pede, em poucas linhas

Vale ter estes pontos em mente, porque quase toda decisão de código vem de um
deles.

- Cap. IV.2: o programa roda com `python3 a_maze_ing.py config.txt`. O nome do
  arquivo e o argumento único são fixos.
- Cap. IV.3: o config é `KEY=VALUE` por linha, `#` é comentário, e existe um
  config default no repositório.
- Cap. IV.4: o labirinto é aleatório mas reproduzível por seed, tem paredes nos
  quatro pontos cardeais, é conectado, sem células isoladas (exceto o "42"), sem
  área aberta maior que 2x3 ou 3x2, e o "42" é desenhado por células totalmente
  fechadas. Com `PERFECT=True` há um único caminho; com `PERFECT=False` (o
  default) o tabuleiro serve para Pac-Man: tudo alcançável, os quatro cantos e o
  centro abertos, e pelo menos dois caminhos independentes (loops).
- Cap. IV.5: cada célula vira um dígito hexadecimal onde cada bit é uma parede
  fechada (N=1, E=2, S=4, W=8). Depois de uma linha em branco vêm entry, exit e
  o caminho mais curto em letras N/E/S/W.
- Cap. V: precisa de exibição visual e das interações de regenerar, mostrar ou
  esconder o caminho, e trocar a cor das paredes.
- Cap. VI: a geração fica numa classe `MazeGenerator` num módulo único,
  instalável por pip como `mazegen-*`, com `LICENSE.md` que permita reuso.
- Cap. VII: o `README.md` segue a lista daquele capítulo.

O `maze_analyzer.py` que o subject entrega é o nosso oráculo. Todo labirinto
gerado passa por ele antes de dizermos que está pronto.

## Linha do tempo dos commits

### `0f21330` chore: checkpoint A-Maze-ing slice 0 (19/08/2026)

O primeiro checkpoint entregou a borda de entrada do sistema. O `a_maze_ing.py`
lia o config, validava as chaves obrigatórias, convertia as coordenadas `(x,y)`
do subject para a representação interna `(row, column)` e aceitava um `SEED`
opcional. O `config.txt` default nasceu aqui, junto com o `maze_graph.py` (um
contador de passagens abertas usado nos testes), os dois primeiros arquivos de
teste, o `.gitignore`, o `LICENSE.md` e o `README.md`.

O problema resolvido foi separar o que é "ler e validar a entrada" do que é
"gerar o labirinto". Erros de config viram uma mensagem clara e um exit code
diferente de zero, como o cap. IV.2 pede, em vez de um traceback.

Ligações com o subject: IV.2 (nome do arquivo e argumento), IV.3 (formato do
config e config default), III.1 (exceções tratadas, type hints, docstrings),
III.3 (`.gitignore` e programas de teste, que não são entregues), VI
(`LICENSE.md`) e VII (README).

Neste ponto ainda não havia geração de labirinto: o checkpoint provava a entrada
do programa e o helper de grafo.

### `9b46826` feat: add generator (26/09/2026)

Entrou o `generator.py` com a classe `Generator`. Ela guarda o grid como
bitmask (N=1, E=2, S=4, W=8), aplica a máscara `_PATTERN_42` e cava o labirinto
com um backtracker recursivo escrito de forma iterativa, usando uma lista
explícita como pilha. O `Config` foi movido do `a_maze_ing.py` para o
`config.py`.

O problema principal aqui era o limite de recursão do Python, que fica perto de
1000 frames. Um backtracker recursivo de verdade estoura em labirintos grandes,
então a pilha é manual. O algoritmo em si (recursive backtracker) é um dos
clássicos citados no cap. I.

A máscara do "42" marca as células como já visitadas, então o backtracker nunca
cava nelas e elas ficam fechadas (`0xF`), que é exatamente o que o cap. IV.4
pede: o "42" é desenhado por células totalmente fechadas.

Ligações com o subject: IV.4 (aleatoriedade com seed, paredes cardeais,
conectividade, coerência, sem área aberta grande, "42" visível) e IV.5 (o
bitmask é a base do dígito hexadecimal).

Esta parte veio do trabalho do Vitor.

### `f0e86bd` feat: add menu to the project (27/09/2026)

Criou o `menu.py` com `clear_terminal()` e um loop que imprime as quatro opções
e lê a escolha: regenerar, mostrar ou esconder o caminho, trocar a cor das
paredes, e sair. O `main` passou a chamar `menu()` em vez de desenhar o
labirinto direto.

O problema era o cap. V, que pede exibição visual e interações. As opções 1 a 4
seguem exatamente a lista de interações obrigatórias.

Neste commit o caminho mais curto ainda não era desenhado de verdade. O
parâmetro `show_path` existia, mas era um espaço reservado.

### `e2072a5` feat: update to make new mazes (27/09/2026)

A opção 1 passou a construir um novo `Generator` e gerar um labirinto novo antes
de redesenhar, imprimindo "New maze". Antes ela só redesenhava o mesmo grid.

O problema era a interação "re-generate a new maze" do cap. V: sem criar um
labirinto novo, o botão não fazia nada de útil.

### `aa89ef5` feat: add color change to terminal (27/09/2026)

Entrou o `color.py` com `Color.pick_color()`. O `display_ascii` passou a receber
`change_color` e a envolver paredes e bordas em códigos ANSI. Também saíram
comentários antigos em português que ficaram dos testes iniciais.

O problema era a interação de trocar a cor das paredes (cap. V). Optamos por
ASCII com ANSI porque não adiciona dependência nenhuma e é seguro na avaliação,
ao contrário do MLX, que é opcional.

### `c213bf7` feat: update invalid option (27/09/2026)

Quando a escolha não era 1 a 4, o menu passou a limpar a tela, redesenhar o
labirinto e só então imprimir "Please enter a number between 1 and 4." O
`clear_terminal()` inicial também foi reposicionado para a tela não nascer em
branco.

O problema era deixar a tela num estado quebrado depois de um input inválido.
O cap. IV.2 e o cap. III.1 pedem erro tratado com mensagem clara, sem quebrar.

### `cc1fc53` feat: adopt mazegen as the single module and write the output file (01/10/2026)

Este commit juntou os dois caminhos que existiam. O `mazegen.py` passou a ser o
módulo único, com a classe `MazeGenerator` (dataclass com `width`, `height`,
`seed` e `draw_42`), o backtracker, a máscara do "42", o `solve` em BFS e o
`write_output`. O `generator.py` do Vitor foi absorvido e deletado.

O `write_output` grava o grid em hexadecimal, uma linha por linha, depois a
linha em branco e o rodapé com entry, exit e o caminho. Foi aqui que o
`menu.py` passou a renderizar a partir do `mazegen` e a escrever o
`OUTPUT_FILE` a cada geração.

Dois problemas apareceram e foram resolvidos.

O primeiro era ter dois geradores no repositório. O cap. VI exige uma classe
`MazeGenerator` num módulo único, importável e empacotável como `mazegen-*`.
Manter o `generator.py` e o `mazegen.py` lado a lado quebraria isso.

O segundo era a troca silenciosa de coordenadas. A representação interna é
`(row, column)`, mas o rodapé do arquivo usa `x,y`, que é `col,row`. Errar essa
troca não dava erro nenhum; o analyzer simplesmente leria entry e exit nos
lugares errados. O `write_output` faz o swap de propósito, e o
`maze_analyzer.py` também lê `(row=y, col=x)`.

Também entraram testes para a máscara e para o caminho ponta a ponta da CLI.

Ligações com o subject: VI (módulo único reusável) e IV.5 (formato do arquivo e
rodapé).

### `bc6726f` fix: regenerate a new maze with a fresh seed (01/10/2026)

O `menu.py` ganhou o `_next_seed(config, first)`: a seed do config vale só na
primeira execução, e cada regeneração sorteia uma seed nova. O `_new_maze`
gera, confere que entry e exit não caíram dentro do "42", e escreve o arquivo.
O menu imprime a seed sempre que ela muda.

O problema era a opção 1 ser um no-op do ponto de vista do resultado: como a
seed do config era reaproveitada, regenerar produzia o mesmo labirinto. O cap.
IV.4 pede reprodutibilidade por seed, então a primeira execução tem que
reproduzir a seed do config, e a regeneração precisa sortear outra para fazer
sentido.

### `a7b8465` chore: update readme and add release.md (01/10/2026)

O `README.md` foi reescrito para o estado real do projeto (config, geração,
solução, serialização, display e interações) em vez do checkpoint do Slice 0, e
este `RELEASE.md` nasceu para registrar commit por commit o que mudou e por quê.

O problema era o README ter ficado preso ao Slice 0, com 11 testes e sem
gerador, o que não descrevia mais o projeto. O cap. VII cobra um README que
qualquer pessoa entenda de primeira.

### `0cb9aaf` feat: add Makefile (02/10/2026, Vitor)

O Vitor adicionou o `Makefile` com os alvos que o cap. III.2 cobra: `install`,
`run`, `debug`, `clean`, `lint` e `lint-strict`, este último com o
`mypy --strict`.

Na primeira versão o `clean` saiu grafado `cleean` e o `install` apontava para
um `requirements.txt` que não existe no repositório. Os dois pontos foram
corrigidos no commit seguinte.

Ligações com o subject: III.2 (os alvos e as flags exatas do `lint`).

### `085541b` feat: add Pac-Man mode, fix Makefile and make lint pass (05/10/2026)

Este commit fechou o modo Pac-Man e deixou o lint limpo.

No `mazegen.py` entrou o campo `perfect` e a pós-produção sobre a spanning
tree: `_braid` abre uma parede em cada dead-end real, e `_add_loops` abre
paredes internas até existirem pelo menos dois loops. Os helpers
`_passage_count`, `_openable_walls` e `_loops` fazem as contas. O `menu.py`
passou a repassar `config.perfect`, e o `config.txt` default virou
`PERFECT=False`, com entry no centro (4,4) e exit no canto (9,9).

O ponto conceitual: Pac-Man não é outro algoritmo, é pós-processamento do
grafo. Abrir uma parede entre duas células já conectadas soma exatamente um
loop, e abrir nunca reduz o grau de uma célula, então o braid não cria dead-end
novo. Os cantos e o centro continuam alcançáveis porque abrir parede não
desconecta nada, e nenhuma parede é aberta para dentro do "42".

Também entraram 7 testes: loops maiores ou iguais a 2, zero dead-end real,
cantos e centro alcançáveis, coerência das paredes, ausência de corredor
desconexo, a regressão do modo perfect e o analyzer aceitando a saída. No
`flake8` e no `mypy`, todas as pendências foram resolvidas, com anotações de
tipo nos testes e quebras de linha no código.

No Makefile, o alvo `clean` passou a remover `__pycache__`, `.mypy_cache` e
`.pytest_cache`; o `install` deixou de apontar para o `requirements.txt`
inexistente e instala `pytest`, `flake8` e `mypy`; e o `flake8` ganhou
`--exclude=.venv`, porque sem isso ele varria o venv e acusava 120 erros.

Ligações com o subject: IV.4 (o board Pac-Man), III.1 (lint), III.2 (Makefile)
e III.3 (testes).

### `67cc032` feat: package mazegen as a pip-installable wheel and sdist (05/10/2026)

Entrou o `pyproject.toml` (backend setuptools, `name = "mazegen"`,
`version = "1.0.0"`, `requires-python = ">=3.10"`, `license = "MIT"` com
`license-files = ["LICENSE.md"]` e `py-modules = ["mazegen"]`). O `install` do
Makefile passou a fazer `pip install -e .` antes de instalar as ferramentas de
desenvolvimento.

O problema era o cap. VI: o módulo precisa ser instalável por pip, e o arquivo
`mazegen-*` precisa ficar na raiz do repositório. O `python -m build` gerou
`mazegen-1.0.0-py3-none-any.whl` e `mazegen-1.0.0.tar.gz`, que foram copiados
para a raiz e liberados no `.gitignore`. As regras genéricas `*.whl` e
`*.tar.gz` continuam valendo para o resto, com uma exceção para `mazegen-*`. O
build em si fica em `dist/`, que segue ignorado.

Validação: o wheel e o sdist foram instalados em dois venvs limpos, com o
`import mazegen` vindo de `site-packages` e a geração nos dois modos conferida.
O wheel carrega só o `mazegen.py` e a metadata, e o sdist reconstrói o pacote a
partir das fontes.

Um detalhe de build: o classifier `License :: OSI Approved :: MIT License` teve
de sair, porque o setuptools novo recusa combiná-lo com a expressão SPDX
`license = "MIT"`.

Ligações com o subject: VI (pacote `mazegen-*` instalável, artefato na raiz,
`LICENSE.md`) e VII (o README como documentação do módulo).

## Onde estamos agora

Estado verificado no fim da sessão de 05/10/2026:

```bash
.venv/bin/python -m pytest -q          # 34 passed
make lint                              # flake8 e mypy limpos
printf '4\n' | make run                # escreve maze.txt, imprime "Seed: 42"
python3 maze_analyzer.py maze.txt      # Verdict: Pac-Man-USABLE (bonus)
python -m build                        # mazegen-1.0.0 wheel + sdist
```

Os dois modos funcionam ponta a ponta. Com `PERFECT=True` o analyzer dá
`PERFECT maze`; com `PERFECT=False` dá `Pac-Man-USABLE`, sem dead-end real
(nota de bônus) e com dois ou mais loops. O `Makefile` expõe `install`, `run`,
`debug`, `clean`, `lint` e `lint-strict`, e o `flake8`/`mypy` passam com as
flags do subject. O pacote `mazegen` builda e instala em venv limpo, tanto pelo
wheel quanto pelo sdist.

## O que vem a seguir

Falta a defesa.

- Ensaio da defesa, incluindo a "brief modification" do cap. IX, com uma lista
  de mudanças prováveis para treinar: trocar a posição do "42", mudar o bit de
  encode, adicionar uma chave no config, e outras do mesmo tamanho.

## Pontos em aberto

- O `maze_analyzer.py` está versionado, apesar de o plano prever que o
  entregável não o inclua. Decidir antes da entrega.
- O subject v2.3 tem a seção Pac-Man idêntica à v2.2, então a implementação não
  muda; o PDF novo ficou no `.gitignore`.
- Os `HANDOFF*.md` seguem untracked, como artefatos de sessão.
