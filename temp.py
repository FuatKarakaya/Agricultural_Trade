from database import execute_query

if __name__ == "__main__":

    X = execute_query(
        r"""DROP TABLE tempcp;
;
        """
    )

    print(X)
