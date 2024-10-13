from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic_settings import BaseSettings
from datetime import datetime, timedelta
from typing import List
import plaid_service
from fastapi import FastAPI, HTTPException
import plaid_service

app = FastAPI(title="Moneywise")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class LinkTokenResponse(BaseSettings):
    link_token: str

class PublicTokenExchange(BaseSettings):
    public_token: str

class AccessTokenResponse(BaseSettings):
    access_token: str

class Transaction(BaseSettings):
    id: str
    amount: float
    date: str
    name: str
    category: List[str]

class Account(BaseSettings):
    id: str
    name: str
    type: str
    subtype: str
    balance: float

@app.post("/create_link_token", response_model=LinkTokenResponse)
async def create_link_token():
    try:
        link_token = plaid_service.create_link_token("test_user_id")
        return {"link_token": link_token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/exchange_public_token", response_model=AccessTokenResponse)
async def exchange_public_token(public_token: PublicTokenExchange, current_user: str = Depends(oauth2_scheme)):
    access_token = plaid_service.exchange_public_token(public_token.public_token)
    # TODO: Save access_token to database associated with current_user
    return {"access_token": access_token}

@app.get("/transactions", response_model=List[Transaction])
async def get_transactions(start_date: str, end_date: str, current_user: str = Depends(oauth2_scheme)):
    # TODO: Retrieve access_token from database for current_user
    access_token = "placeholder_access_token"
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    added, modified, removed = plaid_service.get_transactions(access_token, start_date, end_date)
    # For simplicity, we're only returning the added transactions
    return added

@app.get("/accounts", response_model=List[Account])
async def get_accounts(current_user: str = Depends(oauth2_scheme)):
    # TODO: Retrieve access_token from database for current_user
    access_token = "placeholder_access_token"
    accounts = plaid_service.get_accounts(access_token)
    return accounts['accounts']

@app.get("/balance")
async def get_balance(current_user: str = Depends(oauth2_scheme)):
    # TODO: Retrieve access_token from database for current_user
    access_token = "placeholder_access_token"
    balance = plaid_service.get_balance(access_token)
    return balance

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)