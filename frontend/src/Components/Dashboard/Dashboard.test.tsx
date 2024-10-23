import React from 'react';
import { render, screen } from '@testing-library/react';
import { MoneywiseProvider } from '../../Context';
import Dashboard from './index';

// Mock the fetch function
global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve({ accounts: [], latest_transactions: [] }),
  })
) as jest.Mock;

describe('Dashboard Component', () => {
  it('renders dashboard elements', async () => {
    render(
      <MoneywiseProvider>
        <Dashboard />
      </MoneywiseProvider>
    );
    expect(screen.getByText('Total Balance')).toBeInTheDocument();
    expect(screen.getByText('Accounts')).toBeInTheDocument();
    expect(screen.getByText('Recent Transactions')).toBeInTheDocument();
    expect(screen.getByText('Spending by Category')).toBeInTheDocument();
  });

  // Add more tests for data fetching, rendering of accounts and transactions, etc.
});