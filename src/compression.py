"""
Funções para compressão e descompressão de arquivos individuais dentro da pasta `output`.

Estratégia usada:
- Comprimir cada arquivo separadamente mantendo a estrutura de pastas.
- Usar algoritmos selecionáveis: zstd (se instalado), lzma (builtin, alto ratio mas mais lento) ou gzip (builtin, mais rápido mas ratio menor).
- Preservar nomes originais adicionando extensão apropriada (.zst/.xz/.gz).

API principal:
- compress_files_in_folder(folder_path='output', algorithm='zstd', level=3, keep_originals=False)
- decompress_files_in_folder(folder_path, algorithm=None)
- compress_file(file_path, algorithm='zstd', level=3, keep_original=False)
- decompress_file(compressed_file_path, keep_compressed=False)
- available_algorithms()

Observação: zstandard oferece ótimo trade-off entre velocidade e compressão; lzma (xz) pode comprimir mais, porém é mais lento.
"""
from __future__ import annotations

import os
import shutil
import time
import glob
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import zstandard as zstd  # type: ignore
    _HAS_ZSTD = True
except Exception:
    zstd = None  # type: ignore
    _HAS_ZSTD = False

import lzma
import gzip


def available_algorithms() -> List[str]:
    """Retorna algoritmos disponíveis no ambiente."""
    algs = ["lzma", "gzip"]
    if _HAS_ZSTD:
        algs.insert(0, "zstd")
    return algs


def _ext_for_algorithm(alg: str) -> str:
    return {
        "zstd": "zst",
        "lzma": "xz",
        "gzip": "gz",
    }.get(alg, "bin")


def compress_file(
    file_path: str,
    algorithm: str = "zstd",
    level: int = 3,
    keep_original: bool = True,
) -> Dict[str, object]:
    """
    Comprime um arquivo individual.
    
    - file_path: caminho do arquivo a ser comprimido
    - algorithm: 'zstd'|'lzma'|'gzip'
    - level: nível de compressão
    - keep_original: se True, mantém o arquivo original
    
    Retorna estatísticas da compressão.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    
    algorithm = algorithm.lower()
    if algorithm == "zstd" and not _HAS_ZSTD:
        raise RuntimeError("zstandard não está instalado. Use 'lzma' ou 'gzip'.")
    
    ext = _ext_for_algorithm(algorithm)
    compressed_path = f"{file_path}.{ext}"
    
    start = time.time()
    original_size = os.path.getsize(file_path)
    
    with open(file_path, "rb") as fin:
        if algorithm == "zstd":
            cctx = zstd.ZstdCompressor(level=level)
            with open(compressed_path, "wb") as fout:
                with cctx.stream_writer(fout) as compressor:
                    shutil.copyfileobj(fin, compressor)
        
        elif algorithm == "lzma":
            preset = max(0, min(9, level))
            with lzma.open(compressed_path, "wb", preset=preset) as fout:
                shutil.copyfileobj(fin, fout)
        
        elif algorithm == "gzip":
            comp_level = max(1, min(9, level))
            with gzip.open(compressed_path, "wb", compresslevel=comp_level) as fout:
                shutil.copyfileobj(fin, fout)
        
        else:
            raise ValueError(f"Algoritmo desconhecido: {algorithm}")
    
    compressed_size = os.path.getsize(compressed_path)
    elapsed = time.time() - start
    ratio = compressed_size / original_size if original_size > 0 else 0
    
    # remover original se solicitado
    if not keep_original:
        os.remove(file_path)
    
    return {
        "file_path": file_path,
        "compressed_path": compressed_path,
        "algorithm": algorithm,
        "level": level,
        "original_size": original_size,
        "compressed_size": compressed_size,
        "ratio": ratio,
        "time_seconds": elapsed,
        "kept_original": keep_original,
    }


def compress_files_in_folder(
    folder_path: str = "output",
    algorithm: str = "zstd",
    level: int = 3,
    keep_originals: bool = True,
    pattern: str = "*",
) -> Dict[str, object]:
    """
    Comprime todos os arquivos de uma pasta individualmente.
    
    - folder_path: pasta contendo os arquivos
    - algorithm: 'zstd'|'lzma'|'gzip'
    - level: nível de compressão
    - keep_originals: se True, mantém os arquivos originais
    - pattern: padrão de arquivos (ex: "*.csv", "*")
    
    Retorna estatísticas agregadas e lista de arquivos processados.
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Pasta não encontrada: {folder_path}")
    
    # encontrar arquivos
    search_pattern = os.path.join(folder_path, pattern)
    files = [f for f in glob.glob(search_pattern) if os.path.isfile(f)]
    
    if not files:
        return {
            "folder_path": folder_path,
            "algorithm": algorithm,
            "files_found": 0,
            "files_processed": [],
            "total_original_size": 0,
            "total_compressed_size": 0,
            "overall_ratio": 0,
            "total_time_seconds": 0,
        }
    
    start_total = time.time()
    processed = []
    total_original = 0
    total_compressed = 0
    
    for file_path in files:
        try:
            result = compress_file(file_path, algorithm, level, keep_originals)
            processed.append(result)
            total_original += result["original_size"]
            total_compressed += result["compressed_size"]
        except Exception as e:
            processed.append({
                "file_path": file_path,
                "error": str(e),
                "compressed_path": None,
            })
    
    elapsed_total = time.time() - start_total
    overall_ratio = total_compressed / total_original if total_original > 0 else 0
    
    return {
        "folder_path": folder_path,
        "algorithm": algorithm,
        "level": level,
        "files_found": len(files),
        "files_processed": processed,
        "total_original_size": total_original,
        "total_compressed_size": total_compressed,
        "overall_ratio": overall_ratio,
        "total_time_seconds": elapsed_total,
        "kept_originals": keep_originals,
    }


