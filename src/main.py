from machine import Pin, I2C
import dht
import time

from i2c_lcd import I2cLcd


# ==========================================
# CHARGEGRID INTELLIGENCE
# Sistema inteligente de gerenciamento
# de recarga de veículos elétricos
# ==========================================


# ==========================================
# 1. COMPONENTES
# ==========================================

# Sensor DHT22
sensor_temp = dht.DHT22(Pin(16))


# ==========================================
# BOTÕES
# ==========================================

# Botão do veículo
botao_veiculo = Pin(
    14,
    Pin.IN,
    Pin.PULL_UP
)


# Botão +
botao_mais = Pin(
    17,
    Pin.IN,
    Pin.PULL_UP
)


# Botão -
botao_menos = Pin(
    18,
    Pin.IN,
    Pin.PULL_UP
)


# ==========================================
# LED
# ==========================================

led_recarga = Pin(
    15,
    Pin.OUT
)


# ==========================================
# 2. CONFIGURAÇÕES
# ==========================================

ENERGIA_MINIMA = 3.0

TEMPERATURA_MAXIMA = 40.0

# Potência simulada do carregador
POTENCIA_RECARGA = 3.3

# Energia solar inicial
energia_solar = 5.0


# ==========================================
# 3. LCD
# ==========================================

i2c = I2C(
    0,
    scl=Pin(5),
    sda=Pin(4),
    freq=400000
)


lcd = I2cLcd(
    i2c,
    0x27,
    2,
    16
)


# ==========================================
# 4. FUNÇÃO DO LCD
# ==========================================

def mostrar_lcd(linha1, linha2):

    lcd.clear()

    lcd.move_to(0, 0)
    lcd.putstr(linha1[:16])

    lcd.move_to(0, 1)
    lcd.putstr(linha2[:16])


# ==========================================
# 5. LEITURA DA TEMPERATURA
# ==========================================

def ler_temperatura():

    try:

        sensor_temp.measure()

        return sensor_temp.temperature()

    except:

        return 25.0


# ==========================================
# 6. ESTADO DOS BOTÕES
# ==========================================

ultimo_veiculo = 1
ultimo_mais = 1
ultimo_menos = 1


# ==========================================
# 7. ESTADO DO VEÍCULO
# ==========================================

veiculo_conectado = False


# ==========================================
# 8. CONTROLE DA SESSÃO
# ==========================================

numero_sessao = 0

sessao_ativa = False

inicio_sessao = 0

tempo_recarga = 0


# ==========================================
# 9. HISTÓRICO
# ==========================================

historico_sessoes = []

motivo_sessao = "RECARGA NORMAL"


# ==========================================
# 10. INICIALIZAÇÃO
# ==========================================

print()

print("========================================")

print("       CHARGEGRID INTELLIGENCE")

print("       SISTEMA INICIADO")

print("========================================")

print()


mostrar_lcd(
    "CHARGEGRID",
    "SISTEMA ONLINE"
)


time.sleep(2)


# ==========================================
# 11. LOOP PRINCIPAL
# ==========================================

