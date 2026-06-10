"""
FarmTech Solutions - Simulador de Sensores IoT (CORRIGIDO)
Sistema de Geração e Ingestão Automática de Dados

Autores: Grupo 37 - FIAP
Data: Novembro 2025

VERSÃO CORRIGIDA: Thread-safe para múltiplos sensores
"""

import random
import time
import threading
from datetime import datetime
from typing import Dict, List
import numpy as np
import sqlite3

# Importar apenas a classe, não usar instância compartilhada
from database_manager import FarmTechDatabase


class SimuladorSensorIoT:
    """
    Simulador de sensor IoT que gera dados realistas de campo
    e os envia automaticamente para o banco de dados.
    VERSÃO CORRIGIDA: Cada sensor tem sua própria conexão DB.
    """

    def __init__(self, sensor_id: str, tipo_sensor: str,
                 farm_id: str, db_path: str = "farmtech_iot.db"):
        """
        Inicializa o simulador de sensor.

        Args:
            sensor_id: ID único do sensor
            tipo_sensor: Tipo do sensor
            farm_id: ID da fazenda
            db_path: Caminho do banco de dados
        """
        self.sensor_id = sensor_id
        self.tipo_sensor = tipo_sensor
        self.farm_id = farm_id
        self.db_path = db_path
        self.ativo = False
        self.intervalo_leitura = 5  # segundos

        # Parâmetros base para geração de dados realistas
        self.parametros_base = {
            'N': 50.0,
            'P': 40.0,
            'K': 45.0,
            'soil_pH': 6.5,
            'soil_moisture': 40.0,
            'temperature_C': 25.0,
            'humidity_percent': 60.0,
            'rainfall_mm': 0.0,
            'sunlight_hours': 8.0,
            'irrigation_volume_mm': 0.0
        }

        # Variação permitida para cada parâmetro
        self.variacoes = {
            'N': 5.0,
            'P': 4.0,
            'K': 4.5,
            'soil_pH': 0.3,
            'soil_moisture': 8.0,
            'temperature_C': 3.0,
            'humidity_percent': 10.0,
            'rainfall_mm': 2.0,
            'sunlight_hours': 1.0,
            'irrigation_volume_mm': 5.0
        }

    def gerar_leitura(self) -> Dict:
        """
        Gera uma leitura simulada do sensor com valores realistas.

        Returns:
            Dicionário com os dados da leitura
        """
        leitura = {}

        for parametro, valor_base in self.parametros_base.items():
            variacao = self.variacoes[parametro]

            # Adicionar variação aleatória
            ruido = np.random.normal(0, variacao / 3)
            valor = valor_base + ruido

            # Aplicar limites realistas
            if parametro == 'soil_pH':
                valor = max(4.0, min(9.0, valor))
            elif parametro == 'soil_moisture':
                valor = max(0.0, min(100.0, valor))
            elif parametro == 'temperature_C':
                valor = max(-5.0, min(50.0, valor))
            elif parametro == 'humidity_percent':
                valor = max(0.0, min(100.0, valor))
            elif parametro in ['N', 'P', 'K']:
                valor = max(0.0, min(100.0, valor))
            elif 'rainfall_mm' in parametro or 'irrigation' in parametro:
                valor = max(0.0, valor)

            leitura[parametro] = round(valor, 2)

        return leitura

    def simular_evento_climatico(self):
        """Simula eventos climáticos aleatórios (chuva, sol intenso, etc)."""
        evento = random.choice(['normal', 'chuva', 'sol_intenso', 'seca'])

        if evento == 'chuva':
            self.parametros_base['rainfall_mm'] = random.uniform(5, 20)
            self.parametros_base['humidity_percent'] = random.uniform(75, 95)
            self.parametros_base['sunlight_hours'] = random.uniform(2, 5)

        elif evento == 'sol_intenso':
            self.parametros_base['temperature_C'] = random.uniform(32, 42)
            self.parametros_base['sunlight_hours'] = random.uniform(10, 12)
            self.parametros_base['humidity_percent'] = random.uniform(30, 50)

        elif evento == 'seca':
            self.parametros_base['rainfall_mm'] = 0.0
            self.parametros_base['soil_moisture'] = max(15,
                                                        self.parametros_base['soil_moisture'] - random.uniform(2, 5))

    def iniciar_coleta_automatica(self, intervalo: int = 5):
        """
        Inicia a coleta automática de dados.
        CORRIGIDO: Cria conexão própria para esta thread.

        Args:
            intervalo: Intervalo entre leituras em segundos
        """
        self.intervalo_leitura = intervalo
        self.ativo = True

        def coletar_dados():
            # ✅ CORREÇÃO: Criar conexão própria para esta thread
            db_local = FarmTechDatabase(self.db_path)
            contador = 0

            while self.ativo:
                try:
                    # Gerar leitura
                    leitura = self.gerar_leitura()

                    # Enviar para o banco de dados usando conexão local
                    sucesso = db_local.inserir_leitura(self.sensor_id, leitura)

                    if sucesso:
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        print(f"[{timestamp}] 📡 {self.sensor_id}: Leitura #{contador + 1} enviada")
                        print(f"   Temp: {leitura['temperature_C']}°C | "
                              f"Umidade Solo: {leitura['soil_moisture']}% | "
                              f"pH: {leitura['soil_pH']}")

                    contador += 1

                    # Simular evento climático ocasionalmente (5% de chance)
                    if random.random() < 0.05:
                        self.simular_evento_climatico()

                    time.sleep(self.intervalo_leitura)

                except Exception as e:
                    print(f"❌ Erro no sensor {self.sensor_id}: {e}")
                    time.sleep(self.intervalo_leitura)

            # ✅ Fechar conexão ao terminar
            db_local.fechar_conexao()

        # Iniciar thread de coleta
        self.thread = threading.Thread(target=coletar_dados, daemon=True)
        self.thread.start()
        print(f"✅ Sensor {self.sensor_id} iniciado (intervalo: {intervalo}s)")

    def parar_coleta(self):
        """Para a coleta automática de dados."""
        self.ativo = False
        print(f"⏹️ Sensor {self.sensor_id} parado")