def decompress_file(
    compressed_file_path: str,
    keep_compressed: bool = False,
) -> Dict[str, object]:
    """
    Descomprime um arquivo individual.
    Detecta algoritmo pela extensão (.zst/.xz/.gz).
    
    - compressed_file_path: caminho do arquivo comprimido
    - keep_compressed: se True, mantém o arquivo comprimido
    
    Retorna estatísticas da descompressão.
    """
    if not os.path.exists(compressed_file_path):
        raise FileNotFoundError(f"Arquivo comprimido não encontrado: {compressed_file_path}")
    
    # detectar algoritmo pela extensão
    name = os.path.basename(compressed_file_path).lower()
    if name.endswith(".zst"):
        alg = "zstd"
        original_path = compressed_file_path[:-4]  # remove .zst
    elif name.endswith(".xz"):
        alg = "lzma"
        original_path = compressed_file_path[:-3]  # remove .xz
    elif name.endswith(".gz"):
        alg = "gzip"
        original_path = compressed_file_path[:-3]  # remove .gz
    else:
        raise ValueError(f"Extensão não reconhecida para descompressão: {compressed_file_path}")
    
    if alg == "zstd" and not _HAS_ZSTD:
        raise RuntimeError("zstandard não disponível para descompressão")
    
    start = time.time()
    compressed_size = os.path.getsize(compressed_file_path)
    
    with open(original_path, "wb") as fout:
        if alg == "zstd":
            dctx = zstd.ZstdDecompressor()
            with open(compressed_file_path, "rb") as fin:
                with dctx.stream_reader(fin) as reader:
                    shutil.copyfileobj(reader, fout)
        
        elif alg == "lzma":
            with lzma.open(compressed_file_path, "rb") as fin:
                shutil.copyfileobj(fin, fout)
        
        elif alg == "gzip":
            with gzip.open(compressed_file_path, "rb") as fin:
                shutil.copyfileobj(fin, fout)
    
    original_size = os.path.getsize(original_path)
    elapsed = time.time() - start
    
    # remover comprimido se solicitado
    if not keep_compressed:
        os.remove(compressed_file_path)
    
    return {
        "compressed_path": compressed_file_path,
        "original_path": original_path,
        "algorithm": alg,
        "compressed_size": compressed_size,
        "original_size": original_size,
        "time_seconds": elapsed,
        "kept_compressed": keep_compressed,
    }


