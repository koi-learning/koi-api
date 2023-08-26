FROM python:3.9

# copy the prebuild wheels to the container
COPY ./dist /wheels

# update pip
RUN python -m pip install --upgrade pip

# install the wheels
RUN pip install --find-links=/wheels koi_api
RUN pip install waitress

ENTRYPOINT [ "waitress-serve", "--port=8080", "--max-request-body-size=8589934592", "--call", "koi_api:create_app" ]