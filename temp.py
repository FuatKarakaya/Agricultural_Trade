from database import execute_query

if __name__ == "__main__":

    X = execute_query(
        r"""alter table production drop constraint production_commodity_code_fkey;"""
        # r"""\copy production FROM 'C:\Users\omerf\Desktop\db\Agricultural_Trade\prod_reduced_clean_scaled.csv' WITH (FORMAT csv, HEADER true)"""
    )

    print(X)
