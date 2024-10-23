import React, { useEffect, useState, useContext } from 'react';
import Context from '../../Context';
import styles from "./index.module.scss";

interface Account {
  account_id: string;
  balances: {
    available: number;
    current: number;
    limit: number | null;
    iso_currency_code: string;
    unofficial_currency_code: string | null;
  };
  mask: string;
  name: string;
  official_name: string;
  type: string;
  subtype: string;
}

interface BalanceResponse {
  accounts: Account[];
}

interface TransactionData {
  name: string;
  amount: string;
  date: string;
}

const Dashboard = () => {
  const [balanceData, setBalanceData] = useState<BalanceResponse | null>(null);
  const [transactions, setTransactions] = useState<TransactionData[]>([]);
  const { jwtToken } = useContext(Context);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const balanceResponse = await fetch('/api/balance', {
          headers: {
            'Authorization': `Bearer ${jwtToken}`,
          },
        });
        const balanceData: BalanceResponse = await balanceResponse.json();
        setBalanceData(balanceData);

        const transactionsResponse = await fetch('/api/transactions', {
          headers: {
            'Authorization': `Bearer ${jwtToken}`,
          },
        });
        const transactionsData = await transactionsResponse.json();
        setTransactions(transactionsData.latest_transactions);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, [jwtToken]);

  const totalBalance = balanceData?.accounts.reduce((sum, account) => sum + account.balances.current, 0) || 0;

  return (
    <div className={styles.dashboard}>
      <div className={styles.balanceCard}>
        <h2>Total Balance</h2>
        <h1>${totalBalance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</h1>
      </div>
      <div className={styles.accountList}>
        <h2>Accounts</h2>
        {balanceData?.accounts.map((account, index) => (
          <div key={index} className={styles.accountItem}>
            <span>{account.name}</span>
            <span>${account.balances.current.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
          </div>
        ))}
      </div>
      <div className={styles.transactionList}>
        <h2>Recent Transactions</h2>
        <div className={styles.transactionHeader}>
          <span>Item</span>
          <span>Amount</span>
          <span>Date</span>
        </div>
        {transactions.map((transaction, index) => (
          <div key={index} className={styles.transactionItem}>
            <span>{transaction.name}</span>
            <span>{transaction.amount}</span>
            <span>{transaction.date}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;