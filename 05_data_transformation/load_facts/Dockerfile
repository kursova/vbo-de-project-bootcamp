FROM spark:3.5.3-java17

USER root

WORKDIR /app

# Create necessary directories with proper permissions
RUN mkdir -p /home/spark/.ivy2/cache && \
    mkdir -p /app/logs && \
    chown -R spark:spark /home/spark/.ivy2 && \
    chown -R spark:spark /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy the entire source structure
COPY src/ ./src/

# Set PYTHONPATH to include the source directory
ENV PYTHONPATH="/app/src:$PYTHONPATH"

# Create the main application file at the expected location
RUN ln -s /app/src/load_facts/spark_load_facts.py /app/load_facts.py

# Switch to spark user for security
USER spark

# Set the entry point
CMD ["python3", "/app/load_facts.py"]