class CentralSensoresIoT:
    """
    Central de gerenciamento de múltiplos sensores IoT.
    Coordena a coleta de dados de vários sensores simultaneamente.
    VERSÃO CORRIGIDA: Thread-safe.
    """

    def __init__(self, db_path: str = "farmtech_iot.db"):
        """
        Inicializa a central de sensores.

        Args:
            db_path: Caminho para o banco de dados
        """
        self.db_path = db_path
        self.db = FarmTechDatabase(db_path)
        self.sensores: List[SimuladorSensorIoT] = []
        self.ativo = False

    def adicionar_sensor(self, sensor_id: str, tipo_sensor: str,
                         localizacao: str, farm_id: str,
                         latitude: float = None, longitude: float = None):
        """
        Adiciona um novo sensor à central.

        Args:
            sensor_id: ID do sensor
            tipo_sensor: Tipo do sensor
            localizacao: Localização do sensor
            farm_id: ID da fazenda
            latitude: Latitude GPS
            longitude: Longitude GPS
        """
        # Registrar sensor no banco de dados
        self.db.inserir_sensor(sensor_id, tipo_sensor, localizacao,
                               farm_id, latitude, longitude)

        # Criar simulador (com path do banco)
        sensor = SimuladorSensorIoT(sensor_id, tipo_sensor, farm_id, self.db_path)
        self.sensores.append(sensor)

        print(f"✅ Sensor {sensor_id} adicionado à central")

    def iniciar_todos_sensores(self, intervalo: int = 5):
        """
        Inicia todos os sensores simultaneamente.

        Args:
            intervalo: Intervalo entre leituras em segundos
        """
        print("\n" + "=" * 60)
        print("🚀 INICIANDO SISTEMA DE SENSORES IoT")
        print("=" * 60)

        for sensor in self.sensores:
            sensor.iniciar_coleta_automatica(intervalo)
            time.sleep(0.1)  # Pequeno delay entre inicializações

        self.ativo = True
        print(f"\n✅ {len(self.sensores)} sensores ativos!")
        print(f"📊 Dados sendo enviados para: {self.db_path}")
        print(f"⏱️  Intervalo de leitura: {intervalo} segundos")
        print("\nPressione Ctrl+C para parar...\n")

    def parar_todos_sensores(self):
        """Para todos os sensores."""
        print("\n⏹️ Parando todos os sensores...")

        for sensor in self.sensores:
            sensor.parar_coleta()

        self.ativo = False
        print("✅ Todos os sensores foram parados")

    def relatorio_status(self):
        """Exibe relatório de status dos sensores."""
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO DE STATUS DOS SENSORES")
        print("=" * 60)

        for sensor in self.sensores:
            status = "🟢 ATIVO" if sensor.ativo else "🔴 INATIVO"
            print(f"\n{sensor.sensor_id} ({sensor.tipo_sensor})")
            print(f"   Status: {status}")
            print(f"   Farm: {sensor.farm_id}")
            print(f"   Intervalo: {sensor.intervalo_leitura}s")

        # Estatísticas do banco de dados
        print("\n" + "-" * 60)
        print("📈 ESTATÍSTICAS DO BANCO DE DADOS")
        print("-" * 60)

        try:
            df_leituras = self.db.obter_ultimas_leituras(limit=1000)
            print(f"Total de leituras: {len(df_leituras)}")

            df_alertas = self.db.obter_alertas_ativos()
            print(f"Alertas ativos: {len(df_alertas)}")
        except Exception as e:
            print(f"⚠️ Erro ao obter estatísticas: {e}")

        print("=" * 60 + "\n")


