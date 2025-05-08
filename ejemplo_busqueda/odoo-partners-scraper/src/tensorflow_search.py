import pandas as pd #use pandas to from excel file
import tensorflow as tf #use tensorflow
from tensorflow.keras.models import Sequential #use Sequential model
from tensorflow.keras.layers import Dense #use Dense layer

# Loading data from excel file
def load_data(filename):
    df = pd.read_excel(filename)
    return df

# Preprocessing the data
def preprocess_data(df):
    # Convert country names to numerical labels
    country_names = df['Country'].tolist()
    # validate if the column 'Number' is in the dataframe
    if 'Number' in df.columns:
        country_numbers = df['Number'].astype(int).tolist() # Convert the 'Number' column to a list
    else:
        raise KeyError("The 'Number' column is missing from the DataFrame")
    
    return country_names, country_numbers #return the country names and country numbers

# Building the model of the neural network
def build_model(input_dim):
    model = Sequential([
        Dense(64, activation='relu', input_dim=input_dim), # use relu as activation function with 64 neurons
        Dense(32, activation='relu'), # second layer with 32 neurons
        Dense(1, activation='linear') # output layer with 1 neuron
    ])
    
    model.compile(optimizer='adam', loss='mean_squared_error') # compile the model with adam optimizer and mean squared error loss function
    return model

def main():
    filename = 'countries_data.xlsx'
    df = load_data(filename)
    country_names, country_numbers = preprocess_data(df)
    
    # Convert country numbers to a numpy array
    X = tf.constant(country_numbers, dtype=tf.float32) # Convert the country numbers to a tensor
    y = tf.constant(country_numbers, dtype=tf.float32) # Convert the country numbers to a tensor
    
    model = build_model(input_dim=1)
    
    # Train the model
    model.fit(X, y, epochs=10, batch_size=1)
    
    # Perform a search
    search_number = 100  # Example search number
    prediction = model.predict([search_number])
    print(f'Predicted number of partners for search number {search_number}: {prediction[0][0]}')

if __name__ == '__main__':
    main()