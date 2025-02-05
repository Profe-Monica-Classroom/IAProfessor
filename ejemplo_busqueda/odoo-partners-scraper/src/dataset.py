def save_dataset(countries_data, filename='countries_data.csv'):
    import pandas as pd

    df = pd.DataFrame(list(countries_data.items()), columns=['Country', 'Number'])
    df.to_csv(filename, index=False)

def load_dataset(filename='countries_data.csv'):
    import pandas as pd

    df = pd.read_csv(filename)
    return dict(zip(df['Country'], df['Number']))