def configurar_fazenda_exemplo():
    """
    Configura uma fazenda de exemplo com múltiplos sensores.
    """
    # Criar central de sensores
    central = CentralSensoresIoT("farmtech_iot.db")

    # Configurar sensores da Fazenda 1
    central.adicionar_sensor(
        sensor_id="SENSOR_NPK_001",
        tipo_sensor="NPK_pH_Temp",
        localizacao="Área Norte - Cultivo Milho",
        farm_id="FARM_001",
        latitude=-23.5505,
        longitude=-46.6333
    )

    central.adicionar_sensor(
        sensor_id="SENSOR_CLIMA_001",
        tipo_sensor="Climático",
        localizacao="Estação Meteorológica Central",
        farm_id="FARM_001",
        latitude=-23.5515,
        longitude=-46.6343
    )

    central.adicionar_sensor(
        sensor_id="SENSOR_NPK_002",
        tipo_sensor="NPK_pH_Temp",
        localizacao="Área Sul - Cultivo Soja",
        farm_id="FARM_001",
        latitude=-23.5525,
        longitude=-46.6353
    )

    # Configurar sensores da Fazenda 2
    central.adicionar_sensor(
        sensor_id="SENSOR_NPK_003",
        tipo_sensor="NPK_pH_Temp",
        localizacao="Área Leste - Cultivo Trigo",
        farm_id="FARM_002",
        latitude=-23.5535,
        longitude=-46.6363
    )

    return central


def main():
    """Função principal para executar o simulador."""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║        🌾 FARMTECH SOLUTIONS - SIMULADOR IoT 🌾           ║
    ║                                                            ║
    ║        Sistema de Ingestão Automática de Dados            ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    # Configurar fazenda
    central = configurar_fazenda_exemplo()

    try:
        # Iniciar coleta automática (intervalo de 5 segundos)
        central.iniciar_todos_sensores(intervalo=5)

        # Manter programa rodando
        while True:
            time.sleep(30)  # Exibir relatório a cada 30 segundos
            central.relatorio_status()

    except KeyboardInterrupt:
        print("\n\n🛑 Interrupção detectada...")
        central.parar_todos_sensores()
        central.db.fechar_conexao()
        print("\n✅ Sistema encerrado com sucesso!")
        print("\n" + "=" * 60)
        print("📁 Dados salvos em: farmtech_iot.db")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    main()