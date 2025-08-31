# sua_app/ml/predict.py (VERSÃO FINAL E COMPLETA)

import joblib
import pandas as pd
import os
import shap

# Construir o caminho para o arquivo do PACOTE (modelo + explicador)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'triage_model_bundle.joblib') # <-- Nome do arquivo atualizado

# Carregar o pacote completo
try:
    bundle = joblib.load(MODEL_PATH)
    model = bundle['model']
    explainer = bundle['explainer']
except (FileNotFoundError, KeyError) as e:
    model = None
    explainer = None
    print(f"Erro: Pacote do modelo não encontrado ou inválido em {MODEL_PATH}. Erro: {e}")

# sua_app/ml/predict.py (substitua a função predict_from_dict)

def predict_from_dict(data: dict):
    if model is None or explainer is None:
        raise RuntimeError("Modelo de Machine Learning ou explicador não foi carregado.")

    df = pd.DataFrame([data])
    
    # 1. Previsão (continua igual)
    prediction_array = model.predict(df)
    prediction = prediction_array[0]
    probabilities = model.predict_proba(df)
    classes = model.classes_
    prob_dict = dict(zip(classes, probabilities[0]))

    # 2. Explicação (lógica ajustada)
    processed_data = model.named_steps['preprocessor'].transform(df)
    
    if hasattr(processed_data, "toarray"):
        processed_data_dense = processed_data.toarray()
    else:
        processed_data_dense = processed_data
    
    feature_names = model.named_steps['preprocessor'].get_feature_names_out()
    
    # Calcular os valores SHAP. A saída agora tem uma estrutura diferente.
    shap_values_matrix = explainer.shap_values(processed_data_dense)
    
    # A matriz de saída tem o formato (n_amostras, n_features, n_classes)
    # Como temos 1 amostra, pegamos o primeiro item.
    shap_values_single_instance = shap_values_matrix[0]

    # Pegamos o índice da classe que foi predita
    predicted_class_index = list(classes).index(prediction)
    
    # Selecionamos os valores SHAP apenas para a classe vencedora
    shap_values_for_prediction = shap_values_single_instance[:, predicted_class_index]
    
    # 3. Construção da Justificativa em Texto (continua igual)
    feature_impacts = sorted(zip(feature_names, shap_values_for_prediction), key=lambda x: abs(x[1]), reverse=True)
    
    justification_parts = ["Decisão baseada nos seguintes fatores principais:"]
    
    for feature, impact in feature_impacts[:3]:
        clean_feature_name = feature.replace('num__', '').replace('cat__', '').replace('text__', '')
        original_value_key = clean_feature_name.split('_')[0]
        original_value = data.get(original_value_key, 'N/A')
        
        direction = "aumentou a chance" if impact > 0 else "diminuiu a chance"
        justification_parts.append(f"- '{original_value_key}' com valor '{original_value}' {direction} desta classificação.")

    justification_str = " ".join(justification_parts)

    return prediction, prob_dict, justification_str