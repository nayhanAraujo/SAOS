from contextlib import contextmanager
import firebird.driver as fbd

@contextmanager
def db_connection():
    try:
        con = fbd.connect(
            r'nayhan/3052:C:\Users\Nayhan.MEDWARE\Documents\PROJETOS AZURE\11 -AZURE - SISTEMA DE ABERTURA DE OS\SAOS\database\SAOS.FDB',
            user='SYSDBA',
            password='masterkey',
            charset='UTF8'
           
        )
        print("Conectado com sucesso ao banco de dados.")
        yield con
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise
    finally:
        try:
            con.close()
            print("Conexão com o banco de dados encerrada.")
        except:
            pass