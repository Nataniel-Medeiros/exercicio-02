import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback_context
from pathlib import Path

# Configuração de cores do tema
COLORS = {
    'background': '#1e293b',     # Azul escuro
    'surface': '#334155',        # Azul escuro médio
    'card': '#475569',           # Azul acinzentado
    'primary': '#3b82f6',        # Azul primário
    'secondary': '#64748b',      # Cinza azulado
    'accent': '#06b6d4',         # Cyan
    'text_primary': '#f8fafc',   # Branco
    'text_secondary': '#cbd5e1', # Cinza claro
    'success': '#10b981',        # Verde
    'warning': '#f59e0b',        # Amarelo
    'error': '#ef4444',          # Vermelho
    'metallic': '#8b949e'        # Cinza metalizado
}

def load_csv_files():
    """Carrega todos os arquivos CSV das pastas setpoints e output"""
    files_data = {}
    
    # Carregar setpoints
    setpoints_path = Path("setpoints")
    if setpoints_path.exists():
        for file in setpoints_path.glob("*.csv"):
            try:
                df = pd.read_csv(file)
                df = create_timestamp(df)
                files_data[f"setpoints/{file.name}"] = {
                    'data': df,
                    'type': 'setpoints',
                    'filename': file.name
                }
            except Exception as e:
                print(f"Erro ao carregar {file}: {e}")
    
    # Carregar output
    output_path = Path("output")
    if output_path.exists():
        for file in output_path.glob("*.csv"):
            try:
                df = pd.read_csv(file)
                df = create_timestamp(df)
                files_data[f"output/{file.name}"] = {
                    'data': df,
                    'type': 'output',
                    'filename': file.name
                }
            except Exception as e:
                print(f"Erro ao carregar {file}: {e}")
    
    return files_data

def create_timestamp(df):
    """Cria coluna timestamp e hours para os dados"""
    if 'Time (s)' in df.columns:
        df['timestamp'] = pd.to_datetime(df['Time (s)'], unit='s')
        df['hours'] = df['Time (s)'] / 3600
    elif 'Time' in df.columns:
        df['timestamp'] = pd.to_datetime(df['Time'], unit='s')
        df['hours'] = df['Time'] / 3600
    else:
        df['timestamp'] = pd.date_range(start='2023-01-01', periods=len(df), freq='s')
        df['hours'] = range(len(df))
    return df

def get_numeric_columns(df):
    """Retorna colunas numéricas excluindo timestamp e time"""
    exclude_cols = ['timestamp', 'hours', 'Time', 'Time (s)']
    return [col for col in df.columns 
            if col not in exclude_cols and pd.api.types.is_numeric_dtype(df[col])]

def create_data_plot(df, filename, file_type):
    """Cria gráfico dos dados ao longo do tempo"""
    numeric_cols = get_numeric_columns(df)
    
    if not numeric_cols:
        return go.Figure().add_annotation(
            text="Nenhuma coluna numérica encontrada",
            x=0.5, y=0.5, xref="paper", yref="paper",
            showarrow=False, font=dict(size=16, color=COLORS['text_secondary'])
        )
    
    # Criar subplots
    n_cols = len(numeric_cols)
    fig = make_subplots(
        rows=n_cols, cols=1,
        subplot_titles=numeric_cols,
        vertical_spacing=0.08,
        shared_xaxes=True
    )
    
    colors = px.colors.qualitative.Set1
    
    for i, col in enumerate(numeric_cols):
        color = colors[i % len(colors)]
        
        # Adicionar linha dos dados
        fig.add_trace(
            go.Scatter(
                x=df['hours'],
                y=df[col],
                mode='lines',
                name=col,
                line=dict(color=color, width=2),
                showlegend=False
            ),
            row=i+1, col=1
        )
        
        # Adicionar linha da média
        mean_val = df[col].mean()
        fig.add_hline(
            y=mean_val,
            line_dash="dash",
            line_color=COLORS['accent'],
            annotation_text=f"Média: {mean_val:.2f}",
            annotation_position="top right",
            row=i+1, col=1
        )
    
    # Atualizar layout
    fig.update_layout(
        title=dict(
            text=f"📈 Dados Temporais - {filename}",
            font=dict(size=20, color=COLORS['text_primary']),
            x=0.5
        ),
        height=150 * n_cols + 100,
        paper_bgcolor=COLORS['background'],
        plot_bgcolor=COLORS['surface'],
        font=dict(color=COLORS['text_primary']),
        margin=dict(t=80, b=60, l=60, r=60)
    )
    
    fig.update_xaxes(
        title_text="Tempo (horas)",
        gridcolor=COLORS['secondary'],
        row=n_cols, col=1
    )
    fig.update_yaxes(gridcolor=COLORS['secondary'])
    
    return fig

