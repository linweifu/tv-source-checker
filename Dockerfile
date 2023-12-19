FROM python:3.10-slim
ENV PYTHONUNBUFFERED 1
ENV TZ="Asia/Shanghai"
LABEL maintainer="Wafer lin"
COPY src /app
WORKDIR /app
RUN pip install -i http://mirrors.aliyun.com/pypi/simple/ \
  --trusted-host mirrors.aliyun.com \
  --upgrade pip -r requirements.txt \
  && find /usr/local/lib -name '*.pyc' -delete
EXPOSE 80
RUN mkdir /app/www

#ENTRYPOINT [ "/bin/bash","-c","tail -f /dev/null" ]
ENTRYPOINT ["python", "app_main.py"]
