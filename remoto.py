#!/usr/bin/env python3
# vim: set foldenable:foldmethod=marker:sts=4:ts=8:sw=4:
# License Info                                                           {{{1
# Controle Remoto para Receiver Denon por CLI
# Copyright (C) 2023  Jose Mauricio Batista Alves Jr
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Importações de módulo                                                         {{{1
import sys
import socket
import argparse
from time import sleep

# Informações de conexão padrão                                                {{{1
# ex.
# default_ip = '192.168.1.100'
default_ip = ''
default_port = '23'

# Comandos padrão                                                       {{{1
default_subparser = 'power'
default_power_cmd = 'status'
default_volume_cmd = 'status'
default_mute_cmd = 'toggle'
default_source_cmd = 'status'
default_mode_cmd = 'status'

# Classe Denon                                                            {{{1
class Denon:

    #### Dicionários ####                                               {{{2
    # Códigos de Comando                                                      {{{3
    codes = {'status': 'status',
             'toggle': 'toggle',
             'on': 'PWON',
             'off': 'PWSTANDBY',
             'up': 'MVUP',
             'down': 'MVDOWN',
             'mute': 'MUON',
             'unmute': 'MUOFF',
             'bluetooth': 'SIBT',
             'tuner': 'SITUNER',
             'aux': 'SIAUX1',
             'iradio': 'SIIRADIO',
             'mplayer': 'SIMPLAY',
             'game': 'SIGAME',
             'dvd': 'SIDVD',
             'bluray': 'SIBD',
             'favorites': 'SIFAVORITES',
             'sirius': 'SISIRIUSXM',
             'pandora': 'SIPANDORA',
             'ipod': 'SIUSB/IPOD',
             'dolby': 'MSDOLBY DIGITAL',
             'stereo': 'MSSTEREO',
             'mstereo': 'MSMCH STEREO',
             'direct': 'MSDIRECT',
             'rock': 'MSROCK ARENA',
             'jazz': 'MSJAZZ CLUB'}

    # Códigos de Comando: Status                                                {{{3
    scodes = {'power': 'PW?',
              'volume': 'MV?',
              'mute': 'MU?',
              'source': 'SI?',
              'mode': 'MS?'}

    # Nomes de entrada: Source                                             {{{3
    src_names = {'BT': 'Bluetooth',
                 'TUNER': 'Tuner',
                 'AUX1': 'Aux',
                 'IRADIO': 'Internet Radio',
                 'MPLAY': 'Media Player',
                 'GAME': 'Game',
                 'DVD': 'DVD',
                 'BD': 'BluRay',
                 'FAVORITES': 'Favorites',
                 'SIRIUSXM': 'Sirius XM',
                 'USB/IPOD': 'iPod'}

    # Nomes de modo: Sound                                                    {{{3
    mode_names = {'DOLBY SURROUND': 'Dolby',
                  'STEREO': 'Stereo',
                  'MCH STEREO': 'MStereo',
                  'DIRECT': 'Direct',
                  'ROCK ARENA': 'Rock',
                  'JAZZ CLUB': 'Jazz'}

    # Mensagem: Labels                                                     {{{3
    labels = {'power': 'Power State:',
              'volume': 'Volume Level:',
              'mute': 'Mute State:',
              'source': 'Source Input:',
              'mode': 'Sound Mode:'}

    # Mensagem: Error                                                     {{{3
    errors = {1: 'Erro ao analisar argumentos',
              2: 'Erro ao conectar ao receptor',
              3: 'Erro ao receber status',
              4: 'Erro ao enviar comando'}

    # Inicializar Objeto Denon                                            {{{2
    def __init__(self, args):
        '''
        Inicialize o objeto Denon.
         args: é um objeto Namespace derivado de Argparse
         contendo os seguintes atributos:
             address: é o endereço IPv4 do AVR(Receiver).
             port: é a porta para se comunicar.
             cmd: é o tipo de comando a ser executado.
             action: é a ação de comando a ser executada.
        '''
        # Informações de conexão e comandos solicitados
        self.address = args.address
        self.port = args.port
        self.cmd = args.cmd
        self.action = args.action

    # Validar endereço IP                                                {{{2
    def validate_ip(self):
        '''
        Teste se self.address é um endereço IPv4 válido
         e retorne True/False.
        '''
        a = self.address.split('.')
        if len(a) != 4:
            return False
        for x in a:
            if not x.isdigit():
                return False
            i = int(x)
            if i < 0 or i > 255:
                return False
        return True

    # Validar informações de conexão                                    {{{2
    def validate_connection_info(self, interactive=False):
        '''
        Teste se os dados de conexão necessários estão presentes e
        retornar True/False. Se não estiver e o script estiver sendo
        execute interativamente e, em seguida, solicite-o.
        interactive: se definido, o script está sendo executado interativamente
        '''
        if self.address == '':
            print('O endereço IP não está definido')
            if interactive:
                self.address = input('Digite o endereço IP: ')
                return self.validate_connection_info(True)
        elif self.port == '':
            print('A porta não está definida')
            if interactive:
                self.port = input('Entrar na porta: ')
                return self.validate_connection_info(True)
        elif not self.validate_ip():
            print('O endereço IP é inválido')
            if interactive:
                self.address = input('Digite o endereço IP: ')
                return self.validate_connection_info(True)
        elif not self.port.isdigit():
            print('A porta é inválida')
            if interactive:
                self.port = input('Entrar na porta: ')
                return self.validate_connection_info(True)
        return True

    # Conectar ao receptor                                              {{{2
    def connect(self):
        '''
        Crie uma conexão de soquete e tente se conectar a ela.
        Retorna o objeto de soquete, a menos que uma exceção seja lançada.
        '''
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        try:
            sock.connect((self.address, int(self.port)))
        except Exception as e:
            print(e)
        else:
            return sock

    # Desconectar do receptor                                           {{{2
    def disconnect(self, sock):
        '''Desligar e fechar a conexão do soquete.'''
        try:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        except Exception as e:
            print(e)

    # Send command code (low level)                                      {{{2
    def send(self, sock, cmd):
        '''Tente enviar comando via socket e retornar True/False.'''
        try:
            sock.send('{}\r'.format(cmd).encode('utf-8'))
        except Exception as e:
            print(e)
        else:
            return True
        return False

    # Receber resposta de comando de status (low level)                        {{{2
    def recv_status(self, sock, cmd, receive_only=False):
        '''Tente enviar um comando de status e retorne a resposta.'''
        resp=''
        try:
            if not receive_only:
                while resp[:2] != cmd[:2] or resp[:5] == 'MVMAX':
                    sock.send('{}\r'.format(cmd).encode('utf-8'))
                    resp = str(sock.recv(32), 'utf-8')
            else:
                resp = str(sock.recv(32), 'utf-8')
        except Exception as e:
            print(e)
        else:
            return self.split(resp)
        return self.errors[3]

    # Dividir uma resposta por retorno                                {{{2
    def split(self, r):
        '''Divida uma resposta em retornos e retorne a resposta correta'''
        x = r.rstrip().split('\r')
        if len(x) > 1:
            for i in x:
                if i in self.codes.values():
                    return i
        return x[0]

    # Alternar entre 2 comandos                                          {{{2
    def toggle(self, status, a, b):
        '''Compare status com a e retorne b se status for igual a a'''
        if status == a:
            return b
        return a

    # Enviar comando (usa send e recv_status)                           {{{2
    def send_command(self, sock, cmd, status_cmd):
        '''Envie um comando para o receiver e retorne a resposta.'''
        resp = self.recv_status(sock, status_cmd)
        if cmd != 'status' and cmd != resp and resp != self.errors[3]:
            pwr_cmd = False
            mute_cmd = False
            if status_cmd[:2] == "PW":
                pwr_cmd = True
                toggle_types = ['on', 'off']
                power_state = resp
            elif status_cmd[:2] == "MU":
                mute_cmd = True
                toggle_types = ['mute', 'unmute']
                power_state = self.recv_status(sock, self.scodes['power'])
            else:
                power_state = self.recv_status(sock, self.scodes['power'])

            if pwr_cmd or mute_cmd:
                if cmd == 'toggle':
                    cmd  = self.toggle(resp,
                                       self.codes[toggle_types[0]],
                                       self.codes[toggle_types[1]])

            if pwr_cmd or power_state == self.codes['on']:
                if self.send(sock, cmd):
                    return self.recv_status(sock, status_cmd)
                else:
                    return self.errors[4]
            else:
                return power_state
        return resp

    # Analisar comando                                                      {{{2
    def parse_command(self, sock):
        '''
        Analise self.cmd e envie o comando.
        Retorna uma tupla de rótulo de mensagem e resposta.
        '''
        if self.action not in self.codes:
            cmd = '{}{:02}'.format(self.scodes[self.cmd][:2],
                                   int(self.action))
            return (self.labels[self.cmd],
                    self.send_command(sock,
                                      cmd,
                                      self.scodes[self.cmd]))
        return (self.labels[self.cmd],
                self.send_command(sock,
                                  self.codes[self.action],
                                  self.scodes[self.cmd]))

    # Analisar resposta                                                     {{{2
    def parse_response(self, msg, resp):
        '''
        Formatar rótulo de mensagem e resposta para saída para stdout
        e retornar a string formatada.
        '''
        if resp in self.errors.values():
            print('[{}] {}'.format(self.address, resp))
            sys.exit(1)

        resp = resp[2:]
        if self.cmd == 'volume':
            if len(resp) == 3:
                resp = '{}.{}'.format(int(resp[:2]), int(resp[2:]))
            elif resp.isdigit():
                resp = int(resp)
        elif self.cmd == 'source':
            if resp in self.src_names:
                resp = self.src_names[resp]
        elif self.cmd == 'mode':
            if resp in self.mode_names:
                resp = self.mode_names[resp]
            else:
                resp = resp.lower().capitalize()
        if resp == 'STANDBY':
            msg = self.labels['power']
        return '[{}] {} {}'.format(self.address, msg, resp)

    # Método principal da classe Denon                                         {{{2
    def main(self):
        '''Iniciar a instância do controlador.'''
        valid = False
        try:
            if sys.stdin.isatty(): # Verifique se está executando interativamente
                while not valid:
                    valid = self.validate_connection_info(True)
            else:
                valid = self.validate_connection_info()
            if valid:
                #print('Controle Remoto Receiver Denon')
                # Conectar ao receiver
                sock = self.connect()
                if sock is not None:
                    # Analisar e executar o comando
                    # Print mensagem com resposta analisada
                    print(self.parse_response(*self.parse_command(sock)))
                    self.disconnect(sock)
                else:
                    print('[{}] {}'.format(sock, self.errors[2]))
                    sys.exit(1)
        except KeyboardInterrupt:
            print('')
            sys.exit(130)


# Definir Default do Subparser                                                  {{{1
def set_default_subparser(self, name, args=None):
    '''
    Seleção de subanalisador padrão.
    Chamada após a configuração, logo antes de parse_args()
    name: é o nome do subparser a ser chamado por padrão
    args: if set é a lista de argumentos entregue a parse_args()

    Testado com 2.7, 3.2, 3.3, 3.4, 3.6, 3.7, 3.8, 3.9, 3.11
    Funciona com 2.6 assumindo que o argparse está instalado
    '''
    subparser_found = False
    for arg in sys.argv[1:]:
        if arg in ['-h', '--help']:  # ajuda global se nenhum subparser
            break
        if arg in ['-v', '--version']: # versão se não houver subparser
            break
        if arg in ['-a', '--address']: # endereço requer subparser
            break
        if arg in ['-p', '--port']: # porta requer subparser
            break
    else:
        for x in self._subparsers._actions:
            if not isinstance(x, argparse._SubParsersAction):
                continue
            for sp_name in x._name_parser_map.keys():
                if sp_name in sys.argv[1:]:
                    subparser_found = True
                if sp_name == name: # Verifique a existência de padrão parser
                    existing_default = True
        if not subparser_found:
            # Inserir padrão na primeira posição, isso implica que não
            # opções globais sem um sub_parsers especificado
            if args is None:
                sys.argv.insert(1, name)
            else:
                args.insert(0, name)


# Configurar o ArgParser                                                      {{{1
argparse.ArgumentParser.set_default_subparser = set_default_subparser
parser = argparse.ArgumentParser(prog='remoto',
                                 description='Controle Remoro Receiver Denon',
                                 add_help=False)

# Adicionar argumento de ajuda                                                      {{{2
parser.add_argument(
    '--help', '-h',
    action='help',
    default=argparse.SUPPRESS,
    help='Show this help message and exit.')

# Adicionar argumento de versão                                                   {{{2
parser.add_argument(
    '--version', '-v',
    action='version',
    version='%(prog)s v0.1beta Copyright (C) 2019 Barry Van Deerlin')

# Adicionar argumento de endereço IP                                                {{{2
parser.add_argument(
    '--address', '-a',
    action='store',
    dest='address',
    default=default_ip,
    help='IP Address of the AVR to connect to.')

# Adicionar argumento de porta                                                      {{{2
parser.add_argument(
    '--port', '-p',
    action='store',
    dest='port',
    default=default_port,
    help='Port to connect on')

# Adicionar subparsers                                                         {{{2
subparser = parser.add_subparsers(dest='cmd')
# Adicionar subparsers de power                                                   {{{3
subparser_cmd = subparser.add_parser('power')
subparser_cmd.add_argument(
    'action',
    type=str.lower,
    action='store',
    default=default_power_cmd,
    nargs='?',
    choices=['status', 'on', 'off', 'toggle'])

# Adicionar subparsers de volume                                                   {{{3
subparser_cmd = subparser.add_parser('volume')
volume_choices = list(range(91))
for i, choice in enumerate(volume_choices):
    volume_choices[i] = str(choice)

volume_choices.insert(0, 'down')
volume_choices.insert(0, 'up')
volume_choices.insert(0, 'status')

subparser_cmd.add_argument(
    'action',
    type=str.lower,
    action='store',
    default=default_volume_cmd,
    nargs='?',
    choices=volume_choices,
    metavar='{status, up, down, [0-90]}')

# Adicionar mute subparser                                                     {{{3
subparser_cmd = subparser.add_parser('mute')
subparser_cmd.add_argument(
    'action',
    type=str.lower,
    action='store',
    default=default_mute_cmd,
    nargs='?',
    choices=['status', 'toggle'])

# Adicioanar source subparser                                                   {{{3
subparser_cmd = subparser.add_parser('source')
subparser_cmd.add_argument(
    'action',
    type=str.lower,
    action='store',
    default=default_source_cmd,
    nargs='?',
    choices=['status',
             'bluetooth',
             'tuner',
             'aux',
             'iradio',
             'mplayer',
             'game',
             'dvd',
             'bluray',
             'favorites',
             'siriusxm',
             'pandora',
             'ipod'])

# Adicioanar mode subparser                                                     {{{3
subparser_cmd = subparser.add_parser('mode')
subparser_cmd.add_argument(
    'action',
    type=str.lower,
    action='store',
    default=default_mode_cmd,
    nargs='?',
    choices=['status',
             'dolby',
             'stereo',
             'mstereo',
             'direct',
             'rock',
             'jazz'])

# Defina power como o subparser padrão e analise os argumentos                      {{{2
parser.set_default_subparser(default_subparser)
args = parser.parse_args()
if args.cmd is None or args.action is None:
            print(Denon.errors[1])
            parser.print_help()
            sys.exit(2)

# Inicializar e executar o controlador                                          {{{1
controller = Denon(args)
controller.main()