def create_statistics_plot(df, filename):
    """Cria gráficos estatísticos"""
    numeric_cols = get_numeric_columns(df)
    
    if not numeric_cols:
        return go.Figure()
    
    # Calcular estatísticas
    stats = []
    for col in numeric_cols:
        stats.append({
            'Variável': col,
            'Média': df[col].mean(),
            'Mediana': df[col].median(),
            'Desvio Padrão': df[col].std(),
            'Mínimo': df[col].min(),
            'Máximo': df[col].max()
        })
    
    stats_df = pd.DataFrame(stats)
    
    # Criar subplots para estatísticas
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            "📊 Média vs Mediana",
            "📈 Desvio Padrão",
            "📦 Distribuição (Boxplot)",
            "🔗 Matriz de Correlação" if len(numeric_cols) > 1 else "📊 Histograma"
        ],
        specs=[
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "box"}, {"type": "heatmap" if len(numeric_cols) > 1 else "histogram"}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # 1. Média vs Mediana
    fig.add_trace(
        go.Bar(
            x=stats_df['Variável'],
            y=stats_df['Média'],
            name='Média',
            marker_color=COLORS['primary'],
            text=[f'{v:.2f}' for v in stats_df['Média']],
            textposition='outside'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=stats_df['Variável'],
            y=stats_df['Mediana'],
            name='Mediana',
            marker_color=COLORS['accent'],
            text=[f'{v:.2f}' for v in stats_df['Mediana']],
            textposition='outside'
        ),
        row=1, col=1
    )
    
    # 2. Desvio Padrão
    fig.add_trace(
        go.Bar(
            x=stats_df['Variável'],
            y=stats_df['Desvio Padrão'],
            name='Desvio Padrão',
            marker_color=COLORS['warning'],
            text=[f'{v:.2f}' for v in stats_df['Desvio Padrão']],
            textposition='outside',
            showlegend=False
        ),
        row=1, col=2
    )
    
    # 3. Boxplot
    for i, col in enumerate(numeric_cols):
        fig.add_trace(
            go.Box(
                y=df[col],
                name=col,
                marker_color=px.colors.qualitative.Set1[i % len(px.colors.qualitative.Set1)],
                showlegend=False
            ),
            row=2, col=1
        )
    
    # 4. Correlação ou Histograma
    if len(numeric_cols) > 1:
        # Matriz de correlação
        corr_matrix = df[numeric_cols].corr()
        fig.add_trace(
            go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=corr_matrix.round(2).values,
                texttemplate="%{text}",
                textfont={"size": 12},
                showscale=True,
                colorbar=dict(title="Correlação")
            ),
            row=2, col=2
        )
    else:
        # Histograma
        fig.add_trace(
            go.Histogram(
                x=df[numeric_cols[0]],
                name=numeric_cols[0],
                marker_color=COLORS['success'],
                opacity=0.7,
                showlegend=False
            ),
            row=2, col=2
        )
    
    # Atualizar layout
    fig.update_layout(
        title=dict(
            text=f"📊 Análise Estatística - {filename}",
            font=dict(size=20, color=COLORS['text_primary']),
            x=0.5
        ),
        height=800,
        paper_bgcolor=COLORS['background'],
        plot_bgcolor=COLORS['surface'],
        font=dict(color=COLORS['text_primary']),
        showlegend=True,
        legend=dict(
            bgcolor=COLORS['surface'],
            bordercolor=COLORS['secondary'],
            borderwidth=1
        ),
        margin=dict(t=80, b=60, l=60, r=60)
    )
    
    # Atualizar eixos
    fig.update_xaxes(gridcolor=COLORS['secondary'])
    fig.update_yaxes(gridcolor=COLORS['secondary'])
    
    return fig

