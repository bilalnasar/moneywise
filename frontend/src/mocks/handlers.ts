import { http, HttpResponse } from 'msw'

export const handlers = [
  http.post('http://localhost:8000/token', () => {
    return HttpResponse.json({
      access_token: 'mocked_access_token',
    })
  }),

  http.post('http://localhost:8000/register', () => {
    return HttpResponse.json({
      message: 'User created successfully',
    })
  }),

  http.post('/api/info', () => {
    return HttpResponse.json({
      access_token: 'mocked_plaid_access_token',
      products: ['transactions'],
    })
  }),

  http.get('/api/balance', () => {
    return HttpResponse.json({
      accounts: [
        {
          account_id: '1234',
          balances: {
            available: 1000,
            current: 1000,
            iso_currency_code: 'USD',
          },
          name: 'Checking Account',
          type: 'depository',
        },
      ],
    })
  }),

  http.get('/api/transactions', () => {
    return HttpResponse.json({
      latest_transactions: [
        {
          name: 'Grocery Store',
          amount: 50.00,
          date: '2023-05-01',
          category: ['Food and Drink', 'Groceries'],
        },
      ],
    })
  }),
]