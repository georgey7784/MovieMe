from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.cluster import KMeans

app = Flask(__name__)

# Loading the datasets (MOVIES & RATINGS)
movies = pd.read_csv('Add-file-path-of-movies.csv-here')

movies_ratings_clust = movies.copy()

# Selecting NUMERICAL | CATEGORICAL features
numerical_features = movies_ratings_clust.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_features = ['title', 'genres']

# Use column transformer from SKLearn to help us deal with the split between feature types
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(drop='first'), categorical_features)
    ],
    remainder='drop'
)

# n_clusters (k) = 4, based on the visualisation
n_clusters = 4
X = preprocessor.fit_transform(movies_ratings_clust)
kmeans = KMeans(n_clusters=n_clusters, random_state=55)
movies_ratings_clust['cluster'] = kmeans.fit_predict(X)

# Rename column for consistency
movies_ratings_clust = movies_ratings_clust.rename(columns={'mean_rating': 'avg_rating'})

def recommend_movies(movie_name, genres, num_recommendations=10):
    # Check if the movie name exists in the dataset
    if movie_name not in movies_ratings_clust['title'].values:
        return pd.DataFrame(columns=['title', 'genres', 'avg_rating'])

    # Get the cluster and genres of the selected movie
    cluster = movies_ratings_clust[movies_ratings_clust['title'] == movie_name]['cluster'].iloc[0]
    selected_movie_genres = genres.split('|')

    # Filter movies
    recommendations_df = movies_ratings_clust[
        (movies_ratings_clust['cluster'] == cluster) &
        (movies_ratings_clust['avg_rating'] >= 3.0) &  # Adjust the rating threshold as needed
        (movies_ratings_clust['title'] != movie_name)
    ]

    # Movies with similar genres
    recommendations_df['genre_overlap'] = recommendations_df['genres'].apply(
        lambda x: len(set(x.split('|')) & set(selected_movie_genres))
    )

    recommendations_df = recommendations_df.sort_values(
        by=['genre_overlap', 'avg_rating'],
        ascending=[False, False]
    ).head(num_recommendations)[['title', 'genres', 'avg_rating']]

    return recommendations_df

@app.route('/', methods=['GET', 'POST'])
def index():
    recommendations = None

    if request.method == 'POST':
        movie_name = request.form['movie_name']
        movie_genres = request.form['movie_genres']

        recommendations = recommend_movies(movie_name, movie_genres).sort_values('avg_rating', ascending=False)

        # Print some debug information
        print(f"Movie Name: {movie_name}, Movie Genres: {movie_genres}")
        print(recommendations)

        # Return the recommendations as a JSON response
        return jsonify(recommendations.to_dict(orient='records'))

    return render_template('index.html', recommendations=recommendations)

@app.route('/loading')
def loading():
    return render_template('loading.html')


@app.route('/get_movie_suggestions', methods=['POST'])
def get_movie_suggestions():
    user_input = request.form.get('input', '')
    
    # Show suggestions only if the input has at least 4 characters
    if len(user_input) >= 4:
        suggestions = movies['title'][movies['title'].str.contains(user_input, case=False)].tolist()
        
        # Format suggestions as a list of dictionaries
        suggestions_list = [{'title': movie} for movie in suggestions]
        
        return jsonify(suggestions_list)
    else:
        # Return an empty list if the input is less than 4 characters
        return jsonify([])
    
@app.route('/get_movie_genres', methods=['POST'])
def get_movie_genres():
    selected_movie = request.form.get('movie_name', '')
    
    # Fetch genres for the selected movie from the DataFrame
    genres = movies[movies['title'] == selected_movie]['genres'].iloc[0]
    
    return jsonify({'genres': genres})
if __name__ == '__main__':
    app.run(debug=True)
