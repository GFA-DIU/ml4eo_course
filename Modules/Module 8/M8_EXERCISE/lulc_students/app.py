import ee

import numpy as np
import pandas as pd
from flask import Flask, request, render_template
from sklearn import preprocessing
import pickle

# Initialize an app
app = Flask(__name__)

# Load the serialized model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# Initialize GEE
service_account = 'ml4eo-420815.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, '.private-key.json')
ee.Initialize(credentials)

# Initialize variables required for GEE dataset preprocessing (similar to the examples in Exercise 6_1)
lat = -1.9441
lon = 30.0619
offset = 0.51
region = [
        [lon + offset, lat - offset],
        [lon + offset, lat + offset],
        [lon - offset, lat + offset],
        [lon - offset, lat - offset]]

roi = ee.Geometry.Polygon([region])

se2bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7','B8','B8A']
trainingbands = se2bands + ['avg_rad']
label = 'smod_code'
scaleFactor=1000

# Remember this function from Exercise 5_03, what does it do?
def se2mask(image):
    """
        This function updates a mask of an ee.Image so that clouds are filtered.
    """
    #TODO: complete this function
    pass

def get_fused_data():
    """
        This function contains the preprocessing steps followed to obtain the preprocessed, merged dataset in 6_1.
        This function is called when the server starts to prepare the dataset.
    """
    # Use the mean and standard deviation obtained from the training dataset
    mean = 0.2062830612359614
    std = 1.1950717918110398

    #  TODO: Convert the mean and std to ee.Number    
    vmu = 
    vstd = 

    #  TODO: Load the COPERNICUS/S2 dataset and filter dates "2015-07-01","2015-12-31"
    se2 = 
    # TODO: Use the filterBounds function to get filter the are specified in ROI
    se2 = 

    #  TODO: Keep pixels that have less than 20% cloud
    se2 = 

    # TODO:Update the mask 
    se2 = 

    # TODO:Get the median image
    se2 = 

    # TODO: select the `se2bands`
    se2 = 
    

    #  Load the NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG dataset and filter dates "2015-07-01","2015-12-31"
    viirs = ee.Image(ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG").filterDate(
        "2015-07-01","2015-12-31").filterBounds(roi).median().select('avg_rad').clip(roi))

    # TODO: Substract the mean and divide by the standard deviation for the viirs samples
    viirsclean = 

    # TODO: Fuse the two datasets
    fusedclean = 

    return fusedclean

# Prepare the fused 
gee_data = get_fused_data()


def get_features(longitude, latitude):
    # TODO: Create an ee.Geometry instance from the coordinates
    poi_geometry = 

    # TODO: Sample features for the given point of interest keeping only the training bands
    dataclean = 

    # TODO: use getInfo to load the sample's features
    sample = 

    # Find the band ordering in the loaded data
    band_order = sample['properties']['band_order']

    # Convert the loaded data to ee.List
    nested_list = dataclean.reduceColumns(ee.Reducer.toList(len(band_order)), band_order).values().get(0)

    # TODO: Convert the `nested_list` to a Pandas dataframe
    data = 
    return data

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():

    features = request.form.to_dict()
    longitude = float(features['longitude'])
    latitude = float(features['latitude'])
    # TODO: get the features for the given location
    final_features = 
    
    # TODO: get predictions from the the model using the features loaded
    prediction = 

    # convert the prediction to an integer
    output = int(prediction[0])

    if output == 1:
        text = "built up land"
    else:
        text = "not built up land"

    # Return a response based on the output of the model
    return render_template('index.html', prediction_text='The area at {}, {} location is {}'.format(longitude, latitude, text))


if __name__ == "__main__":
    app.run(debug=True)
