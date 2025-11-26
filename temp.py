from database import execute_query

if __name__ == "__main__":

    X = execute_query(
        r"""ALTER TABLE tempnotnormalpp DROP COLUMN IF EXISTS "Y2000";
        """
    )

    print(X)
