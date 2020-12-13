FROM python
# bakal buat image python
WORKDIR /app
# folder dalam container docker yang mau dipake
ADD . /app
# mau mindahin seluruh file yang ada di tutorial ke folder slash app
RUN pip install -r requirements.txt
# buat install semua yang ada di requirements.txt

CMD ["python","app.py"]
# run python app.py

# build docker-compose build app
# docker images buat check
# docker run -p 6000:5000 run di port, di :6000 di arahin ke :5000, yang kiri buat di browser, yang kanan di aplikasi