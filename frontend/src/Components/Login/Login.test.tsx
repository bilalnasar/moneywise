import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MoneywiseProvider } from '../../Context';
import Login from './index';

describe('Login Component', () => {
  it('renders login form', () => {
    render(
      <MoneywiseProvider>
        <Login />
      </MoneywiseProvider>
    );
    expect(screen.getByPlaceholderText('Username')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Login' })).toBeInTheDocument();
  });

  it('switches to register mode', () => {
    render(
      <MoneywiseProvider>
        <Login />
      </MoneywiseProvider>
    );
    fireEvent.click(screen.getByText('Switch to Register'));
    expect(screen.getByRole('button', { name: 'Register' })).toBeInTheDocument();
  });

  // Add more tests for form submission, error handling, etc.
});