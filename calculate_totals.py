import pandas as pd
pd.options.mode.copy_on_write = True

def main():

    # Load ingredients list.
    path_ingredients = 'ingredients_list.xlsx'
    df_ingredients = pd.read_excel(path_ingredients, skiprows = 1)

    # Load packing list.
    path_packing = 'packing_list.xlsx'
    df_packing = pd.read_excel(path_packing)

    # Get column names for nutritional values (energy, fat, ...) 
    nutrition_keys = list(df_ingredients.columns)[4:]
    nutrition_total_keys = ['{:} (total)'.format(key) for key in nutrition_keys]

    # Add the nutritional information to the packing list.
    df_packing = df_packing.merge(df_ingredients, on = 'Name', how = 'inner')

    # Separate packing list into items defined by weight, and items defined
    # by unit.
    df_by_weight = df_packing[df_packing['Unit type'] == 'by_weight']
    df_by_unit = df_packing[df_packing['Unit type'] == 'by_unit']

    # Loop over the different nutritional values (energy, fat, ...) and
    # calculate the totals for the packing list.
    for nutrition_key in nutrition_keys:
        
        nutrition_total_key = '{:} (total)'.format(nutrition_key)

        # Case 1: Nutrition by weight. The total is given by the product of
        #   (nutrition per 100 g) and (weight in units of 100 g).
        df_by_weight[nutrition_total_key] = (df_by_weight['Amount (g)'] / 100.0) * df_by_weight[nutrition_key]

        # Case 2: Nutrition by item. The total is given by the product of
        #   (nutrition per 100 g) and (number of items) and (weight of item in units of 100 g).
        df_by_unit[nutrition_total_key] = df_by_unit['Amount (units)'] * (df_by_unit['Weight (g) per unit'] / 100.0) * df_by_unit[nutrition_key]

    # Combine the weight- and unit-based lists.
    df_packing = pd.concat([df_by_weight, df_by_unit])

    # Calculate the total amount of each nutritional value.
    totals = df_packing[nutrition_total_keys].sum()

    # Rename (we no longer care about the nutrition per 100g).
    rename_dict = {nutrition_total_key : nutrition_key for nutrition_key, nutrition_total_key in zip(nutrition_keys, nutrition_total_keys)}
    totals = totals.rename(rename_dict)

    # Divide by the number of days to get the daily amount of each nutrient.
    n_days = 7 + (1.0/3.0)
    daily_totals = totals / n_days
    
    print("Daily totals for {:.2f} days:".format(n_days))
    with pd.option_context("display.precision", 1):
        print(daily_totals)

    return

if __name__ == '__main__':

    main()
