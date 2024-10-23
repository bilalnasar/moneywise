# Moneywise: A simpler budgeting app

Since Mint shutdown last year, I've been thinking about build a financial planning app that allows users to connect their accounts, and have access to the most important features, such as net worth, spending, and more. Plaid stood out amongst other API providers because of its amazing developer resources and expansive suite of products. So here's Moneywise:

Moneywise is a full-stack personal finance management web app that allows users to connect their bank accounts, view their total balances, and track their transactions. Built with React, FastAPI, and the Plaid API, this app can help users manage their finances securely and effectively.

## Features

- User authentication and registration
- Display of total account balances
- Transaction history and categorization
- Real-time financial data synchronization
- Responsive and intuitive user interface
- Secure account access with Plaid API (which supports over 5,000 institutions)

## Technical Details

The backend is a Python FastAPI server that uses the Plaid API to fetch and process financial data. The frontend is a React application that communicates with the server to display the data.

- Frontend: React.js with TypeScript
- Backend: FastAPI (Python)
- Database: PostgreSQL
- Authentication: JWT (JSON Web Tokens)
- API Integration: Plaid API

## Getting Started

Run the app locally!

Prerequisites
- Node.js (v14.0.0 or later)
- Python (v3.8 or later)
- PostgreSQL

1. Clone the repository
```
git clone https://github.com/yourusername/moneywise.git
cd moneywise
```
2. Create a `.env` file and add your Plaid API keys and other necessary credentials.
3. Install the required Python packages using `pip install -r requirements.txt`
4. Install the required Node packages using `npm install`
5. Start the server with `python server.py` or `python3 server.py`
6. Start the frontend with `npm start`

The app should be running on `http://localhost:3000`.

The benefit of using FastAPI is that you can also view the api documentation easily at `http://localhost:8000/docs`.

## Security

I've currently configured the Plaid API to run in sandbox mode, so as of right now, you won't be able to access real financial data. This is because I want to expand more on the security features of the app. Currently, the API endpoints are protected with JWT tokens, and all requests are made over HTTPS.

## Acknowledgements

I based the structure of this project on the Plaid API Quickstart guide, which you can find [here](https://github.com/plaid/quickstart), which was originally built with Flask.
