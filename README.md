![image](https://github.com/user-attachments/assets/7f4dae35-0499-43ce-810a-2fe9ed962b4a)Sistema de Triagem de Pacientes (Versão Protótipada)

## Rodar o Projeto

# Criando a VENV
1 - venv/Scripts/activate
2 - pip install -r requirements.txt

# Rodando o BACK
1 - python manage.py migrate
2 - python manage.py runserver

## Mensagem para o DEV FRONT

1 - Arquivos de Forms estão no forms.py para alterar a classe
2 - Não mexa no type data nem no type datetime-local
3 - Arquivos do HTML estão em Templates/site/
4 - Arquivos para usar o CSS estão em static/front/css/

## Para Subir projeto no GIT

1 - Terceiro ícone da barra lateral esquerda do VScode, Source Control
2 - Na aba Changes, digitar a versão seguinte do projeto + o que foi feito (obrigatorio)
3 - Ao lado do botão Commit, clique na seta, depois em "Commit & Push"
4 - O projeto foi subido para o GitHub

## Regras pra Alteração da Versão

1 - vX.Y Altere Y caso tenha tido alterações significativas
2 - vX.Y.Z Altere Z Caso tenha tido alterações pequenas
