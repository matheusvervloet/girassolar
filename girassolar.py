#importando as bibliotecas
import mraa
import time
import sys, signal, atexit
import pyupm_i2clcd as upmlcd
import pyupm_grove
import pyupm_uln200xa as upmstepper
DIR_CW = upmstepper.ULN200XA.DIR_CW
DIR_CCW = upmstepper.ULN200XA.DIR_CCW

# Registro do exit handler, que nos permite dar release no stepper motor ao parar a execucao
def exitHandler():
        stepper.release()
        print "Exiting"
        sys.exit(0)
atexit.register(exitHandler)

######################################################
##### Funcoes utilizadas pelo programa principal #####
######################################################

# Seleciona a linha (primeira ou segunda) e escreve o texto desejado
def writeLcd(text, line):
        lcd.setCursor(line, 0)
        lcd.write(text)

# Salva dados no arquivo de dados selecionado.
# Arquivos de dados sao utilizados para que as informacoes sejam lidas pelo painel web (freeboard)
# Temos um arquivo para cada informacao (painel, sensor, posicao e status)
def writeData(filename, data):
        f = open(filename, 'w')
        f.write(str(data))
        f.close()

# Controla os passos do stepper, nao permitindo se passar de um certo limite
def step(steps):
        global position # Position e uma variavel que monitora quantos steps ja foram dados para que direcao
        writeData('position.data', position) # Salva posicao atual no arquivo de dados
        if(position < 15 and steps >= 0): # Steps positivos sao no sentido horario
                stepper.setDirection(DIR_CW)
                stepper.stepperSteps(steps)
                position += steps
                time.sleep(0.2)
        elif(position > -15 and steps < 0): # Steps negativos sao no sentido anti-horario
                stepper.setDirection(DIR_CCW)
                stepper.stepperSteps(-steps)
                position += steps
                time.sleep(0.2)
        else:
            print 'Reached maximum steps (' + str(position) + ').'

# Faz a leitura do painel solar, exibindo no LCD
def readPanel():
        reading = round(solarPanel.read()/205.0, 2) # Funciona como um map(), converte de 0-1024 para uma voltagem
        writeLcd('Panel: ' + str(reading) + 'V ', 1)
        writeData('panel.data', reading) # Salva leitura do painel no arquivo de dados
        return reading

# Faz a leitura do sensor de luz, exibindo no LCD
def readLight():
        reading = lightSensor.read()
        writeLcd('Light: ' + str(reading), 0)
        writeData('light.data', reading) # Salva a leitura do sensor no arquivo de dados
        readPanel() # Realiza a leitura do painel sempre que ler o sensor de luz
        return reading

# Deixa o sistema em modo standby, liberando o stepper, desligando o display e o rele
def standby():
        global relay, lcd, stepper, position
        relay.off()
        lcd.clear()
        lcd.setColor(0, 0, 0) # Seta o display para cor preta, que equivale a apagar o backlight
        step(-position)
        stepper.release()
        writeData('status.data', 'off')

# Retorna do standby, ligando o display e o rele
def activate():
        global relay, lcd
        relay.on()
        lcd.setColor(255, 255, 255)
        writeData('status.data', 'on')

# Interrupcao usada pelo botao que coloca o sistema em standby
def buttonISR(arg):
        global mode
        if(mode == 0):
                mode = 1
        else:
                mode = 0

###################################################################################
##### Inicializacao dos sensores, atuadores e variaveis utilizadas no sistema #####
###################################################################################

# Inicializacao do LCD
lcd = upmlcd.Jhd1313m1(0, 0x3E, 0x62)
lcd.setColor(0, 0, 0)

# Inicializacao do rele
relay = pyupm_grove.GroveRelay(6)

# Inicializacao do sensor de luz como uma entrada analogica
lightSensor = mraa.Aio(3)

# Inicializacao do painel solar como uma entrada analogica
solarPanel = mraa.Aio(0)

# Inicializacao do botao como uma entrada digital, que tem uma interrupcao associada
button = mraa.Gpio(4)
button.dir(mraa.DIR_IN)
button.isr(mraa.EDGE_FALLING, buttonISR, buttonISR)

# Inicializacao do motor de passo
stepper = upmstepper.ULN200XA(96, 8, 9, 10, 11)
stepper.setSpeed(30) #30 rpm

# Variavel que indica se o sistema esta ativo(1) ou em standby (0)
mode = 0
# Variavel que conta os passos dados pelo motor de passo
position = 0

while(1):
        # Verifica se o botao de standby foi pressionado, caso sim, mantem o sistema em espera
        if(mode == 0):
                standby() # Chama funcao de standby para desligar componentes
                while(mode == 0):
                        time.sleep(0.1)

        # Reativa o sistema assim que o botao for pressionado novamente
        activate()
        firstValue = readLight()

        # Enquanto a leitura do sensor de luz nao variar, ficamos parados
        reading = readLight()
        while(reading > firstValue - 5 and reading < firstValue + 5 and mode == 1 ):
            reading = readLight()
            time.sleep(0.5)

        # Busca a posicao da luz
        stable = False
        while(not stable and mode == 1): # Se o modo mudar para standby, quebramos a rotina de busca
            reading = readLight() # Leitura na posicao atual

            step(3) # Gira para um lado e faz uma leitura
            clockReading = readLight()
            step(-6) # Gira para o outro e faz mais uma leitura
            counterReading = readLight()

            if(clockReading > reading + 3): # Se a leitura do sentido horario for maior que a atual, vamos para aquele lado
                step(6)
            elif(counterReading < reading + 3): # Se a leitura do sentido anti horario nao for maior que a atual, voltamos para onde estavamos e indicamos estabilidade
                step(3)
                stable = True
