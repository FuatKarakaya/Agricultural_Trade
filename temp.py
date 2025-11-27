from database import execute_query

if __name__ == "__main__":

    X = execute_query(
        r"""
            DELETE FROM production p
            WHERE NOT EXISTS (
                SELECT 1
                FROM commodities c
                WHERE c.fao_code = p.commodity_code
            );
        """
    )

    print(X)