def create_statistics_table(df):
    """Cria tabela de estatísticas descritivas"""
    numeric_cols = get_numeric_columns(df)
    
    if not numeric_cols:
        return html.Div("Nenhuma coluna numérica encontrada")
    
    stats_data = []
    for col in numeric_cols:
        stats_data.append([
            col,
            f"{df[col].mean():.3f}",
            f"{df[col].median():.3f}",
            f"{df[col].std():.3f}",
            f"{df[col].min():.3f}",
            f"{df[col].max():.3f}",
            f"{df[col].var():.3f}"
        ])
    
    return html.Table([
        html.Thead([
            html.Tr([
                html.Th("Variável", style={'background-color': COLORS['primary']}),
                html.Th("Média", style={'background-color': COLORS['primary']}),
                html.Th("Mediana", style={'background-color': COLORS['primary']}),
                html.Th("Desvio Padrão", style={'background-color': COLORS['primary']}),
                html.Th("Mínimo", style={'background-color': COLORS['primary']}),
                html.Th("Máximo", style={'background-color': COLORS['primary']}),
                html.Th("Variância", style={'background-color': COLORS['primary']})
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td(cell, style={
                    'background-color': COLORS['surface'] if i % 2 == 0 else COLORS['card'],
                    'color': COLORS['text_primary'],
                    'padding': '10px',
                    'border': f'1px solid {COLORS["secondary"]}'
                }) for cell in row
            ]) for i, row in enumerate(stats_data)
        ])
    ], style={
        'width': '100%',
        'border-collapse': 'collapse',
        'margin-top': '20px',
        'box-shadow': f'0 4px 6px rgba(0, 0, 0, 0.1)'
    })

# Carregar dados
files_data = load_csv_files()

# Inicializar app Dash
app = dash.Dash(__name__)
app.title = "TCLab Analytics Pro"

# Layout da aplicação
app.layout = html.Div([
    # Header
    html.Div([
        html.H1([
            html.I(className="fas fa-chart-line", style={'margin-right': '15px'}),
            "TCLab Analytics Pro"
        ], style={
            'text-align': 'center',
            'color': COLORS['text_primary'],
            'margin': '0',
            'font-weight': '300',
            'font-size': '2.5rem'
        }),
        html.P("Análise Profissional de Dados de Controle de Temperatura", style={
            'text-align': 'center',
            'color': COLORS['text_secondary'],
            'margin': '10px 0 0 0',
            'font-size': '1.1rem'
        })
    ], style={
        'background': f'linear-gradient(135deg, {COLORS["background"]} 0%, {COLORS["surface"]} 100%)',
        'padding': '30px',
        'margin-bottom': '30px',
        'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
    }),
    
    # Controles
    html.Div([
        html.Div([
            html.Label("📁 Selecione o Arquivo:", style={
                'color': COLORS['text_primary'],
                'font-weight': 'bold',
                'margin-bottom': '10px',
                'display': 'block'
            }),
            dcc.Dropdown(
                id='file-selector',
                options=[
                    {'label': f"📊 {data['filename']} ({data['type'].upper()})", 'value': key}
                    for key, data in files_data.items()
                ],
                value=list(files_data.keys())[0] if files_data else None,
                style={
                    'background-color': COLORS['surface'],
                    'color': COLORS['text_primary'],
                    'border': f'1px solid {COLORS["secondary"]}'
                },
                placeholder="Selecione um arquivo para análise..."
            )
        ], style={
            'background-color': COLORS['card'],
            'padding': '20px',
            'border-radius': '10px',
            'box-shadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
            'margin-bottom': '20px'
        })
    ], style={'max-width': '1200px', 'margin': '0 auto', 'padding': '0 20px'}),
    
    # Conteúdo principal
    html.Div(id='main-content', style={
        'max-width': '1200px',
        'margin': '0 auto',
        'padding': '0 20px'
    }),
    
    # Footer
    html.Div([
        html.P([
            "🔬 TCLab Analytics Pro | ",
            html.A("Desenvolvido com Dash & Plotly", 
                  href="https://plotly.com/dash/", 
                  style={'color': COLORS['accent'], 'text-decoration': 'none'})
        ], style={
            'text-align': 'center',
            'color': COLORS['text_secondary'],
            'margin': '0'
        })
    ], style={
        'background-color': COLORS['surface'],
        'padding': '20px',
        'margin-top': '40px'
    })
], style={
    'background-color': COLORS['background'],
    'min-height': '100vh',
    'font-family': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
})

