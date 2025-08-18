import smtplib
from email.message import EmailMessage
import os

def enviar_email(sistema, tipo, nome, telefone, email_solicitante, descricao, caminho_anexo):
    msg = EmailMessage()
    msg['Subject'] = f'Nova Solicitação - {sistema}'
    msg['From'] = 'nayhanbsb@gmail.com'
    msg['To'] = 'nayhanzimmm@gmail.com'

    corpo = f'''
    Sistema: {sistema}
    Tipo: {tipo}
    Nome: {nome}
    Telefone: {telefone}
    Email: {email_solicitante}

    Descrição:
    {descricao}
    '''
    msg.set_content(corpo)

    if caminho_anexo and os.path.exists(caminho_anexo):
        with open(caminho_anexo, 'rb') as f:
            anexo = f.read()
        msg.add_attachment(anexo, maintype='application', subtype='octet-stream', filename=os.path.basename(caminho_anexo))

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('nayhanbsb@gmail.com', 'anby stye adol fccr')
        smtp.send_message(msg)