while True:


    # ======================================
    # BOTÃO DO VEÍCULO
    # ======================================

    estado_veiculo = botao_veiculo.value()


    if estado_veiculo == 0 and ultimo_veiculo == 1:

        # Guarda o estado anterior
        estava_conectado = veiculo_conectado


        # Alterna o estado do veículo
        veiculo_conectado = not veiculo_conectado


        # ==================================
        # NOVA SESSÃO
        # ==================================

        if not estava_conectado and veiculo_conectado:

            numero_sessao += 1

            sessao_ativa = True

            inicio_sessao = time.ticks_ms()

            tempo_recarga = 0

            motivo_sessao = "RECARGA NORMAL"


            print()
            print("========================================")
            print("       NOVA SESSAO DE RECARGA")
            print("       SESSAO:", numero_sessao)
            print("========================================")
            print()


        # ==================================
        # FINALIZAÇÃO DA SESSÃO
        # ==================================

        elif estava_conectado and not veiculo_conectado:

            if sessao_ativa:


                # ------------------------------
                # Duração da sessão
                # ------------------------------

                duracao = time.ticks_diff(
                    time.ticks_ms(),
                    inicio_sessao
                ) / 1000


                # ------------------------------
                # Energia utilizada
                # ------------------------------

                energia_utilizada = (
                    POTENCIA_RECARGA
                    * tempo_recarga
                    / 3600
                )


                # ------------------------------
                # Temperatura
                # ------------------------------

                temperatura_final = (
                    ler_temperatura()
                )


                # ------------------------------
                # Cria registro
                # ------------------------------

                sessao = {

                    "numero":
                        numero_sessao,

                    "duracao":
                        duracao,

                    "temperatura":
                        temperatura_final,

                    "energia_solar":
                        energia_solar,

                    "tempo_recarga":
                        tempo_recarga,

                    "energia_utilizada":
                        energia_utilizada,

                    "resultado":
                        motivo_sessao
                }


                # ------------------------------
                # Salva no histórico
                # ------------------------------

                historico_sessoes.append(
                    sessao
                )


                # ------------------------------
                # Finaliza sessão
                # ------------------------------

                sessao_ativa = False


                # ==================================
                # RESULTADO
                # ==================================

                print()

                print("========================================")

                print("          SESSAO FINALIZADA")

                print("========================================")


                print(
                    "Sessao:",
                    numero_sessao
                )


                print(
                    "Duracao: %.1f segundos"
                    % duracao
                )


                print(
                    "Temperatura: %.1f C"
                    % temperatura_final
                )


                print(
                    "Energia solar: %.1f kW"
                    % energia_solar
                )


                print(
                    "Tempo de recarga: %.1f segundos"
                    % tempo_recarga
                )


                print(
                    "Energia utilizada: %.4f kWh"
                    % energia_utilizada
                )


                print(
                    "Resultado:",
                    motivo_sessao
                )


                print("========================================")


                # ==================================
                # CSV
                # ==================================

                print()

                print("CSV:")


                print(
                    "%d;%.1f;%.1f;%.1f;%.4f;%s"
                    % (

                        numero_sessao,

                        duracao,

                        temperatura_final,

                        energia_solar,

                        energia_utilizada,

                        motivo_sessao
                    )
                )


                print()


                # Prepara para próxima sessão
                motivo_sessao = "RECARGA NORMAL"


        time.sleep(0.2)


    ultimo_veiculo = estado_veiculo


    # ======================================
    # BOTÃO +
    # ======================================

    estado_mais = botao_mais.value()


    if estado_mais == 0 and ultimo_mais == 1:

        energia_solar += 0.5


        if energia_solar > 6.0:

            energia_solar = 6.0


        print()

        print(
            "ENERGIA SOLAR AUMENTADA:",
            energia_solar,
            "kW"
        )


        time.sleep(0.2)


    ultimo_mais = estado_mais


    # ======================================
    # BOTÃO -
    # ======================================

    estado_menos = botao_menos.value()


    if estado_menos == 0 and ultimo_menos == 1:

        energia_solar -= 0.5


        if energia_solar < 0.0:

            energia_solar = 0.0


        print()

        print(
            "ENERGIA SOLAR REDUZIDA:",
            energia_solar,
            "kW"
        )


        time.sleep(0.2)


    ultimo_menos = estado_menos


    # ======================================
    # LEITURA DO SENSOR
    # ======================================

    temperatura = ler_temperatura()


    # ======================================
    # DECISÃO AUTOMÁTICA
    # ======================================


    # --------------------------------------
    # VEÍCULO OFF
    # --------------------------------------

    if not veiculo_conectado:

        status = "VEICULO OFF"

        led_recarga.value(0)


        mostrar_lcd(
            "VEICULO OFF",
            "AGUARDANDO..."
        )


    # --------------------------------------
    # TEMPERATURA ALTA
    # --------------------------------------

    elif temperatura > TEMPERATURA_MAXIMA:

        status = "TEMP. ALTA"

        led_recarga.value(0)

        motivo_sessao = "TEMPERATURA ALTA"


        mostrar_lcd(
            "TEMP. ALTA!",
            "RECARGA OFF"
        )


    # --------------------------------------
    # ENERGIA BAIXA
    # --------------------------------------

    elif energia_solar < ENERGIA_MINIMA:

        status = "ENERGIA BAIXA"

        led_recarga.value(0)

        motivo_sessao = "ENERGIA BAIXA"


        mostrar_lcd(
            "ENERGIA BAIXA",
            "RECARGA OFF"
        )


    # --------------------------------------
    # RECARGA ATIVA
    # --------------------------------------

    else:

        status = "RECARGA ATIVA"

        led_recarga.value(1)


        # Só altera para normal quando
        # realmente existe energia suficiente

        motivo_sessao = "RECARGA NORMAL"


        mostrar_lcd(
            "SOL: %.1f kW"
            % energia_solar,

            "RECARGA: ATIVA"
        )


        # Acumula tempo somente enquanto
        # a recarga estiver ativa

        if sessao_ativa:

            tempo_recarga += 0.5


    # ======================================
    # MONITORAMENTO
    # ======================================

    print("----------------------------------------")

    print(
        "       CHARGEGRID INTELLIGENCE"
    )

    print("----------------------------------------")


    print(
        "Temperatura: %.1f C"
        % temperatura
    )


    print(
        "Energia solar: %.1f kW"
        % energia_solar
    )


    if veiculo_conectado:

        print(
            "Veiculo: CONECTADO"
        )

    else:

        print(
            "Veiculo: DESCONECTADO"
        )


    if sessao_ativa:

        print(
            "Sessao:",
            numero_sessao
        )


        print(
            "Tempo recarga: %.1f s"
            % tempo_recarga
        )


    print(
        "STATUS:",
        status
    )


    print("----------------------------------------")


    time.sleep(0.5)