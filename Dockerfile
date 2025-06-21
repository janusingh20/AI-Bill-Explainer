# Use a lightweight Python image
FROM python:3.10-slim

# Ensure output is shown in real time
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port your Flask app runs on
EXPOSE 5000

# Use Gunicorn to run the app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
