FROM waynedd/cithub-base:1.2

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

WORKDIR /cithub-generation
COPY . /cithub-generation

EXPOSE 6000

ENTRYPOINT [ "gunicorn", "-w", "4", "-b", "0.0.0.0:6000", "--timeout", "40000", "--chdir", "/cithub-generation", "app:app"]
CMD [""]
