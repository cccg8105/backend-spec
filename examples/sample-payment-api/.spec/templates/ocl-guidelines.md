# Guía y Estándar de OCL (Object Constraint Language) para backend-spec

Este documento define el subconjunto formal y práctico de **Object Constraint Language (OCL)** adoptado por `backend-spec` para eliminar la ambigüedad en contratos de negocio, precondiciones, postcondiciones e invariantes de dominio.

---

## 1. Subconjunto de Sintaxis Autorizado para Backend

Para mantener la máxima claridad y facilidad de traducción a código por cualquier LLM, se utiliza el siguiente subconjunto estándar:

| Elemento OCL | Ámbito | Significado y Traducción a Código |
| :--- | :--- | :--- |
| `context [Tipo]::[operación]` | Operación | Ámbito del método, caso de uso o entidad. |
| `pre [Nombre]: [expresión]` | Precondición | Condición que **DEBE** cumplirse antes de ejecutar. Se traduce a validaciones `if (!cond) throw new Error(...)`. |
| `post [Nombre]: [expresión]` | Postcondición | Estado que **DEBE** cumplirse al finalizar. Se traduce a aserciones de prueba unitaria `expect(...)`. |
| `inv [Nombre]: [expresión]` | Invariante | Condición permanente de una entidad. Se traduce a validaciones en el constructor y setters de la entidad de dominio. |
| `@pre` | Expresión | Valor de un atributo antes de la ejecución de la operación (ej. `self.balance = self.balance@pre - amount`). |
| `implies` | Lógica | Implicación (A → B). Si A es verdadero, B debe ser verdadero. |
| `self` | Instancia | Referencia a la instancia de la clase actual. |
| `->forAll(x \| ...)` | Colecciones | Valida que todos los elementos de una colección cumplan una condición. |
| `->exists(x \| ...)` | Colecciones | Valida que al menos un elemento cumpla la condición. |

---

## 2. Ejemplos Prácticos de Traducción

### A. Precondiciones y Postcondiciones en Casos de Uso (`docs/functional/use-cases/`)

#### En la especificación OCL:
```ocl
context TransferService::execute(source: Account, target: Account, amount: Decimal)
pre PositiveAmount: 
    amount > 0
pre SameCurrency: 
    source.currency = target.currency
pre SufficientFunds: 
    source.balance >= (amount + self.calculateFee(amount))
pre TargetActive: 
    target.status = AccountStatus::ACTIVE
post SourceDebited: 
    source.balance = source.balance@pre - (amount + self.calculateFee(amount))
post TargetCredited: 
    target.balance = target.balance@pre + amount
```

#### Traducción generada en el Caso de Uso (`src/application/`):
```typescript
if (amount <= 0) throw new InvalidAmountError('El monto debe ser positivo');
if (source.currency !== target.currency) throw new CurrencyMismatchError();
const fee = this.calculateFee(amount);
if (source.balance < amount + fee) throw new InsufficientFundsError();
if (target.status !== AccountStatus.ACTIVE) throw new TargetAccountInactiveError();

source.balance -= (amount + fee);
target.balance += amount;
```

#### Traducción generada en Pruebas Unitarias (`tests/unit/`):
```typescript
it('debe cumplir con la postcondición SourceDebited y TargetCredited', async () => {
  const initialSourceBalance = source.balance;
  const initialTargetBalance = target.balance;
  
  await transferService.execute(source, target, 100);
  
  expect(source.balance).toBe(initialSourceBalance - 102); // 100 + 2 de comisión
  expect(target.balance).toBe(initialTargetBalance + 100);
});
```

---

### B. Invariantes de Entidad en Diseño Técnico (`docs/technical/component-design.md`)

#### En la especificación OCL:
```ocl
context Account
-- El saldo real nunca puede ser inferior al límite de sobregiro
inv ValidEffectiveBalance:
    self.balance >= -self.overdraftLimit

-- Cuentas congeladas o cerradas son inmutables en balance
inv FrozenAccountBalanceImmutable:
    (self.status = AccountStatus::FROZEN or self.status = AccountStatus::CLOSED) 
    implies self.balance = self.balance@pre
```

#### Traducción generada en la Entidad de Dominio (`src/domain/`):
```typescript
export class Account {
  private validateInvariants(): void {
    if (this.balance < -this.overdraftLimit) {
      throw new DomainInvariantViolationError('El saldo supera el límite de sobregiro permitido');
    }
  }

  public debit(amount: number): void {
    if (this.status === AccountStatus.FROZEN || this.status === AccountStatus.CLOSED) {
      throw new AccountNotOperableError('Cuenta inactiva');
    }
    this.balance -= amount;
    this.validateInvariants();
  }
}
```
