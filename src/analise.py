import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Configuração do matplotlib
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def load_and_analyze_folder(folder_path, folder_name):
    """
    Carrega todos os arquivos CSV de uma pasta e cria gráficos de dados e estatísticas.
    
    Args:
        folder_path (str): Caminho para a pasta com arquivos CSV
        folder_name (str): Nome da pasta para títulos dos gráficos
    """
    print(f"\n{'='*60}")
    print(f"ANALISANDO PASTA: {folder_name.upper()}")
    print(f"{'='*60}")
    
    if not os.path.exists(folder_path):
        print(f"❌ Pasta '{folder_path}' não encontrada!")
        return
    
    # Listar todos os arquivos CSV
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"❌ Nenhum arquivo CSV encontrado em '{folder_path}'!")
        return
    
    print(f"📁 Encontrados {len(csv_files)} arquivo(s) CSV:")
    for i, file in enumerate(csv_files, 1):
        print(f"   {i}. {file}")
    
    # Processar cada arquivo
    for csv_file in csv_files:
        file_path = os.path.join(folder_path, csv_file)
        print(f"\n🔍 Analisando: {csv_file}")
        
        try:
            # Carregar dados
            df = pd.read_csv(file_path)
            print(f"   ✅ Carregado com sucesso: {len(df)} linhas, {len(df.columns)} colunas")
            print(f"   📊 Colunas: {list(df.columns)}")
            
            # Criar timestamp se necessário
            df_processed = create_timestamp(df.copy())
            
            # Criar gráficos
            create_data_plots(df_processed, csv_file, folder_name)
            create_statistics_plots(df_processed, csv_file, folder_name)
            
        except Exception as e:
            print(f"   ❌ Erro ao processar {csv_file}: {e}")

def create_timestamp(df):
    """
    Cria coluna timestamp a partir das colunas de tempo disponíveis.
    """
    if 'Time (s)' in df.columns:
        # Para dados de output do TCLab
        df['timestamp'] = pd.to_datetime(df['Time (s)'], unit='s')
        df['hours'] = df['Time (s)'] / 3600  # Para gráficos em horas
    elif 'Time' in df.columns:
        # Para dados de setpoints
        df['timestamp'] = pd.to_datetime(df['Time'], unit='s')
        df['hours'] = df['Time'] / 3600  # Para gráficos em horas
    else:
        # Fallback: criar timestamp sequencial
        df['timestamp'] = pd.date_range(start='2023-01-01', periods=len(df), freq='s')
        df['hours'] = range(len(df))
    
    return df

def create_data_plots(df, filename, folder_name):
    """
    Cria gráficos dos dados ao longo do tempo.
    """
    # Identificar colunas numéricas (excluindo timestamp e hours)
    exclude_cols = ['timestamp', 'hours', 'Time', 'Time (s)']
    numeric_cols = [col for col in df.columns 
                   if col not in exclude_cols and pd.api.types.is_numeric_dtype(df[col])]
    
    if not numeric_cols:
        print(f"   ⚠️  Nenhuma coluna numérica encontrada para plotar")
        return
    
    # Determinar quantos subplots precisamos
    n_cols = len(numeric_cols)
    n_rows = (n_cols + 1) // 2  # 2 colunas por linha
    
    fig, axes = plt.subplots(n_rows, 2, figsize=(15, 4 * n_rows))
    fig.suptitle(f'Dados ao Longo do Tempo - {filename}\n{folder_name}', fontsize=14, fontweight='bold')
    
    # Se só temos uma linha, garantir que axes seja uma lista
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    elif n_cols == 1:
        axes = axes.reshape(-1, 1)
    
    for i, col in enumerate(numeric_cols):
        row = i // 2
        col_idx = i % 2
        ax = axes[row, col_idx]
        
        # Plotar dados
        if 'hours' in df.columns:
            ax.plot(df['hours'], df[col], linewidth=1.5, alpha=0.8)
            ax.set_xlabel('Tempo (horas)')
        else:
            ax.plot(df.index, df[col], linewidth=1.5, alpha=0.8)
            ax.set_xlabel('Índice')
        
        ax.set_ylabel(col)
        ax.set_title(f'{col}')
        ax.grid(True, alpha=0.3)
        
        # Adicionar estatísticas no gráfico
        mean_val = df[col].mean()
        std_val = df[col].std()
        ax.axhline(mean_val, color='red', linestyle='--', alpha=0.7, label=f'Média: {mean_val:.2f}')
        ax.legend()
    
    # Remover subplots vazios se houver número ímpar de colunas
    if n_cols % 2 == 1:
        fig.delaxes(axes[n_rows-1, 1])
    
    plt.tight_layout()
    plt.show()

