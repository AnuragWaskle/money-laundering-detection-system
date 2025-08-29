<<<<<<< HEAD
# # Use an official Python runtime as a parent image
# FROM python:3.10-slim

# # Set the working directory in the container
# WORKDIR /app

# # Copy the dependencies file to the working directory
# COPY requirements.txt .

# # Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the content of the local src directory to the working directory
# COPY . .

# # Make port 5001 available to the world outside this container
# EXPOSE 5001

# # Define environment variable
# ENV FLASK_APP app.py
# ENV FLASK_RUN_HOST 0.0.0.0
# ENV FLASK_RUN_PORT 5001

# # Run app.py when the container launches
# CMD ["flask", "run"]




=======
>>>>>>> 878aa4807e99ba5a524b32f89c231a7c1196f533
# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Define environment variable
<<<<<<< HEAD
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5001

# Run app.py when the container launches
CMD ["flask", "run"]
=======
ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 5001

# Run app.py when the container launches
CMD ["flask", "run"]
>>>>>>> 878aa4807e99ba5a524b32f89c231a7c1196f533
