# Plantilla BDD Bridge: Scaffolding de Tests Unitarios Spec-First

Esta plantilla estandariza la generación de pruebas antes de codificar la solución, vinculando cada test a las reglas de negocio del caso de uso o al bug reproducido en modo *Fast-Track (`PATCH`)*.

## Ejemplo en TypeScript (Vitest / Jest)

```typescript
import { describe, it, expect, beforeEach } from 'vitest';

/**
 * @spec UC-[DOMAIN]-[ID]
 * @req REQ-[DOMAIN]-[ID]
 */
describe('UseCase: [Nombre del Caso de Uso]', () => {
  beforeEach(() => {
    // 1. Configuración de mocks e inyección de dependencias
  });

  describe('Contratos y Flujo Principal', () => {
    it('debe ejecutar exitosamente cuando los inputs son válidos', async () => {
      expect(true).toBe(false); // Estado inicial RED
    });
  });

  describe('Reglas de Negocio Invariantes', () => {
    /**
     * @businessRule BR-01
     */
    it('debe hacer cumplir la regla [BR-01]: [Descripción corta]', async () => {
      expect(true).toBe(false); // Estado inicial RED
    });
  });
});
```

## Ejemplo en Python (`pytest` / `unittest`)

```python
import pytest

# @spec UC-[DOMAIN]-[ID]
# @req REQ-[DOMAIN]-[ID]
class TestUseCaseSpec:
    def test_valid_execution(self):
        assert False, "Estado inicial RED"

    # @businessRule BR-01
    def test_business_rule_br01(self):
        assert False, "Estado inicial RED"
```
