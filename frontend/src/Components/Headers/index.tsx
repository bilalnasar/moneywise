import React, { useContext } from "react";
import Callout from "plaid-threads/Callout";
import Button from "plaid-threads/Button";
import Link from "../Link";
import Context from "../../Context";
import styles from "./index.module.scss";

const Header = () => {
  const {
    linkToken,
    linkSuccess,
    backend,
    isItemAccess,
  } = useContext(Context);

  return (
    <div className={styles.container}>
      <div className={styles.grid}>
        <h3 className={styles.title}>Moneywise</h3>

        {!linkSuccess ? (
          <>
            <h4 className={styles.subtitle}>
              Connect your bank account with Plaid
            </h4>
            {!backend ? (
              <Callout warning>
                Please make sure your backend server is running and configured correctly.
              </Callout>
            ) : linkToken ? (
              <div className={styles.linkButton}>
                <Link />
              </div>
            ) : (
              <div className={styles.linkButton}>
                <Button large disabled>
                  Loading...
                </Button>
              </div>
            )}
          </>
        ) : (
          <>
            <h4 className={styles.subtitle}>
              Thanks for connecting your bank!
            </h4>
            {isItemAccess && (
              <p className={styles.confirmation}>
                You have successfully created an Item and linked your account.
              </p>
            )}
          </>
        )}
      </div>
    </div>
  );
};

Header.displayName = "Header";

export default Header;