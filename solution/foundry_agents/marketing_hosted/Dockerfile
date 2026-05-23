FROM mcr.microsoft.com/azurelinux/distroless/python:3.12

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY main.py ./

ENV PYTHONUNBUFFERED=1
EXPOSE 8088

CMD ["python", "main.py"]
