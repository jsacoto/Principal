# Motor matemático

## Capa 1 — Madurez Estructural

`C_d = Σ(E_i · I_i,d) / Σ(I_i,d)`

`M_d = 5 · C_d`

`IGMD = Σ(v_d · M_d)` con `Σv_d = 1`.

Niveles: Inicial ≤1.0; Emergente >1.0–2.5; En desarrollo >2.5–3.5; Avanzado >3.5–4.5; Transformador >4.5–5.0.

## Capa 2 — Cumplimiento Estratégico

Crecimiento/logro: `c_kr = min(1, x/m)`.

Reducción expresada como reducción lograda: `c_kr = min(1, r/r*)`.

El motor soporta también `lower_is_better = min(1, target/current)` cuando el KR se almacena como nivel bruto a reducir.

`O_o = Σ(w_kr · c_kr)` y `IOC = Σ(α_o · O_o)`; `IOC(5)=5·IOC`.

## Capa 3 — Desempeño Operativo

Mayor es mejor: `n_k = min(1, x/m)`.

Menor es mejor: `n_k = min(1, m/x)`.

`IKO = Σ(β_k · n_k)`; `IKO(5)=5·IKO`.

## Índice Global

`IGTD = λ1·IGMD + λ2·IOC(5) + λ3·IKO(5)`

Configuración estándar: `λ=(0.50, 0.30, 0.20)`.

## Sensibilidad

`ΔM_d / ΔE_i = 5·I_i,d / ΣI_i,d`.

La priorización selecciona iniciativas con contribución 2 o 3 en dimensiones bajo 3.0 y KRs bajo 0.60.

Implementación: `apps/api/app/engine.py`.
