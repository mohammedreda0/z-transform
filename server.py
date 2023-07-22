from __future__ import print_function  # In python 2.7
import os
from flask import Flask, render_template, request, redirect, url_for, Blueprint, jsonify, g
from numpy.lib.function_base import place
from werkzeug.datastructures import Headers
from werkzeug.utils import html
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import json

import sys

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('test.html')


@app.route('/filter', methods=['GET', 'POST'])
def filter():
    dataGet = request.get_json()
    # print(dataGet, file=sys.stderr)
    p = complex(dataGet[0], dataGet[1])
    z = 1.0/complex(dataGet[0], ((dataGet[1])*-1))

    w, h = signal.freqz_zpk(z=z, p=p, k=1.0, fs=1000)
    angles = (np.angle(h))
    phase = list(angles)
    w = list(w)
    dataReply = {"w": w, "phase": phase}

    return jsonify(dataReply)

    # return '<h1>hello</h1>'


@app.route('/func', methods=['GET', 'POST'])
def func():

    dataGet = request.get_json()
    con = dataGet[1]
    data = dataGet[0]
    print(len(data), file=sys.stderr)

    cntZero = dataGet[3]
    cntPole = dataGet[2]
    a_pass_filters_list = dataGet[4]

    p = []
    z = []

    # if (con == False):
    #     for i in data:
    #         if (i.startswith("p") and not ("Con" in i)):
    #             p.append((data[i]["place"][0] - 256)/179)
    #         elif (i.startswith("z") and not ("Con" in i)):
    #             z.append((data[i]["place"][0]-256)/179)
    # else:
    for i in data:
        if (i.startswith("p") and not ("Con" in i)):
            real = (data[i]["place"][0] - 256)/179
            imag = (data[i]["place"][1] - 435)/179
            p.append(complex(real, imag))
            p.append(complex(real, -imag))
        elif (i.startswith("z") and not ("Con" in i)):
            real = (data[i]["place"][0] - 256)/179
            imag = (data[i]["place"][1] - 443)/179
            z.append(complex(real, imag))
            z.append(complex(real, -imag))
    for element in a_pass_filters_list:
        p.append(
            complex(a_pass_filters_list[element][0], a_pass_filters_list[element][1]))
        p.append(
            complex(a_pass_filters_list[element][0], (a_pass_filters_list[element][1])*-1))

        z.append(
            1.0/complex(a_pass_filters_list[element][0], ((a_pass_filters_list[element][1])*-1)))
        z.append(
            1.0/complex(a_pass_filters_list[element][0], (a_pass_filters_list[element][1])))
    print(p, file=sys.stderr)
    print(z, file=sys.stderr)
    w, h = signal.freqz_zpk(z=z, p=p, k=1.0, fs=1000)
    mag = 20 * np.log10(abs(h))
    angles = (np.angle(h))
    w = list(w)
    mag = list(mag)
    phase = list(angles)
    dataReply = {"magnitude": mag, "w": w, "phase": phase}
    global poles
    poles = p
    global zeros
    zeros = z

    return jsonify(dataReply)


@app.route('/correctPhase', methods=['GET', 'POST'])
def correctPhase():
    dataGet = request.get_json()
    data = dataGet[0]
    con = dataGet[1]
    cntPole = dataGet[2]
    cntZero = dataGet[3]
    a_pass_filters_list = dataGet[4]

    p = []
    z = []

    # if (con == False):
    #     for i in data:
    #         print(data, file=sys.stderr)

    #         if (i.startswith("p") and not ("Con" in i)):
    #             p.append((data[i]["place"][0] - 256)/179)
    #         elif (i.startswith("z") and not ("Con" in i)):
    #             z.append((data[i]["place"][0]-256)/179)
    # else:
    for i in data:
        print(data, file=sys.stderr)
        if (i.startswith("p") and not ("Con" in i)):
            real = (data[i]["place"][0] - 256)/179
            imag = (data[i]["place"][1] - 435)/179
            p.append(complex(real, imag))
            p.append(complex(real, -imag))
        elif (i.startswith("z") and not ("Con" in i)):
            real = (data[i]["place"][0] - 256)/179
            imag = (data[i]["place"][1] - 443)/179
            z.append(complex(real, imag))
            z.append(complex(real, -imag))
    for element in a_pass_filters_list:
        p.append(
            complex(a_pass_filters_list[element][0], a_pass_filters_list[element][1]))
        p.append(
            complex(a_pass_filters_list[element][0], (a_pass_filters_list[element][1])*-1))

        z.append(
            1.0/complex(a_pass_filters_list[element][0], ((a_pass_filters_list[element][1])*-1)))
        z.append(
            1.0/complex(a_pass_filters_list[element][0], (a_pass_filters_list[element][1])))

    print(p, file=sys.stderr)
    print(z, file=sys.stderr)
    w, h = signal.freqz_zpk(z=z, p=p, k=1.0, fs=1000)
    mag = 20 * np.log10(abs(h))
    angles = (np.angle(h))  
    w = list(w)
    mag = list(mag)
    phase = list(angles)
    dataReply = {"magnitude": mag, "w": w, "phase": phase}

    global poles
    poles = p
    global zeros
    zeros = z
    return jsonify(dataReply)


# @app.route('/applyFilter', methods=['GET', 'POST'])
# def applyFilter():
#     dataGet = request.get_json()
#     # print(poles, file=sys.stderr)
#     # print(zeros, file=sys.stderr)
#     return jsonify()


@app.route('/chooseFile', methods=['GET', 'POST'])
def chooseFile():
    dataGet = request.get_json()
    b, a = signal.zpk2tf(zeros, poles, 1)
    filteredSignal = signal.lfilter(b, a,dataGet[:len(dataGet)-1]).tolist()
    filteredSignalArr = np.array(filteredSignal)  # to array
    filteredSignal = filteredSignalArr.real.tolist()
    return jsonify({"data": filteredSignal})


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    dataGet = request.get_json()


if __name__ == '__main__':
    app.run(debug=True)
