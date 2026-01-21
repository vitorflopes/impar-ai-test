FROM ollama/ollama

COPY ollama-setup.sh /ollama-setup.sh

# Converte CRLF para LF e dá permissão de execução
RUN sed -i 's/\r$//' /ollama-setup.sh && \
    chmod +x /ollama-setup.sh

ENTRYPOINT ["/bin/bash", "/ollama-setup.sh"]
