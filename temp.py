from database import execute_query

if __name__ == "__main__":

    X = execute_query(
        """
        COPY staging_prod FROM '/prod.csv' DELIMITER ',' CSV HEADER;
        """
    )

    print(X)
