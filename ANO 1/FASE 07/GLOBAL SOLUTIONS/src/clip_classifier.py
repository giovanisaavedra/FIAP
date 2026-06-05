"""
Classificação de cena via CLIP (zero-shot).

Recebe uma imagem aérea e retorna probabilidades de cada categoria semântica
relevante para due diligence empresarial.

CLIP é um modelo multimodal da OpenAI/HuggingFace. Usamos a variante
`openai/clip-vit-base-patch32` por ser leve (~600MB) e suficiente para
classificação zero-shot.

Hardware: roda em CPU. Em Apple Silicon (M1/M2/M3), usa MPS automaticamente
para aceleração via Metal Performance Shaders; em GPUs NVIDIA, usa CUDA.
"""

import logging
import os
from typing import Dict

import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor


# Categorias semânticas para due diligence empresarial.
# Cada categoria tem uma descrição em inglês otimizada para CLIP
# (CLIP foi treinado predominantemente em inglês — prompts em pt-br
# costumam ter performance bem inferior).
SCENE_CATEGORIES: Dict[str, str] = {
    "industrial": (
        "an aerial top-down view of a large industrial facility with "
        "factories, warehouses, and loading bays"
    ),
    "commercial_dense": (
        "an aerial top-down view of a dense commercial area with many "
        "small shops and busy streets"
    ),
    "residential": (
        "an aerial top-down view of a residential neighborhood with "
        "houses and small streets"
    ),
    "green_area": (
        "an aerial top-down view of a forest, park, or natural green "
        "area with trees"
    ),
    "parking_or_storage": (
        "an aerial top-down view of a large parking lot or vehicle "
        "storage area"
    ),
    "agricultural": (
        "an aerial top-down view of agricultural fields and farmland"
    ),
}


_MODEL_ID = "openai/clip-vit-base-patch32"

# Cache do modelo/processor por processo — CLIP é grande (~600MB) e não
# faz sentido recarregar a cada chamada.
_clip_model_cache: dict = {}
_clip_processor_cache: dict = {}


def _get_device() -> str:
    """Detecta o melhor device disponível: MPS (Apple Silicon), CUDA, ou CPU."""
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def _get_model_and_processor():
    """Carrega CLIP uma única vez (cache em memória)."""
    if _MODEL_ID not in _clip_model_cache:
        logging.info("Carregando CLIP %s...", _MODEL_ID)
        device = _get_device()
        model = CLIPModel.from_pretrained(_MODEL_ID).to(device)
        model.eval()
        processor = CLIPProcessor.from_pretrained(_MODEL_ID)
        _clip_model_cache[_MODEL_ID] = (model, device)
        _clip_processor_cache[_MODEL_ID] = processor

    model, device = _clip_model_cache[_MODEL_ID]
    processor = _clip_processor_cache[_MODEL_ID]
    return model, processor, device


def classify_scene(image_path: str) -> Dict:
    """
    Classifica uma imagem aérea em categorias semânticas via CLIP zero-shot.

    Args:
        image_path: caminho da imagem (PNG/JPG) a classificar

    Returns:
        dict com:
            - 'category_probabilities': dict {category: probability}
            - 'dominant_category': str (categoria com maior probabilidade)
            - 'dominant_score': float (probabilidade da categoria dominante)
            - 'top3': list[tuple] [(category, prob), ...] ordenado decrescente
            - 'model_used': str (identificador do modelo CLIP utilizado)
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

    model, processor, device = _get_model_and_processor()

    # Carrega imagem e força modo RGB (alguns PNGs vêm em RGBA / paleta).
    image = Image.open(image_path).convert("RGB")

    # Prepara os prompts em inglês na ordem das chaves de SCENE_CATEGORIES
    # para podermos mapear o índice da saída de volta para a categoria.
    category_keys = list(SCENE_CATEGORIES.keys())
    text_prompts = [SCENE_CATEGORIES[k] for k in category_keys]

    inputs = processor(
        text=text_prompts,
        images=image,
        return_tensors="pt",
        padding=True,
    ).to(device)

    # Forward sem grad — economiza memória, é só inferência.
    with torch.no_grad():
        outputs = model(**inputs)

    # logits_per_image é matriz [1, N_prompts]; softmax → probabilidades.
    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]

    category_probabilities = {
        category_keys[i]: float(round(float(probs[i]), 4))
        for i in range(len(category_keys))
    }

    sorted_categories = sorted(
        category_probabilities.items(),
        key=lambda kv: kv[1],
        reverse=True,
    )

    dominant_category, dominant_score = sorted_categories[0]
    top3 = sorted_categories[:3]

    return {
        "category_probabilities": category_probabilities,
        "dominant_category": dominant_category,
        "dominant_score": float(dominant_score),
        "top3": top3,
        "model_used": _MODEL_ID,
    }
