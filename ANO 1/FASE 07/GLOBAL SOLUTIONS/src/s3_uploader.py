"""
Uploader de artefatos para AWS S3.

Persiste em bucket dedicado todos os arquivos gerados por cada análise
SatVerify, organizados por `analysis_id` sob o prefixo `analyses/`.

Princípio de design: graceful degradation. Se o upload falhar (credenciais
inválidas, sem internet, rate limit), o pipeline NÃO quebra — a análise
continua disponível localmente em `outputs/<analysis_id>/`.

Hardware/rede: chamadas HTTP para AWS S3 (região configurada em AWS_REGION).
Latência típica: 1-3s por arquivo.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from src.config import (
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    AWS_S3_BUCKET,
    AWS_SECRET_ACCESS_KEY,
)


# Prefixo no bucket: s3://<bucket>/<S3_PREFIX>/<analysis_id>/
S3_PREFIX = "analyses"

# Extensões consideradas "artefato" e elegíveis para upload. Deixa de fora
# `.npy` (arrays brutos do Sentinel — grandes e raramente úteis para humanos).
_ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".md", ".json"}


def _get_s3_client():
    """Cria e retorna um client boto3 S3 com as credenciais do .env."""
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )


def _guess_content_type(suffix: str) -> Optional[str]:
    """Mapeamento simples de extensão para Content-Type HTTP."""
    mapping = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".md": "text/markdown; charset=utf-8",
        ".json": "application/json",
    }
    return mapping.get(suffix)


def upload_analysis_artifacts(
    analysis_dir: str,
    analysis_id: str,
) -> Dict:
    """
    Faz upload de todos os arquivos de uma análise para S3.

    Args:
        analysis_dir: caminho da pasta local com os artefatos
            (ex: `outputs/<uuid>`)
        analysis_id: UUID da análise (usado como subpasta no S3)

    Returns:
        dict com:
            - 'uploaded': bool (True se pelo menos 1 arquivo subiu)
            - 'bucket': str
            - 'prefix': str (ex: 'analyses/<uuid>/')
            - 'files_uploaded': list[str] (keys S3 dos que subiram)
            - 'files_failed': list[str] (caminhos locais dos que falharam)
            - 's3_uri': str (URI base, ex: s3://bucket/analyses/<uuid>/)
            - 'error': Optional[str] (mensagem de erro geral)
    """
    result: Dict = {
        "uploaded": False,
        "bucket": AWS_S3_BUCKET,
        "prefix": f"{S3_PREFIX}/{analysis_id}/",
        "files_uploaded": [],
        "files_failed": [],
        "s3_uri": f"s3://{AWS_S3_BUCKET}/{S3_PREFIX}/{analysis_id}/",
        "error": None,
    }

    analysis_path = Path(analysis_dir)
    if not analysis_path.exists() or not analysis_path.is_dir():
        result["error"] = f"Pasta de análise não encontrada: {analysis_dir}"
        return result

    try:
        s3 = _get_s3_client()
    except Exception as exc:  # noqa: BLE001
        result["error"] = f"Falha ao criar client S3: {exc}"
        return result

    # Itera sobre arquivos da pasta — só sobe os de extensão permitida.
    for file_path in analysis_path.iterdir():
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in _ALLOWED_EXTENSIONS:
            continue

        s3_key = f"{S3_PREFIX}/{analysis_id}/{file_path.name}"
        try:
            content_type = _guess_content_type(file_path.suffix.lower())
            extra_args = {"ContentType": content_type} if content_type else {}

            s3.upload_file(
                Filename=str(file_path),
                Bucket=AWS_S3_BUCKET,
                Key=s3_key,
                ExtraArgs=extra_args,
            )
            result["files_uploaded"].append(s3_key)
        except (ClientError, BotoCoreError, OSError) as exc:
            result["files_failed"].append(str(file_path))
            logging.warning("Falha ao subir %s: %s", file_path.name, exc)

    result["uploaded"] = len(result["files_uploaded"]) > 0
    if not result["uploaded"] and not result["error"]:
        result["error"] = "Nenhum arquivo foi enviado com sucesso."

    return result


def get_bucket_stats() -> Dict:
    """
    Retorna estatísticas agregadas do bucket S3 (todos os objetos sob o
    prefixo `analyses/`).

    Returns:
        dict com:
            - 'bucket': str
            - 'region': str
            - 'total_files': int
            - 'total_bytes': int
            - 'total_mb': float
            - 'free_tier_limit_gb': int (= 5)
            - 'free_tier_used_pct': float (0-100)
            - 'estimated_monthly_cost_usd': float
            - 'last_modified': Optional[str] (ISO datetime do mais recente)
            - 'error': Optional[str]
    """
    result: Dict = {
        "bucket": AWS_S3_BUCKET,
        "region": AWS_REGION,
        "total_files": 0,
        "total_bytes": 0,
        "total_mb": 0.0,
        "free_tier_limit_gb": 5,
        "free_tier_used_pct": 0.0,
        "estimated_monthly_cost_usd": 0.0,
        "last_modified": None,
        "error": None,
    }

    try:
        s3 = _get_s3_client()
        paginator = s3.get_paginator("list_objects_v2")
        pages = paginator.paginate(
            Bucket=AWS_S3_BUCKET, Prefix=f"{S3_PREFIX}/"
        )

        latest_modified = None
        for page in pages:
            for obj in page.get("Contents", []) or []:
                result["total_files"] += 1
                result["total_bytes"] += int(obj.get("Size", 0))
                last_mod = obj.get("LastModified")
                if last_mod and (
                    latest_modified is None or last_mod > latest_modified
                ):
                    latest_modified = last_mod

        result["total_mb"] = round(result["total_bytes"] / (1024 * 1024), 3)
        result["free_tier_used_pct"] = round(
            (result["total_bytes"] / (5 * 1024 * 1024 * 1024)) * 100, 4
        )
        # S3 standard us-east-1: ~US$ 0.023 por GB/mês, com 5 GB grátis no
        # Free Tier durante 12 meses. Estimativa simplificada.
        gb_used = result["total_bytes"] / (1024 * 1024 * 1024)
        gb_billable = max(0.0, gb_used - 5.0)
        result["estimated_monthly_cost_usd"] = round(gb_billable * 0.023, 4)

        if latest_modified:
            result["last_modified"] = latest_modified.isoformat()

    except (ClientError, BotoCoreError) as exc:
        result["error"] = f"Erro ao listar bucket: {exc}"
    except Exception as exc:  # noqa: BLE001
        result["error"] = f"Erro inesperado: {exc}"

    return result


def get_console_url(analysis_id: Optional[str] = None) -> str:
    """
    Monta a URL do console AWS S3 apontando para o bucket ou pasta da análise.

    Args:
        analysis_id: se fornecido, aponta para `analyses/<id>/`; senão, para
            a raiz do bucket.

    Returns:
        URL HTTPS do console AWS (abrir em nova aba).
    """
    base = (
        f"https://{AWS_REGION}.console.aws.amazon.com/s3/buckets/"
        f"{AWS_S3_BUCKET}"
    )
    if analysis_id:
        return (
            f"{base}?prefix={S3_PREFIX}/{analysis_id}/&region={AWS_REGION}"
        )
    return f"{base}?region={AWS_REGION}"


def generate_presigned_urls(
    s3_keys: List[str],
    expires_in_seconds: int = 3600,
) -> Dict[str, str]:
    """
    Gera URLs pré-assinadas para download direto dos arquivos via HTTPS.

    Útil para incluir links no relatório, dashboard ou compartilhar com
    terceiros sem expor credenciais.

    Args:
        s3_keys: lista de keys S3 (ex: ['analyses/<uuid>/metadata.json', ...])
        expires_in_seconds: duração da URL (default 1h)

    Returns:
        dict `{s3_key: presigned_url}`. Keys que falharem são omitidas.
    """
    urls: Dict[str, str] = {}
    try:
        s3 = _get_s3_client()
    except Exception as exc:  # noqa: BLE001
        logging.warning(
            "Não foi possível criar client S3 para presigned URLs: %s", exc
        )
        return urls

    for key in s3_keys:
        try:
            url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": AWS_S3_BUCKET, "Key": key},
                ExpiresIn=expires_in_seconds,
            )
            urls[key] = url
        except Exception as exc:  # noqa: BLE001
            logging.warning(
                "Falha ao gerar presigned URL para %s: %s", key, exc
            )
    return urls
