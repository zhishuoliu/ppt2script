FROM ppt_convert:latest
ENV LANG C.UTF-8
COPY * /data/ppt2script/
COPY /data/self_check* /data/ppt2script/data/self_check/
COPY /API* /data/ppt2script/API/
WORKDIR /data/ppt2script
RUN pip install -r requirements.txt
ENTRYPOINT ["sh", "/data/ppt2script/start_server.sh"]