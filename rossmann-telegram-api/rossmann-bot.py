# This Python file uses the following encoding: utf-8

import os 
import pandas as pd
import json
import requests
from flask import Flask, request, Response


#constants
TOKEN = '5123866572:AAEwgTTFPatkhE-4qmMBVdkqpv5yqDo2OY8'

#info about the bot
#https://api.telegram.org/bot5123866572:AAEwgTTFPatkhE-4qmMBVdkqpv5yqDo2OY8/getMe

#get updates
#https://api.telegram.org/bot5123866572:AAEwgTTFPatkhE-4qmMBVdkqpv5yqDo2OY8/getUpdates

#Webhook: tem que ser setado toda a vez eu gerar a url nova no local host
#https://api.telegram.org/bot5123866572:AAEwgTTFPatkhE-4qmMBVdkqpv5yqDo2OY8/setWebhook?url=https://54262412b69680.lhrtunnel.link

#Webhook Heroku: 
#https://api.telegram.org/bot5123866572:AAEwgTTFPatkhE-4qmMBVdkqpv5yqDo2OY8/setWebhook?url=https://rossmann-telegram-botwill.herokuapp.com/


#send message 
#https://api.telegram.org/bot5123866572:AAEwgTTFPatkhE-4qmMBVdkqpv5yqDo2OY8/sendMessage?chat_id=182917810&text=Hi Will

#local host para conexão: ssh -R 80:localhost:5000 localhost.run

# envia a mensagem
def send_message( chat_id, text ):
    url = 'https://api.telegram.org/bot{}/'.format( TOKEN )
    url = url + 'sendMessage?chat_id={}'.format(chat_id)
    
    r = requests.post(url, json={'text': text })
    print('Status Code {}'.format(r.status_code))

    return None


# carrega o dataset das casas
def load_dataset( store_id ):
    #loading test dataset
    df10 = pd.read_csv('test.csv')
    df_store_raw = pd.read_csv('store.csv')

    # merge test dataset + store
    df_test = pd.merge( df10, df_store_raw, how = 'left', on = 'Store' ) 

    #choose store for prediction
    # to put various stores: [df_test['Store'].isin([24, 12, 11, etc]) ]
    df_test = df_test[df_test['Store'] == store_id ]

    if not df_test.empty:
        #remove closed days
        df_test = df_test[df_test['Open'] != 0 ]
        df_test = df_test[~df_test['Open'].isnull() ]
        df_test = df_test.drop('Id', axis = 1)

        #convert dataframe to .json
        data = json.dumps( df_test.to_dict( orient = 'records') )

    else:
        data = 'error'

    return data


# aplica o modelo da nuvem no dataset    
def predict( data ):

    #API Call
    url = 'https://modelo-testador-heroku.herokuapp.com/rossmann/predict' 
    header = {'Content-type': 'application/json'}   #tipo de requisição
    data   = data

    r = requests.post( url, data = data, headers = header)
    print('Status Code {}'.format( r.status_code ) )

    d1 = pd.DataFrame (r.json(), columns = r.json()[0].keys() )

    return d1

# analise da mensagem
def parse_message( message ):

    chat_id = message['message']['chat']['id']
    store_id = message['message']['text']    
    # para tirar a barra que vem com a mensagem do telegram
    store_id = store_id.replace('/','')

    try: 
        store_id = int( store_id )


    except ValueError: 
        store_id = 'error '

    return chat_id, store_id


#API initialize    
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])

def index():

    if request.method == 'POST':
        message = request.get_json()
        chat_id, store_id = parse_message( message ) 
        
        if store_id != 'error':
            # loading data
            data = load_dataset( store_id )

            if data != 'error':

                # prediction
                d1 = predict( data )

                # calculation
                d2 = d1[['store', 'prediction']].groupby('store').sum().reset_index()

                # send message
                msg = 'Store Number {} will sell R${:,.2f} in the next 6 weeks'.format(
                         d2['store'].values[0],
                         d2['prediction'].values[0] )
                
                send_message(chat_id, msg)
                return Response('Ok', status = 200)
                

            else: 
                send_message (chat_id, 'Store Not Available' ) 
                return Response ( 'Ok', status = 200 )


        else:
            send_message( chat_id, 'Store ID is Wrong' )        
            return Response( 'Ok', status = 200 )


    else:
        return '<h1> Rossmann Telegram BOT </h1>'


if __name__ == '__main__':
    port = os.environ.get( 'PORT', 5000 )
    app.run( host= '0.0.0.0', port = port )

    