def decompress_file_to_folder(
    compressed_file_path: str,
    output_folder: str,
    keep_compressed: bool = True,
) -> Dict[str, object]:
    """
    Descomprime um arquivo individual para uma pasta específica.
    """
    if not os.path.exists(compressed_file_path):
        raise FileNotFoundError(f"Arquivo comprimido não encontrado: {compressed_file_path}")
    
    # detectar algoritmo pela extensão
    name = os.path.basename(compressed_file_path).lower()
    if name.endswith(".zst"):
        alg = "zstd"
        original_name = os.path.basename(compressed_file_path)[:-4]  # remove .zst
    elif name.endswith(".xz"):
        alg = "lzma"
        original_name = os.path.basename(compressed_file_path)[:-3]  # remove .xz
    elif name.endswith(".gz"):
        alg = "gzip"
        original_name = os.path.basename(compressed_file_path)[:-3]  # remove .gz
    else:
        raise ValueError(f"Extensão não reconhecida para descompressão: {compressed_file_path}")
    
    if alg == "zstd" and not _HAS_ZSTD:
        raise RuntimeError("zstandard não disponível para descompressão")
    
    # criar pasta de destino se necessário
    os.makedirs(output_folder, exist_ok=True)
    original_path = os.path.join(output_folder, original_name)
    
    start = time.time()
    compressed_size = os.path.getsize(compressed_file_path)
    
    with open(original_path, "wb") as fout:
        if alg == "zstd":
            dctx = zstd.ZstdDecompressor()
            with open(compressed_file_path, "rb") as fin:
                with dctx.stream_reader(fin) as reader:
                    shutil.copyfileobj(reader, fout)
        
        elif alg == "lzma":
            with lzma.open(compressed_file_path, "rb") as fin:
                shutil.copyfileobj(fin, fout)
        
        elif alg == "gzip":
            with gzip.open(compressed_file_path, "rb") as fin:
                shutil.copyfileobj(fin, fout)
    
    original_size = os.path.getsize(original_path)
    elapsed = time.time() - start
    
    # remover comprimido se solicitado
    if not keep_compressed:
        os.remove(compressed_file_path)
    
    return {
        "compressed_path": compressed_file_path,
        "original_path": original_path,
        "algorithm": alg,
        "compressed_size": compressed_size,
        "original_size": original_size,
        "time_seconds": elapsed,
        "kept_compressed": keep_compressed,
    }


