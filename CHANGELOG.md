# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-14

### 🎉 Primeira Release

#### ✨ Adicionado
- **Simulações TCLab**:
  - Controle ON/OFF puro sem histerese (`main-sh.py`)
  - Controle ON/OFF com histerese (`main-ch.py`)
  - Configuração flexível de precisão de dados (float16/32/64)
  - Tipos de aquecedor configuráveis (int8/bool)
  - Setpoints dinâmicos ao longo de 7 dias

- **Análises de Dados**:
  - Análise estatística completa via terminal (`analise2.py`)
  - Dashboard web interativo (`analise_web.py`)
  - Gráficos temporais das temperaturas
  - Análises estatísticas descritivas
  - Boxplots e distribuições
  - Matrizes de correlação

- **Interface Web Profissional**:
  - Design responsivo e moderno
  - Tema azul escuro, branco e cinza metalizado
  - Seleção interativa de arquivos
  - Gráficos interativos com Plotly
  - Tabelas de estatísticas formatadas
  - Cards informativos sobre os dados

- **Documentação Completa**:
  - README.md detalhado
  - Arquivo requirements.txt
  - Licença MIT
  - .gitignore para Python
  - pyproject.toml para configuração

#### 🔧 Técnico
- Suporte a Python 3.12+
- Integração com TCLab para simulações
- Pandas para manipulação de dados
- Matplotlib e Plotly para visualizações
- Dash para interface web
- Estrutura modular do código

#### 📊 Dados e Formatos
- **Setpoints**: CSV com colunas Time, T1_setpoint, T2_setpoint
- **Output**: CSV com colunas Time (s), T1, T2, Q1, Q2
- **Conversão automática** de timestamps
- **Tratamento robusto** de erros de carregamento

#### 🎯 Resultados Demonstrados
- Controle com histerese mais eficiente que sem histerese
- Redução de oscilações nas temperaturas
- Diminuição significativa do chattering
- Análises comparativas detalhadas

#### 🌐 Interface Web
- **URL**: http://127.0.0.1:8050
- **Porta configurável**: 8050 (padrão)
- **Modo debug**: Habilitado para desenvolvimento
- **CSS customizado**: Tema profissional
- **Responsividade**: Desktop e mobile

### 📈 Melhorias Futuras Planejadas
- [ ] Exportação de relatórios em PDF
- [ ] Mais tipos de controladores (PID, etc.)
- [ ] Análise de estabilidade do sistema
- [ ] Comparação automática entre simulações
- [ ] API REST para integração externa
- [ ] Suporte a múltiplos idiomas
- [ ] Modo escuro/claro alternável
- [ ] Salvamento de configurações personalizadas

---

## Como Interpretar as Versões

- **MAJOR** (X.0.0): Mudanças incompatíveis na API
- **MINOR** (0.X.0): Funcionalidades adicionadas de forma compatível
- **PATCH** (0.0.X): Correções de bugs compatíveis

## Tipos de Mudanças

- **✨ Adicionado**: Para novas funcionalidades
- **🔄 Modificado**: Para mudanças em funcionalidades existentes
- **🗑️ Removido**: Para funcionalidades removidas
- **🐛 Corrigido**: Para correções de bugs
- **🔒 Segurança**: Para correções de vulnerabilidades