def create_statistics_plots(df, filename, folder_name):
    """
    Cria gráficos estatísticos dos dados.
    """
    # Identificar colunas numéricas
    exclude_cols = ['timestamp', 'hours', 'Time', 'Time (s)']
    numeric_cols = [col for col in df.columns 
                   if col not in exclude_cols and pd.api.types.is_numeric_dtype(df[col])]
    
    if not numeric_cols:
        return
    
    # Calcular estatísticas
    stats_data = []
    for col in numeric_cols:
        stats_data.append({
            'Variável': col,
            'Média': df[col].mean(),
            'Mediana': df[col].median(),
            'Desvio Padrão': df[col].std(),
            'Mínimo': df[col].min(),
            'Máximo': df[col].max(),
            'Variância': df[col].var()
        })
    
    stats_df = pd.DataFrame(stats_data)
    
    # Criar figura com múltiplos subplots para estatísticas
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'Estatísticas - {filename}\n{folder_name}', fontsize=14, fontweight='bold')
    
    # 1. Gráfico de barras - Médias e Medianas
    ax1 = axes[0, 0]
    x_pos = np.arange(len(stats_df))
    width = 0.35
    
    bars1 = ax1.bar(x_pos - width/2, stats_df['Média'], width, label='Média', alpha=0.8)
    bars2 = ax1.bar(x_pos + width/2, stats_df['Mediana'], width, label='Mediana', alpha=0.8)
    
    ax1.set_xlabel('Variáveis')
    ax1.set_ylabel('Valor')
    ax1.set_title('Média vs Mediana')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(stats_df['Variável'], rotation=45)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Adicionar valores nas barras
    for bar in bars1:
        height = bar.get_height()
        ax1.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)
    
    # 2. Gráfico de barras - Desvio Padrão
    ax2 = axes[0, 1]
    bars3 = ax2.bar(stats_df['Variável'], stats_df['Desvio Padrão'], alpha=0.8, color='orange')
    ax2.set_xlabel('Variáveis')
    ax2.set_ylabel('Desvio Padrão')
    ax2.set_title('Desvio Padrão por Variável')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    
    # Adicionar valores nas barras
    for bar in bars3:
        height = bar.get_height()
        ax2.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)
    
    # 3. Boxplot
    ax3 = axes[1, 0]
    df_numeric = df[numeric_cols]
    box_plot = ax3.boxplot([df_numeric[col].dropna() for col in numeric_cols], 
                          tick_labels=numeric_cols, patch_artist=True)
    
    # Colorir boxplots
    colors = plt.cm.Set3(np.linspace(0, 1, len(numeric_cols)))
    for patch, color in zip(box_plot['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax3.set_xlabel('Variáveis')
    ax3.set_ylabel('Valor')
    ax3.set_title('Distribuição dos Dados (Boxplot)')
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(True, alpha=0.3)
    
    # 4. Histograma ou Matriz de Correlação
    ax4 = axes[1, 1]
    
    if len(numeric_cols) > 1:
        # Matriz de correlação se houver múltiplas variáveis
        corr_matrix = df[numeric_cols].corr()
        im = ax4.imshow(corr_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
        
        # Adicionar labels
        ax4.set_xticks(range(len(numeric_cols)))
        ax4.set_yticks(range(len(numeric_cols)))
        ax4.set_xticklabels(numeric_cols, rotation=45)
        ax4.set_yticklabels(numeric_cols)
        ax4.set_title('Matriz de Correlação')
        
        # Adicionar valores na matriz
        for i in range(len(numeric_cols)):
            for j in range(len(numeric_cols)):
                text = ax4.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                               ha="center", va="center", color="black", fontsize=8)
        
        # Adicionar colorbar
        plt.colorbar(im, ax=ax4, shrink=0.8)
    else:
        # Histograma se houver apenas uma variável
        ax4.hist(df[numeric_cols[0]].dropna(), bins=30, alpha=0.7, edgecolor='black')
        ax4.set_xlabel(numeric_cols[0])
        ax4.set_ylabel('Frequência')
        ax4.set_title(f'Histograma - {numeric_cols[0]}')
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Imprimir tabela de estatísticas
    print(f"\n📊 ESTATÍSTICAS DESCRITIVAS - {filename}")
    print("="*80)
    print(stats_df.to_string(index=False, float_format='%.3f'))

def main():
    """
    Função principal para análise dos dados.
    """
    print("🚀 INICIANDO ANÁLISE DOS DADOS TCLab")
    print("="*60)
    
    # Definir caminhos das pastas
    base_path = Path(".")
    setpoints_path = base_path / "setpoints"
    output_path = base_path / "output"
    
    # Analisar pasta de setpoints
    load_and_analyze_folder(setpoints_path, "SETPOINTS")
    
    # Analisar pasta de output
    load_and_analyze_folder(output_path, "OUTPUT TCLab")
    
    print(f"\n{'='*60}")
    print("✅ ANÁLISE CONCLUÍDA!")
    print("="*60)

if __name__ == "__main__":
    main()
