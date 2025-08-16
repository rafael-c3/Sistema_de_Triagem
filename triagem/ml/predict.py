import joblib
import pandas as pd
import os

# Construir o caminho para o arquivo do modelo de forma robusta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'triage_model.joblib')

# Carregar o modelo uma vez quando o módulo é importado
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    model = None
    print(f"Erro: Arquivo do modelo não encontrado em {MODEL_PATH}")

def predict_from_dict(data: dict):
    """
    Realiza a predição da classificação de risco a partir de um dicionário de dados do paciente.
    """
    if model is None:
        raise RuntimeError("Modelo de Machine Learning não foi carregado.")

    # 1. Converter o dicionário para um DataFrame do Pandas.
    #    É CRUCIAL que a ordem e os nomes das colunas sejam os mesmos usados no treinamento.
    df = pd.DataFrame([data])
    
    # Garantir a ordem correta das colunas
    feature_order = ['temperatura', 'pressaoArterial', 'pulso', 'frequenciaRespiratoria', 'saturacao', 'glicemia', 'dor', 'sintomas_associados', 'queixa']
    df = df[feature_order]

    # 2. Fazer a predição
    # O pipeline cuidará de todo o pré-processamento
    prediction = model.predict(df)
    probabilities = model.predict_proba(df)
    
    # Mapear as probabilidades para as classes para melhor entendimento
    classes = model.classes_
    prob_dict = dict(zip(classes, probabilities[0]))

    # Retorna a classe predita (ex: 'Amarelo') e as probabilidades de cada classe
    return prediction[0], prob_dict