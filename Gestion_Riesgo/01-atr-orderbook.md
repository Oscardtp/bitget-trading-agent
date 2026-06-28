# Gestión Dinámica: ATR + Order Book

**Tipo:** Adaptativa
**Uso:** Ajustar SL/TP según volatilidad y liquidez real

---

## 1. Análisis de Contexto

### ATR – Rango Promedio Verdadero

Calcula ATR(5) para evaluar volatilidad reciente:

| ATR Nivel | Interpretación | Acción |
|---|---|---|
| Bajo (≤ 0.8%) | Movimiento limitado | SL más ajustado, TP más corto |
| Medio (0.8%–1.2%) | Condición estándar | SL/TP normales |
| Alto (≥ 1.2%) | Movimiento agresivo | SL más amplio, TP más ambicioso |

### Order Book – Presión de Liquidez

| Situación | Implicación | Acción |
|---|---|---|
| Ask wall fuerte arriba | Resistencia alta | TP justo antes de la pared |
| Bid wall fuerte abajo | Soporte potencial | SL detrás del muro |
| Poco volumen cercano | Riesgo de slippage | SL más conservador |

---

## 2. Cálculo de SL y TP

```python
# Supongamos:
ATR_5 = 1.0  # volatilidad moderada
Entry = 100.00

# Estrategia adaptativa:
if ATR_5 <= 0.8:
    TP_pct = 1.3
    SL_pct = 0.8
elif ATR_5 > 1.2:
    TP_pct = 1.8
    SL_pct = 1.2
else:
    TP_pct = 1.5
    SL_pct = 1.0

TP = Entry * (1 + TP_pct / 100)
SL = Entry * (1 - SL_pct / 100)
```

---

## 3. Ajuste por Order Book

### TP final
- Si hay ask wall justo antes del TP calculado → recortar al precio antes del muro
- Si hay poca liquidez → TP puede mantenerse o ampliarse

### SL final
- Colocar justo detrás del bid wall más relevante
- O bajo el último swing técnico + buffer
- Evitar zonas con vacíos de órdenes

---

## 4. Trailing Stop Inteligente

| Condición | Acción |
|---|---|
| Gana +0.8% | Mover SL a Break Even (BE) |
| Gana +1.2% | SL a +0.3% o bajo último HL |
| Gana +1.6% | SL a +0.6% o trailing dinámico (0.5% detrás del precio) |

---

## Ejemplo: BTC/USDT

| Parámetro | Valor |
|---|---|
| Entrada | $65,000 |
| ATR(5) | 0.75% (volatilidad baja) |
| Ask wall | $65,800 |
| Bid wall | $64,400 |
| TP calculado | $65,845 → ajustado a $65,790 (antes de ask wall) |
| SL calculado | $64,480 → ajustado a $64,350 (detrás de bid wall) |
| R:R aproximado | 2.0:1 con trailing activo |

---

## Resumen del Sistema

| Elemento | Basado en | Acción |
|---|---|---|
| SL inicial | ATR + Bid wall | SL técnico, no emocional |
| TP inicial | ATR + Ask wall | TP realista, no imaginado |
| Trailing Stop | % ganancia o HL | Dinámico, asegura ganancias |
| Stop técnico | Último HL o detrás de pared | A prueba de liquidez falsa |
| Volumen como filtro | Confirmar validez | Sin volumen → no mover SL/TP |

---

## Checklist

- [ ] ATR(5) calculado
- [ ] Order Book analizado (paredes identificadas)
- [ ] TP ajustado según ask wall
- [ ] SL ajustado según bid wall
- [ ] Trailing stop planificado
- [ ] R:R ≥ 2:1
