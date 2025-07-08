from xgpt import *
from ppt2text import *
import os

def pts(filepath):
    cfp = os.path.abspath(os.path.dirname(__file__))
    os.chdir(cfp)
    slides_text,title,content=ppt2text.get_text(filepath)
    template = build_template(title, content)
    all_script = []
    for index in range(len(title)):
        slide_content = str(template[index])
        if index==0:
            result = get_res(slide_index=index+1,role="opening",\
                content=slide_content, conversation_id='')
            id = result["conversation_id"]
        # Write the ending for the last slide
        elif index==len(title):
            result = get_res(slide_index=index+1,role="ending",\
                content=slide_content,conversation_id=id)

        # Continue generating for the main part of slides
        else:
            result = get_res(slide_index=index+1,role="main",\
                content=slide_content,conversation_id=id)
        # if does not exceed the maximum allowed token
        if result:
            answer = result["answer"]
            # Check if the script is json format
            if check_script_empty(answer):
                # Check if the script is empty
                result = get_res(slide_index=index+1,role="rewrite",\
                    content=slide_content,conversation_id=id)
                answer = result["answer"]
        else:
            while not result:
                # empty response
                history = str(all_script[-2:])
                result = get_res(slide_index=index+1,role="opening",\
                    content=slide_content,conversation_id='',history=history)
            id = result["conversation_id"]

        template[index]["script"] = answer.split(':')[-1].strip("'")
        all_script.append(template[index])
    # Store the script and ppt file, which can be removed if the docker meet the maximum capacity
    dir_path, file_name = os.path.split(filepath)
    script_name = os.path.join(dir_path + "/",f"script_{file_name}.json")
    script_json = json.dumps(all_script, ensure_ascii=False, indent=4)
    

    #script_name = "./data/script/script_"+filepath.split("\\")[-1].split(".")[0]+".json"
    with open(script_name, "w+",encoding='utf-8') as f:
        f.write(script_json)
    return(script_json)

