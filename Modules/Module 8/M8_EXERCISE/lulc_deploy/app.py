import ee

import numpy as np
import pandas as pd
from flask import Flask, request, render_template
from sklearn import preprocessing
import pickle

app = Flask(__name__)
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

service_account = 'ml4eo-420815.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, '.private-key.json')
ee.Initialize(credentials)

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
    quality_band = image.select('QA60')
    cloudmask = 1 << 10
    cirrusmask = 1 << 11
    mask = quality_band.bitwiseAnd(cloudmask).eq(0) and (quality_band.bitwiseAnd(cirrusmask).eq(0))
    return image.updateMask(mask).divide(10000)


def get_fused_data():
    """
        This function contains the preprocessing steps followed to obtain the preprocessed, merged dataset in 6_1.
    """

    mean = 0.2062830612359614
    std = 1.1950717918110398
    
    vmu = ee.Number(mean)
    vstd = ee.Number(std)


    se2 = ee.ImageCollection('COPERNICUS/S2').filterDate("2015-07-01","2015-12-31")

    # TODO: Use the filterBounds function to get filter the are specified in ROI
    se2 = se2.filterBounds(roi)

    # Keep pixels that have less than 20% cloud
    se2 = se2.filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE",20))

    # Update the mask 
    se2 = se2.map(se2mask)

    # Get the median image
    se2 = se2.median()

    se2 = se2.select(se2bands)
    

    viirs = ee.Image(ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG").filterDate(
        "2015-07-01","2015-12-31").filterBounds(roi).median().select('avg_rad').clip(roi))

    viirsclean = viirs.subtract(vmu).divide(vstd)

    fusedclean = se2.addBands(viirsclean)
    return fusedclean

gee_data = get_fused_data()


def get_features(longitude, latitude):
    poi_geometry = ee.Geometry.Point([longitude, latitude])

    feature = gee_data.sampleRegions(
        collection=poi_geometry,
        scale=1000,
    )
    dataclean = gee_data.select(trainingbands).sampleRegions(
        collection=poi_geometry,
        scale=scaleFactor)
    
    sample = dataclean.getInfo()
    band_order = sample['properties']['band_order']

    nested_list = dataclean.reduceColumns(ee.Reducer.toList(len(band_order)), band_order).values().get(0)
    data = pd.DataFrame(nested_list.getInfo(), columns=band_order)
    return data

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():

    features = request.form.to_dict()
    longitude = float(features['longitude'])
    latitude = float(features['latitude'])
    final_features = get_features(longitude, latitude)
    
    prediction = model.predict(final_features)
    print(prediction)
    output = int(prediction[0])
    if output == 1:
        text = "built up land"
    else:
        text = "not built up land"

    return render_template('index.html', prediction_text='The area at {}, {} location is {}'.format(longitude, latitude, text))


if __name__ == "__main__":
    app.run(debug=True)
