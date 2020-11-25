FROM python:3.8
COPY ./ ./src
RUN pip install ./src
RUN pip install waitress

# wait-for-it by Giles Hall! see: https://github.com/vishnubob/wait-for-it
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

ENTRYPOINT [ "waitress-serve", "--port", "8080", "--call", "koi_api:create_app" ]