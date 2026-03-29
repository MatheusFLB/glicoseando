# 🛰️ Glicoseando - Dashboard de Análise NDVI em Agricultura de Precisão

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit App](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg)](https://streamlit.io/)

> **Análise Geoespacial | Sensoriamento Remoto | Observação da Terra**

Um dashboard geoespacial interativo para **análise de séries temporais NDVI** (26 anos: 2000–2026) com visualizações de dinâmica vegetativa e detecção de padrões sazonais.

---

## 🎯 Visão Geral

Este projeto analisa uma **série temporal de NDVI** de uma área agrícola no Brasil usando dados de satélite MODIS/Sentinel-2 da API SATVeg (Embrapa). O dashboard detecta:

- ✅ **Padrões Sazonais**: Ciclos de crescimento e dormência da vegetação
- ✅ **Picos de Vegetação**: Momentos de máximo vigor em cada ciclo
- ✅ **Tendências Anuais**: Evolução do NDVI ao longo de 26 anos
- ✅ **Análise Interativa**: Zoom em períodos específicos para investigação detalhada
- ✅ **Visualizações Dinâmicas**: Mapa colorido, gráficos Plotly responsivos

### ⚡ Funcionalidades Principais

| Recurso | Descrição |
|---------|-----------|
| 🗺️ **Mapa Interativo** | Visualização Folium com seletor de data e overlay de polígono colorido por NDVI |
| 📈 **Série Temporal** | Linha de tendência com detecção automática de picos de vegetação |
| 🔍 **Zoom por Ano** | Filtro interativo para examinar períodos específicos em detalhe |
| 📊 **Métricas Anuais** | Gráfico de tendências mostrando min/média/max NDVI por ano |
| 🌍 **Dual-Language** | Interface em Português (PT) e Inglês (EN) |
| 💾 **Código Comentado** | 370+ linhas de comentários explicativos para fácil compreensão |

---

## 📊 Fonte de Dados

**NDVI via API SATVeg (Embrapa)**

- **Satélites**: MODIS (Terra/Aqua) + Sentinel-2
- **Resolução**: 250m espacial × 8–16 dias temporal
- **Período**: 2000-02-18 a 2026-02-10 (1,142+ observações)
- **Fornecedor**: Embrapa Informática Agropecuária - SATVeg
- **Integração**: Brazil Data Cube (INPE)

**Área de Estudo**:
- **Localização**: Brasil (~-13.5°, ~-58.9°)
- **Área**: ~250 hectares
- **Coordenadas**: Polígono com múltiplos vértices

---

## 🚀 Início Rápido

### Pré-requisitos

- **Python 3.9+**
- **pip** ou **conda** para gerenciar pacotes

### Instalação

1. **Clone o repositório:**

```bash
git clone https://github.com/yourusername/glicoseando.git
cd glicoseando
```

2. **Crie um ambiente virtual (recomendado):**

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. **Instale as dependências:**

```bash
pip install -r requirements.txt
```

### Executar o Dashboard

```bash
streamlit run streamlit_app.py
```

A aplicação abrirá em `http://localhost:8501`

---

## 📁 Estrutura do Projeto

```
glicoseando/
├── data/
│   ├── ndvi_request.json         # Parâmetros da requisição da API
│   └── ndvi_timeseries.json      # Série temporal de NDVI (1,144 observações)
│
├── src/
│   ├── __init__.py               # Inicialização do package
│   ├── data_processing.py        # Carregamento e limpeza de dados NDVI
│   ├── polygon_processing.py     # Processamento geométrico e cálculo de área
│   ├── ndvi_analysis.py          # Análise temporal e detecção de picos
│   └── map_generator.py          # Geração de mapas interativos com Folium
│
├── streamlit_app.py              # Aplicação principal do dashboard
├── requirements.txt              # Dependências Python
│
├── DOCUMENTAÇÃO/
│   ├── START_HERE.md             # **Comece aqui!**
│   ├── QUICK_REFERENCE.md        # Guia prático rápido
│   ├── ARCHITECTURE.md           # Detalhes técnicos profundos
│   ├── CODE_COMMENTS_GUIDE.md    # Estratégia de comentários
│   ├── DOCUMENTATION_INDEX.md    # Índice de documentação
│   └── REVISION_SUMMARY.md       # Resumo de revisão
│
└── README.md                     # Este arquivo
```

---

## 🔧 Descrição dos Módulos

### 1. `src/data_processing.py`

Carregamento e validação de dados NDVI em formato JSON.

**Funções Principais:**
- `load_ndvi_data()` - Carrega JSON e cria DataFrame estruturado
- `clean_ndvi_data()` - Remove valores inválidos (fora de [-1, 1])
- `get_data_summary()` - Gera estatísticas descritivas

**Exemplo:**
```python
from src.data_processing import load_ndvi_data, get_data_summary
df = load_ndvi_data("data/ndvi_timeseries.json")
stats = get_data_summary(df)
print(f"NDVI Médio: {stats['mean_ndvi']:.3f}")
```

---

### 2. `src/polygon_processing.py`

Operações geométricas com polígonos usando GeoPandas e Shapely.

**Funções Principais:**
- `parse_polygon_string()` - Converte string de coordenadas em tuplas
- `create_geodataframe()` - Cria estrutura geométrica (GeoDataFrame)
- `calculate_area_hectares()` - Calcula área usando EPSG:6933 (igual-área)
- `get_polygon_stats()` - Compila estatísticas do polígono

**Nota Técnica:**
- Entrada: WGS84 (EPSG:4326)
- Cálculo de Área: EPSG:6933 (South America Equidistant)
- Saída: Dados estruturados com geometria validada

---

### 3. `src/ndvi_analysis.py`

Análise temporal de séries NDVI com detecção de padrões.

**Funções Principais:**
- `identify_peaks()` - Detecta máximos locais (picos de vegetação) com scipy
- `extract_annual_metrics()` - Calcula min/média/max NDVI por ano

**Parâmetro Crítico:**
```python
# Proeminência = altura do pico acima do vale adjacente
identify_peaks(series, prominence=0.08)
# 0.08 = muito seletivo (padrão)
# 0.05 = mais sensível (mais picos)
# 0.15 = muito seletivo (menos picos)
```

---

### 4. `src/map_generator.py`

Criação de visualizações cartográficas interativas com Folium.

**Funções Principais:**
- `get_color_for_ndvi()` - Mapeia NDVI para cor em 5 escalas
- `create_interactive_map()` - Gera mapa base com polígono
- `create_full_featured_map()` - Mapa completo com todos recursos

**Escala de Cores NDVI:**
```
0.0-0.3:   #8B4513  Marrom escuro (vegetação muito baixa)
0.3-0.5:   #CD853F  Marrom claro (esparsa)
0.5-0.7:   #ADFF2F  Amarelo-verde (moderada)
0.7-0.85:  #32CD32  Verde claro (alta)
0.85-1.0:  #006400  Verde escuro (densa)
```

---

### 5. `streamlit_app.py`

Aplicação principal que orquestra todos os módulos.

**Seções do Dashboard:**
- Seletor de Idioma (PT/EN)
- Mapa Interativo com Seletor de Data
- Série Temporal com Detecção de Picos
- Gráfico de Tendências Anuais
- Rodapé com Informações do Criador

**Caching:**
```python
@st.cache_resource
def load_all_data():
    # Dados carregados uma vez e reutilizados
    # Melhora desempenho significativamente
```

---

## 🧪 Exemplos de Uso

### Carregar e Processar Dados

```python
from src.data_processing import load_ndvi_data
from src.polygon_processing import parse_polygon_string, create_geodataframe

# Carregar dados
df = load_ndvi_data("data/ndvi_timeseries.json")

# Processar polígono
coords = parse_polygon_string("-58.914 -13.507,-58.865 -13.513,...")
gdf = create_geodataframe(coords)
```

### Análise Temporal

```python
from src.ndvi_analysis import identify_peaks, extract_annual_metrics

# Detectar picos
peaks = identify_peaks(df["ndvi"].values)
print(f"Picos detectados: {len(peaks)}")

# Métricas por ano
annual = extract_annual_metrics(df)
print(annual)
```

### Criar Mapa

```python
from src.map_generator import create_full_featured_map

# Gerar mapa
mapa = create_full_featured_map(gdf, center, mean_ndvi=0.65, area_ha=250)
mapa.save('analise.html')
```

---

## 📚 Documentação Completa

**Comece por aqui:** [`START_HERE.md`](START_HERE.md)

| Documento | Propósito | Tempo |
|-----------|-----------|-------|
| [`START_HERE.md`](START_HERE.md) | Guia inicial rápido | 5 min |
| [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) | Referência prática | 15 min |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Detalhes técnicos | 60 min |
| [`CODE_COMMENTS_GUIDE.md`](CODE_COMMENTS_GUIDE.md) | Padrão de comentários | 20 min |
| [`DOCUMENTATION_INDEX.md`](DOCUMENTATION_INDEX.md) | Índice completo | Consulta |

---

## 🛠️ Stack Tecnológico

| Componente | Tecnologia | Propósito |
|------------|-----------|----------|
| **Dados** | Pandas, NumPy | Manipulação de séries temporais |
| **Geoespacial** | GeoPandas, Shapely | Processamento de polígonos |
| **Análise** | SciPy | Detecção de picos |
| **Visualização** | Plotly, Folium | Gráficos e mapas interativos |
| **Dashboard** | Streamlit | Interface web |
| **Linguagem** | Python 3.9+ | Implementação |

---

## 📦 Dependências

```
pandas>=1.5.0
numpy>=1.23.0
geopandas>=0.12.0
shapely>=2.0.0
folium>=0.14.0
plotly>=5.14.0
streamlit>=1.28.0
scipy>=1.10.0
pyproj>=3.5.0
```

---

## 🌐 Deployment

### Desenvolvimento Local

```bash
streamlit run streamlit_app.py
```

### Streamlit Cloud

```bash
# 1. Push para GitHub
git push origin main

# 2. Visite: https://share.streamlit.io/
# 3. Conecte repositório e deploy
```

### Docker (Opcional)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py"]
```

---

## 📖 Referências

- **SATVeg System**: [Sistema de Análise Temporal da Vegetação](https://www.sativeg.cnptia.embrapa.br/)
- **Brazil Data Cube**: [INPE - Cubo Brasil](http://www.brazildatacube.org/)
- **NDVI**: [Normalized Difference Vegetation Index (Wikipedia)](https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index)
- **MODIS**: [NASA MODIS Instrument](https://modis.gsfc.nasa.gov/)
- **GeoPandas**: [GeoPandas Documentation](https://geopandas.org/)
- **Streamlit**: [Streamlit Documentation](https://docs.streamlit.io/)

---

## 📝 Licença

Este projeto está licenciado sob a **Licença MIT** — veja o arquivo LICENSE para detalhes.

---

## 👨‍💻 Autor

**Matheus Bissoli**

Análise geoespacial | Sensoriamento remoto | Agricultura de precisão

- 🌐 [Site Pessoal](https://matheusflb.github.io/)
- 💼 [LinkedIn](https://www.linkedin.com/in/matheusbissoli/)
- 💻 [GitHub](https://github.com/MatheusFLB)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o repositório
2. Crie uma branch de feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub
- Consulte a [documentação completa](DOCUMENTATION_INDEX.md)
- Comece por [`START_HERE.md`](START_HERE.md)

---

**Keywords:** `ndvi` | `agriculture` | `remote-sensing` | `geospatial` | `earth-observation` | `satellite-data` | `streamlit` | `geopython` | `precision-agriculture`

