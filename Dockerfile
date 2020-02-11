FROM waynedd/ccag-system

COPY requirements.txt ./
RUN pip3.7 install --no-cache-dir -r requirements.txt

WORKDIR /cithub-generation
COPY . /cithub-generation

EXPOSE 6000

# ENTRYPOINT ["python", "/cithub-generation/app.py"]
ENTRYPOINT [ "gunicorn", "-w", "1", "-b", "0.0.0.0:6000", "--timeout", "20000", "--chdir", "/cithub-generation", "app:app"]
CMD [""]
