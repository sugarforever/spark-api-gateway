# Use a base image (e.g., Python 3.11)
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Expose the port your FastAPI app will run on (default is 8000)
EXPOSE 8000

# Define build arguments
ARG SSL_KEYFILE
ARG SSL_CERTFILE

# Set default values for arguments if not provided during build
ARG DEFAULT_SSL_KEYFILE=./key.pem
ARG DEFAULT_SSL_CERTFILE=./cert.pem

# Use the build arguments as environment variables
ENV SSL_KEYFILE=${SSL_KEYFILE:-$DEFAULT_SSL_KEYFILE}
ENV SSL_CERTFILE=${SSL_CERTFILE:-$DEFAULT_SSL_CERTFILE}

# Define the command to run your FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", f"--ssl-keyfile={SSL_KEYFILE}", f"--ssl-certfile={SSL_CERTFILE}"]