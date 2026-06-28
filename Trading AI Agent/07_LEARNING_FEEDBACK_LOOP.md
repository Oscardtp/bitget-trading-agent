# Learning Feedback Loop

> 📄 **Módulo:** `07_LEARNING_FEEDBACK_LOOP.md`

## 🧠 Propósito

Este módulo tiene como objetivo utilizar la información histórica registrada por el sistema para mejorar progresivamente la toma de decisiones futuras.

El aprendizaje debe ser:

- Supervisado.
- Trazable.
- Reversible.
- Basado en evidencia estadística.

El sistema **NO** debe modificar su comportamiento basándose únicamente en resultados aislados.

---

## 🎯 Objetivos del módulo

El sistema debe ser capaz de:

- Detectar degradación de estrategias.
- Identificar fortalezas y debilidades.
- Ajustar pesos del motor de scoring.
- Optimizar parámetros de riesgo.
- Reconocer cambios en el comportamiento del mercado.
- Generar recomendaciones de mejora.
- Mantener un historial de todas las modificaciones realizadas.

---

## 🔗 Dependencias

Este módulo utiliza la información almacenada por:

- `06_LOGGING_SCHEMA.md`

Y genera actualizaciones para:

- `02_STRATEGY_SELECTOR.md`
- `03_RISK_ENGINE.md`
- Dashboards y reportes del sistema.

---

## 🗂️ Principios de aprendizaje

### Evidencia antes que intuición
- Las modificaciones del sistema deben estar respaldadas por datos.
- Nunca modificar parámetros por percepciones subjetivas.

### Cambios graduales
- Los ajustes deben realizarse en pequeños incrementos.
- Evitar cambios bruscos.

### Reversibilidad
- Toda modificación debe poder deshacerse.
- Debe existir un historial de versiones.

### Estabilidad
- El sistema debe priorizar robustez sobre optimización extrema.
- Evitar sobreajuste (*overfitting*).

---

## 📊 Frecuencia de evaluación

Dependiendo de la estrategia utilizada:

- **Scalping:** Cada 100–200 operaciones cerradas.
- **Swing Trading:** Mensualmente o cada 20–50 operaciones.
- **Breakout:** Cada 50–100 señales evaluadas.
- **Mean Reversion:** Cada 50–100 eventos similares.

---

## 📈 Métricas analizadas

### Rendimiento
- Win Rate
- Profit Factor
- Expectancy
- Net Profit
- Average Trade

### Riesgo
- Maximum Drawdown
- Recovery Factor
- Risk of Ruin
- Consecutive Losses

### Ejecución
- Slippage promedio
- Comisiones promedio
- Tasa de rechazo
- Latencia promedio

### Estrategias
- PnL por estrategia
- Win Rate por estrategia
- Profit Factor por estrategia
- Drawdown por estrategia

### Contexto de mercado
- Rendimiento por tendencia
- Rendimiento por volatilidad
- Rendimiento por sesión
- Rendimiento por liquidez

---

## 🔍 Detección de degradación

**🧠 Objetivo**
Identificar cuándo una estrategia deja de comportarse como históricamente lo hacía.

**🚨 Señales de alerta**
- **Profit Factor:** `PF actual < PF histórico × 0.80`
- **Drawdown:** `DD actual > DD histórico × 1.50`
- **Win Rate:** `WR actual < WR histórico − 10%`

**⚡ Acción**
1. Marcar estrategia para revisión.
2. Reducir exposición temporalmente.

---

## ⚙️ Ajuste de pesos del Strategy Selector

**🧠 Objetivo**
Actualizar la importancia relativa de cada variable.

**Variables ajustables**
- Volumen
- Volatilidad
- Liquidez
- Spread
- Sentimiento
- Tendencia

**Restricción**
Cada ajuste individual no debe exceder: `±5%` por ciclo de revisión.

**Ejemplo**

*Antes:*
```json
{
  "breakout": {
    "volume": 0.45,
    "volatility": 0.30,
    "liquidity": 0.25
  }
}
```

*Después:*
```json
{
  "breakout": {
    "volume": 0.48,
    "volatility": 0.28,
    "liquidity": 0.24
  }
}
```

---

## 🛡️ Optimización del Risk Engine

**🧠 Objetivo**
Ajustar parámetros sin comprometer la supervivencia del sistema.

**Ajustables**
- Capital allocation
- Stop multipliers
- RR ratios
- Max positions

**Restricción**
Los cambios deben mantenerse dentro de límites predefinidos.

**Ejemplo**
*Capital Allocation:*
- **Mínimo:** `1%`
- **Máximo:** `5%`

---

## 📦 Clasificación de regímenes de mercado

**🧠 Objetivo**
Reconocer patrones recurrentes.

**Regímenes sugeridos**
- Trending Bull
- Trending Bear
- Sideways Low Volatility
- Sideways High Volatility
- Expansion Phase
- Contraction Phase

**Uso**
Evaluar qué estrategias funcionan mejor en cada régimen.

---

## 🧪 Proceso de actualización

1. **Paso 1:** Extraer datos históricos.
2. **Paso 2:** Calcular métricas.
3. **Paso 3:** Comparar contra benchmarks históricos.
4. **Paso 4:** Generar recomendaciones.
5. **Paso 5:** Simular cambios.
6. **Paso 6:** Validar mediante backtest.
7. **Paso 7:** Aplicar cambios aprobados.
8. **Paso 8:** Registrar nueva versión del sistema.

---

## 🗃️ Versionado

Toda actualización debe registrarse.

**Ejemplo:**
```json
{
  "version": "v1.3.2",
  "date": "2026-06-22",
  "changes": [
    "Breakout volume weight +3%",
    "Swing capital allocation -1%"
  ],
  "approved_by": "SYSTEM"
}
```

---

## 📤 Output del módulo

```json
{
  "learning_cycle": "2026-Q2",
  "recommendations": [
    "Reduce breakout exposure by 1%",
    "Increase swing trend weight by 3%"
  ],
  "degraded_strategies": [
    "mean_reversion"
  ],
  "approved_updates": [
    "breakout_weight_adjustment"
  ],
  "new_version": "v1.3.2"
}
```

---

## 🚫 Restricciones obligatorias

- Nunca actualizar parámetros con una muestra insuficiente.
- Nunca optimizar utilizando el mismo conjunto de datos usado para validar.
- Nunca modificar múltiples componentes críticos simultáneamente.
- Nunca eliminar registros históricos.
- Nunca desplegar cambios sin backtest.
- Nunca reemplazar supervisión humana en cambios significativos.