# Callbacks
@app.callback(
    Output('main-content', 'children'),
    Input('file-selector', 'value')
)
def update_content(selected_file):
    if not selected_file or selected_file not in files_data:
        return html.Div([
            html.Div([
                html.H3("⚠️ Nenhum arquivo selecionado", style={'color': COLORS['warning']}),
                html.P("Selecione um arquivo no menu acima para visualizar os dados.", 
                      style={'color': COLORS['text_secondary']})
            ], style={'text-align': 'center', 'padding': '50px'})
        ])
    
    data_info = files_data[selected_file]
    df = data_info['data']
    filename = data_info['filename']
    file_type = data_info['type']
    
    # Informações do arquivo
    info_card = html.Div([
        html.H3(f"📈 {filename}", style={'color': COLORS['text_primary'], 'margin-bottom': '15px'}),
        html.Div([
            html.Span(f"📊 Linhas: {len(df):,}", style={'margin-right': '20px'}),
            html.Span(f"📋 Colunas: {len(df.columns)}", style={'margin-right': '20px'}),
            html.Span(f"🏷️ Tipo: {file_type.upper()}", style={'margin-right': '20px'}),
            html.Span(f"💾 Tamanho: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")
        ], style={'color': COLORS['text_secondary']})
    ], style={
        'background-color': COLORS['card'],
        'padding': '20px',
        'border-radius': '10px',
        'margin-bottom': '30px',
        'box-shadow': '0 2px 4px rgba(0, 0, 0, 0.1)'
    })
    
    # Gráfico dos dados
    data_plot = dcc.Graph(
        figure=create_data_plot(df, filename, file_type),
        style={'margin-bottom': '30px'}
    )
    
    # Gráfico de estatísticas
    stats_plot = dcc.Graph(
        figure=create_statistics_plot(df, filename),
        style={'margin-bottom': '30px'}
    )
    
    # Tabela de estatísticas
    stats_table_card = html.Div([
        html.H3("📊 Estatísticas Descritivas", style={
            'color': COLORS['text_primary'],
            'margin-bottom': '20px'
        }),
        create_statistics_table(df)
    ], style={
        'background-color': COLORS['card'],
        'padding': '20px',
        'border-radius': '10px',
        'box-shadow': '0 2px 4px rgba(0, 0, 0, 0.1)'
    })
    
    return html.Div([
        info_card,
        data_plot,
        stats_plot,
        stats_table_card
    ])

# CSS personalizado
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body {
                margin: 0;
                padding: 0;
                font-family: 'Inter', sans-serif;
            }
            .Select-control {
                background-color: ''' + COLORS['surface'] + ''' !important;
                border-color: ''' + COLORS['secondary'] + ''' !important;
                color: ''' + COLORS['text_primary'] + ''' !important;
            }
            .Select-menu-outer {
                background-color: ''' + COLORS['surface'] + ''' !important;
                border-color: ''' + COLORS['secondary'] + ''' !important;
            }
            .Select-option {
                background-color: ''' + COLORS['surface'] + ''' !important;
                color: ''' + COLORS['text_primary'] + ''' !important;
            }
            .Select-option:hover {
                background-color: ''' + COLORS['card'] + ''' !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    print("🚀 Iniciando TCLab Analytics Pro...")
    print(f"📊 Arquivos carregados: {len(files_data)}")
    print("🌐 Acesse: http://127.0.0.1:8050")
    app.run(debug=True, host='127.0.0.1', port=8050)