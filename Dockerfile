FROM python:3.8
COPY ./ ./src
RUN pip install ./src
RUN pip install waitress
ENTRYPOINT [ "waitress-serve", "--call", "koi_api:create_app" ]