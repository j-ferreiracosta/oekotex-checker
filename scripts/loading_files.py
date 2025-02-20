import pandas as pd

def load_file(file_path):
    
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        print(f"An error occurred while loading the Excel file: {e}")
        return None
    

def load_files_to_json(product_file_path='../files/Products.xlsx', certification_file_path='../files/Scopes.xlsx'):
    try:
        df_certification = load_file(certification_file_path)

        df_product = load_file(product_file_path)

        #remove the rows where the column Scope = NaN
        df_certification = df_certification.dropna(subset=['Scope'])

        df = pd.merge(df_certification, df_product, how='cross')

        #remove columns that are not needed
        #df = df.drop(columns=['Code','ID', 'ValidDate'])

        #add columns to the dataframe
        # df['InScope'] = ''
        # df['Confidence'] = ''
        # df['Justification'] = ''

        #convert the df into a json
        df_json = df.to_json(orient='records')
        df_json = "<TABLE>"+df_json+"</TABLE>"
        return df_json
    except Exception as e:
        print(f"An error occurred while loading the Excel files to JSON: {e}")
        return None

