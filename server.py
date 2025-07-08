# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort, jsonify
from pts import *
from ppt2text import *
from pptx import Presentation
import argparse
import datetime
import os

base_path = os.path.realpath(__file__)
this_path = os.path.dirname(base_path)

app = Flask(__name__)


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        uploaded_file = request.files['file']
    except Exception as e: 
        return(f"error:accept failed\n\n{e}")
    if uploaded_file.filename != '':
        if allowed_file(uploaded_file.filename):
            try:
                nowtime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                os.makedirs("./data/" + nowtime, exist_ok=True)
            except:
                return("makedir failed")
            save_file = os.path.join("./data/" + nowtime, uploaded_file.filename)
            uploaded_file.save(save_file)
            script = pts(save_file)
            return(script)

    else:
        return jsonify({'error': 'Invalid file format'})

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'ppt', 'pptx'}

@app.route('/health_status',methods=['GET'])
def health_status():
    if request.method == 'GET':
        success = True
        if success:
            return "success"
        else:
            abort(400)  

@app.route('/self_check', methods=['GET'])
def self_check():
    check_file = this_path + '/data/self_check/check.pptx'
    if request.method == 'GET':
        try:
            Presentation(check_file)
            try:
                check_scripts = pts(check_file)
            except:
                return (f"error:failed to generate sript")
        except:
            return(f"error:invalid path:{check_file},current_path:{os.getcwd()},list:{os.listdir(os.getcwd())}")
        return(check_scripts)


@app.route('/help', methods=['GET'])
def help():
    with open(this_path+"/help.md", "r", encoding='utf-8') as f:
        txt = f.read()

    return txt



def args_parser():
    params = argparse.ArgumentParser()
    params.add_argument('--host', type=str, required=False, default="0.0.0.0", help='host ip adress')
    params.add_argument('--port', type=int, required=False, default=8080, help='port')
    return params.parse_args()

if __name__ == '__main__':
    args = args_parser()
    app.run(host=args.host, port=args.port)
    """args = args_parser()
    server = pywsgi.WSGIServer((args.host, args.port),app)
    server.serve_forever()"""
