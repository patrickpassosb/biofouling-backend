# context.md — Transpetro Hackathon Project Context

## Overview

This document summarizes the full context of the project, team composition, objectives, and strategic direction for use by an AI assistant during the Transpetro Hackathon.

## Hackathon

* **Event:** Hackathon Transpetro 2025
* **Theme:** Bioincrustação (biofouling) em embarcações
* **Goal:** Criar uma solução tecnológica que auxilie a Transpetro a identificar, monitorar ou prever níveis de bioincrustação em cascos de navios, reduzindo custos, consumo de combustível e emissões.

## Challenge Clarification

Com base na live oficial do hackathon, o principal foco da Transpetro é:

* **Classificar o nível atual de bioincrustação** do casco de um navio.
* Exemplos: “Está no nível 1?”, “Está no nível 2?”, “Com X% de probabilidade está no nível Y?”
* **Não** é necessário prever o melhor momento de limpeza do casco.
* Outras abordagens são possíveis, mas a classificação de nível é a necessidade central.

## Current Team

The team currently consists of:

* **Patrick**

  * Tecnologia, AI direction, comunicação com especialistas.
* **Engenheira de Machine Learning (Gabrielly)**

  * Responsável por modelos de classificação, pipeline de dados, feature engineering.
* **Designer (Lucas)**

  * Responsável por UI/UX, dashboards e apresentação.

A equipe pode eventualmente incluir um **engenheiro naval ou especialista em bioincrustação**, caso um candidato ideal responda à abordagem.

## Project Direction

A solução seguirá o eixo técnico abaixo:

### 1. **Classificação de Nível de Bioincrustação**

* Tipo de ML: Classificação supervisionada
* Modelos recomendados: XGBoost, RandomForest, CatBoost
* Output esperado: Probabilidades por nível (ex: nível 1 = 72%, nível 2 = 18%, nível 3 = 10%)

### 2. **Features Relevantes**

* Dados operacionais do navio: velocidade, RPM, potência, consumo, calado.
* Dados ambientais: temperatura da água, salinidade, clorofila, localização, sazonalidade.
* Dados de manutenção: tempo desde última limpeza, tipo de coating.

### 3. **Dashboard / Interface**

* Desenvolvido em **Streamlit** para agilidade.
* Exibe nível atual de bioincrustação + gráficos explicativos.

### 4. **Justificativa Técnica**

* Aumento de arrasto -> aumento de consumo -> impacto econômico.
* Classificação do nível permite ação operacional direta.

## Communication and Outreach

Patrick fez contato com possíveis especialistas:

* Engenheiros navais da Petrobras, Transpetro e Marinha.
* Engenheiros de dados e especialistas em eficiência energética marítima.
* Pessoas encontradas via LinkedIn e grupos de WhatsApp do hackathon.

## Key Notes

* A solução da equipe será **estritamente focada na classificação do nível de bioincrustação**, conforme informado oficialmente.
* O foco é manter o time **enxuto (3 pessoas)** para comunicação clara e rapidez.

## Summary

Este contexto deve ser usado pela IA para:

* Ajudar na modelagem do sistema de classificação.
* Sugerir features, arquiteturas e visualizações.
* Apoiar na comunicação técnica.
* Manter alinhamento com os objetivos do hackathon.

---