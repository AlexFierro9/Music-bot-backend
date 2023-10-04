# Use an official Python runtime as a parent image
FROM python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV FLASK_ENV production

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container and install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt
RUN pip install torch==2.0.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install gunicorn

# Copy your application code into the container
COPY . /app/

# Expose the port that Gunicorn will listen on
EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "main:app"]
