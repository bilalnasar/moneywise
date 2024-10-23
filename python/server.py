import asyncio
import base64
import os
import datetime as dt
import json
import time
from datetime import date, timedelta
import uuid
import uvicorn

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from auth import User, get_current_user, authenticate_user, create_access_token, Token, pwd_context, SessionLocal
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel
import plaid
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.user_create_request import UserCreateRequest
from plaid.model.auth_get_request import AuthGetRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.identity_get_request import IdentityGetRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.item_get_request import ItemGetRequest
from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
from plaid.model.statements_list_request import StatementsListRequest
from plaid.model.link_token_create_request_statements import LinkTokenCreateRequestStatements
from plaid.model.link_token_create_request_cra_options import LinkTokenCreateRequestCraOptions
from plaid.model.statements_download_request import StatementsDownloadRequest
from plaid.model.consumer_report_permissible_purpose import ConsumerReportPermissiblePurpose
from plaid.api import plaid_api

load_dotenv()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_ENV = os.getenv('sandbox')
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions').split(',')
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US').split(',')

def empty_to_none(field):
    value = os.getenv(field)
    if value is None or len(value) == 0:
        return None
    return value

host = plaid.Environment.Sandbox

if PLAID_ENV == 'sandbox':
    host = plaid.Environment.Sandbox

if PLAID_ENV == 'production':
    host = plaid.Environment.Production

PLAID_REDIRECT_URI = empty_to_none('PLAID_REDIRECT_URI')

configuration = plaid.Configuration(
    host=host,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
        'plaidVersion': '2020-09-14'
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

products = []
for product in PLAID_PRODUCTS:
    products.append(Products(product))

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (dt.datetime, dt.date)):  # Changed from datetime.datetime to dt.datetime
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

item_id = None

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    jwt_token = create_access_token(data={"sub": user.username})
    return {"access_token": jwt_token, "token_type": "bearer"}

