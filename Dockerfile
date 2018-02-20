FROM python:latest

COPY requirements.txt /tmp/requirements.txt

RUN pip install -U pip && pip install jupyter ipykernel && pip install -r /tmp/requirements.txt

RUN useradd -m -U jupyter-runner --uid 1000

WORKDIR /home/jupyter-runner

RUN mkdir notebooks && chown -R jupyter-runner:jupyter-runner notebooks
RUN mkdir /run/jupyter && chown -R jupyter-runner:jupyter-runner /run/jupyter

ENV JUPYTER_RUNTIME_DIR /run/jupyter
ENV PYTHONPATH /home/jupyter-runner

EXPOSE 8888

USER jupyter-runner
CMD jupyter notebook --ip 0.0.0.0 --no-browser --port 8888 --notebook-dir=/home/jupyter-runner/notebooks /home/jupyter-runner
