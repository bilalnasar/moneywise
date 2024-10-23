import React, { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import Link from '../Link';
import Context from '../../Context';
import styles from './index.module.scss';

const Sidebar = () => {
  const { linkSuccess, username, logout } = useContext(Context);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className={styles.sidebar}>
      <div className={styles.welcome}>
        <h2>Welcome,</h2>
        <h3>{username}</h3>
      </div>
      <div className={styles.changeAccount}>
        <p>Want to connect a different account?</p>
        <Link isSmall />
      </div>
      <div className={styles.logoutContainer}>
        <button onClick={handleLogout} className={styles.logoutButton}>
          Logout
        </button>
      </div>
    </div>
  );
};

export default Sidebar;