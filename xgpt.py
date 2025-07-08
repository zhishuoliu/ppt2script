import json
import re
import os
import ppt2text
import requests

def str2json(string):
    pattern = r'"([^"]+)":\s*("[^"]+"|\[[^\]]+\]|[^,"]+)'
    matches = re.findall(pattern, string)
    # 构建字典
    script = {}
    for match in matches:
        key = match[0]
        value = match[1]
        if value.isnumeric():
            value = int(value)
        script[key] = value
    return script


def get_res(slide_index, role, content='', conversation_id='', history=''):
    # Header
    cfp = os.path.abspath(os.path.dirname(__file__))
    os.chdir(cfp)
    with open('./API/headers.json', encoding='utf-8') as f:
        headers = json.loads(f.read())
    # Get Role and Prompt
    prompt_dict = extract_content_from_file("prompt2.md")
    _prompt = prompt_dict[role]
    role_dict = extract_content_from_file("role.md")
    _role = role_dict["讲师"]
    if history:
        prompt+=f"\n\n这是之前ppt的大纲以及对应的讲稿，请参考:\n```\n{str(history)}```"
    else:
        # Fisrt conversation, remind the model about its role
        prompt = _role + _prompt
    question = prompt + f"\n\n 当前是你本次演讲的第{slide_index}页ppt，在你的讲稿中不需要提及当前ppt的页数\n\n 输入\n\n ```" + content + "```\n\n输出："


    # Formulate the data
    if conversation_id:
        data = { 
        "inputs": {}, 
        "query": question, 
        "response_mode": "blocking", 
        "conversation_id": conversation_id,
        "user": "user1" 
        }
    else:
        data = { 
        "inputs": {}, 
        "query": question, 
        "response_mode": "blocking", 
        "user": "user1" 
        }

    # Post the request
    response = requests.post('https://dify.cvte.com/v1/chat-messages', headers=headers, json=data) 
    if response.status_code != 200: 
        return(0)
    result = json.loads(response.content)

    return result

def check_script_empty(json_text):
    try:
        data = json.loads(json_text)
        script = data.get('script')
        if script:
            return False
        else:
            return True
    except json.JSONDecodeError:
        return False

def extract_content_from_file(file_path):
    with open(file_path, 'r',encoding='utf-8') as file:
        markdown = file.read()

    lines = markdown.split("\n")
    headers = {}
    current_header = None
    current_content = ""

    for line in lines:
        if line.startswith("##"):
            if current_header is not None:
                headers[current_header] = current_content.strip()
                current_content = ""
            current_header = line[2:].strip()
        else:
            current_content += line + "\n"

    if current_header is not None:
        headers[current_header] = current_content.strip()

    return headers


