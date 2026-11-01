# btop for its README screenshot: a throwaway Linux container, so what it shows is the container's
FROM debian:stable-slim
RUN apt-get update && apt-get install -y --no-install-recommends btop python3 && rm -rf /var/lib/apt/lists/*
COPY btop.conf /root/.config/btop/btop.conf
COPY load.py /load.py
CMD ["sh", "-c", "python3 /load.py & sleep infinity & exec btop"]
