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
from torch import optim
from torch import nn
from utils import *
import os
from main import *
from model import net_G
args=args()
model_ml = net_G(args)

app = Flask(__name__, static_folder='projects')
@app.route('/start-gen/<uuid>', methods=['GET', 'POST'])
def start(uuid):
      try:
        tree = ET.parse(f'/projects/{uuid}/project.xml')
        root = tree.getroot()
        a=[]
        h=0
        cor = np.array([])
        for elem in root.findall('coordinates'):
          for subelem in elem:
              a.append(subelem.text.split(', '))
        for i in range(len(a)):
          for j in range(2):
            cor = np.append(cor, float(a[i][j]))
        print(cor)
        for elem in root.findall('height'):
            h=elem.text
        cor_df = cor
        cor_df = pd.DataFrame
        cor_df = pd.DataFrame({'x':cor[::2], 'y':cor[1::2]})
        res=jsonify(success=True) # генерация началась
        return res
      except Exception as e:
        print(f'caught {type(e)}: e')
def generation(uuid):
    tree = ET.parse(f'/projects/{uuid}/project.xml')
    root = tree.getroot()
    a=[]
    h=0
    cor = np.array([])
    for elem in root.findall('coordinates'):
      for subelem in elem:
        a.append(subelem.text.split(', '))
    for i in range(len(a)):
      for j in range(2):
        cor = np.append(cor, float(a[i][j]))
    for elem in root.findall('height'):
        h=elem.text
    cor_df = cor
    cor_df = pd.DataFrame
    cor_df = pd.DataFrame({'x':cor[::2], 'y':cor[1::2]})
    dl=((cor[0]-cor[2])**2+(cor[1]-cor[3])**2)**(1/2)
    sh=((cor[2]-cor[4])**2+(cor[2]-cor[4])**2)**(1/2)
    def generation_parals(sh, dl, h, i):
        # Create a blank model
        model = ifcopenshell.file()

        # All projects must have one IFC Project element
        project = run("root.create_entity", model, ifc_class="IfcProject", name="My Project")

        # Geometry is optional in IFC, but because we want to use geometry in this example, let's define units
        # Assigning without arguments defaults to metric units
        run("unit.assign_unit", model)

        # Let's create a modeling geometry context, so we can store 3D geometry (note: IFC supports 2D too!)
        context = run("context.add_context", model, context_type="Model")

        # In particular, in this example we want to store the 3D "body" geometry of objects, i.e. the body shape
        body = run("context.add_context", model, context_type="Model",
            context_identifier="Body", target_view="MODEL_VIEW", parent=context)

        # Create a site, building, and storey. Many hierarchies are possible.
        site = run("root.create_entity", model, ifc_class="IfcSite", name="My Site")
        building = run("root.create_entity", model, ifc_class="IfcBuilding", name="Building A")
        storey = run("root.create_entity", model, ifc_class="IfcBuildingStorey", name="Ground Floor")

        # Since the site is our top level location, assign it to the project
        # Then place our building on the site, and our storey in the building
        run("aggregate.assign_object", model, relating_object=project, products=[site])
        run("aggregate.assign_object", model, relating_object=site, products=[building])
        run("aggregate.assign_object", model, relating_object=building, products=[storey])

        # Let's create a new wall
        wall = run("root.create_entity", model, ifc_class="IfcWall")

        # Give our wall a local origin at (0, 0, 0)
        run("geometry.edit_object_placement", model, product=wall)
        representation = run("geometry.add_wall_representation", model, context=body, length=dl, height=h, thickness=sh)
        # Assign our new body geometry back to our wall
        run("geometry.assign_representation", model, product=wall, representation=representation)

        # Place our wall in the ground floor
        run("spatial.assign_container", model, relating_structure=storey, product=wall)
        model.write(f'/projects/{uuid}/var{i}.obj')
        return model
  #  P.S. HERE MUST BE CONVERTER FROM IFC TO OBJ FOR MODEL
  #model_obj_1= ?converter?(generation_parals(sh, dl, h, 1))
  #model_obj_2= ?converter?(generation_parals(sh, dl, h, 2))
      #preds1 = model_ml.forward(model_obj)
      #preds2 = model_ml.forward(model_obj)
        preds1 = model_ml.forward(generation_parals(sh, dl, h, 1))
        preds2 = model_ml.forward(generation_parals(sh, dl, h, 2))

@app.route('/get-status/<uuid>')
def get_status(uuid):
    if not os.listdir(f'/projects/{uuid}'):
        return jsonify(state='process')
    else:
        return jsonify(state='ready')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8989)
