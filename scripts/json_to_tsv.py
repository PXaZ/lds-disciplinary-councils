default_column_order = [
    'name',
    'sex',
    'wikipedia_url',
    'jsp_url',
    'recording_url',
    'birth_date',
    'birth_date_md',
    'best_birth_date',
    'best_birth_year',
    'best_birth_month',
    'best_birth_day',
    'death_date',
    'death_date_md',
    'best_death_date',
    'best_death_year',
    'best_death_month',
    'best_death_day',
    'date',
    'date_md',
    'best_date',
    'best_year',
    'best_month',
    'best_day',
    'tagline',
    'tagline_md',
    'office',
    'outcome',
    'for',
    'alt_for',
    'notes',
    'notes_md',
    'unit',
    'unit_md',
    'location',
    'location_md',
    'sections',
    'tags',
    'birth_place',
    'rebaptism_date',
    'rebaptism_date_md',
    'baptism_date',
    'baptism_date_md'
]

if __name__=="__main__":
    import argparse
    import sys

    import numpy as np
    import pandas as pd

    parser = argparse.ArgumentParser(description='Expand JSON by processing various fields.')
    parser.add_argument("filename", help="Path to JSON to expand")
    parser.add_argument("--col_order", help="The order of the columns", action="store", default=','.join(default_column_order))

    args = parser.parse_args()

    column_order = args.col_order.split(",")

    data = pd.read_json(args.filename, orient='records')

    diff = set(data.columns).difference(set(column_order))
    if diff:
        for col in diff:
            sys.stderr.write("Error: unrecognized column: %s\n" % col)
        sys.stderr.write("You may need to add the unrecognized columns to the column order using --col_order\n")
    else:

        columns_not_in_data = set(column_order).difference(set(data.columns))
        for col in columns_not_in_data:
            data[col] = np.nan

        data.to_csv(args.filename.replace(".json",".tsv"), sep="\t", index=False, columns=column_order)
