# 📐 ARQUITETURA DO PROJETO - Glicoseando

## 🎯 Visão Geral

**Glicoseando** é um dashboard interativo de análise NDVI para agricultura de precisão. O projeto integra análise geoespacial, processamento de séries temporais e visualizações interativas para monitorar mudanças de uso do solo ao longo de 26 anos (2000-2026).

---

## 📦 Estrutura de Módulos

### 1. **streamlit_app.py** (Aplicação Principal)
**Responsabilidade**: Orquestrador central que integra todos os módulos

**Funcionalidades Principais**:
- Configuração de idioma dual (Português/Inglês)
- Layout responsivo com 3 colunas
- Carregamento de dados com caching
- Renderização de mapa interativo
- Gráficos de série temporal e análise anual

**Fluxo de Execução**:
```
1. Carrega dados NDVI e polígono
2. Processa geometria do polígono
3. Exibe mapa interativo com seletor de data
4. Mostra série temporal com detecção de picos
5. Exibe métricas anuais (min/média/max)
```

---

### 2. **src/data_processing.py**
**Responsabilidade**: Processamento de dados brutos e validação

**Funções Principais**:
- `load_ndvi_data()`: Carrega JSON com série temporal NDVI
- `clean_ndvi_data()`: Remove valores inválidos fora de [-1, 1]
- `resample_to_monthly()`: Agrega dados para média mensal
- `get_data_summary()`: Gera estatísticas descritivas

**Fluxo de Dados**:
```
JSON (listaSerie, listaDatas)
        ↓
DataFrame (date, ndvi)
        ↓
Validação e limpeza
        ↓
Dados prontos para análise
```

**Validações**:
- Arquivo existe
- JSON contém chaves obrigatórias
- Arrays têm mesmo tamanho
- Valores NDVI no intervalo [-1, 1]

---

### 3. **src/polygon_processing.py**
**Responsabilidade**: Processamento geométrico de polígonos

**Funções Principais**:
- `parse_polygon_string()`: Converte string "lon lat, lon lat" em lista de tuplas
- `create_geodataframe()`: Cria estrutura geométrica (GeoDataFrame)
- `calculate_area_hectares()`: Calcula área com projeção de igual-área
- `get_polygon_center()`: Retorna centroide (lat, lon)
- `get_polygon_stats()`: Compila todas as informações

**Sistemas de Coordenadas**:
- **EPSG:4326** (WGS84): Entrada e visualização (lat/lon global)
- **EPSG:6933** (South America Equidistant): Cálculo de área (igual-área)

**Conversão de Coordenadas**:
```
String de entrada: "-58.914 -13.507, -58.865 -13.513"
                            ↓
Lista de tuplas: [(-58.914, -13.507), (-58.865, -13.513)]
                            ↓
GeoDataFrame (WGS84)
                            ↓
Reprojeção para EPSG:6933 (cálculo de área)
                            ↓
Resultado: área em hectares
```

---

### 4. **src/ndvi_analysis.py**
**Responsabilidade**: Análise temporal de séries NDVI

**Funções Principais**:
- `identify_peaks()`: Detecta máximos locais (picos de vegetação)
- `extract_annual_metrics()`: Calcula min/média/max por ano

**Lógica de Detecção de Picos**:
- **Critério**: Proeminência (prominence = 0.08)
- **Significado**: Pico deve estar ≥0.08 acima do vale adjacente
- **Interpretação**: Momento de máximo vigor vegetativo (crescimento)

**Saída Típica de Métricas Anuais**:
```
year  mean_ndvi  max_ndvi  min_ndvi
2000      0.612     0.845     0.234
2001      0.618     0.852     0.241
...
2026      0.620     0.860     0.240
```

---

### 5. **src/map_generator.py**
**Responsabilidade**: Criação de visualizações cartográficas

**Funções Principais**:
- `get_color_for_ndvi()`: Mapeia NDVI para cor (5 escalas)
- `create_interactive_map()`: Cria mapa base com polígono
- `create_full_featured_map()`: Mapa completo com todos recursos

**Esquema de Cores (NDVI → RGB)**:
```
0.0 - 0.3:   #8B4513  (Marrom escuro - Vegetação muito baixa)
0.3 - 0.5:   #CD853F  (Marrom claro - Vegetação esparsa)
0.5 - 0.7:   #ADFF2F  (Amarelo-verde - Vegetação moderada)
0.7 - 0.85:  #32CD32  (Verde claro - Vegetação alta)
0.85 - 1.0:  #006400  (Verde escuro - Vegetação densa)
```

**Recursos do Mapa**:
- Polígono colorido (representa saúde da vegetação)
- Marcador no centroide
- Popup com informações (área, NDVI médio, período)
- Controle de camadas
- Botão de tela cheia

---

## 🔄 Fluxo de Dados Integrado

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT_APP.PY                          │
│                  (Orquestrador Principal)                    │
└──────────────────┬────────────────────────────────────────────┘
                   │
        ┌──────────┼──────────┬──────────────────────┐
        │          │          │                      │
        ▼          ▼          ▼                      ▼
   ┌────────┐ ┌──────────┐ ┌─────────┐    ┌──────────────┐
   │ DATA   │ │ POLYGON  │ │ NDVI    │    │ MAP          │
   │PROCESS │ │PROCESSING│ │ANALYSIS │    │GENERATOR     │
   └────┬───┘ └──────┬───┘ └────┬────┘    └──┬───────────┘
        │           │           │           │
        │ (JSON)    │ (coords)  │ (series)  │ (gdf)
        │           │           │           │
        ▼           ▼           ▼           ▼
   ┌─────────────────────────────────────────────────┐
   │   COMPONENTES VISUAIS STREAMLIT                 │
   ├─────────────────────────────────────────────────┤
   │  1. Seletor de Idioma                           │
   │  2. Mapa Interativo (Folium)                    │
   │  3. Gráfico de Série Temporal (Plotly)          │
   │  4. Gráfico de Tendências Anuais (Plotly)       │
   │  5. Rodapé com Informações do Criador           │
   └─────────────────────────────────────────────────┘
