from database import execute_query

if __name__ == "__main__":

    execute_query('''UPDATE trade_data_long SET partner_countries = countries.country_id FROM countries WHERE trade_data_long.partner_countries = countries.country_name;''')