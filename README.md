# Sistema de Triagem de Pacientes (Versão Protótipada)

- (Sem descrição por enquanto)

## Rodar o Projeto

### Criando a VENV
- ```venv/Scripts/activate
- pip install -r requirements.txt```

### Rodando o BACK
- ```python manage.py migrate
- python manage.py runserver```

#### Mensagem para o DEV FRONT

- Arquivos de Forms estão no forms.py para alterar a classe
- Não mexa no type data nem no type datetime-local
- Arquivos do HTML estão em Templates/site/
- Arquivos para usar o CSS estão em static/front/css/

#### Para Subir projeto no GIT

- Terceiro ícone da barra lateral esquerda do VScode, Source Control
- Na aba Changes, digitar a versão seguinte do projeto + o que foi feito (obrigatorio)
- Ao lado do botão Commit, clique na seta, depois em "Commit & Push"
- O projeto foi subido para o GitHub

#### Regras pra Alteração da Versão

- vX.Y Altere Y caso tenha tido alterações significativas
- vX.Y.Z Altere Z Caso tenha tido alterações pequenas