```

---

## 📊 Ciclo de Análise

### Fase 1: Exploração Visual (Mapa Interativo)
- Usuário seleciona uma data
- Visualiza NDVI naquele momento específico
- Cores indicam saúde da vegetação
- Util para ver dinâmica sazonal

### Fase 2: Análise Temporal (Série Histórica)
- Mostra série de 26 anos
- Detecta picos (máximos de vegetação)
- Mostra limites de anos com linhas vermelhas
- Permite zoom em anos específicos

### Fase 3: Síntese Anual (Tendências)
- Compara anos diferentes
- Identifica tendências de longo prazo
- Detecta padrões degradação/intensificação
- Mostra min/média/max por ano

---

## 🧮 Cálculos Importantes

### Cálculo de Área
```python
# 1. Entrada: Polígono em WGS84 (lat/lon)
# 2. Reprojeção para EPSG:6933 (projeção de igual-área)
# 3. Cálculo de área em m²
# 4. Conversão: m² → hectares (÷ 10000)
```

### Detecção de Picos
```python
# Usa scipy.signal.find_peaks com prominence
# prominence = altura do pico acima do vale adjacente
# Valor default: 0.08
# Significa: pico deve estar ≥0.08 acima da linha base local

Exemplo:
Série: [0.3, 0.4, 0.6, 0.5, 0.3, 0.4, 0.7, 0.5]
              ↑ pico em 0.6   ↑ pico em 0.7
            índice: 2          índice: 6
```

### Métricas Anuais
```python
# Para cada ano (por ex: 2000):
# - mean_ndvi = média de todos os valores NDVI em 2000
# - max_ndvi = maior valor NDVI em 2000 (pico)
# - min_ndvi = menor valor NDVI em 2000 (vale)
```

---

## 🎛️ Configurações Principais

### Idiomas Suportados
- **Português** (pt): Interface em português
- **Inglês** (en): Interface em inglês

### Parâmetros de Análise
- **Prominence (picos)**: 0.08 (ajustável em `identify_peaks`)
- **Zoom inicial (mapa)**: 13 (médio, bom para visualizar local)
- **Intervalo NDVI válido**: [-1.0, 1.0]
- **Período de dados**: 2000-2026 (26 anos)

### Sistemas de Cores
- 5 escalas de cores (marrom → verde)
- Baseado em valor NDVI atual
- Facilita reconhecimento visual instantâneo

---

## 🔍 Tratamento de Erros

### Erros de Carregamento de Dados
- Arquivo não existe → `FileNotFoundError`
- JSON inválido → `ValueError`
- Arrays incompatíveis → `ValueError`

### Erros de Processamento de Polígono
- String de coordenadas inválida → `ValueError`
- Menos de 3 vértices → `ValueError`
- Geometria inválida → `ValueError`

### Validações de Dados
- NDVI fora de [-1, 1] → removido
- Valores NaN → removidos
- Datas duplicadas → mantidas (série histórica)

---

## 🚀 Performance e Otimizações

### Caching de Dados
```python
@st.cache_resource
def load_all_data():
    # Carrega dados uma vez e reutiliza
    # Melhora desempenho drasticamente
```

### Renderização Responsiva
- Mapa 100% da largura/altura
- Gráficos adaptam-se ao tamanho da tela
- Mobile-friendly com `prefer_canvas=True`

### Agregações de Dados
- Opção de resample para média mensal
- Reduz ruído em visualizações

---

## 📈 Exemplos de Uso

### Carregar e Processar Dados
```python
from src.data_processing import load_ndvi_data, get_data_summary
df = load_ndvi_data("data/ndvi_timeseries.json")
stats = get_data_summary(df)
print(f"Observações: {stats['n_observations']}")
```

### Processar Polígono
```python
from src.polygon_processing import parse_polygon_string, create_geodataframe
coords = parse_polygon_string("-58.914 -13.507,-58.865 -13.513")
gdf = create_geodataframe(coords)
```

### Análise NDVI
```python
from src.ndvi_analysis import identify_peaks, extract_annual_metrics
peaks = identify_peaks(df["ndvi"].values)
annual = extract_annual_metrics(df)
```

### Criar Mapa
```python
from src.map_generator import create_full_featured_map
m = create_full_featured_map(gdf, center, mean_ndvi=0.65, area_ha=150)
m.save('mapa.html')
```

---

## 📝 Notas Técnicas

### Por Que EPSG:6933?
- É uma projeção de **igual-área** (não distorce áreas)
- Apropriada para América do Sul
- Garante cálculos de área precisos

### Por Que Prominence?
- Melhor que simples busca de máximos
- Evita detecção de ruído como picos
- Parâmetro ajustável conforme necessidade

### Estrutura Dual-Language
- Dicionário centralizado `STRINGS`
- Facilita manutenção e tradução
- Estado persiste na sessão Streamlit

---

## 🔧 Extensões Futuras

1. **Exportar Relatórios**: PDF com gráficos e análises
2. **Comparação Multi-Polígono**: Análise de múltiplas áreas simultâneas
3. **Previsões**: ML para prever NDVI futuro
4. **API REST**: Servir dados via API
5. **Dados Adicionais**: Incluir temperatura, precipitação
6. **Análise Espectral**: Adicionar outras bandas (EVI, LAI)

