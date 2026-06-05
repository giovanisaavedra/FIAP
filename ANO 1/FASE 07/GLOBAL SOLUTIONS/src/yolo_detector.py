"""
Detecção de objetos com YOLOv8 — modelo especializado em imagens aéreas
(`yolov8n-obb.pt`, treinado no dataset DOTA).

Roda sobre as imagens coletadas (Sentinel-2 RGB e Mapbox aerial) e devolve
contagens estruturadas + imagem anotada.

Histórico: começamos usando `yolov8n.pt` (treinado em COCO), mas COCO foi
construído a partir de fotos horizontais ao nível do solo — em imagens
aéreas top-down ele não reconhece praticamente nada. Migramos para o
modelo OBB (Oriented Bounding Boxes) treinado em DOTA, que tem classes
específicas de visão aérea: small-vehicle, large-vehicle, storage-tank,
plane, ship, helicopter, harbor, etc.

Observação: o modelo `yolov8n-obb.pt` é baixado automaticamente pela
Ultralytics na primeira execução (~6MB).
"""

import os

import numpy as np
from PIL import Image as PILImage
from ultralytics import YOLO


# Cache de modelos por caminho — carrega o YOLO uma única vez por processo
# para evitar o overhead de inicialização a cada chamada de detect_objects.
_yolo_model_cache: dict = {}


def _get_model(model_path: str) -> YOLO:
    """Devolve um modelo YOLO carregado, reutilizando o cache em memória."""
    if model_path not in _yolo_model_cache:
        _yolo_model_cache[model_path] = YOLO(model_path)
    return _yolo_model_cache[model_path]


def detect_objects(
    image_path: str,
    output_annotated_path: str,
    confidence_threshold: float = 0.25,
    model_path: str = "yolov8n-obb.pt",
) -> dict:
    """
    Roda YOLOv8 em uma imagem e retorna detecções estruturadas.

    Args:
        image_path: caminho da imagem de entrada (PNG/JPG)
        output_annotated_path: caminho onde salvar a imagem com bounding boxes
        confidence_threshold: confiança mínima para considerar detecção (0-1)
        model_path: nome ou caminho do modelo YOLO. Default: `yolov8n-obb.pt`
                    (modelo aéreo treinado em DOTA). Para usar o modelo COCO
                    clássico, passar `"yolov8n.pt"` — esta função detecta o
                    formato de saída automaticamente.

    Returns:
        dict com chaves:
            - 'total_detections': int
            - 'class_counts': dict (ex: {'small-vehicle': 12, 'storage-tank': 2})
            - 'confidence_avg': float
            - 'annotated_image_path': str
            - 'detections': list[dict] com 'class', 'confidence' e:
                  * 'bbox_poly' (4 pontos [[x,y], ...]) — modelos OBB
                  * 'bbox'      ([x1, y1, x2, y2])      — modelos retangulares
            - 'model_used': str (caminho/nome do modelo, para auditoria)
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

    model = _get_model(model_path)
    # `verbose=False` evita logs poluindo o stdout do pipeline.
    results = model(image_path, conf=confidence_threshold, verbose=False)

    detections: list = []
    class_counts: dict = {}
    confidences: list = []

    for result in results:
        # Modelos OBB expõem `result.obb`; modelos retangulares expõem
        # `result.boxes`. Tratamos os dois para manter retrocompatibilidade
        # caso alguém troque o modelo de volta para `yolov8n.pt` (COCO).
        obb = getattr(result, "obb", None)
        boxes = getattr(result, "boxes", None)

        # --- Caminho 1: modelo OBB (aéreo, ex. yolov8n-obb.pt) -------------
        if obb is not None and len(obb) > 0:
            n = len(obb)
            for i in range(n):
                cls_id = int(obb.cls[i])
                class_name = result.names[cls_id]
                confidence = float(obb.conf[i])
                # `xyxyxyxy` é um polígono rotacionado (4 pontos).
                bbox_poly = obb.xyxyxyxy[i].tolist()

                detections.append({
                    "class": class_name,
                    "confidence": round(confidence, 3),
                    "bbox_poly": [[round(v, 1) for v in pt] for pt in bbox_poly],
                })
                class_counts[class_name] = class_counts.get(class_name, 0) + 1
                confidences.append(confidence)

        # --- Caminho 2: modelo retangular padrão (fallback, ex. COCO) ------
        elif boxes is not None and len(boxes) > 0:
            for box in boxes:
                cls_id = int(box.cls[0])
                class_name = result.names[cls_id]
                confidence = float(box.conf[0])
                bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]

                detections.append({
                    "class": class_name,
                    "confidence": round(confidence, 3),
                    "bbox": [round(v, 1) for v in bbox],
                })
                class_counts[class_name] = class_counts.get(class_name, 0) + 1
                confidences.append(confidence)

    # Salva a imagem anotada (`result.plot()` funciona tanto para OBB quanto
    # para boxes retangulares). Devolve numpy array em BGR — convertemos
    # para RGB antes de salvar via PIL.
    for result in results:
        annotated_bgr = result.plot()
        annotated_rgb = annotated_bgr[:, :, ::-1]
        PILImage.fromarray(np.ascontiguousarray(annotated_rgb)).save(
            output_annotated_path
        )
        break  # só processamos uma imagem por chamada

    confidence_avg = (
        round(sum(confidences) / len(confidences), 3) if confidences else 0.0
    )

    return {
        "total_detections": len(detections),
        "class_counts": class_counts,
        "confidence_avg": confidence_avg,
        "annotated_image_path": output_annotated_path,
        "detections": detections,
        "model_used": model_path,
    }
