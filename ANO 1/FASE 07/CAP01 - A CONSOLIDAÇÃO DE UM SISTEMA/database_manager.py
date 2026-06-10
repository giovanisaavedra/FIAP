"""
FarmTech Solutions - Módulo de Gerenciamento do Banco de Dados
Sistema de Ingestão de Dados IoT

Autores: Grupo 37 - FIAP
Data: Novembro 2025
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os
from typing import Dict, List, Tuple, Optional
import json


class FarmTechDatabase:
    """
    Classe para gerenciar o banco de dados SQLite do FarmTech Solutions.
    Adaptado para funcionar sem dependências externas complexas.
    """

    def __init__(self, db_path: str = "farmtech_iot.db"):
        """
        Inicializa a conexão com o banco de dados.

        Args:
            db_path: Caminho para o arquivo do banco de dados SQLite
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Estabelece conexão com o banco de dados.

        Usa ``timeout=10`` para que operações que disputam o lock
        (ex.: simulador IoT gravando ao mesmo tempo) aguardem antes
        de levantar ``OperationalError: database is locked``.
        """
        try:
            self.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=10,
            )
            self.cursor = self.conn.cursor()
            print(f"✅ Conectado ao banco de dados: {self.db_path}")
        except Exception as e:
            print(f"❌ Erro ao conectar ao banco: {e}")
            raise

    def _create_tables(self):
        """Cria as tabelas necessárias no banco de dados."""

        # Tabela de Sensores
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS sensores
                            (
                                sensor_id         TEXT PRIMARY KEY,
                                tipo_sensor       TEXT NOT NULL,
                                localizacao       TEXT,
                                farm_id           TEXT,
                                latitude          REAL,
                                longitude         REAL,
                                data_instalacao   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                status            TEXT      DEFAULT 'ativo',
                                ultima_calibracao TIMESTAMP
                            )
                            """)

        # Tabela de Leituras dos Sensores
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS leituras_sensores
                            (
                                leitura_id           INTEGER PRIMARY KEY AUTOINCREMENT,
                                sensor_id            TEXT NOT NULL,
                                timestamp            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                                -- Parâmetros do Solo
                                N                    REAL,
                                P                    REAL,
                                K                    REAL,
                                soil_pH              REAL,
                                soil_moisture        REAL,

                                -- Parâmetros Climáticos
                                temperature_C        REAL,
                                humidity_percent     REAL,
                                rainfall_mm          REAL,
                                sunlight_hours       REAL,

                                -- Parâmetros de Manejo
                                irrigation_volume_mm REAL,

                                -- Metadados
                                qualidade_leitura    TEXT      DEFAULT 'normal',

                                FOREIGN KEY (sensor_id) REFERENCES sensores (sensor_id)
                            )
                            """)

        # Tabela de Culturas
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS culturas
                            (
                                cultura_id             INTEGER PRIMARY KEY AUTOINCREMENT,
                                farm_id                TEXT NOT NULL,
                                crop_type              TEXT NOT NULL,
                                area_hectares          REAL,
                                data_plantio           DATE,
                                data_colheita_prevista DATE,
                                data_colheita_real     DATE,
                                status_cultura         TEXT DEFAULT 'em_crescimento'
                            )
                            """)

        # Tabela de Previsões ML
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS previsoes_ml
                            (
                                previsao_id               INTEGER PRIMARY KEY AUTOINCREMENT,
                                cultura_id                INTEGER,
                                timestamp                 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                                -- Inputs do modelo
                                input_N                   REAL,
                                input_P                   REAL,
                                input_K                   REAL,
                                input_soil_pH             REAL,
                                input_temperature         REAL,
                                input_humidity            REAL,
                                input_rainfall            REAL,

                                -- Outputs do modelo
                                previsao_irrigacao_mm     REAL,
                                previsao_N_fertilizacao   REAL,
                                previsao_P_fertilizacao   REAL,
                                previsao_K_fertilizacao   REAL,
                                previsao_rendimento_kg_ha REAL,

                                -- Métricas do modelo
                                modelo_usado              TEXT,
                                confianca_previsao        REAL,

                                FOREIGN KEY (cultura_id) REFERENCES culturas (cultura_id)
                            )
                            """)

        # Tabela de Alertas
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS alertas
                            (
                                alerta_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                                sensor_id      TEXT,
                                timestamp      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                tipo_alerta    TEXT NOT NULL,
                                severidade     TEXT      DEFAULT 'baixa',
                                mensagem       TEXT,
                                resolvido      INTEGER   DEFAULT 0,
                                data_resolucao TIMESTAMP,

                                FOREIGN KEY (sensor_id) REFERENCES sensores (sensor_id)
                            )
                            """)

        # Tabela de Análises Visuais (Fase 6 - YOLO)
        # Criada com IF NOT EXISTS — não quebra bancos pré-existentes.
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS analises_visuais
                            (
                                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                                timestamp       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                imagem          TEXT,
                                deteccoes_json  TEXT,
                                status          TEXT,
                                num_deteccoes   INTEGER,
                                confianca_media REAL
                            )
                            """)

        # Tabela de Histórico de Decisões de Irrigação (Fase 3)
        # Criada com IF NOT EXISTS para não quebrar bancos pré-existentes.
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS historico_irrigacao
                            (
                                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                sensor_id TEXT,
                                acao      TEXT,
                                motivo    TEXT,
                                umidade   REAL,
                                ph        REAL,

                                FOREIGN KEY (sensor_id) REFERENCES sensores (sensor_id)
                            )
                            """)

        # Migration leve (Fase 5): adiciona coluna ``enviado_sns`` na
        # tabela ``alertas`` se ainda não existir, sem quebrar bancos
        # populados. ``ALTER TABLE ADD COLUMN`` falha se já existir;
        # try/except torna a operação idempotente.
        try:
            self.cursor.execute(
                "ALTER TABLE alertas ADD COLUMN enviado_sns INTEGER DEFAULT 0"
            )
        except Exception:
            pass  # coluna já existe

        self.conn.commit()
        print("✅ Tabelas criadas/verificadas com sucesso")

    def inserir_sensor(self, sensor_id: str, tipo_sensor: str,
                       localizacao: str, farm_id: str,
                       latitude: float = None, longitude: float = None) -> bool:
        """
        Insere um novo sensor no banco de dados.

        Args:
            sensor_id: Identificador único do sensor
            tipo_sensor: Tipo do sensor (ex: 'NPK_pH_Temp', 'Climático')
            localizacao: Localização física do sensor
            farm_id: ID da fazenda
            latitude: Latitude GPS (opcional)
            longitude: Longitude GPS (opcional)

        Returns:
            bool: True se inserido com sucesso
        """
        try:
            self.cursor.execute("""
                INSERT OR REPLACE INTO sensores 
                (sensor_id, tipo_sensor, localizacao, farm_id, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (sensor_id, tipo_sensor, localizacao, farm_id, latitude, longitude))

            self.conn.commit()
            print(f"✅ Sensor {sensor_id} inserido/atualizado com sucesso")
            return True

        except Exception as e:
            print(f"❌ Erro ao inserir sensor: {e}")
            return False

    def inserir_leitura(self, sensor_id: str, dados: Dict) -> bool:
        """
        Insere uma nova leitura de sensor no banco de dados.

        Args:
            sensor_id: ID do sensor
            dados: Dicionário com os dados da leitura

        Returns:
            bool: True se inserido com sucesso
        """
        try:
            # Validação básica dos dados
            qualidade = self._validar_leitura(dados)

            self.cursor.execute("""
                                INSERT INTO leituras_sensores (sensor_id, N, P, K, soil_pH, soil_moisture,
                                                               temperature_C, humidity_percent, rainfall_mm,
                                                               sunlight_hours, irrigation_volume_mm, qualidade_leitura)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    sensor_id,
                                    dados.get('N'),
                                    dados.get('P'),
                                    dados.get('K'),
                                    dados.get('soil_pH'),
                                    dados.get('soil_moisture'),
                                    dados.get('temperature_C'),
                                    dados.get('humidity_percent'),
                                    dados.get('rainfall_mm'),
                                    dados.get('sunlight_hours'),
                                    dados.get('irrigation_volume_mm'),
                                    qualidade
                                ))

            self.conn.commit()

            # Verificar se precisa criar alertas
            self._verificar_alertas(sensor_id, dados)

            return True

        except Exception as e:
            print(f"❌ Erro ao inserir leitura: {e}")
            return False

    def _validar_leitura(self, dados: Dict) -> str:
        """
        Valida os dados de uma leitura e retorna a qualidade.

        Args:
            dados: Dicionário com os dados da leitura

        Returns:
            str: 'normal' ou 'anomalia'
        """
        # Validações básicas
        soil_pH = dados.get('soil_pH', 7.0)
        temperature = dados.get('temperature_C', 25.0)
        humidity = dados.get('humidity_percent', 50.0)

        if soil_pH < 0 or soil_pH > 14:
            return 'anomalia'

        if temperature < -10 or temperature > 60:
            return 'anomalia'

        if humidity < 0 or humidity > 100:
            return 'anomalia'

        return 'normal'

    def _verificar_alertas(self, sensor_id: str, dados: Dict):
        """
        Verifica se os dados requerem criação de alertas.

        Args:
            sensor_id: ID do sensor
            dados: Dicionário com os dados da leitura
        """
        # Alerta de baixa umidade
        soil_moisture = dados.get('soil_moisture', 50.0)
        if soil_moisture < 20:
            self.cursor.execute("""
                                INSERT INTO alertas (sensor_id, tipo_alerta, severidade, mensagem)
                                VALUES (?, ?, ?, ?)
                                """, (
                                    sensor_id,
                                    'BAIXA_UMIDADE',
                                    'alta',
                                    f'Umidade do solo crítica: {soil_moisture:.1f}%'
                                ))

        # Alerta de temperatura alta
        temperature = dados.get('temperature_C', 25.0)
        if temperature > 40:
            self.cursor.execute("""
                                INSERT INTO alertas (sensor_id, tipo_alerta, severidade, mensagem)
                                VALUES (?, ?, ?, ?)
                                """, (
                                    sensor_id,
                                    'TEMPERATURA_ALTA',
                                    'media',
                                    f'Temperatura elevada: {temperature:.1f}°C'
                                ))

        # Alerta de pH extremo
        soil_pH = dados.get('soil_pH', 7.0)
        if soil_pH < 5.0 or soil_pH > 8.0:
            self.cursor.execute("""
                                INSERT INTO alertas (sensor_id, tipo_alerta, severidade, mensagem)
                                VALUES (?, ?, ?, ?)
                                """, (
                                    sensor_id,
                                    'PH_EXTREMO',
                                    'media',
                                    f'pH do solo fora da faixa ideal: {soil_pH:.1f}'
                                ))

        self.conn.commit()

    def obter_ultimas_leituras(self, limit: int = 100) -> pd.DataFrame:
        """
        Obtém as últimas leituras do banco de dados.

        Args:
            limit: Número máximo de registros

        Returns:
            DataFrame com as leituras
        """
        query = f"""
            SELECT 
                l.*,
                s.tipo_sensor,
                s.localizacao,
                s.farm_id
            FROM leituras_sensores l
            LEFT JOIN sensores s ON l.sensor_id = s.sensor_id
            ORDER BY l.timestamp DESC
            LIMIT {limit}
        """

        df = pd.read_sql_query(query, self.conn)
        return df

    def obter_alertas_ativos(self) -> pd.DataFrame:
        """
        Obtém todos os alertas ativos.

        Returns:
            DataFrame com os alertas ativos
        """
        query = """
                SELECT a.*, \
                       s.localizacao, \
                       s.farm_id
                FROM alertas a
                         LEFT JOIN sensores s ON a.sensor_id = s.sensor_id
                WHERE a.resolvido = 0
                ORDER BY a.severidade DESC, a.timestamp DESC \
                """

        df = pd.read_sql_query(query, self.conn)
        return df

    def obter_estatisticas_sensor(self, sensor_id: str,
                                  dias: int = 7) -> Dict:
        """
        Obtém estatísticas de um sensor nos últimos N dias.

        Args:
            sensor_id: ID do sensor
            dias: Número de dias para análise

        Returns:
            Dicionário com as estatísticas
        """
        query = f"""
            SELECT 
                AVG(temperature_C) as avg_temp,
                MIN(temperature_C) as min_temp,
                MAX(temperature_C) as max_temp,
                AVG(humidity_percent) as avg_humidity,
                AVG(soil_moisture) as avg_moisture,
                AVG(soil_pH) as avg_pH,
                SUM(rainfall_mm) as total_rainfall,
                COUNT(*) as total_leituras
            FROM leituras_sensores
            WHERE sensor_id = ?
            AND timestamp >= datetime('now', '-{dias} days')
        """

        self.cursor.execute(query, (sensor_id,))
        result = self.cursor.fetchone()

        if result:
            return {
                'avg_temp': result[0],
                'min_temp': result[1],
                'max_temp': result[2],
                'avg_humidity': result[3],
                'avg_moisture': result[4],
                'avg_pH': result[5],
                'total_rainfall': result[6],
                'total_leituras': result[7]
            }
        return {}

    def inserir_previsao_ml(self, previsao_data: Dict) -> int:
        """
        Insere uma previsão de ML no banco de dados.

        Args:
            previsao_data: Dicionário com os dados da previsão

        Returns:
            ID da previsão inserida
        """
        try:
            self.cursor.execute("""
                                INSERT INTO previsoes_ml (cultura_id, input_N, input_P, input_K, input_soil_pH,
                                                          input_temperature, input_humidity, input_rainfall,
                                                          previsao_irrigacao_mm, previsao_N_fertilizacao,
                                                          previsao_P_fertilizacao, previsao_K_fertilizacao,
                                                          previsao_rendimento_kg_ha, modelo_usado, confianca_previsao)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    previsao_data.get('cultura_id'),
                                    previsao_data.get('input_N'),
                                    previsao_data.get('input_P'),
                                    previsao_data.get('input_K'),
                                    previsao_data.get('input_soil_pH'),
                                    previsao_data.get('input_temperature'),
                                    previsao_data.get('input_humidity'),
                                    previsao_data.get('input_rainfall'),
                                    previsao_data.get('previsao_irrigacao_mm'),
                                    previsao_data.get('previsao_N_fertilizacao'),
                                    previsao_data.get('previsao_P_fertilizacao'),
                                    previsao_data.get('previsao_K_fertilizacao'),
                                    previsao_data.get('previsao_rendimento_kg_ha'),
                                    previsao_data.get('modelo_usado'),
                                    previsao_data.get('confianca_previsao')
                                ))

            self.conn.commit()
            return self.cursor.lastrowid

        except Exception as e:
            print(f"❌ Erro ao inserir previsão: {e}")
            return -1

    def exportar_dados_csv(self, tabela: str, caminho: str) -> bool:
        """
        Exporta uma tabela para CSV.

        Args:
            tabela: Nome da tabela
            caminho: Caminho do arquivo CSV

        Returns:
            bool: True se exportado com sucesso
        """
        try:
            df = pd.read_sql_query(f"SELECT * FROM {tabela}", self.conn)
            df.to_csv(caminho, index=False)
            print(f"✅ Dados exportados para {caminho}")
            return True
        except Exception as e:
            print(f"❌ Erro ao exportar dados: {e}")
            return False

    # ============================================
    # OPERAÇÕES DE LEITURA AUXILIARES (Fase 7)
    # ============================================

    def listar_tabelas(self) -> List[str]:
        """Retorna a lista de tabelas do banco (exclui internas do SQLite).

        Returns:
            Lista ordenada com os nomes das tabelas existentes.
        """
        try:
            self.cursor.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
                "ORDER BY name"
            )
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"❌ Erro ao listar tabelas: {e}")
            return []

    def contar_registros(self, tabela: str) -> int:
        """Conta o total de registros de uma tabela.

        Args:
            tabela: Nome da tabela (deve existir).

        Returns:
            Quantidade de linhas (0 em caso de erro).
        """
        try:
            # Proteção básica contra SQL injection no identificador.
            if tabela not in self.listar_tabelas():
                return 0
            self.cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            return int(self.cursor.fetchone()[0] or 0)
        except Exception as e:
            print(f"❌ Erro ao contar registros de {tabela}: {e}")
            return 0

    def obter_registros_tabela(self, tabela: str, limit: int = 200) -> pd.DataFrame:
        """Lê genericamente até ``limit`` registros de qualquer tabela.

        Args:
            tabela: Nome da tabela existente no banco.
            limit: Limite de linhas a serem retornadas.

        Returns:
            DataFrame com os registros (vazio em caso de erro).
        """
        try:
            if tabela not in self.listar_tabelas():
                return pd.DataFrame()
            query = f"SELECT * FROM {tabela} LIMIT {int(limit)}"
            return pd.read_sql_query(query, self.conn)
        except Exception as e:
            print(f"❌ Erro ao ler {tabela}: {e}")
            return pd.DataFrame()

    def listar_sensores(self) -> pd.DataFrame:
        """Retorna todos os sensores cadastrados, ordenados por ID.

        Returns:
            DataFrame com sensores (vazio se nenhum existir).
        """
        try:
            return pd.read_sql_query(
                "SELECT * FROM sensores ORDER BY sensor_id", self.conn
            )
        except Exception as e:
            print(f"❌ Erro ao listar sensores: {e}")
            return pd.DataFrame()

    def obter_leituras_filtradas(
        self,
        sensor_id: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        limit: int = 200,
    ) -> pd.DataFrame:
        """Retorna leituras com filtros opcionais por sensor e período.

        Args:
            sensor_id: ID do sensor (ou ``None`` para todos).
            data_inicio: Data ISO ``YYYY-MM-DD`` inclusiva (ou ``None``).
            data_fim:    Data ISO ``YYYY-MM-DD`` inclusiva (ou ``None``).
            limit: Limite de linhas.

        Returns:
            DataFrame com as leituras filtradas.
        """
        try:
            query = (
                "SELECT l.*, s.localizacao, s.farm_id "
                "FROM leituras_sensores l "
                "LEFT JOIN sensores s ON l.sensor_id = s.sensor_id "
                "WHERE 1=1 "
            )
            params: List = []
            if sensor_id:
                query += "AND l.sensor_id = ? "
                params.append(sensor_id)
            if data_inicio:
                query += "AND date(l.timestamp) >= date(?) "
                params.append(data_inicio)
            if data_fim:
                query += "AND date(l.timestamp) <= date(?) "
                params.append(data_fim)
            query += f"ORDER BY l.timestamp DESC LIMIT {int(limit)}"
            return pd.read_sql_query(query, self.conn, params=params)
        except Exception as e:
            print(f"❌ Erro ao filtrar leituras: {e}")
            return pd.DataFrame()

    # ============================================
    # OPERAÇÕES DE ATUALIZAÇÃO (UPDATE)
    # ============================================

    def atualizar_status_sensor(self, sensor_id: str, novo_status: str) -> bool:
        """Atualiza o ``status`` de um sensor.

        Args:
            sensor_id:    Identificador do sensor.
            novo_status:  ``"ativo"``, ``"inativo"`` ou ``"manutencao"``.

        Returns:
            ``True`` se atualizado, ``False`` em caso de erro.
        """
        permitidos = {"ativo", "inativo", "manutencao"}
        if novo_status not in permitidos:
            print(f"❌ Status inválido: {novo_status!r}")
            return False
        try:
            self.cursor.execute(
                "UPDATE sensores SET status = ? WHERE sensor_id = ?",
                (novo_status, sensor_id),
            )
            self.conn.commit()
            if self.cursor.rowcount == 0:
                print(f"⚠️ Sensor {sensor_id} não encontrado.")
                return False
            print(f"✅ Sensor {sensor_id} atualizado para status={novo_status}")
            return True
        except Exception as e:
            print(f"❌ Erro ao atualizar status do sensor: {e}")
            return False

    def marcar_alerta_resolvido(self, alerta_id: int) -> bool:
        """Marca um alerta como resolvido (resolvido=1, data_resolucao=now).

        Args:
            alerta_id: ID numérico do alerta.

        Returns:
            ``True`` se o alerta foi marcado, ``False`` caso contrário.
        """
        try:
            self.cursor.execute(
                """
                UPDATE alertas
                   SET resolvido = 1,
                       data_resolucao = CURRENT_TIMESTAMP
                 WHERE alerta_id = ?
                """,
                (int(alerta_id),),
            )
            self.conn.commit()
            if self.cursor.rowcount == 0:
                print(f"⚠️ Alerta {alerta_id} não encontrado.")
                return False
            print(f"✅ Alerta {alerta_id} marcado como resolvido")
            return True
        except Exception as e:
            print(f"❌ Erro ao resolver alerta: {e}")
            return False

    # ============================================
    # OPERAÇÕES DE EXCLUSÃO (DELETE)
    # ============================================

    def deletar_leitura(self, leitura_id: int) -> bool:
        """Remove uma leitura específica pelo ID.

        Args:
            leitura_id: ID da leitura.

        Returns:
            ``True`` se removida, ``False`` caso contrário.
        """
        try:
            self.cursor.execute(
                "DELETE FROM leituras_sensores WHERE leitura_id = ?",
                (int(leitura_id),),
            )
            self.conn.commit()
            if self.cursor.rowcount == 0:
                print(f"⚠️ Leitura {leitura_id} não encontrada.")
                return False
            print(f"✅ Leitura {leitura_id} removida")
            return True
        except Exception as e:
            print(f"❌ Erro ao remover leitura: {e}")
            return False

    def contar_leituras_sensor(self, sensor_id: str) -> int:
        """Conta quantas leituras estão associadas a um sensor.

        Args:
            sensor_id: ID do sensor.

        Returns:
            Quantidade de leituras (0 em caso de erro).
        """
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM leituras_sensores WHERE sensor_id = ?",
                (sensor_id,),
            )
            return int(self.cursor.fetchone()[0] or 0)
        except Exception as e:
            print(f"❌ Erro ao contar leituras do sensor: {e}")
            return 0

    def deletar_sensor(self, sensor_id: str, cascade: bool = False) -> Tuple[bool, int]:
        """Remove um sensor pelo ID, opcionalmente apagando suas leituras.

        Args:
            sensor_id: ID do sensor a remover.
            cascade:   Se ``True``, remove também leituras e alertas
                associados; se ``False`` e existirem leituras
                associadas, **não** apaga e devolve ``(False, n)``.

        Returns:
            Tupla ``(sucesso, leituras_associadas)``.
        """
        try:
            n_leituras = self.contar_leituras_sensor(sensor_id)
            if n_leituras > 0 and not cascade:
                return (False, n_leituras)

            if cascade:
                self.cursor.execute(
                    "DELETE FROM leituras_sensores WHERE sensor_id = ?",
                    (sensor_id,),
                )
                self.cursor.execute(
                    "DELETE FROM alertas WHERE sensor_id = ?",
                    (sensor_id,),
                )

            self.cursor.execute(
                "DELETE FROM sensores WHERE sensor_id = ?",
                (sensor_id,),
            )
            self.conn.commit()
            if self.cursor.rowcount == 0:
                return (False, n_leituras)
            print(f"✅ Sensor {sensor_id} removido (cascade={cascade})")
            return (True, n_leituras)
        except Exception as e:
            print(f"❌ Erro ao remover sensor: {e}")
            return (False, 0)

    # ============================================
    # HISTÓRICO DE IRRIGAÇÃO (Fase 3)
    # ============================================

    def inserir_decisao_irrigacao(
        self,
        sensor_id: str,
        acao: str,
        motivo: str,
        umidade: Optional[float] = None,
        ph: Optional[float] = None,
    ) -> bool:
        """Registra uma decisão do ``ControladorIrrigacao`` no banco.

        Args:
            sensor_id: ID do sensor avaliado.
            acao:      ``"LIGAR"``, ``"DESLIGAR"`` ou ``"BLOQUEADA"``.
            motivo:    Explicação curta vinda do controlador.
            umidade:   Umidade do solo (%) considerada na decisão.
            ph:        pH do solo considerado na decisão.

        Returns:
            ``True`` se inserido com sucesso.
        """
        try:
            self.cursor.execute(
                """
                INSERT INTO historico_irrigacao
                    (sensor_id, acao, motivo, umidade, ph)
                VALUES (?, ?, ?, ?, ?)
                """,
                (sensor_id, acao, motivo, umidade, ph),
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Erro ao registrar decisão de irrigação: {e}")
            return False

    def obter_historico_irrigacao(self, limit: int = 50) -> pd.DataFrame:
        """Devolve as últimas decisões de irrigação registradas.

        Args:
            limit: Número máximo de linhas a retornar.

        Returns:
            DataFrame ordenado da decisão mais recente para a mais antiga.
        """
        try:
            query = f"""
                SELECT id, timestamp, sensor_id, acao, motivo, umidade, ph
                FROM historico_irrigacao
                ORDER BY timestamp DESC, id DESC
                LIMIT {int(limit)}
            """
            return pd.read_sql_query(query, self.conn)
        except Exception as e:
            print(f"❌ Erro ao ler histórico de irrigação: {e}")
            return pd.DataFrame()

    # ============================================
    # ANÁLISES VISUAIS (Fase 6 - YOLO)
    # ============================================

    def inserir_analise_visual(
        self,
        imagem: str,
        deteccoes_json: str,
        status: str,
        num_deteccoes: int,
        confianca_media: Optional[float] = None,
    ) -> bool:
        """Persiste o resultado de uma análise visual (YOLO).

        Args:
            imagem:          Caminho/arquivo da imagem analisada.
            deteccoes_json:  Detecções serializadas em JSON (lista de dicts).
            status:          Mensagem-resumo do diagnóstico agrícola.
            num_deteccoes:   Quantidade total de objetos detectados.
            confianca_media: Média das confianças (0–1), ou ``None``
                quando não há detecções.

        Returns:
            ``True`` se inserido com sucesso.
        """
        try:
            self.cursor.execute(
                """
                INSERT INTO analises_visuais
                    (imagem, deteccoes_json, status,
                     num_deteccoes, confianca_media)
                VALUES (?, ?, ?, ?, ?)
                """,
                (imagem, deteccoes_json, status,
                 int(num_deteccoes), confianca_media),
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Erro ao registrar análise visual: {e}")
            return False

    def obter_analises_visuais(self, limit: int = 50) -> pd.DataFrame:
        """Devolve as últimas análises visuais registradas.

        Args:
            limit: Quantidade máxima de linhas a retornar.

        Returns:
            DataFrame ordenado da mais recente para a mais antiga.
        """
        try:
            query = f"""
                SELECT id, timestamp, imagem, status,
                       num_deteccoes, confianca_media, deteccoes_json
                FROM analises_visuais
                ORDER BY timestamp DESC, id DESC
                LIMIT {int(limit)}
            """
            return pd.read_sql_query(query, self.conn)
        except Exception as e:
            print(f"❌ Erro ao ler analises_visuais: {e}")
            return pd.DataFrame()

    def fechar_conexao(self):
        """Fecha a conexão com o banco de dados."""
        if self.conn:
            self.conn.close()
            print("✅ Conexão com banco de dados fechada")


# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def criar_banco_exemplo():
    """Cria um banco de dados de exemplo com dados iniciais."""

    db = FarmTechDatabase("farmtech_iot_exemplo.db")

    # Inserir sensores de exemplo
    sensores_exemplo = [
        {
            'sensor_id': 'SENSOR_001',
            'tipo_sensor': 'NPK_pH_Temp',
            'localizacao': 'Área Norte',
            'farm_id': 'FARM_001',
            'latitude': -23.5505,
            'longitude': -46.6333
        },
        {
            'sensor_id': 'SENSOR_002',
            'tipo_sensor': 'Climático',
            'localizacao': 'Área Sul',
            'farm_id': 'FARM_001',
            'latitude': -23.5515,
            'longitude': -46.6343
        },
        {
            'sensor_id': 'SENSOR_003',
            'tipo_sensor': 'NPK_pH_Temp',
            'localizacao': 'Área Leste',
            'farm_id': 'FARM_002',
            'latitude': -23.5525,
            'longitude': -46.6353
        }
    ]

    for sensor in sensores_exemplo:
        db.inserir_sensor(**sensor)

    print("✅ Banco de dados de exemplo criado!")

    return db


if __name__ == "__main__":
    # Teste do módulo
    print("=== Teste do Módulo de Banco de Dados ===\n")

    db = criar_banco_exemplo()

    # Inserir uma leitura de teste
    leitura_teste = {
        'N': 45.2,
        'P': 38.5,
        'K': 42.1,
        'soil_pH': 6.5,
        'soil_moisture': 35.8,
        'temperature_C': 28.5,
        'humidity_percent': 65.2,
        'rainfall_mm': 5.3,
        'sunlight_hours': 8.5,
        'irrigation_volume_mm': 10.0
    }

    db.inserir_leitura('SENSOR_001', leitura_teste)

    # Obter últimas leituras
    print("\n=== Últimas Leituras ===")
    df_leituras = db.obter_ultimas_leituras(5)
    print(df_leituras)

    db.fechar_conexao()