from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator


# инициализация приложения на fastAPI
app = FastAPI()

# Словарь для хранения балансов кошельков

BALANCE = {}


class OperationRequest(BaseModel):
    wallet_name: str = Field(..., max_length=127)
    amount: float
    description: str | None = Field(None, max_length=255)

    @field_validator('amount')
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError(
                "Amount must be greater than 0"
            )
        return v

    @field_validator('wallet_name')
    def wallet_name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Wallet name cannot be empty")
        return v


class CreateWalletRequest(BaseModel):
    name: str = Field(..., max_length=127)
    initial_balance: float = 0

    @field_validator('name')
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name name cannot be empty")
        return v

    @field_validator('initial_balance')
    def initial_balance_not_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError(
                "initial_balance must be greater than 0"
            )
        return v


@app.get("/balance")
def get_balance(wallet_name: str | None = None):
    # Если имя не указано - считаем общий баланс
    if wallet_name is None:
        return {"total_balace": sum(BALANCE.values())}
    # Проверяем существуем ли кошелек
    if wallet_name not in BALANCE:
        raise HTTPException(
            status_code=404,
            detail=f"Wallet {wallet_name} not found"
        )
    # Возвращаем баланс конкретного кошелька
    return {"wallet": wallet_name, "balance": BALANCE[wallet_name]}


@app.post("/wallets")
def create_wallet(wallet: CreateWalletRequest):
    if wallet.name in BALANCE:
        raise HTTPException(
            status_code=400,
            detail=f"Wallet {wallet.name} already exists"
        )
    # Создаем кошелек с начальным балансом
    BALANCE[wallet.name] = wallet.initial_balance
    # Возвращаем информацию
    return {
        "message": f"Wallet {wallet.name} created",
        "wallet": wallet.name,
        "balance": BALANCE[wallet.name]
    }


@app.post("/operations/income")
def add_income(operation: OperationRequest):
    if operation.wallet_name  not in BALANCE:
        raise HTTPException(
            status_code=404,
            detail=f"Wallet {operation.wallet_name} not found"
        )


    BALANCE[operation.wallet_name] += operation.amount

    return {
        "message": f"Wallet {operation.wallet_name} income added",
        "wallet": operation.wallet_name,
        "amount": operation.amount,
        "new_balance": BALANCE[operation.wallet_name],
        "description": operation.description
    }


@app.post("/operations/expense")
def add_expense(operation: OperationRequest):
    if operation.wallet_name  not in BALANCE:
        raise HTTPException(
            status_code=404,
            detail=f"Wallet {operation.wallet_name} not found"
        )

    if operation.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"Amount must be greater than 0"
        )

    if BALANCE[operation.wallet_name] < operation.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds. Available: {BALANCE[operation.wallet_name]}"
        )

    # Вычитаем расход из баланса кошелька
    BALANCE[operation.wallet_name] -= operation.amount

    return {
        "message": f"Expense {operation.wallet_name} added",
        "wallet": operation.wallet_name,
        "amount": operation.amount,
        "new_balance": BALANCE[operation.wallet_name],
        "description": operation.description
    }
