import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
import requests as req
import pickle
import datetime
import time
import math
from datetime import date, timedelta
import cv2
import os
import warnings
from dotenv import load_dotenv
from statistics import mode
from time import strftime

warnings.filterwarnings("ignore")
load_dotenv()


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
# BASE_DIR = r'D:/Outgrow Digital/otgrow-premium flask/'

# getting all secrets
key = str(PREMIUM_API_KEY)

app = Flask(__name__)


@app.route("/spray-condition", methods=['GET'])
def sprayConditionOW():
    try:
        import math
        def dt_calculator(temp, hum):
            tw = temp * (math.atan(0.151977 * np.sqrt(hum + 8.313659))) + math.atan(temp + hum) - math.atan(
                hum - 1.676331) + (0.00391838 * (hum ** (3 / 2)) * math.atan(0.023101 * hum)) - 4.686035
            dt = temp - tw
            return dt

        args = request.args
        ApiKey = args.get('ApiKey', type=str)
        latitude = args.get('lat', type=float)
        longitude = args.get('long', type=float)

        if key == ApiKey:
            current = date.today()
            day2 = current + timedelta(days=2)
            lat = latitude
            long = longitude
            date_hr = []
            temp_hr = []
            hum_hr = []
            headers = {'x-api-key': '854a7687-e2d9-46ff-b5ae-7886a3f2623f'}
            url = 'https://weather.outgrowdigital.com/api/v1/weather/apple-weather-kit?lat=%s&long=%s&startDate=%s&endDate=%s' % (
            lat, long, current, day2)
            data = req.request("GET", url, headers=headers).json()
            # Hourly data collection
            for i in range(len(data['data'][0]['hourly'])):
                temp_hr.append(data['data'][0]['hourly'][i]['temperature'])
                hum_hr.append(data['data'][0]['hourly'][i]['humidity'])
                date_hr.append(data['data'][0]['hourly'][i]['time'])

            hourly = pd.DataFrame()
            hourly['day'] = date_hr
            hourly['temperature'] = temp_hr
            hourly['humidity'] = hum_hr
            hourly['datetime'] = np.nan
            for i in range(len(hourly)):
                hourly['datetime'][i] = datetime.datetime.strptime(hourly['day'][i], "%Y-%m-%dT%H:%M:%S.000Z").strftime(
                    "%Y-%m-%d %H")
                hourly['day'][i] = datetime.datetime.strptime(hourly['day'][i], "%Y-%m-%dT%H:%M:%S.000Z").strftime(
                    "%Y-%m-%d")

            delta_t = []
            for i in range(0, len(hourly)):
                delta_t.append(dt_calculator(hourly['temperature'][i], hourly['humidity'][i]))
            hourly['delta_t'] = delta_t
            hourly['condition'] = np.nan
            for i in range(0, len(hourly)):
                if hourly['delta_t'][i] >= 2 and hourly['delta_t'][i] <= 8:
                    hourly['condition'].loc[i] = 'ideal'
                elif hourly['delta_t'][i] > 8 and hourly['delta_t'][i] <= 10:
                    hourly['condition'].loc[i] = 'good'
                else:
                    hourly['condition'].loc[i] = 'bad'
            day = hourly['day'].unique()
            data = hourly[['day', 'datetime', 'condition', 'delta_t']]
            day1 = data[data['day'] == day[1]]
            day2 = data[data['day'] == day[2]]
            day1 = day1[['datetime', 'delta_t', 'condition']]
            day2 = day2[['datetime', 'delta_t', 'condition']]
            Today = day1 = day1.to_dict(orient='records')
            Tomorrow = day2 = day2.to_dict(orient='records')
            return jsonify(status=True, message='Success', data={'Today': Today, 'Tomorrow': Tomorrow})
        else:
            return jsonify(status=False, message='Please Check your API Key', data=[])

    except Exception as error:
        return jsonify(status=False, message=str(error), data=[])
    


    if __name__ == '__main__':
        app.run()
