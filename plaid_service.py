import plaid
from plaid.api import plaid_api
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from datetime import datetime, timedelta
from config import settings
import time

configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': settings.PLAID_CLIENT_ID,
        'secret': settings.PLAID_SECRET,
    }
)

api_client = plaid.ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)

def create_link_token(user_id: str):
    request = plaid.LinkTokenCreateRequest(
        user=plaid.LinkTokenCreateRequestUser(
            client_user_id=user_id
        ),
        client_name="Moneywise",
        products=[plaid.Products("transactions")],
        country_codes=[plaid.CountryCode("US")],
        language="en"
    )
    response = plaid_client.link_token_create(request)
    return response.link_token

def exchange_public_token(public_token: str):
    exchange_request = plaid.ItemPublicTokenExchangeRequest(
        public_token=public_token
    )
    exchange_response = plaid_client.item_public_token_exchange(exchange_request)
    return exchange_response.access_token

def get_transactions(access_token: str, start_date: datetime, end_date: datetime):
    cursor = ''
    added = []
    modified = []
    removed = []
    has_more = True
    try:
        while has_more:
            request = TransactionsSyncRequest(
                access_token=access_token,
                cursor=cursor,
            )
            response = plaid_client.transactions_sync(request).to_dict()
            cursor = response['next_cursor']
            added.extend(response['added'])
            modified.extend(response['modified'])
            removed.extend(response['removed'])
            has_more = response['has_more']
        
        return added, modified, removed
    except plaid.ApiException as e:
        raise e

def get_accounts(access_token: str):
    try:
        request = AccountsGetRequest(
            access_token=access_token
        )
        response = plaid_client.accounts_get(request)
        return response.to_dict()
    except plaid.ApiException as e:
        raise e

def get_balance(access_token: str):
    try:
        request = AccountsBalanceGetRequest(
            access_token=access_token
        )
        response = plaid_client.accounts_balance_get(request)
        return response.to_dict()
    except plaid.ApiException as e:
        raise e