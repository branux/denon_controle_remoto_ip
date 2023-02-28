# denon_controle_remoto_ip
Script em Python para controlar o recever Denon por IP

--      ###
--       ##
--       ##    ####    #####     ####    #####
--    #####   ##  ##   ##  ##   ##  ##   ##  ##
--   ##  ##   ######   ##  ##   ##  ##   ##  ##
--   ##  ##   ##       ##  ##   ##  ##   ##  ##
--    ######   #####   ##  ##    ####    ##  ##

Este script foi testado com receiver Denon AVR-4520CI e pode não ser compatível com outros receptores

Outros testes: AVR-S710W

Este script permite que você controle um Denon Audio Video Receiver a partir da linha de comando via rede.

Se você não deseja inserir um endereço IP toda vez que enviar um comando, abra o script em um editor de texto
e altere default_ip para o endereço IP do seu receptor.

```
# Default IP
# ex.
# default_ip = "192.168.1.100"
default_ip = ""
```

Lista de Comandos:

```
    power [-h] (status, on, off, toggle)
    volume [-h] (status, up, down, [0-90])
    mute [-h] (status, toggle)
    source [-h] status
                bluetooth
                tuner
                aux
                iradio
                mplayer
                game
                dvd
                bluray
                favorites
                siriusxm
                pandora
                ipod
    mode [-h] status
              dolby
              stereo
              mstereo
              direct
              rock
              jazz
```

Como usar:

```
# Template:
$ script primary_command secondary_command

# Exemplos: (Todos os exemplos neste bloco executam a mesma tarefa)
# Uso Padrão
# Se default_ip ou default_port não estiverem definidos no script, então
# vai perguntar por eles interativamente
$ /remote.py power status

# Uso quando default_ip e default_port NÃO SÃO definidos no script
# e você deseja executar o script de forma não interativa. Ou se você quiser
# use um ip ou porta diferente dos padrões.

$ /remote.py -a 192.168.0.100 -p 23 power status

# O comando secundário padrão para todos os comandos primários, exceto mute
# é status (o padrão do mute é alternado)
# 
$ /remote.py power

# O comando primário padrão se nenhum comando for dado é power
# -a e -p não funcionam com este método de chamada
# o roteiro. Você deve incluir o comando principal se desejar usá-los.
$ /remote.py
```
