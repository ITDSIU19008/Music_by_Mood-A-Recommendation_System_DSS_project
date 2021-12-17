from flask import Flask,render_template,request,redirect,url_for,session
app = Flask(__name__,template_folder='')
import requests

import pandas as pd
import random
import authorization
import numpy as np
from numpy.linalg import norm

################################################################################
#Plot
import plotly
import plotly.express as px
import json
#Function 1 Location
import numpy as np
import pandas as pd 
import sklearn
from sklearn.cluster import KMeans
from scipy.sparse.linalg import svds
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel


@app.route("/")
def main():
    return "Welcome!"
@app.route("/track_id", methods=['GET','POST'])
def track_id():
    output=None
    if request.method == 'POST':
        track_id=request.form['track_id']
        genre=request.form['genre']
        #Load data
        df = pd.read_csv("./valence_arousal_dataset.csv")

        #Create mood vector
        df["mood_vec"] = df[["valence", "energy"]].values.tolist()

        sp = authorization.authorize()

        # In order to compute distances between two tracks, we need to transform the seperate valence and energy columns to a mood-vector column. 
        # This can be done by using df.apply() alongside a lambda function

        #The algorithm that finds similar tracks to a given input track

        #1.Crawl the track's valence and energy values from the Spotify API.
        #2.Compute the distances of the input track to each track in the reference dataset.
        #3.Sort the reference track from lowest to highest distance.
        #4.Return the n most similar tracks

        def recommend(track_id, ref_df, sp, n_recs = 5):
    
            # Crawl valence and arousal of given track from spotify api
            track_features = sp.track_audio_features(track_id)
            track_moodvec = np.array([track_features.valence, track_features.energy])
            print(f"mood_vec for {track_id}: {track_moodvec}")
    
            # Compute distances to all reference tracks
            ref_df["distances"] = ref_df["mood_vec"].apply(lambda x: norm(track_moodvec-np.array(x)))
            # Sort distances from lowest to highest
            ref_df_sorted = ref_df.sort_values(by = "distances", ascending = True)
            # If the input track is in the reference set, it will have a distance of 0, but should not be recommended
            ref_df_sorted = ref_df_sorted[ref_df_sorted["id"] != track_id]
    
            # Return n recommendations
            return ref_df_sorted.iloc[:n_recs]
        rec = recommend(track_id=track_id, ref_df= df, sp= sp, n_recs=5)
        if(genre):
            rec= df[df['genre']==genre]
        output= makeObject(rec)

    return render_template('abc.html',output=output)
@app.route("/popularity_recomendation", methods=['GET','POST'])
def popularity_recomendation():
    output=None
    if request.method == 'POST':

        rec = recommend(track_id=track_id, ref_df= df, sp= sp, n_recs=5)
        output= makeObject(rec)

    return render_template('abcde.html',output=output)

def makeObject(df):
    
    objectList=[]
    for index, row in df.iterrows():
        item={
            'id':row['id'],
            'artist_name':row['artist_name'],
            'track_name':[row['track_name']],
        }
        
        objectList.append(item)
    return objectList

if __name__ == "__main__":
    app.run(debug=True)