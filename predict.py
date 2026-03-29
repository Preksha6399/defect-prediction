import json
import os
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

def features_to_text(features):
    la = features.get('la', 0)
    ld = features.get('ld', 0)
    nf = features.get('nf', 0)
    ns = features.get('ns', 0)
    nd = features.get('nd', 0)
    entropy = features.get('entropy', 0.0)
    ndev = features.get('ndev', 0)
    lt = features.get('lt', 0)
    nuc = features.get('nuc', 0)
    age = features.get('age', 0.0)
    exp = features.get('exp', 0)
    rexp = features.get('rexp', 0.0)
    sexp = features.get('sexp', 0)

    entropy_level = 'HIGH' if entropy > 2.0 else 'MED' if entropy > 1.0 else 'LOW'

    text = (
        f"[CHG] +{la} -{ld} nf:{nf} ns:{ns} nd:{nd} "
        f"[CMP] E:{entropy_level} LT:{lt} NUC:{nuc} "
        f"[EXP] DEV:{ndev} exp:{exp} rexp:{rexp} sexp:{sexp} age:{age}"
    )
    return text

def predict_defect(features):
    model_repo = os.environ.get('HF_MODEL_REPO', 'Preksha172/jit-defect-prediction-codebert')
    
    print(f"Loading model from {model_repo}...")
    tokenizer = AutoTokenizer.from_pretrained(model_repo)
    model = AutoModelForSequenceClassification.from_pretrained(model_repo)
    model.eval()
    print("Model loaded successfully.")

    text = features_to_text(features)
    print(f"Input text: {text}")

    inputs = tokenizer(
        text,
        return_tensors='pt',
        max_length=256,
        truncation=True,
        padding=True
    )

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=-1)
        defect_prob = probs[0][1].item()

    if defect_prob >= 0.60:
        risk = 'HIGH'
    elif defect_prob >= 0.30:
        risk = 'MEDIUM'
    else:
        risk = 'LOW'

    return defect_prob, risk

with open('features.json', 'r') as f:
    features = json.load(f)

print("Loaded features:", features)

probability, risk = predict_defect(features)

result = {
    "probability": round(probability, 4),
    "risk": risk
}

print(f"\nResult: Risk={risk}, Probability={probability:.4f}")

with open('prediction_result.json', 'w') as f:
    json.dump(result, f)

print("Saved to prediction_result.json")

