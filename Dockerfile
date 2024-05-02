FROM python:3.10

WORKDIR /app
RUN mkdir /app/hamcontestanalysis_data
ENV HAMCONTESTANALYSISSTORAGE "/app/hamcontestanalysis_data"

ARG tag
RUN pip install hamcontestanalysis==$tag

EXPOSE 8050
ENTRYPOINT ["hamcontestanalysis"]
CMD ["dashboard", "contest-analysis", "--host", "0.0.0.0"]

# USEFUL COMMANDS
# docker build -t "hamcontestanalysis:<tag>" --build-arg tag=<tag> .
# docker run -p 8050:8050 -v <local_data_folder>:/app/hamcontestanalysis_data <image_hash>:<tag>
# docker login
# docker tag hamcontestanalysis:<tag> docker.io/rogercaminal/hamcontestanalysis:<tag>
# docker push docker.io/rogercaminal/hamcontestanalysis:<tag>
# docker exec -it <container_hash> bash
