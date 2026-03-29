# 📚 GUIA DE REFERÊNCIA RÁPIDA

## 🎯 O que Este Dashboard Faz?

Este dashboard analisa **26 anos de dados NDVI** (Índice de Vegetação por Diferença Normalizada) de uma área agrícola. O NDVI é um número entre -1 e 1 que indica quão verde e saudável está a vegetação.

**Interpretação de NDVI**:
- 🟫 **0.0-0.3**: Pouca ou nenhuma vegetação (marrom)
- 🟫 **0.3-0.5**: Vegetação esparsa (marrom claro)
- 🟨 **0.5-0.7**: Vegetação moderada (amarelo-verde)
- 🟩 **0.7-0.85**: Vegetação densa (verde claro)
- 🟢 **0.85-1.0**: Muito densa e saudável (verde escuro)

---

## 🔑 Conceitos Principais

### O que é um Pico de Vegetação?
Um **pico** é um máximo local onde a vegetação atinge seu vigor máximo. Geralmente corresponde a:
- Momento em que a cultura está na sua fase de maior crescimento
- Melhor período para monitorar produtividade
- Transição entre fases do ciclo de cultivo

### O que Significa cada Métrica Anual?

| Métrica | Significado |
|---------|-----------|
| **NDVI Máximo** | Melhor momento do ano para vegetação |
| **NDVI Médio** | Saúde geral/típica da vegetação no ano |
| **NDVI Mínimo** | Pior momento do ano (seca/repouso) |

---

## 📂 Módulos Explicados

### 1️⃣ data_processing.py - Processamento de Dados

**O que faz**: Carrega e valida dados do arquivo JSON

**Funções úteis**:
```python
# Carregar dados
df = load_ndvi_data("arquivo.json")

# Limpar valores ruins (opcional)
df_limpo = clean_ndvi_data(df)

# Obter estatísticas
stats = get_data_summary(df)
print(f"NDVI médio: {stats['mean_ndvi']:.3f}")
print(f"Período: {stats['date_range']}")
```

**Validações automáticas**:
- ✅ Arquivo existe?
- ✅ JSON tem estrutura correta?
- ✅ Arrays têm mesmo tamanho?
- ✅ NDVI está entre -1 e 1?

---

### 2️⃣ polygon_processing.py - Processamento de Polígonos

**O que faz**: Processa as coordenadas e calcula propriedades geométricas

**Funções úteis**:
```python
# Converter string de coordenadas
coords = parse_polygon_string("-58.914 -13.507,-58.865 -13.513")

# Criar estrutura geométrica
gdf = create_geodataframe(coords)

# Calcular área
area_ha = calculate_area_hectares(gdf)
print(f"Área: {area_ha:.2f} hectares")

# Obter centro (útil para mapa)
center = get_polygon_center(gdf)  # (latitude, longitude)

# Compilar estatísticas
stats = get_polygon_stats(gdf, mean_ndvi=0.65)
```

**Coordenadas**: Sempre em formato **latitude/longitude** (válido globalmente, WGS84)

---

### 3️⃣ ndvi_analysis.py - Análise de NDVI

**O que faz**: Encontra padrões e calcula métricas na série temporal

**Funções úteis**:
```python
# Encontrar picos (momentos de máximo vigor)
picos = identify_peaks(df["ndvi"].values, prominence=0.08)
print(f"Encontrados {len(picos)} picos")

# Calcular estatísticas anuais
annual = extract_annual_metrics(df)
print(annual)
#    year  mean_ndvi  max_ndvi  min_ndvi
# 0  2000      0.612     0.845     0.234
# 1  2001      0.618     0.852     0.241
```

**Parâmetro Prominence**: Quanto maior, menos picos são detectados


---

### 4️⃣ map_generator.py - Geração de Mapas

**O que faz**: Cria mapas interativos coloridos com Folium

**Funções úteis**:
```python
# Mapear NDVI para cor
cor = get_color_for_ndvi(0.65)  # Retorna "#32CD32" (verde claro)

# Criar mapa completo
mapa = create_full_featured_map(
    gdf,              # Dados geométricos
    center,           # (latitude, longitude)
    mean_ndvi=0.65,   # Para colorir polígono
    area_ha=150.5     # Para popup
)

# Salvar como HTML
mapa.save('mapa.html')
```

**Recursos do Mapa**:
- 🗺️ Polígono colorido
- 🔵 Marcador no centro
- ℹ️ Popup com informações
- 🎫 Controle de camadas

---

### 5️⃣ streamlit_app.py - Aplicação Principal

**O que faz**: Integra tudo e cria interface visual interativa

**Seções principais**:
1. **Seletor de Idioma** (PT/EN)
2. **Mapa Interativo** com escolha de data
3. **Gráfico de Série Temporal** com picos
4. **Gráfico de Tendências Anuais**
5. **Informações do Criador**

**Como executar**:
```bash
streamlit run streamlit_app.py
```

---

## 🎨 Interpretando Cores

Quando você vê o polígono no mapa, a cor indica algo:

```
┌─────────────────────────────────────────┐
│  COR               NDVI    SIGNIFICADO   │
├─────────────────────────────────────────┤
│  🟫 Marrom Escuro  0.0-0.3  Seco/Vazio  │
│  🟫 Marrom Claro   0.3-0.5  Pouco verde │
│  🟨 Amarelo-Verde  0.5-0.7  Verde OK    │
│  🟩 Verde Claro    0.7-0.85 Muito verde │
│  🟢 Verde Escuro   0.85-1.0 Máximo vigor│
└─────────────────────────────────────────┘
```

---

## 📊 Interpretando Gráficos

### Série Temporal (Linha Azul)
- **Sobe**: Vegetação está crescendo (estação chuvosa/plantio)
- **Desce**: Vegetação reduzindo (seca/colheita)
- ⭐ **Estrelas vermelhas**: Picos = momentos de máximo vigor

### Tendências Anuais (Gráfico preenchido)
- **Verde escuro**: Marca NDVI médio anual (principal métrica)
- **Linha tracejada superior**: Máximo do ano
- **Linha tracejada inferior**: Mínimo do ano

**Interpretação**:
- Linha subindo? → Vegetação melhorando ao longo dos anos
- Linha descendo? → Sinal possível de degradação
- Picos altos? → Bom desempenho produtivo

---

## 🔍 Exemplos Práticos de Interpretação

### Exemplo 1: Ciclo Agrícola Claro
```
NDVI alto (0.8-0.9)    ⭐ Pico detectado aqui
    │                      ↑
    │                      │
    var               Crescimento máximo
    │                      │
    │ ╱╲ ╱╲ ╱╲           │
    │ ╱  ╲╱  ╱           │
    │                  Colheita aqui
   └──────────────────────→ tempo

Interpretação: Duas safras por ano (duas estações de crescimento)
```

### Exemplo 2: Mudança de Uso (Degradação)
```
Série completa (2000-2026):
0.8 │     ╱╲    ╱╲    ╱╲
    │    ╱  ╲  ╱  ╲  ╱  ╲
0.6 │   ╱    ╳    ╲╱    ╲╱    ← Picos ficam menores
    │
0.4 │
   └────────────────────────→ anos

Interpretação: Vegetação degradando ao longo do tempo
```

---

## ✅ Checklist de Funcionalidades

### Mapa Interativo
- [x] Mudar data e ver NDVI atualizar
- [x] Clicar no polígono para ver informações
- [x] Polígono muda cor com NDVI
- [x] Zoom e pan do mapa funcionam

### Série Temporal
- [x] Mostra 26 anos de dados
- [x] Detecta e marca picos
- [x] Permite zoom em anos específicos
- [x] Mostra limites de anos

### Métricas Anuais
- [x] Calcula min/média/max por ano
- [x] Mostra tendência visual
- [x] Permite comparação entre anos

### Idioma
- [x] Português completo
- [x] Inglês completo
- [x] Muda conforme seleção

---

## 🐛 Resolvendo Problemas Comuns

### Mapa não aparece?
- Verificar se `geodataframe` está válido
- Coordenadas devem estar em WGS84 (lat/lon)
- Polígono precisa ter pelo menos 3 vértices

### Picos não aparecem?
- Aumentar `prominence` (menos picos)
- Diminuir `prominence` (mais picos)
- Série precisa ter pelo menos 5 pontos

### Dados não carregam?
- Arquivo JSON existe?
- JSON tem `listaSerie` e `listaDatas`?
- Arrays têm mesmo tamanho?

### Área calcula errada?
- Verificar se polígono é válido
- Coordenadas devem estar em WGS84
- Usar EPSG:6933 para cálculo (já automático)

---

## 📞 Referência de Funções

| Módulo | Função | Entrada | Saída |
|--------|--------|---------|-------|
| `data_processing` | `load_ndvi_data()` | caminho JSON | DataFrame |
| `polygon_processing` | `parse_polygon_string()` | string coords | lista tuplas |
| `polygon_processing` | `calculate_area_hectares()` | GeoDataFrame | float (ha) |
| `ndvi_analysis` | `identify_peaks()` | array NDVI | lista índices |
| `ndvi_analysis` | `extract_annual_metrics()` | DataFrame | DataFrame anual |
| `map_generator` | `get_color_for_ndvi()` | float NDVI | string hex |
| `map_generator` | `create_full_featured_map()` | GeoDataFrame + dados | Folium.Map |

---

## 🎓 Aprendendo Mais

### Sobre NDVI
- NDVI = (NIR - RED) / (NIR + RED)
- Desenvolvido para distinguir vegetação de outros materiais
- Padrão em análises agrícolas e ambientais

### Sobre Geopandas
- Estende Pandas com operações geométricas
- Permite projeções e transformações de coordenadas
- Integra-se com Shapely para geometrias

### Sobre Folium
- Cria mapas interativos com Leaflet.js
- Baseado em OpenStreetMap por padrão
- Suporta múltiplos tipos de camadas

---

## 📝 Dicas de Uso

1. **Para Agricultura**: Compare anos safra para safra
2. **Para Monitoramento**: Procure quedas abruptas (problemas)
3. **Para Planejamento**: Use picos para identificar períodos ótimos
4. **Para Pesquisa**: Exporte dados anuais para análises estatísticas

---

