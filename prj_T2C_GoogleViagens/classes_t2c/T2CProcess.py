from botcity.web import WebBot, Browser
from botcity.core import DesktopBot
from prj_T2C_GoogleViagens.classes_t2c.utils.T2CMaestro import T2CMaestro, LogLevel, ErrorType
from prj_T2C_GoogleViagens.classes_t2c.utils.T2CExceptions import BusinessRuleException
import datetime
from botcity.web import By
from clicknium import clicknium as cc, locator
from time import sleep
import sqlite3
from pathlib import Path
import re

#Classe responsável pelo processamento principal, necessário preencher com o seu código no método execute
class T2CProcess:
    """
    Classe responsável pelo processamento principal.

    Parâmetros:
    
    Retorna:
    """
    #Iniciando a classe, pedindo um dicionário config e o bot que vai ser usado e enviando uma exceção caso nenhum for informado
    def __init__(self, arg_dictConfig:dict, arg_clssMaestro:T2CMaestro, arg_botWebbot:WebBot=None, arg_botDesktopbot:DesktopBot=None):
        """
        Inicializa a classe T2CProcess.

        Parâmetros:
        - arg_dictConfig (dict): dicionário de configuração.
        - arg_clssMaestro (T2CMaestro): instância de T2CMaestro.
        - arg_botWebbot (WebBot): instância de WebBot (opcional, default=None)
        - arg_botDesktopbot (DesktopBot): instância de DesktopBot (opcional, default=None)

        Retorna:

        Raises:
        - Exception: caso nenhum bot seja fornecido.
        """
        if(arg_botWebbot is None and arg_botDesktopbot is None): raise Exception("Não foi possível inicializar a classe, forneça pelo menos um bot")
        else:
            self.var_botWebbot = arg_botWebbot
            self.var_botDesktopbot = arg_botDesktopbot
            self.var_dictConfig = arg_dictConfig
            self.var_clssMaestro = arg_clssMaestro
            
    #Parte principal do código, deve ser preenchida pelo desenvolvedor
    #Acesse o item a ser processado pelo arg_tplQueueItem
    def execute(self, arg_tplQueueItem:tuple):
        """
        Método principal para execução do código.

        Parâmetros:
        - arg_tplQueueItem (tuple): item da fila a ser processado.

        Retorna:
        """
        ROOT_DIR = Path(__file__).parent.parent.__str__()

        var_strNomePais  = str(arg_tplQueueItem[8]).strip()
        if(var_strNomePais=='Dominicana'): var_strNomePais = 'República Dominicana'
        if(var_strNomePais=='Emirados Árabes'): var_strNomePais = 'Emirados Árabes Unidos'
            
        var_strOrigem = str(arg_tplQueueItem[7]).strip()

        tab = cc.chrome.open('https://www.google.com/travel/explore')

        tab.find_element(locator.google.escolha_data).click()
        sleep(1)

        tab.find_element(locator.google.data_esp).click()
        sleep(1)

        tab.find_element(locator.google.text_partida).set_text('20/04/2024')
        cc.send_hotkey("{TAB}")
        sleep(1)

        tab.find_element(locator.google.text_volta).set_text('23/04/2024')
        cc.send_hotkey("{TAB}")
        cc.send_hotkey("{TAB}")
        sleep(3)

        tab.find_element(locator.google.combobox_de_onde).set_text(var_strOrigem)
        sleep(1)
        cc.send_hotkey("{TAB}")
        cc.send_hotkey("{TAB}")
        tab.find_element(locator.google.combobox_para_onde).set_text(var_strNomePais)
        sleep(1)

        #Repassa o nome do País para o locator
        variables = {"pais":var_strNomePais}
        tab.find_element(locator.google.option_frança,variables).click()
        sleep(5)

        #conecta a tabela do banco que irá receber os dados de cada passagem
        var_strPathToDb = ROOT_DIR + "\\resources\\sqlite\\banco_dados.db"
        var_csrCursor = sqlite3.connect(var_strPathToDb)

        #captura nome cidade e valor passagem para todos resultados
        index=1
        while(True):
            variables = {"index":str(index)}
            try:
                #captura os valores
                valor = tab.find_element(locator.google.passagens.valor_passagem,variables).get_text(timeout=5)
                valor = ''.join(re.findall(r'[\d\,]', valor))
                cidade = tab.find_element(locator.google.passagens.nome_cidade,variables).get_text(timeout=5)
                #envia valores à tabela
                var_strInsert = f"INSERT INTO tbl_Dados_Passagem (pais,cidade,valor) VALUES ('"+var_strNomePais+"','"+cidade+"','"+valor+"')"
                print(var_strInsert)
                var_csrCursor.execute(var_strInsert)
                var_csrCursor.commit()
            except:
                break
            index+=1
        
        tab.close()
        
        
        
