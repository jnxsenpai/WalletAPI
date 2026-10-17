from fastapi import HTTPException

from app.schemas import CreateWalletRequest
from app.repository import wallets as wallets_repository

def get_wallet(wallet_name: str | None = None):
    # Если имя не указано - считаем общий баланс
    if wallet_name is None:
        wallets = wallets_repository.get_all_wallets()
        return {"total_balace": sum(wallets.values())}
    # Проверяем существуем ли кошелек
    if not wallets_repository.is_wallet_exist(wallet_name):
        raise HTTPException(
            status_code=404,
            detail=f"Wallet {wallet_name} not found"
        )
    # Возвращаем баланс конкретного кошелька
    balance = wallets_repository.get_wallet_balace_by_name(wallet_name)
    return {"wallet": wallet_name, "balance": balance}

def create_wallet(wallet: CreateWalletRequest):
    if wallets_repository.is_wallet_exist(wallet.name):
        raise HTTPException(
            status_code=400,
            detail=f"Wallet {wallet.name} already exists"
        )
    # Создаем кошелек с начальным балансом
    new_balance = wallets_repository.create_wallet(wallet.name, wallet.initial_balance)
    # Возвращаем информацию
    return {
        "message": f"Wallet {wallet.name} created",
        "wallet": wallet.name,
        "balance": new_balance
    }