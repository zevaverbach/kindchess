# this file tells AWS Beanstalk how to run the app
rest_api: \
  num_cores=$(python -c "import multiprocessing; print(multiprocessing.cpu_count())") \
    && gunicorn -w $num_cores app
ws: python ws_server.py