import os
import requests
import traceback
import json
from flask import Flask, request, render_template
from watson_developer_cloud import ConversationV1
import psycopg2 as postgreSQL
import datetime
from flask_cors import CORS
from watson_developer_cloud import PersonalityInsightsV3

def create_msg(vetor):
    result = ''
    for item in vetor:
        result += (item + '\n')
    return result

personality_insights = PersonalityInsightsV3(
    version='2016-10-20',
    username='64e0eb53-ae81-4ca8-b786-1dc731ff4f2e',
    password='V2b5F8T7qfbR'
)

workspace_id = '2274717e-75d7-41b1-bc46-d788f600e25f'
conversation = ConversationV1(username='406557dc-8baa-4543-bad8-d613cc7e8840', password='pDTcuJyUFOkr', version='2017-05-26')
token = 'EAAO1Xba6Y2oBAKWRLwSqWu2PX5sPEcCvW0u3FNAI4kZBcseb8FGnd1FzRt9d0b4XDvkVXuY29E9s4x8XaG2Sgtm2bUBZBPa9bgYQIHbcTMV1hfvA9voTHAE6lQt6jIunWz72ugmnR5dWMvIRHqsgM0zUuf0m1iVTriP2lysV4gptoVz5r2'
token_frase = "O Alan tem que fazer o CRUD até terça."
hostname = 'localhost'
username = 'postgres'
password = '@Kevin14Silva'
port=5432
database = 'sophia'
conn = postgreSQL.connect(host=hostname, user=username, password=password, dbname=database, port=port)
cur = conn.cursor()

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        try:
            data = json.loads(request.data.decode())

            sender = data['entry'][0]['messaging'][0]['sender']['id']
            texto_recebido = None
            if sender == '970999103039765' or 'message' not in data['entry'][0]['messaging'][0]:
               if "entry" in data:
                  if len(data["entry"]) > 0:
                     if "messaging" in data["entry"][0]:
                        if len(data["entry"][0]["messaging"]) > 0:
                           if "postback" in data["entry"][0]["messaging"][0]:
                              if "payload" in data["entry"][0]["messaging"][0]["postback"]:
                                 if data["entry"][0]["messaging"][0]["postback"]["payload"] == "GET_BOTAO_INICIAR_PAYLOAD":
                                    texto_recebido = data["entry"][0]["messaging"][0]["postback"]["payload"]
               if texto_recebido == None:
                  return '{}'
            else:
               texto_recebido = data['entry'][0]['messaging'][0]['message']['text']

            contexto = {}
            query = " select context_ibm_conversation from dialogo where pid_id_usuario_pagina = %s "
            cur.execute(query, (sender,))
            lista_dados = cur.fetchall()
            for item in lista_dados:
               contexto = item[0]

            if contexto == {}:
               cur.execute("insert into dialogo (pid_id_usuario_pagina, context_ibm_conversation) values(%s, %s)", (sender, json.dumps(contexto),))
               conn.commit()

            saida = conversation.message(workspace_id=workspace_id,
                                         message_input={'text': texto_recebido},
                                         context=contexto)

            try:
                if saida['output']['nodes_visited'][0] == 'fim':

                    exatas = 0
                    humanas = 0
                    biologicas = 0

                    stringAnalise = str(saida['context']['pUm_animal'])
                    stringAnalise += ' ' + str(saida['context']['pDois_filme'])
                    stringAnalise += ' ' + str(saida['context']['pTres_disciplinas'])
                    stringAnalise += ' ' + str(saida['context']['pQuatro_competicao'])
                    stringAnalise += ' ' + str(saida['context']['pCinco_desejo'])
                    stringAnalise += ' ' + str(saida['context']['pSeis_preferencias'])
                    stringAnalise += ' ' + str(saida['context']['pSete_herois'])
                    stringAnalise += ' ' + str(saida['context']['pOito_hvagas'])
                    stringAnalise += ' ' + str(saida['context']['pNove_texto'])
                    stringAnalise += ' ' + str(stringAnalise)

                    try:
                        profile = personality_insights.profile(stringAnalise, content_type='text/plain',
                                                               accept='application/json', accept_language='pt-br',
                                                               raw_scores=False,
                                                               consumption_preferences=False, csv_headers=False)
                    except:
                        profile = 0

                    try:
                        for i in profile['personality']:
                            for j in i['children']:
                                if j['name'] == "Desejo de aventura":
                                    if j['percentile'] >= 0.4:
                                        exatas += 1

                                if j['name'] == "Interesses artísticos":
                                    if j['percentile'] >= 0.4:
                                        humanas += 1

                                if j['name'] == "Emotividade":
                                    if j['percentile'] >= 0.4:
                                        humanas += 1

                                if j['name'] == "Imaginação":
                                    if j['percentile'] >= 0.4:
                                        humanas += 1
                                        exatas += 1

                                if j['name'] == "Intelecto":
                                    if j['percentile'] >= 0.4:
                                        humanas += 1

                                if j['name'] == "Desafio à autoridade":
                                    if j['percentile'] >= 0.4:
                                        humanas += 1
                                        exatas += 1

                                if j['name'] == "Esforço para realização":
                                    if j['percentile'] >= 0.4:
                                        humanas += 1
                                        exatas += 1
                                        biologicas += 1

                                if j['name'] == "Cautela":
                                    if j['percentile'] >= 0.4:
                                        biologicas += 1
                                        humanas += 1

                                if j['name'] == "Respeito":
                                    if j['percentile'] >= 0.4:
                                        humanas += 1
                                        exatas += 1
                                        biologicas += 1

                                if j['name'] == "Regularidade":
                                    if j['percentile'] >= 0.4:
                                        biologicas += 1

                                if j['name'] == "Autodisciplina":
                                    if j['percentile'] >= 0.4:
                                        biologicas += 1

                                if j['name'] == "Autoeficiência":
                                    if j['percentile'] >= 0.4:
                                        exatas += 1

                                if j['name'] == "Nível de atividade":
                                    if j['percentile'] >= 0.4:
                                        biologicas += 1
                                        exatas += 1

                                if j['name'] == "Assertividade":
                                    if j['percentile'] >= 0.4:
                                        biologicas += 1
                                        exatas += 1

                                if j['name'] == "Bom Humor":
                                    if j['percentile'] >= 0.4:
                                        humanas += 1

                                if j['name'] == "Busca de empolgação":
                                    if j['percentile'] >= 0.4:
                                        biologicas += 1
                                        exatas += 1

                                if j['name'] == "Extrovertido":
                                    if j['percentile'] >= 0.4:
                                        biologicas += 1
                                        humanas += 1

                                if j['name'] == "Gregarismo":
                                    if j['percentile'] >= 0.4:
                                        humanas += 1

                                if j['name'] == "Altruísmo":
                                    if j['percentile'] >= 0.4:
                                        exatas += 1

                                if j['name'] == "Cooperação":
                                    if j['percentile'] >= 0.4:
                                        biologicas += 1

                                if j['name'] == "Modéstia":
                                    if j['percentile'] >= 0.4:
                                        biologicas += 1
                                        exatas += 1

                                if j['name'] == "Determinação":
                                    if j['percentile'] >= 0.4:
                                        exatas += 1

                                if j['name'] == "Simpatia":
                                    if j['percentile'] >= 0.4:
                                        biologicas += 1
                                        exatas += 1

                                if j['name'] == "Confiança":
                                    if j['percentile'] >= 0.4:
                                        humanas += 1

                                if j['name'] == "Furioso":
                                    if j['percentile'] >= 0.4:
                                        biologicas += 1
                                        exatas += 1
                                        humanas += 1

                                if j['name'] == "Propenso a se preocupar":
                                    if j['percentile'] >= 0.4:
                                        exatas += 1

                                if j['name'] == "Melancolia":
                                    if j['percentile'] >= 0.4:
                                        biologicas += 1
                                        humanas += 1

                                if j['name'] == "Imoderação":
                                    if j['percentile'] >= 0.4:
                                        humanas += 1

                                if j['name'] == "Autoconsciência":
                                    if j['percentile'] >= 0.4:
                                        biologicas += 1
                                        exatas += 1

                                if j['name'] == "Suscetível ao stress":
                                    if j['percentile'] >= 0.4:
                                        exatas += 1
                    except:
                        pass

                    if biologicas > exatas and biologicas > humanas:
                        saida['output']['text'][0] = 'Muito bem!! Já tenho dados suficientes para analisar a sua personalidade . Parabéns! De acordo com a análise realizada você ficaria muito bem na área de Ciências Biológicas!!'

                    if exatas > biologicas and exatas > humanas:
                        saida['output']['text'][0] = 'Muito bem!! Já tenho dados suficientes para analisar a sua personalidade . Parabéns! De acordo com a análise realizada você ficaria muito bem na área de Exatas!!'

                    if humanas > biologicas and humanas > exatas:
                        saida['output']['text'][0] = 'Muito bem!! Já tenho dados suficientes para analisar a sua personalidade . Parabéns! De acordo com a análise realizada você ficaria muito bem na área de Humanas!!'

                    if humanas == 0 and biologicas == 0 and exatas == 0:
                        saida['output']['text'][0] = 'Desculpe, mas você não me contou muito sobre você! Precisa responder as perguntas com o maior nível de detalhe possível!'

            except:
                pass

            cur.execute("update dialogo set context_ibm_conversation = %s where pid_id_usuario_pagina = %s", (json.dumps(saida["context"]), sender,))
            conn.commit()


            if "links" in saida["output"]:
               payload = {'recipient': {'id': sender}, 'message': {'text': create_msg(saida["output"]["text"])}}
               r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + token, json=payload)
               for link in saida["output"]["links"]:
                  payload = {'recipient': {'id': sender}, 'message': {'text': link}}
                  r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + token, json=payload)

            else:
               payload = {'recipient': {'id': sender}, 'message': {'text': create_msg(saida["output"]["text"])}}
               r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + token, json=payload)
        except Exception as e:
            print('Erro: ' + str(e))
    elif request.method == 'GET':
        if request.args.get('hub.verify_token') == token_frase:
            return request.args.get('hub.challenge')
        return "Wrong Verify Token"
    return "Nothing"

if __name__ == '__main__':
    app.run(debug=True, host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8000)))
