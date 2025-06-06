## Run spark docker container
```commandline
docker run --rm --name spark -p 8888:8888 -p 4040:4040 veribilimiokulu/pyspark:3.5.3_python-3.12_java17 sleep infinity
```

## Run Jupyter lab
```commandline
docker exec -it spark jupyter lab --ip 0.0.0.0 --port 8888 --allow-root
```

### 