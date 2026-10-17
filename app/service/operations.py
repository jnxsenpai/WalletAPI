from fastapi import HTTPException

from app.schemas import OperationRequest
from app.repository import wallets as wallets_repository

def add_income(operation: OperationRequest):
    if not wallets_repository.is_wallet_exist(operation.wallet_name):
        raise HTTPException(
            status_code=404,
            detail=f"Wallet {operation.wallet_name} not found"
        )


    new_balance = wallets_repository.add_income(operation.wallet_name, operation.amount)

    return {
        "message": f"Wallet {operation.wallet_name} income added",
        "wallet": operation.wallet_name,
        "amount": operation.amount,
        "new_balance": new_balance,
        "description": operation.description
    }

def add_expense(operation: OperationRequest):
    if not wallets_repository.is_wallet_exist(operation.wallet_name):
        raise HTTPException(
            status_code=404,
            detail=f"Wallet {operation.wallet_name} not found"
        )

    balance = wallets_repository.get_wallet_balace_by_name(operation.wallet_name)

    if balance < operation.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds. Available: {balance}"
        )

    new_balance = wallets_repository.add_expense(operation.wallet_name, operation.amount)

    return {
        "message": f"Expense {operation.wallet_name} added",
        "wallet": operation.wallet_name,
        "amount": operation.amount,
        "new_balance": new_balance,
        "description": operation.description
    }