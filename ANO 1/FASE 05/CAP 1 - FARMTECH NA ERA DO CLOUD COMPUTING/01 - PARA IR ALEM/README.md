

---

# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
  <a href="https://www.fiap.com.br/">
    <img src="https://github.com/giovanisaavedra/FIAP/blob/main/assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" border="0" width="40%">
  </a>
</p>

<br>

# 🌱 Farm Status – Monitoramento Inteligente com IoT e Cloud Computing

---

# 👥 Equipe do Projeto

## 👨‍🎓 Integrantes

| Nome                                | RM       |
| ----------------------------------- | -------- |
| Giovani Saavedra                    | RM566797 |
| Marcio Elifas                       | RM567871 |
| Felipe Bernardo Papaleo de Oliveira | RM567782 |

---

## 👩‍🏫 Orientação

**Tutor(a):** Sabrina Otoni
**Coordenador(a):** André Godoi Chiovatto

---

# 📜 Descrição

O projeto **Farm Status** tem como objetivo demonstrar a aplicação prática de tecnologias de **Internet das Coisas (IoT)** e **Cloud Computing** no monitoramento remoto de ambientes agrícolas.

A solução desenvolvida utiliza um dispositivo embarcado **ESP32 XIAO ESP32S3 CAM**, equipado com câmera e sensor ambiental **DHT22**, capaz de capturar imagens do ambiente em vista de avaliar visualmente a condição de clima pragas e periodo exato quando o fruto ou cultura pode ser colhido (maduro) e coletar dados de **temperatura** e **umidade** em tempo real.

Essas informações são enviadas via rede **Wi-Fi** para um servidor desenvolvido em **Python utilizando Flask**, que recebe, processa e armazena os dados em um banco de dados.

Além disso, foi desenvolvido um **dashboard web interativo** que permite visualizar os dados coletados de forma gráfica, possibilitando acompanhar as condições ambientais do ambiente monitorado.

A solução proposta demonstra como tecnologias modernas de **dispositivos embarcados**, **computação em nuvem** e **visualização de dados** podem ser aplicadas para criar sistemas inteligentes de monitoramento ambiental.

Entre as principais funcionalidades implementadas estão:

* Captura automática de imagens utilizando ESP32 CAM
* Leitura de temperatura e umidade com sensor DHT22
* Transmissão de dados via Wi-Fi para um servidor Flask
* Armazenamento das informações em banco de dados
* Dashboard web com gráficos para visualização dos dados
* Monitoramento remoto em tempo real

O projeto demonstra a integração entre **hardware IoT, backend em Python e visualização web**, aplicando os conceitos estudados na disciplina **FarmTech na Era do Cloud Computing**.

---

# 🎥 Demonstração do Projeto

O vídeo abaixo apresenta o funcionamento completo do sistema:

* captura de imagem com ESP32 CAM
* leitura do sensor de temperatura e umidade
* envio de dados para o servidor
* armazenamento no banco de dados
* visualização no dashboard

[![Demonstração do projeto](https://img.youtube.com/vi/Thj4urXqfDo/0.jpg)](https://youtu.be/Thj4urXqfDo)

🔗 Link direto:
[https://youtu.be/Thj4urXqfDo](https://youtu.be/Thj4urXqfDo)

---

# 📁 Estrutura de pastas

Dentre os arquivos e pastas presentes na raiz do projeto, definem-se:

* **app.py**
  Arquivos de configuração do sistema e servidor.

* **templates**
  Documento de criação do dashboard em html.

* **readings.csv**
  Arquivo que controla o histórico de dados capturados pelos sensores.

* **uploads**
  Pasta utilizada para armazenar temporariamente as imagens capturadas pelo ESP32.

* **README.md**
  Arquivo de documentação do projeto.

---

# 🔧 Como executar o código

## Pré-requisitos

Para executar o projeto são necessários:

### Hardware

* ESP32 XIAO ESP32S3 CAM
* Sensor DHT22
* Conexão Wi-Fi

### Software

* Python 3.10 ou superior
* Arduino IDE
* MySQL
* Bibliotecas Python & Esp32 :

```
Flask
xaamp
mysql-connector-python
requests
```

---

# 1️⃣ Configuração do ESP32

1. Instale a **Arduino IDE**

2. Instale o suporte para placas **ESP32**

3. Selecione a placa

```
XIAO ESP32S3
```

4. Instale as bibliotecas necessárias

* WiFi
* esp_camera
* DHT sensor library

5. Configure no código

* SSID da rede WiFi
* senha da rede WiFi
* endereço do servidor Flask

6. Faça o upload do firmware para o ESP32.

---

# 2️⃣ Configuração do servidor

Clone o repositório:

```
git clone https://github.com/giovanisaavedra/FIAP.git
```

Entre na pasta do projeto.

Instale as dependências:

```
pip install flask
pip install mysql-connector-python
```

Execute o servidor:

```
python app.py
```

O servidor ficará disponível em:

```
http://localhost:5000
```

---

# 3️⃣ Funcionamento do sistema

Fluxo do sistema:

```
ESP32
↓
Captura imagem + dados do sensor
↓
Envia dados via HTTP
↓
Servidor Flask recebe
↓
Armazena no banco de dados
↓
Dashboard consulta os dados
↓
Exibição em gráficos
```

---



# 📋 Licença

<img src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1" width="30"> <img src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1" width="30">

[MODELO GIT FIAP](https://github.com/agodoi/template) por [Fiap](https://fiap.com.br) está licenciado sobre
[Attribution 4.0 International](http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1).

---

