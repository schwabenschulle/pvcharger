FROM ubuntu
RUN apt-get update && apt-get install -y python3-pip vim git
RUN git clone https://github.com/schwabenschulle/pvcharger.git
RUN pip install requests
COPY main.py .
CMD ["python3", "pvcharger/pvcharger.py"]