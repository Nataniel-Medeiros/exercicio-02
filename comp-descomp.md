# Sistema de Compressão e Descompressão de Dados

## Visão Geral

Este documento apresenta o sistema de compressão desenvolvido para otimizar o armazenamento de dados tabulares do projeto TCLab Analytics. O sistema implementa múltiplos algoritmos de compressão sem perda de dados (lossless) com foco em alta eficiência e facilidade de uso.

## Algoritmos Implementados

### 1. LZMA (Lempel–Ziv–Markov chain Algorithm)
- **Extensão**: `.xz`
- **Características**: Máxima taxa de compressão
- **Complexidade**: O(n) tempo, O(n) espaço
- **Velocidade**: Compressão lenta, descompressão rápida
- **Uso recomendado**: Dados que serão comprimidos ocasionalmente e armazenados por longos períodos

### 2. Zstandard (zstd)
- **Extensão**: `.zst`
- **Características**: Melhor trade-off velocidade × compressão
- **Complexidade**: O(n) tempo, O(1) espaço
- **Velocidade**: Compressão e descompressão rápidas
- **Uso recomendado**: Uso frequente, dados em tempo real
- **Nota**: Requer instalação da biblioteca `zstandard`

### 3. Gzip
- **Extensão**: `.gz`
- **Características**: Máxima velocidade, compatibilidade universal
- **Complexidade**: O(n) tempo, O(1) espaço
- **Velocidade**: Muito rápido para compressão e descompressão
- **Uso recomendado**: Quando velocidade é prioridade absoluta

## Estratégia de Compressão

O sistema utiliza uma abordagem de **compressão individual por arquivo**, mantendo a estrutura organizacional dos dados:

1. **Preservação de originais**: Os arquivos originais são mantidos por padrão
2. **Compressão individual**: Cada arquivo é comprimido separadamente
3. **Nomenclatura consistente**: Arquivos comprimidos recebem extensão apropriada (.xz, .zst, .gz)
4. **Descompressão isolada**: Arquivos são descomprimidos para pasta separada (`descomp/`)

## Como Usar

### Instalação de Dependências (Opcional)
Para usar o algoritmo Zstandard (recomendado):
```bash
pip install zstandard
```

### Uso Programático

```python
import src.compression as comp

# Listar algoritmos disponíveis
print(comp.available_algorithms())

# Comprimir arquivos CSV mantendo originais
resultado = comp.compress_files_in_folder(
    folder_path='output',
    algorithm='lzma',
    level=6,
    keep_originals=True,
    pattern='*.csv'
)

# Descomprimir para pasta separada
comp.decompress_files_in_folder(
    folder_path='output',
    output_folder='descomp',
    keep_compressed=True
)
```

### Uso via Linha de Comando

```bash
# Comprimir arquivos CSV com LZMA nível 6
python -m src.compression compress --folder output --alg lzma --level 6 --pattern "*.csv"

# Descomprimir para pasta 'descomp'
python -m src.compression decompress --folder output --output descomp

# Listar algoritmos disponíveis
python -m src.compression list
```

### Parâmetros de Nível de Compressão

- **LZMA**: 0-9 (padrão: 6)
  - 0-3: Rápido, compressão menor
  - 4-6: Balanceado (recomendado)
  - 7-9: Lento, máxima compressão

- **Zstandard**: 1-22 (padrão: 3)
  - 1-5: Muito rápido
  - 6-12: Balanceado
  - 13-22: Alta compressão

- **Gzip**: 1-9 (padrão: 6)
  - 1-3: Rápido
  - 4-6: Balanceado
  - 7-9: Máxima compressão

## Estrutura do Módulo

```
src/compression.py
├── compress_file()                    # Comprime arquivo individual
├── compress_files_in_folder()         # Comprime arquivos de uma pasta
├── decompress_file()                  # Descomprime arquivo individual
├── decompress_file_to_folder()        # Descomprime para pasta específica
├── decompress_files_in_folder()       # Descomprime arquivos de uma pasta
└── available_algorithms()             # Lista algoritmos disponíveis
```