def decompress_files_in_folder(
    folder_path: str,
    algorithm: Optional[str] = None,
    keep_compressed: bool = True,
    output_folder: str = "descomp",
) -> Dict[str, object]:
    """
    Descomprime todos os arquivos comprimidos de uma pasta para uma pasta de destino.
    
    - folder_path: pasta contendo arquivos comprimidos
    - algorithm: se especificado, filtra apenas arquivos deste algoritmo
    - keep_compressed: se True, mantém os arquivos comprimidos
    - output_folder: pasta onde colocar os arquivos descomprimidos
    
    Retorna estatísticas agregadas.
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Pasta não encontrada: {folder_path}")
    
    # criar pasta de destino se não existir
    os.makedirs(output_folder, exist_ok=True)
    
    # encontrar arquivos comprimidos
    extensions = []
    if algorithm is None or algorithm.lower() == "zstd":
        extensions.append("*.zst")
    if algorithm is None or algorithm.lower() == "lzma":
        extensions.append("*.xz")
    if algorithm is None or algorithm.lower() == "gzip":
        extensions.append("*.gz")
    
    files = []
    for ext in extensions:
        pattern = os.path.join(folder_path, ext)
        files.extend(glob.glob(pattern))
    
    if not files:
        return {
            "folder_path": folder_path,
            "output_folder": output_folder,
            "algorithm_filter": algorithm,
            "files_found": 0,
            "files_processed": [],
            "total_compressed_size": 0,
            "total_original_size": 0,
            "total_time_seconds": 0,
        }
    
    start_total = time.time()
    processed = []
    total_compressed = 0
    total_original = 0
    
    for file_path in files:
        try:
            # modificar decompress_file para aceitar pasta de destino
            result = decompress_file_to_folder(file_path, output_folder, keep_compressed)
            processed.append(result)
            total_compressed += result["compressed_size"]
            total_original += result["original_size"]
        except Exception as e:
            processed.append({
                "compressed_path": file_path,
                "error": str(e),
                "original_path": None,
            })
    
    elapsed_total = time.time() - start_total
    
    return {
        "folder_path": folder_path,
        "output_folder": output_folder,
        "algorithm_filter": algorithm,
        "files_found": len(files),
        "files_processed": processed,
        "total_compressed_size": total_compressed,
        "total_original_size": total_original,
        "total_time_seconds": elapsed_total,
        "kept_compressed": keep_compressed,
    }


if __name__ == "__main__":
    # Suporte mínimo de linha de comando para testes rápidos.
    import argparse

    parser = argparse.ArgumentParser(description="Compress/Decompress arquivos individuais da pasta 'output'")
    sub = parser.add_subparsers(dest="cmd")

    p1 = sub.add_parser("compress")
    p1.add_argument("--folder", default="output", help="Pasta com arquivos para comprimir")
    p1.add_argument("--alg", default=("zstd" if _HAS_ZSTD else "lzma"), help="Algoritmo de compressão")
    p1.add_argument("--level", type=int, default=3, help="Nível de compressão")
    p1.add_argument("--no-keep", action="store_true", help="NÃO manter arquivos originais")
    p1.add_argument("--pattern", default="*", help="Padrão de arquivos (ex: *.csv)")

    p2 = sub.add_parser("decompress")
    p2.add_argument("--folder", default="output", help="Pasta com arquivos comprimidos")
    p2.add_argument("--alg", default=None, help="Filtrar por algoritmo específico")
    p2.add_argument("--output", default="descomp", help="Pasta de destino dos descomprimidos")
    p2.add_argument("--no-keep", action="store_true", help="NÃO manter arquivos comprimidos")

    p3 = sub.add_parser("list")

    args = parser.parse_args()
    if args.cmd == "list":
        print("Algoritmos disponíveis:", available_algorithms())
    elif args.cmd == "compress":
        info = compress_files_in_folder(
            folder_path=args.folder, 
            algorithm=args.alg, 
            level=args.level, 
            keep_originals=not args.no_keep,
            pattern=args.pattern
        )
        print("Resultado da compressão:")
        print(f"  Pasta: {info['folder_path']}")
        print(f"  Algoritmo: {info['algorithm']} (nível {info['level']})")
        print(f"  Arquivos encontrados: {info['files_found']}")
        print(f"  Tamanho original total: {info['total_original_size']:,} bytes")
        print(f"  Tamanho comprimido total: {info['total_compressed_size']:,} bytes")
        if info['total_original_size'] > 0:
            ratio = info['overall_ratio']
            print(f"  Taxa geral: {ratio*100:.1f}% (redução {100 - ratio*100:.1f}%)")
        print(f"  Tempo total: {info['total_time_seconds']:.2f}s")
        print(f"  Originais mantidos: {'Sim' if info['kept_originals'] else 'Não'}")
        
    elif args.cmd == "decompress":
        info = decompress_files_in_folder(
            folder_path=args.folder,
            algorithm=args.alg,
            keep_compressed=not args.no_keep,
            output_folder=args.output
        )
        print("Resultado da descompressão:")
        print(f"  Pasta origem: {info['folder_path']}")
        print(f"  Pasta destino: {info['output_folder']}")
        print(f"  Filtro algoritmo: {info['algorithm_filter'] or 'Todos'}")
        print(f"  Arquivos encontrados: {info['files_found']}")
        print(f"  Tamanho comprimido total: {info['total_compressed_size']:,} bytes")
        print(f"  Tamanho original total: {info['total_original_size']:,} bytes")
        print(f"  Tempo total: {info['total_time_seconds']:.2f}s")
        print(f"  Comprimidos mantidos: {'Sim' if info['kept_compressed'] else 'Não'}")
    else:
        parser.print_help()