@app.post("/register")
async def register(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = db.query(User).filter(User.username == form_data.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = pwd_context.hash(form_data.password)
    new_user = User(username=form_data.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}


@app.post("/api/info")
async def info(current_user: User = Depends(get_current_user)):
    try:
        access_token = current_user.plaid_access_token
        if not access_token:
            access_token = None
        
        return JSONResponse({
            'access_token': access_token,
            'products': PLAID_PRODUCTS
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/create_link_token')
async def create_link_token():
    try:
        request = LinkTokenCreateRequest(
            products=products,
            client_name="Plaid Quickstart",
            country_codes=list(map(lambda x: CountryCode(x), PLAID_COUNTRY_CODES)),
            language='en',
            user=LinkTokenCreateRequestUser(
                client_user_id=str(time.time())
            )
        )
        if PLAID_REDIRECT_URI is not None:
            request['redirect_uri'] = PLAID_REDIRECT_URI
        if Products('statements') in products:
            statements = LinkTokenCreateRequestStatements(
                end_date=date.today(),
                start_date=date.today() - timedelta(days=30)
            )
            request['statements'] = statements


        # create link token
        response = client.link_token_create(request)
        return JSONResponse(json.loads(json.dumps(response.to_dict(), default=json_serial)))
    except plaid.ApiException as e:
        print(e)
        raise HTTPException(status_code=e.status, detail=json.loads(e.body))
# Create a user token which can be used for Plaid Check, Income, or Multi-Item link flows
# https://plaid.com/docs/api/users/#usercreate
@app.post('/api/create_user_token')
async def create_user_token(current_user: User = Depends(get_current_user)):
    db = None
    try:
        user_create_request = UserCreateRequest(
            # Typically this will be a user ID number from your application. 
            client_user_id="user_" + str(uuid.uuid4())
        )
        user_response = client.user_create(user_create_request)
        user_token = user_response['user_token']

        db = SessionLocal()
        db_user = db.query(User).filter(User.id == current_user.id).first()
        db_user.plaid_user_token = user_token
        db.commit()
        db.refresh(db_user)
        db.close()
        return JSONResponse(user_response.to_dict())
    except plaid.ApiException as e:
        print(e)
        raise HTTPException(status_code=e.status, detail=json.loads(e.body))


@app.post('/api/set_access_token')
async def set_access_token(public_token: str = Form(...), current_user: User = Depends(get_current_user)):
    global item_id
    db = None
    try:
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token)
        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']

        db = SessionLocal()
        db_user = db.query(User).filter(User.id == current_user.id).first()
        db_user.plaid_access_token = access_token
        db.commit()
        db.refresh(db_user)

        return JSONResponse({"status": "success", "message": "Access token set successfully"})
    except plaid.ApiException as e:
        return JSONResponse(json.loads(e.body))
    finally:
        db.close()


# Retrieve ACH or ETF account numbers for an Item
# https://plaid.com/docs/#auth


@app.get('/api/auth')
async def get_auth(current_user: User = Depends(get_current_user)):
    try:
        access_token = current_user.plaid_access_token
        if not access_token:
            raise HTTPException(status_code=400, detail="Plaid access token not found for this user")
        request = AuthGetRequest(
            access_token=access_token
        )
        response = client.auth_get(request)
        pretty_print_response(response.to_dict())
        return JSONResponse(response.to_dict())
    except plaid.ApiException as e:
        error_response = format_error(e)
        return JSONResponse(error_response)


# Retrieve Transactions for an Item
# https://plaid.com/docs/#transactions


@app.get('/api/transactions')
async def get_transactions(current_user: User = Depends(get_current_user)):
    # Set cursor to empty to receive all historical updates
    cursor = ''

    # New transaction updates since "cursor"
    added = []
    modified = []
    removed = [] # Removed transaction ids
    has_more = True
    try:
        access_token = current_user.plaid_access_token
        if not access_token:
            raise HTTPException(status_code=400, detail="Plaid access token not found for this user")
        # Iterate through each page of new transaction updates for item
        while has_more:
            request = TransactionsSyncRequest(
                access_token=access_token,
                cursor=cursor,
            )
            response = client.transactions_sync(request).to_dict()
            cursor = response['next_cursor']
            # If no transactions are available yet, wait and poll the endpoint.
            if cursor == '':
                await asyncio.sleep(2)
                continue  
            # If cursor is not an empty string, we got results, 
            # so add this page of results
            added.extend(response['added'])
            modified.extend(response['modified'])
            removed.extend(response['removed'])
            has_more = response['has_more']
            pretty_print_response(response)

        # Return the 8 most recent transactions
        latest_transactions = sorted(added, key=lambda t: t['date'])[-8:]
        return JSONResponse({
            'latest_transactions': json.loads(json.dumps(latest_transactions, default=json_serial)),
            'access_token': access_token
        })

    except plaid.ApiException as e:
        error_response = format_error(e)
        return JSONResponse(error_response)

# Retrieve Identity data for an Item
# https://plaid.com/docs/#identity


@app.get('/api/identity')
async def get_identity(current_user: User = Depends(get_current_user)):
    try:
        access_token = current_user.plaid_access_token
        if not access_token:
            raise HTTPException(status_code=400, detail="Plaid access token not found for this user")
        request = IdentityGetRequest(
            access_token=access_token
        )
        response = client.identity_get(request)
        pretty_print_response(response.to_dict())
        return JSONResponse({
            'error': None, 
            'identity': response.to_dict()['accounts']
        })
    except plaid.ApiException as e:
        error_response = format_error(e)
        return JSONResponse(error_response)


# Retrieve real-time balance data for each of an Item's accounts
# https://plaid.com/docs/#balance


@app.get('/api/balance')
async def get_balance(current_user: User = Depends(get_current_user)):
    try:
        access_token = current_user.plaid_access_token
        if not access_token:
            raise HTTPException(status_code=400, detail="Plaid access token not found for this user")
        request = AccountsBalanceGetRequest(
            access_token=access_token
        )
        response = client.accounts_balance_get(request)
        pretty_print_response(response.to_dict())
        return JSONResponse(response.to_dict())
    except plaid.ApiException as e:
        error_response = format_error(e)
        return JSONResponse(error_response)


# Retrieve an Item's accounts
# https://plaid.com/docs/#accounts


@app.get('/api/accounts')
async def get_accounts(current_user: User = Depends(get_current_user)):
    try:
        access_token = current_user.plaid_access_token
        if not access_token:
            raise HTTPException(status_code=400, detail="Plaid access token not found for this user")
        request = AccountsGetRequest(
            access_token=access_token
        )
        response = client.accounts_get(request)
        pretty_print_response(response.to_dict())
        return JSONResponse(response.to_dict())
    except plaid.ApiException as e:
        error_response = format_error(e)
        return JSONResponse(error_response)

@app.get('/api/statements')
async def statements(current_user: User = Depends(get_current_user)):
    try:
        access_token = current_user.plaid_access_token
        if not access_token:
            raise HTTPException(status_code=400, detail="Plaid access token not found for this user")
        request = StatementsListRequest(access_token=access_token)
        response = client.statements_list(request)
        pretty_print_response(response.to_dict())
    except plaid.ApiException as e:
        error_response = format_error(e)
        return JSONResponse(error_response)
    
    try:
        request = StatementsDownloadRequest(
            access_token=access_token,
            statement_id=response['accounts'][0]['statements'][0]['statement_id']
        )
        pdf = client.statements_download(request)
        return JSONResponse({
            'error': None,
            'json': response.to_dict(),
            'pdf': base64.b64encode(pdf.read()).decode('utf-8'),
        })
    except plaid.ApiException as e:
        error_response = format_error(e)
        return JSONResponse(error_response)




# Retrieve high-level information about an Item
# https://plaid.com/docs/#retrieve-item


@app.get('/api/item')
async def item(current_user: User = Depends(get_current_user)):
    try:
        access_token = current_user.plaid_access_token
        if not access_token:
            raise HTTPException(status_code=400, detail="Plaid access token not found for this user")
        request = ItemGetRequest(access_token=access_token)
        response = client.item_get(request)
        request = InstitutionsGetByIdRequest(
            institution_id=response['item']['institution_id'],
            country_codes=list(map(lambda x: CountryCode(x), PLAID_COUNTRY_CODES))
        )
        institution_response = client.institutions_get_by_id(request)
        pretty_print_response(response.to_dict())
        pretty_print_response(institution_response.to_dict())
        return JSONResponse({
            'error': None, 
            'item': response.to_dict()['item'], 
            'institution': institution_response.to_dict()['institution']
        })
    except plaid.ApiException as e:
        error_response = format_error(e)
        return JSONResponse(error_response)

def pretty_print_response(response):
    print(json.dumps(response, indent=2, sort_keys=True, default=str))

def format_error(e):
    response = json.loads(e.body)
    return {'error': {'status_code': e.status, 'display_message':
                      response['error_message'], 'error_code': response['error_code'], 'error_type': response['error_type']}}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 8000)))