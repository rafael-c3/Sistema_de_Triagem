import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
import joblib

# 1. Carregar os dados
print("Carregando dados...")
df = pd.read_csv('dados_triagem.csv')

# Definir as features (X) e o alvo (y)
features = ['temperatura', 'pressaoArterial', 'pulso', 'frequenciaRespiratoria', 'saturacao', 'glicemia', 'dor', 'sintomas_associados', 'queixa']
target = 'classificacao'

X = df[features]
y = df[target]

# 2. Definir o pré-processamento
# Features numéricas que precisam ser escaladas
numeric_features = ['temperatura', 'pressaoArterial', 'pulso', 'frequenciaRespiratoria', 'saturacao', 'glicemia', 'dor']

# Feature categórica que precisa de One-Hot Encoding
categorical_features = ['sintomas_associados']

# Feature de texto que precisa de vetorização
text_feature = 'queixa'

# Criar o transformador de colunas
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
        ('text', TfidfVectorizer(), text_feature)
    ],
    remainder='passthrough' # Mantém outras colunas, se houver
)

# 3. Criar o pipeline do modelo
# O pipeline irá:
# a) Aplicar o pré-processamento
# b) Treinar o modelo de classificação (RandomForestClassifier é uma boa escolha)
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
])

# 4. Dividir dados em treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 5. Treinar o modelo
print("Treinando o modelo...")
model_pipeline.fit(X_train, y_train)

# 6. Avaliar o modelo (opcional, mas recomendado)
print("Avaliando o modelo...")
y_pred = model_pipeline.predict(X_test)
print(classification_report(y_test, y_pred))

# 7. Salvar o pipeline completo (pré-processador + modelo)
model_filename = 'triage_model.joblib'
print(f"Salvando o modelo em '{model_filename}'...")
joblib.dump(model_pipeline, model_filename)

print("Treinamento concluído e modelo salvo com sucesso!")