## Estatísticas de Performance - Dados Reais

### Dataset Utilizado
- **Pasta**: `output/`
- **Arquivos**: 3 arquivos CSV de dados do TCLab
- **Tamanho total**: 51.336.618 bytes (~51 MB)

#### Arquivo 1: `tclab_data_7days.csv`
- Tamanho original: 20.495.582 bytes (~20 MB)
- Dados: 7 dias de coleta contínua

#### Arquivo 2: `tclab_data_float16_int8_10080min_noH.csv`
- Tamanho original: 15.362.989 bytes (~15 MB)
- Dados: 10.080 minutos sem aquecimento

#### Arquivo 3: `tclab_data_histerese_float16_int8_10080min.csv`
- Tamanho original: 15.478.047 bytes (~15 MB)
- Dados: 10.080 minutos com histerese

### Resultados da Compressão (LZMA Nível 6)

```
Algoritmo: LZMA (nível 6)
Arquivos processados: 3
Tamanho original total: 51.336.618 bytes
Tamanho comprimido total: 4.109.528 bytes
Taxa de compressão: 8.0% do original
Redução obtida: 92.0%
Tempo de compressão: 20.74 segundos
Comportamento: Arquivos originais mantidos
```

#### Detalhamento por Arquivo:
- **tclab_data_7days.csv**: 20.495.582 → 2.931.256 bytes (14.3% do original)
- **tclab_data_float16_int8_10080min_noH.csv**: 15.362.989 → 585.512 bytes (3.8% do original)
- **tclab_data_histerese_float16_int8_10080min.csv**: 15.478.047 → 592.760 bytes (3.8% do original)

### Resultados da Descompressão

```
Pasta origem: output/
Pasta destino: descomp/
Arquivos processados: 3
Tamanho comprimido total: 4.109.528 bytes
Tamanho descomprimido total: 51.336.618 bytes
Tempo de descompressão: 0.39 segundos
Comportamento: Arquivos comprimidos mantidos
Integridade: 100% - todos os arquivos restaurados com tamanho original
```

### Análise de Performance

#### Eficiência de Compressão
- **Taxa média**: 92% de redução de espaço
- **Melhor resultado**: 96.2% (arquivos com histerese)
- **Economia de espaço**: 47.227.090 bytes economizados

#### Eficiência Temporal
- **Velocidade de compressão**: ~2.5 MB/s
- **Velocidade de descompressão**: ~131 MB/s
- **Ratio tempo**: Descompressão 53x mais rápida que compressão

#### Benefícios Práticos
1. **Armazenamento**: Redução de 51MB para 4MB (economia de 92%)
2. **Backup**: Arquivos de backup 12.5x menores
3. **Transferência**: Downloads/uploads 12.5x mais rápidos
4. **Custos**: Redução proporcional em custos de armazenamento cloud

## Recomendações de Uso

### Para Apresentações e Demonstrações
- **Algoritmo**: LZMA nível 6
- **Motivo**: Máxima compressão visual (92% de redução impressiona)
- **Trade-off**: Aceitar tempo de compressão mais longo para demonstrar eficácia

### Para Uso em Produção
- **Algoritmo**: Zstandard nível 3-6
- **Motivo**: Melhor balance velocidade × compressão
- **Benefício**: Compressão/descompressão rápidas para uso cotidiano

### Para Arquivamento de Longo Prazo
- **Algoritmo**: LZMA nível 9
- **Motivo**: Máxima compressão possível
- **Justificativa**: Compressão única, múltiplas descompressões

## Conclusão

O sistema desenvolvido demonstra excelente eficiência para dados tabulares científicos, alcançando reduções superiores a 90% com algoritmos padrão da indústria. A implementação modular permite fácil integração e uso tanto programático quanto via linha de comando, atendendo diferentes necessidades de workflow científico.

A performance obtida (92% de redução) supera significativamente o requisito inicial de "reduzir pela metade", demonstrando a eficácia da solução para otimização de armazenamento de dados experimentais.