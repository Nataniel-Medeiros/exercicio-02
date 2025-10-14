import tclab
import time
import pandas as pd
import numpy as np
from typing import Literal


def run_simulation(
    duration_minutes: float = 60 * 24 * 7,  # 7 dias padrão
    speedup_factor: int = 600,
    temp_precision: Literal['float64', 'float32', 'float16'] = 'float16',
    heater_type: Literal['int8', 'bool'] = 'int8',
    setpoints_t1: dict | None = None,
    setpoints_t2: dict | None = None
):
  """
  Executa a simulação do TCLab com controle ON/OFF puro (sem histerese).

  Args:
      duration_minutes (float): Duração da simulação em minutos.
      speedup_factor (int): Fator de aceleração da simulação.
      temp_precision (str): Precisão de ponto flutuante ('float16', 'float32', 'float64').
      heater_type (str): Tipo de dado para Q1 e Q2 ('int8' ou 'bool').
      setpoints_t1, setpoints_t2 (dict): Mapas tempo->setpoint (em segundos).
  """
  allowed_precisions = ['float64', 'float32', 'float16']
  allowed_heater_types = ['int8', 'bool']
  assert temp_precision in allowed_precisions
  assert heater_type in allowed_heater_types

  tclab.setup(connected=False, speedup=speedup_factor)
  tf = duration_minutes * 60
  n = int(tf) + 1

  with tclab.TCLabModel() as lab:
    T1_data, T2_data, Q1_data, Q2_data, times = [], [], [], [], []

    if setpoints_t1 is None:
      setpoints_t1 = {0: 24}
    if setpoints_t2 is None:
      setpoints_t2 = {0: 24}

    current_sp1 = setpoints_t1[0]
    current_sp2 = setpoints_t2[0]

    print(
        f"Iniciando simulação de {duration_minutes:.0f} min "
        f"(≈ {duration_minutes/60:.2f} h) com speedup {speedup_factor}x"
    )
    print(f"Precisão: {temp_precision}, Tipo do Aquecedor: {heater_type}")

    try:
      for i in range(n):
        # Atualiza setpoints se definidos no tempo atual
        if i in setpoints_t1:
          current_sp1 = setpoints_t1[i]
        if i in setpoints_t2:
          current_sp2 = setpoints_t2[i]

        # --- Controle ON/OFF sem histerese ---
        q1 = 1 if lab.T1 < current_sp1 else 0
        q2 = 1 if lab.T2 < current_sp2 else 0

        lab.Q1(100 if q1 else 0)
        lab.Q2(100 if q2 else 0)

        # Armazena dados
        times.append(i)
        T1_data.append(lab.T1)
        T2_data.append(lab.T2)
        Q1_data.append(lab.U1)
        Q2_data.append(lab.U2)

        if i % 3600 == 0:
          print(
              f"t = {i/3600:.1f}h | "
              f"T1={lab.T1:.2f}°C (SP1={current_sp1}), "
              f"T2={lab.T2:.2f}°C (SP2={current_sp2})"
          )

    except KeyboardInterrupt:
      print("Simulação interrompida pelo usuário.")

  # --- Conversão e salvamento ---
  print("\nConvertendo tipos de dados...")
  data = pd.DataFrame({
      'Time (s)': times,
      'T1': np.array(T1_data, dtype=temp_precision),
      'T2': np.array(T2_data, dtype=temp_precision),
      'Q1': np.array(Q1_data, dtype=np.int8 if heater_type == 'int8' else np.bool_),
      'Q2': np.array(Q2_data, dtype=np.int8 if heater_type == 'int8' else np.bool_)
  })

  filename = f"output/tclab_data_{temp_precision}_{heater_type}_{int(duration_minutes)}min_noH.csv"
  data.to_csv(filename, index=False)

  print(f"Dados salvos em '{filename}'")
  print("\nInformações de memória:")
  data.info(memory_usage='deep')


def create_daily_pattern(base_pattern, total_days, max_temp, fluctuation=3):
  pattern = []
  for day in range(total_days):
    daily = [min(max_temp, max(0, val + np.random.randint(-fluctuation, fluctuation+1)))
             for val in base_pattern]
    pattern.extend(daily)
  return pattern[:total_intervals]


if __name__ == '__main__':
  speedup_factor = 100000

  experiment_days = 7
  interval_h = 6              # alteração a cada 6 horas
  max_temp = 70
  base_pattern_t1 = [30, 50, 65, 55]  # padrão base para T1
  base_pattern_t2 = [25, 45, 60, 50]  # padrão base para T2
  intervals_per_day = 24 // interval_h
  total_intervals = experiment_days * intervals_per_day
  time_points_s = np.arange(
      0, total_intervals * interval_h * 3600, interval_h * 3600)

  # --- Função para criar padrões diários com pequenas flutuações ---
  np.random.seed(42)

  t1_values = create_daily_pattern(base_pattern_t1, experiment_days, max_temp)
  t2_values = create_daily_pattern(base_pattern_t2, experiment_days, max_temp)

  # --- Criar dicionários tempo (s) -> setpoint (°C) ---
  setpoints_t1 = {int(t): float(sp) for t, sp in zip(time_points_s, t1_values)}
  setpoints_t2 = {int(t): float(sp) for t, sp in zip(time_points_s, t2_values)}

  # --- Salvar em CSV para usar depois ---
  df_setpoints = pd.DataFrame({
      'Time': time_points_s,
      'T1_setpoint': t1_values,
      'T2_setpoint': t2_values
  })

  csv_filename = f'setpoints/setpoints_7days_{interval_h}h.csv'
  df_setpoints.to_csv(csv_filename, index=False)
  print(f"CSV de setpoints salvo em '{csv_filename}'")

  duration_minutes = experiment_days * 24 * 60

  run_simulation(duration_minutes, speedup_factor,
                 setpoints_t1=setpoints_t1, setpoints_t2=setpoints_t2)
