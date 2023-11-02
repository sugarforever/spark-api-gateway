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

# Define the command to run your FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]