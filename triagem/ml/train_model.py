import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
import joblib
import shap

# 1. Carregar os dados
print("Carregando dados...")
df = pd.read_csv('dados_triagem.csv')

# Definir as features (X) e o alvo (y)
features = ['temperatura', 'pressao_sistolica', 'pressao_diastolica', 'pulso', 'frequenciaRespiratoria', 'saturacao', 'glicemia', 'dor', 'sintomas_associados', 'queixa']
target = 'classificacao'

X = df[features]
y = df[target]

# 2. Definir o pré-processamento
# Features numéricas que precisam ser escaladas
numeric_features = ['temperatura', 'pressao_sistolica', 'pressao_diastolica', 'pulso', 'frequenciaRespiratoria', 'saturacao', 'glicemia', 'dor']

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

# 7. Criar o explicador SHAP
print("Criando o explicador SHAP...")

# Transformamos os dados de treino
processed_X_train = model_pipeline.named_steps['preprocessor'].transform(X_train)

# --- A CORREÇÃO ESTÁ AQUI ---
# Verificamos se a saída é uma matriz esparsa e a convertemos para um array denso
if hasattr(processed_X_train, "toarray"):
    processed_X_train_dense = processed_X_train.toarray()
else:
    processed_X_train_dense = processed_X_train
# --- FIM DA CORREÇÃO ---

# Criamos o explicador com os dados no formato denso e correto
print("Criando o explicador SHAP (usando a abordagem robusta)...")
explainer = shap.Explainer(
    model_pipeline.named_steps['classifier'].predict_proba,
    processed_X_train_dense
)

# 8. Salvar o modelo E o explicador juntos
model_filename = 'triage_model_bundle.joblib'
print(f"Salvando o modelo e o explicador em '{model_filename}'...")
joblib.dump({'model': model_pipeline, 'explainer': explainer}, model_filename)

print("Treinamento concluído e pacote (modelo + explicador) salvo com sucesso!")
