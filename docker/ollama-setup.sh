#!/bin/bash

# Inicia o servidor do Ollama em background
ollama serve &

# Espera o servidor ficar pronto
echo "Aguardando o servidor Ollama iniciar..."
while ! ollama list > /dev/null 2>&1; do
    sleep 1
done

# Faz o pull do modelo
echo "Fazendo o pull do modelo: $OLLAMA_MODEL"
ollama pull $OLLAMA_MODEL

# Mantém o processo em foreground
wait
