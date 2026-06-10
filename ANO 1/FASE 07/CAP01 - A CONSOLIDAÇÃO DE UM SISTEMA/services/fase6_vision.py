"""
FarmTech Solutions - Serviço da Fase 6: Visão Computacional (YOLO)
Detecção de objetos com YOLOv8 + camada de **diagnóstico agrícola**
sobre as classes do COCO. O modelo é carregado em *lazy-loading*
(uma única vez por processo) e o resultado de cada imagem é
persistido em ``analises_visuais``.

NOTA — A camada de diagnóstico agrícola é didática: o ``yolov8n.pt``
é treinado no dataset COCO (80 classes genéricas: pessoas, animais,
veículos, objetos do dia a dia) e não tem labels específicos de
pragas. Mapeamos animais comuns (pássaro, vaca, ovelha…) para um
alerta de "possível praga/animal na lavoura" como demonstração da
integração com o dashboard; em produção, treina-se um modelo
específico no domínio agrícola.

Autores: Giovani Saavedra e Marcio Elifas
RM: RM566797 e RM567871
GRUPO 37
1TIAOS - FIAP

FIAP - Fase 7 - 2026
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

import cv2
import numpy as np


# ==========================================================
#         MAPEAMENTO AGRÍCOLA SOBRE CLASSES COCO
# ==========================================================

# Classes COCO consideradas "animais" — em campo, qualquer animal
# pode representar ameaça/perda à lavoura (pássaros bicando grãos,
# vacas/ovelhas pisoteando o talhão etc.).
CLASSES_ANIMAIS_COCO = {
    "bird",
    "cat",
    "dog",
    "horse",
    "sheep",
    "cow",
    "elephant",
    "bear",
    "zebra",
    "giraffe",
}

# Extensões suportadas para varrer assets/images/.
EXTENSOES_IMAGEM = {".jpg", ".jpeg", ".png"}


# ==========================================================
#         CAMADA DE DIAGNÓSTICO
# ==========================================================

def diagnosticar(deteccoes: List[Dict]) -> Dict:
    """Resume as detecções num diagnóstico agrícola.

    Args:
        deteccoes: lista de dicts ``{"classe", "confianca", "bbox"}``.

    Returns:
        Dicionário ``{"status", "mensagem", "severidade"}`` em que
        ``severidade`` é uma de ``"ok"``, ``"info"`` ou ``"alta"``.
    """
    if not deteccoes:
        return {
            "status": "saudavel",
            "mensagem": "🌱 Lavoura aparentemente saudável — sem anomalias detectadas.",
            "severidade": "ok",
        }

    classes = [d["classe"] for d in deteccoes]
    animais = [c for c in classes if c in CLASSES_ANIMAIS_COCO]
    pessoas = [c for c in classes if c == "person"]

    if animais:
        especies = ", ".join(sorted(set(animais)))
        return {
            "status": "praga",
            "mensagem": (
                f"⚠️ Possível praga/animal na lavoura "
                f"({len(animais)} ocorrência(s): {especies})."
            ),
            "severidade": "alta",
        }

    if pessoas:
        return {
            "status": "pessoa",
            "mensagem": (
                f"👤 Pessoa detectada no talhão "
                f"({len(pessoas)} ocorrência(s))."
            ),
            "severidade": "info",
        }

    # Outras detecções (objetos genéricos) — apenas informativo.
    outras = sorted(set(classes))
    return {
        "status": "objetos",
        "mensagem": "🔎 Objetos genéricos detectados: " + ", ".join(outras) + ".",
        "severidade": "info",
    }


# ==========================================================
#         ANALISADOR (lazy-load do YOLO)
# ==========================================================

class AnalisadorVisual:
    """Frente para o YOLOv8 com cache de modelo em **atributo de classe**.

    Como ``_modelo`` é de classe (não de instância), o peso é
    carregado uma única vez por processo Python — várias instâncias
    do analisador compartilham o mesmo modelo em memória.
    """

    _modelo = None  # cache compartilhado entre instâncias
    _modelo_nome: str = "yolov8n.pt"

    def __init__(self, modelo: str = "yolov8n.pt", confianca_minima: float = 0.25):
        """Cria o analisador (sem carregar o modelo ainda).

        Args:
            modelo: Nome ou caminho do peso YOLOv8 a usar (default
                ``yolov8n.pt`` — baixa automaticamente na 1ª chamada).
            confianca_minima: Limiar de confiança para considerar
                uma detecção válida.
        """
        self.modelo_nome = modelo
        self.confianca_minima = float(confianca_minima)

    # ------------------------------------------------------
    def _get_modelo(self):
        """Retorna o modelo YOLO, carregando-o se ainda não estiver."""
        cls = type(self)
        if cls._modelo is None or cls._modelo_nome != self.modelo_nome:
            # Import local — evita atrasar o boot do Streamlit caso
            # o usuário só esteja navegando entre outras páginas.
            from ultralytics import YOLO

            cls._modelo = YOLO(self.modelo_nome)
            cls._modelo_nome = self.modelo_nome
        return cls._modelo

    # ------------------------------------------------------
    @staticmethod
    def _bgr_to_rgb(imagem_bgr: np.ndarray) -> np.ndarray:
        """Converte OpenCV BGR -> RGB (mais natural para Streamlit/Plotly)."""
        return cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2RGB)

    # ------------------------------------------------------
    def analisar_imagem(self, caminho: str) -> Dict:
        """Roda o YOLO numa única imagem.

        Args:
            caminho: Caminho do arquivo (``.jpg``, ``.jpeg`` ou ``.png``).

        Returns:
            Dicionário com:

            * ``imagem``: caminho original.
            * ``deteccoes``: lista de dicts
              ``{"classe", "confianca", "bbox": [x1,y1,x2,y2]}``.
            * ``imagem_anotada``: ``np.ndarray`` RGB com as caixas
              desenhadas (pronto para ``st.image``).
            * ``diagnostico``: dict do :func:`diagnosticar`.
            * ``confianca_media``: média das confianças (ou ``None``).

        Raises:
            FileNotFoundError: se o caminho não existir.
        """
        p = Path(caminho)
        if not p.exists():
            raise FileNotFoundError(f"Imagem não encontrada: {caminho}")

        modelo = self._get_modelo()
        resultados = modelo(str(p), conf=self.confianca_minima, verbose=False)

        resultado = resultados[0]
        nomes = resultado.names  # {id: 'classe'}

        deteccoes: List[Dict] = []
        if resultado.boxes is not None and len(resultado.boxes) > 0:
            xyxy = resultado.boxes.xyxy.cpu().numpy()
            confs = resultado.boxes.conf.cpu().numpy()
            cls_ids = resultado.boxes.cls.cpu().numpy().astype(int)
            for (x1, y1, x2, y2), conf, cid in zip(xyxy, confs, cls_ids):
                deteccoes.append(
                    {
                        "classe": str(nomes.get(int(cid), str(cid))),
                        "confianca": round(float(conf), 4),
                        "bbox": [
                            round(float(x1), 2),
                            round(float(y1), 2),
                            round(float(x2), 2),
                            round(float(y2), 2),
                        ],
                    }
                )

        # result.plot() devolve BGR — converter para RGB.
        anotada_bgr = resultado.plot()
        anotada_rgb = self._bgr_to_rgb(anotada_bgr)

        diagnostico = diagnosticar(deteccoes)
        confianca_media: Optional[float] = (
            round(float(np.mean([d["confianca"] for d in deteccoes])), 4)
            if deteccoes
            else None
        )

        return {
            "imagem": str(p),
            "deteccoes": deteccoes,
            "imagem_anotada": anotada_rgb,
            "diagnostico": diagnostico,
            "confianca_media": confianca_media,
        }

    # ------------------------------------------------------
    def analisar_pasta(self, caminho: str = "assets/images") -> List[Dict]:
        """Processa todas as imagens válidas de uma pasta.

        Args:
            caminho: Pasta a ser varrida.

        Returns:
            Lista de resultados (mesmo formato de :meth:`analisar_imagem`).
        """
        pasta = Path(caminho)
        if not pasta.exists():
            return []

        arquivos = sorted(
            [p for p in pasta.iterdir() if p.suffix.lower() in EXTENSOES_IMAGEM]
        )
        resultados: List[Dict] = []
        for arq in arquivos:
            try:
                resultados.append(self.analisar_imagem(str(arq)))
            except Exception as exc:  # pragma: no cover - defensivo
                resultados.append(
                    {
                        "imagem": str(arq),
                        "deteccoes": [],
                        "imagem_anotada": None,
                        "diagnostico": {
                            "status": "erro",
                            "mensagem": f"Falha ao analisar: {exc}",
                            "severidade": "alta",
                        },
                        "confianca_media": None,
                    }
                )
        return resultados


# ==========================================================
#         HELPER DE SERIALIZAÇÃO PARA O BANCO
# ==========================================================

def serializar_deteccoes(deteccoes: List[Dict]) -> str:
    """Serializa as detecções para gravação na coluna ``deteccoes_json``."""
    return json.dumps(deteccoes, ensure_ascii=False)


# ==========================================================
#         EXECUÇÃO DIRETA (auto-teste)
# ==========================================================

if __name__ == "__main__":
    analisador = AnalisadorVisual()
    resultados = analisador.analisar_pasta("assets/images")
    for r in resultados:
        print(
            f"{Path(r['imagem']).name}: "
            f"{len(r['deteccoes'])} detecção(ões); "
            f"diagnóstico = {r['diagnostico']['mensagem']}"
        )
