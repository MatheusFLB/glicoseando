"""
PACKAGE: Glicoseando - Dashboard de Análise NDVI em Agricultura de Precisão

DESCRIÇÃO GERAL:
Este pacote Python integra múltiplos módulos especializados para criar um dashboard
completo de análise geoespacial, utilizando dados de séries temporais NDVI de 26 anos
(2000-2026) obtidos do sistema SATVeg da Embrapa.

OBJETIVO:
Fornecer ferramentas para análise de mudanças no uso do solo e dinâmica da vegetação
em áreas agrícolas através de visualizações interativas e métricas estatísticas.

ESTRUTURA DO PACKAGE:
- data_processing: Carregamento, validação e processamento de dados NDVI
- polygon_processing: Processamento geométrico de polígonos (área, centróide, etc)
- ndvi_analysis: Análise temporal (picos, métricas anuais, padrões sazonais)
- map_generator: Geração de mapas interativos com Folium

FLUXO TÍPICO DE USO:
1. Carrega dados NDVI em arquivo JSON (data_processing.load_ndvi_data)
2. Processa polígono de interesse (polygon_processing.parse_polygon_string)
3. Analisa série temporal para identificar padrões (ndvi_analysis.identify_peaks)
4. Visualiza em mapa interativo (map_generator.create_full_featured_map)
5. Gera relatório com métricas anuais (ndvi_analysis.extract_annual_metrics)

PRINCIPAIS BIBLIOTECAS UTILIZADAS:
- pandas: Manipulação e análise de dados tabulares
- geopandas: Processamento de dados geoespaciais
- folium: Criação de mapas interativos
- plotly: Gráficos interativos
- scipy: Processamento de sinais (detecção de picos)
- streamlit: Framework para webapps
"""

