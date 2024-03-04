FROM python:3.11

# copy the prebuild wheels to the container
COPY ./dist /wheels

# update pip
RUN python -m pip install --no-cache-dir --upgrade pip

# install the wheels
RUN pip install --no-cache-dir --find-links=/wheels koi_api
RUN pip install --no-cache-dir waitress

ENTRYPOINT [ "waitress-serve", "--port=8080", "--max-request-body-size=8589934592", "--call", "koi_api:create_app" ]