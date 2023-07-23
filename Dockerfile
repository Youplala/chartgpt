FROM python:3.11-slim
ENV DASH_DEBUG_MODE False
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE 7860
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:server"]
