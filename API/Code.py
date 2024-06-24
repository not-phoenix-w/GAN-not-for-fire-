
import sys
from flask import Flask, jsonify, request
import requests  # for using API
import xml.etree.ElementTree as ET  # for parsing XML
import numpy as np  # for using pandas
import pandas as pd  # for using dataframes
import xml.etree.ElementTree as ET
import torch
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
# import torchvision.transforms as transforms
import pandas as pd
from ctgan import CTGAN
from torch import optim
import os


app = Flask(__name__, static_folder='projects')
@app.route('/start-gen/<uuid>', methods=['GET', 'POST'])
def start(uuid):
      try:
          tree = ET.parse(f'/projects/{uuid}/project.xml')
          root = tree.getroot()
          a=[]
          h=0
          pl=0
          n=0
          s=0
          fl=0
          cor = np.array([])
          for elem in root.findall('coordinates'):
            for subelem in elem:
              a.append(subelem.text.split(', '))
          for i in range(len(a)):
            for j in range(2):
              cor = np.append(cor, float(a[i][j]))
          for elem in root.findall('height'):
              h=elem.text
          for elem in root.findall('buildingarea'):
              s=elem.text
          for elem in root.findall('places'):
              pl=elem.text
          for elem in root.findall('floors'):
              fl=elem.text
          cor_df = cor
          cor_df = pd.DataFrame
          cor_df = pd.DataFrame({'x':cor[::2], 'y':cor[1::2]})
          dl=((cor[0]-cor[2])**2+(cor[1]-cor[3])**2)**(1/2)
          sh=((cor[2]-cor[4])**2+(cor[2]-cor[4])**2)**(1/2)
          def data_filter(data=pd.DataFrame, high=float, S2=float, meters=float, places=int):
              model_cord = data[(data[0] == high) & (S2-1000<data[34] < S2+1000) & (meters-5<data[36] < meters+5) & (data[38] == places)]
              slice_model = model.loc[:, model_cord.columns[38:]]
              slice_model = slice_model.transpose()
              slice_model.to_csv(r'/projects/{uuid}', header='model', index=None, sep=' ', mode='a')
          model = CTGAN.load('my_model.pkl')  # подгрузка матрицы
          new_data = model.sample(30000)  # генерация 300 сэмплов (300 строк с данными). ЧИСЛО ГЕНЕРАЦИЙ СТАВИТЬ КРАТНЫМ 3!!!
          data_filter(new_data, fl, s, h, pl)
          return jsonify(success=True)
      except Exception as e:
            return jsonify(success=True)
@app.route('/get-status/<uuid>')
def get_status(uuid):
    if not os.listdir(f'/projects/{uuid}'):
        return jsonify(state='process')
    else:
        return jsonify(state='ready')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8989)
