# 🔬 TCLab Analytics Pro

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![Dash](https://img.shields.io/badge/Dash-2.0+-green.svg)](https://dash.plotly.com)
[![Plotly](https://img.shields.io/badge/Plotly-5.0+-orange.svg)](https://plotly.com/python)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Descrição

**TCLab Analytics Pro** é uma solução acadêmica para análise de dados de controle de temperatura do TCLab (Temperature Control Laboratory). O projeto implementa simulações de controle ON/OFF com e sem histerese, oferecendo análises estatísticas avançadas e visualizações interativas através de uma interface web moderna.

### 🎯 Objetivos do Projeto

- Simular sistemas de controle de temperatura industrial
- Comparar eficiência de controle ON/OFF puro vs. com histerese
- Analisar dados de processo através de dashboards interativos
- Gerar relatórios estatísticos detalhados para tomada de decisão

## ✨ Características Principais

### 🔧 Simulações Implementadas
- **Controle ON/OFF Puro**: Sem histerese (main-sh.py)
- **Controle ON/OFF com Histerese**: Com banda morta de 0.5°C (main-ch.py)
- **Configuração Flexível**: Precisão de dados (float16/32/64) e tipos de aquecedor (int8/bool)
- **Setpoints Dinâmicos**: Padrões de temperatura variáveis ao longo de 7 dias

### 📊 Análises e Visualizações
- **Gráficos Temporais**: Evolução das temperaturas e estados dos aquecedores
- **Estatísticas Descritivas**: Média, mediana, desvio padrão, variância
- **Distribuições**: Boxplots e histogramas
- **Correlações**: Matriz de correlação entre variáveis
- **Interface Web**: Dashboard interativo com design profissional

### 🗜️ Sistema de Compressão Avançado
- **Compressão Lossless**: Redução de até 92% no tamanho dos arquivos
- **Múltiplos Algoritmos**: LZMA, Zstandard (zstd) e Gzip
- **Preservação de Dados**: Mantém arquivos originais por padrão
- **Descompressão Isolada**: Restaura arquivos em pasta separada (`descomp/`)
- **Interface Dupla**: Uso programático e linha de comando

### 🎨 Interface Moderna
- **Design Responsivo**: Compatível com desktop e mobile
- **Tema Profissional**: Cores azul escuro, branco e cinza metalizado
- **Navegação Intuitiva**: Seleção de arquivos via dropdown
- **Gráficos Interativos**: Zoom, pan e exportação de imagens

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.12 ou superior
- Ambiente virtual (recomendado)

### 1. Na pasta do projeto
```bash
cd exercicio-02
```

### 2. Criar e Ativar Ambiente Virtual
```bash
# Windows
python -m venv exec2-venv
exec2-venv\Scripts\activate

# Linux/Mac
python -m venv exec2-venv
source exec2-venv/bin/activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Instalar Dependências Opcionais (Recomendado para Compressão)
```bash
pip install zstandard  # Para algoritmo zstd (melhor performance)
```

### 5. Instalar Dependências Manualmente (se necessário)
```bash
pip install tclab pandas numpy matplotlib plotly dash zstandard
```

## 📁 Estrutura do Projeto

```
exercicio-02/
├── 📁 src/                          # Código fonte
│   ├── 🐍 main-sh.py               # Simulação sem histerese
│   ├── 🐍 main-ch.py               # Simulação com histerese
│   ├── 🐍 analise.py               # Análise com matplotlib
│   ├── 🐍 analise2.py              # Análise completa via terminal
│   ├── 🐍 analise_web.py           # Dashboard web interativo
│   ├── � compression.py           # Sistema de compressão avançado
│   └── 🐍 __init__.py              # Inicializador do pacote
├── �📁 setpoints/                    # Arquivos de setpoints
│   ├── 📄 setpoints_7days_6h.csv
│   └── 📄 setpoints_7days_histerese_6h.csv
├── 📁 output/                       # Dados de simulação
│   ├── 📄 tclab_data_7days.csv     # Dados completos de 7 dias
│   ├── 📄 tclab_data_*.csv.xz      # Arquivos comprimidos (LZMA)
│   └── 📄 tclab_data_*.csv         # Dados originais (mantidos)
├── 📁 descomp/                      # Arquivos descomprimidos
│   └── 📄 tclab_data_*.csv         # Cópias restauradas
├── 📁 exec2-venv/                   # Ambiente virtual
├── 📄 comp-descomp.md              # Documentação do sistema de compressão
├── 📄 README.md                     # Este arquivo
└── 📄 requirements.txt              # Dependências
```

## 🔧 Como Usar

### 1. Executar Simulações

#### Simulação sem Histerese:
```bash
python src/main-sh.py
```

#### Simulação com Histerese:
```bash
python src/main-ch.py
```

### 2. Análise de Dados

#### Análise via Terminal:
```bash
python src/analise2.py
```

#### Dashboard Web Interativo:
```bash
python src/analise_web.py
```
Acesse: http://127.0.0.1:8050

### 3. Sistema de Compressão

#### Comprimir Arquivos da Pasta Output:
```bash
# Comprimir todos os CSV mantendo originais
python -m src.compression compress --folder output --alg lzma --level 6 --pattern "*.csv"

# Comprimir com Zstandard (mais rápido)
python -m src.compression compress --folder output --alg zstd --level 3 --pattern "*.csv"
```

#### Descomprimir Arquivos:
```bash
# Descomprimir para pasta 'descomp'
python -m src.compression decompress --folder output --output descomp

# Listar algoritmos disponíveis
python -m src.compression list
```

#### Uso Programático:
```python
import src.compression as comp

# Comprimir mantendo originais
result = comp.compress_files_in_folder(
    folder_path='output',
    algorithm='lzma',
    level=6,
    pattern='*.csv'
)

# Descomprimir para pasta separada
comp.decompress_files_in_folder(
    folder_path='output',
    output_folder='descomp'
)
```

### 3. Configurações de Simulação

As simulações podem ser customizadas editando os parâmetros:

```python
# Parâmetros principais
duration_minutes = 60 * 24 * 7  # 7 dias
speedup_factor = 100000         # Aceleração da simulação
temp_precision = 'float16'      # Precisão dos dados
heater_type = 'int8'           # Tipo do aquecedor
```

## 📊 Tipos de Análise Disponíveis

### 🔍 Análise Temporal
- Evolução das temperaturas T1 e T2 ao longo do tempo
- Estados dos aquecedores Q1 e Q2
- Comparação com setpoints definidos
- Identificação de overshooting e settling time

### 📈 Análise Estatística
- **Medidas de Tendência Central**: Média, mediana
- **Medidas de Dispersão**: Desvio padrão, variância, amplitude
- **Distribuições**: Quartis, outliers, normalidade
- **Correlações**: Relacionamentos entre variáveis

### 🎯 Análise de Performance
- **Eficiência Energética**: Tempo de ativação dos aquecedores
- **Precisão de Controle**: Desvio médio dos setpoints
- **Estabilidade**: Oscilações e chattering
- **Tempo de Resposta**: Dinâmica do sistema

## 📊 Resultados de Exemplo

### Controle sem Histerese vs. com Histerese

| Métrica | Sem Histerese | Com Histerese | Melhoria |
|---------|---------------|---------------|----------|
| Temperatura T1 média | 52.26°C | 50.74°C | ✅ Mais próximo do setpoint |
| Desvio padrão T1 | 18.12°C | 17.99°C | ✅ Menor oscilação |
| Ativação Q1 | 48.3% | 54.2% | ⚠️ Maior consumo |
| Chattering | Alto | Baixo | ✅ Menos chaveamento |

### Conclusões
- ✅ **Controle com histerese é mais eficiente** em termos de precisão
- ✅ **Menor oscilação** nas temperaturas
- ⚠️ **Ligeiro aumento** no consumo energético
- ✅ **Redução significativa** do chattering

## �️ Sistema de Compressão - Estatísticas

### Performance com Dados Reais (51MB de dados CSV)

| Algoritmo | Taxa Compressão | Redução | Tempo Compressão | Tempo Descompressão |
|-----------|-----------------|---------|------------------|---------------------|
| **LZMA** | 8.0% | **92.0%** | 20.74s | 0.39s |
| **Zstd** | ~12-15% | **85-88%** | ~3-5s | ~0.2s |
| **Gzip** | ~20-25% | **75-80%** | ~1-2s | ~0.15s |

### Benefícios Obtidos
- 🎯 **Economia de Espaço**: 51MB → 4MB (redução de 92%)
- ⚡ **Backup Rápido**: Arquivos 12.5x menores
- 💾 **Armazenamento**: Significativa redução de custos
- 🔒 **Integridade**: 100% dos dados preservados sem perda

📖 **Documentação Completa**: Ver `comp-descomp.md` para detalhes técnicos

## �🛠️ Tecnologias Utilizadas

- **🐍 Python 3.12**: Linguagem principal
- **📊 TCLab**: Simulador de controle de temperatura
- **📈 Pandas**: Manipulação e análise de dados
- **📉 NumPy**: Computação numérica
- **📊 Matplotlib**: Visualizações estáticas
- **📈 Plotly**: Gráficos interativos
- **🌐 Dash**: Framework web para dashboards
- **🗜️ LZMA/Zstd/Gzip**: Algoritmos de compressão lossless
- **🎨 CSS3**: Estilização da interface

## 📋 Formato dos Dados

### Setpoints (setpoints/*.csv)
```csv
Time,T1_setpoint,T2_setpoint
0,33,27
21600,50,46
43200,66,60
```

### Output TCLab (output/*.csv)
```csv
Time (s),T1,T2,Q1,Q2
0,20.95,20.95,100,100
1,20.62,20.95,100,100
2,20.95,20.95,100,100
```

## 👨‍💻 Autores

**Nataniel Medeiros**
<br>
**Dawesley Mota**
<br>
**Josilene Ferreira**
<br>
**Rivelino Nunes**

----
<div align="center">
  <strong>🚀 TCLab Analytics Pro - Análise de Controle de Temperatura 🚀</strong>
</div>