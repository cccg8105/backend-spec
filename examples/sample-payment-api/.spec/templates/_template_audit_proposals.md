# Molde de Referencia: Propuesta de Auditoría y Deuda Técnica
*Este documento reside en `.spec/templates/_template_audit_proposals.md` como blueprint del agente.*

```markdown
### [AUDIT-[DOMINIO]-[NUMERO]] [Título conciso del hallazgo o deuda técnica]
- **Dominio:** `[dominio]`
- **Categoría:** [Deuda Técnica | Seguridad | Concurrencia | Doc Drift | Brecha de Tests | Código Muerto]
- **Severidad Sugerida:** [P1 (Crítica) | P2 (Media) | P3 (Baja)]
- **Impacto Estimado:** [MAJOR | MINOR | PATCH]
- **Evidencia en Código:** `[ruta/al/archivo.ext:L10-L25]`
- **Estado:** [Propuesto | Promovido a REQ-... | Descartado]

#### Descripción del Hallazgo:
[Explicación objetiva y fundamentada en código. ¿Por qué es un problema o discrepancia frente a la arquitectura/documentación?]

#### Propuesta de Remediación:
[Breve recomendación técnica de cómo abordarlo cuando se decida promover a un requerimiento formal en pending.md.]
```
