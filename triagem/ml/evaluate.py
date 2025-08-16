# evaluate.py

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# --- Carregamento ---
# Carrega o modelo treinado
print("Carregando modelo...")
model_pipeline = joblib.load('triage_model.joblib')

# Carrega o mesmo conjunto de dados usado para treinar
print("Carregando dados para avaliação...")
df = pd.read_csv('dados_triagem.csv')

# --- Preparação dos Dados de Teste ---
# Garanta que a divisão seja a MESMA do script de treino (usando o mesmo random_state)
features = ['temperatura', 'pressaoArterial', 'pulso', 'frequenciaRespiratoria', 'saturacao', 'glicemia', 'dor', 'sintomas_associados', 'queixa']
target = 'classificacao'

X = df[features]
y = df[target]

# Dividimos os dados novamente APENAS para pegar o conjunto de teste
# É crucial usar o mesmo random_state e test_size do script de treino
_, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# --- Avaliação ---
print("Fazendo previsões no conjunto de teste...")
y_pred = model_pipeline.predict(X_test)

# --- Exibição dos Resultados ---
# 1. Acurácia Geral
accuracy = accuracy_score(y_test, y_pred)
print("\n--- Resultados da Avaliação ---")
print(f"Acurácia do Modelo: {accuracy:.2%}")

# 2. Relatório de Classificação Detalhado
print("\nRelatório de Classificação:")
print(classification_report(y_test, y_pred))

# 3. Matriz de Confusão (uma forma visual de ver os erros e acertos)
print("\nMatriz de Confusão:")
cm = confusion_matrix(y_test, y_pred, labels=model_pipeline.classes_)
print("Linhas: Real / Colunas: Previsão do Modelo")
print(pd.DataFrame(cm, index=model_pipeline.classes_, columns=model_pipeline.classes_))

# Opcional: Plotar a matriz de confusão para ficar mais bonito
# (pode precisar instalar: pip install matplotlib seaborn)
plt.figure(figsize=(10, 7))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=model_pipeline.classes_, yticklabels=model_pipeline.classes_)
plt.xlabel('Previsão do Modelo')
plt.ylabel('Classe Real')
plt.title('Matriz de Confusão')
plt.show()