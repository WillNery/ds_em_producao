import pickle
import pandas as pd
import xgboost as xgb
from xgboost import XGBRegressor
from flask import Flask, request, Response
from rossmann.Rossmann import Rossmann #import: é o nome da classe


#loading model
model = pickle.load( open('C:/Users/Will/repos/comunidadeds/ds_em_producao/api/handler.pkl', 'rb'))  

# inicializando a API
app = Flask(__name__)

#definição do endpoint
#toda vez que ele receber uma chamada via post, ele executa a primeira função embaixo dele
@app.route('/rossmann/predict', methods = ['POST'] ) # POST: envia algum dado depois de receber, não fica pedindo


def rossmann_predict():
    test_json = request.get_json()   #pega o json que vai ser enviado via API
    
    # if para a verificação se o dado chegou mesmo
    if test_json:
        if isinstance( test_json, dict ): #se for 1 linha de .json:
            test_raw = pd.DataFrame(test_json, index = [0]) 
        else: #se vierem varios .json concatenados
            test_raw = pd.DataFrame(test_json, columns = test_json[0].keys() )
            
        #Instantiate Rossmann class
        pipeline = Rossmann()
        
        # data cleaning
        df1 = pipeline.data_cleaning( test_raw )
        
        # feature engineering
        df2 = pipeline.feature_engineering( df1 )
        
        # data preparation
        df3 = pipeline.data_preparation( df2 )
        
        # prediction
        df_response = pipeline.get_prediction( model, test_raw, df3 )
        
        return df_response
    
    
        
    else:
        return Response( '{}', status = 200, mimetype = 'application/json' )
    
    
    
if __name__ == '__main__':
    app.run('127.0.0.1')
