#--------------IMPORT PACKAGES--------------#
import dash
from dash import Dash, html, dash_table, dcc
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import plotly.express as px




#--------------read data--------------#
df = pd.read_csv("universal_top_spotify_songs.csv") 


#--------------convert date to date time--------------#
df['snapshot_date'] = pd.to_datetime(df['snapshot_date'])
df['album_release_date'] = pd.to_datetime(df['album_release_date'])
df['year'] = df['snapshot_date'].dt.year

# Convert 'is_explicit' column to readable format
df['is_explicit_label'] = df['is_explicit'].apply(lambda x: 'Explicit' if x == True else 'Non-Explicit')

#--------------removing missing values--------------#
df = df.dropna() 




#--------------Create Line Chart Tab-------------#
tab_1 = html.Div([
    html.Label("Select View", className='view_label'),
    dcc.Dropdown(
        id='view_dropdown',
        options=[
            {'label': 'Song', 'value': 'song'},
            {'label': 'Artist', 'value': 'artist'}
        ],
        value='song',  
        className='view_dropdown'
    ),
    
    html.Label("Select Song/Artist", className='song_artist_label'),
    dcc.Dropdown(id='song_artist_dropdown', className='song_artist_dropdown'),

    html.Label("Select Time Range", className='time_range_label'),
    dcc.RangeSlider(
        id='time_range_slider',
        min=2023,  
        max=2025,
        step=1,
        value=[2023, 2025],  
        marks={year: {'label': str(year), 'style': {'color': '#ffffff'}} for year in range(2023, 2026)},
        className='time_range_slider'
    ),
    
    dcc.Graph(id='line_chart', className='line_chart')
])


#--------------Create scatter plot Tab-------------#
tab_2 = html.Div([
    dcc.RadioItems(
        id='scatter_plot_feature',
        options=[
            {'label': 'Danceability', 'value': 'danceability'},
            {'label': 'Energy', 'value': 'energy'},
            {'label': 'Tempo', 'value': 'tempo'},
            {'label': 'Acousticness', 'value': 'acousticness'},
            {'label': 'Speechiness', 'value': 'speechiness'},
            {'label': 'Loudness', 'value': 'loudness'}
        ],
        value='danceability', 
        inline=True,
        className='radio-buttons'
    ),
    dcc.Graph(id='scatter_plot')
])


#--------------Create dual chart Tab-------------#
tab_3 = html.Div([
    html.H2("Explicit vs Non-Explicit Songs Popularity Trends", style={'textAlign': 'center', 'color': 'white'}),

    html.Label("Select Year", className='year_label'),
    dcc.Dropdown(
        id='year_dropdown',
        options=[{'label': str(year), 'value': year} for year in sorted(df['snapshot_date'].dt.year.unique())],
        value=sorted(df['snapshot_date'].dt.year.unique())[0],  
        className='year_dropdown'
    ),

    html.Div([
        dcc.Graph(id='pie_chart', style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='bar_chart', style={'width': '50%', 'display': 'inline-block'})
    ], className='tab3_charts', style={'textAlign': 'center', 'backgroundColor': '#1e1e1e', 'padding': '20px'})
])
#--------------Create custom chart Tab-------------#
tab_4 = html.Div([
    html.H2("Country-Wise Music Trends", style={'textAlign': 'center', 'color': 'white'}),

    html.Label("Select Country", className='country_label'),
    dcc.Dropdown(
        id='country_dropdown',
        options=[{'label': country, 'value': country} for country in df['country'].unique()],
        value=df['country'].unique()[0],  
        className='country_dropdown'
    ),

    dcc.Graph(id='country_top_songs_chart', className='country_chart')
])


#--------------define the layout--------------#

layout_of_app = [
    html.H1("Spotify Songs", className='head_section'),
    html.H3("Spotify Songs Dashboard to visualize songs over popularity", className='sub_head_section'),

    dcc.Tabs(id='tabs', value='tab_1', className="tabs", children=[
        dcc.Tab(label='Line Chart Popularity', value='tab_1', children=tab_1, className='tab_content'),
        dcc.Tab(label='Scatter Plot Correlation', value='tab_2', children=tab_2, className='tab_content'),
        dcc.Tab(label='Explicit vs Non-Explicit Songs Popularity Trends', value='tab_3', children=tab_3, className='tab_content'),
        dcc.Tab(label='Country-Wise Music Trends', value='tab_4', children=tab_4, className='tab_content')
    ])
]



#--------------INITIALIZE THE APP--------------#
app = Dash(__name__)
app.layout =layout_of_app
app.title = 'Spotify Songs Dashboard'

#-------defining call back tab 1---------#
@app.callback(
    Output('song_artist_dropdown', 'options'),
    Output('song_artist_dropdown', 'value'),
    Input('view_dropdown', 'value')
)
def update_song_artist_dropdown(view):
    # Update options based on the selected view (song or artist)
    if view == 'song':
        options = [{'label': song, 'value': song} for song in df['name'].unique()]
        value = df['name'].unique()[0]
    else:
        options = [{'label': artist, 'value': artist} for artist in df['artists'].unique()]
        value = df['artists'].unique()[0]
    return options, value


@app.callback(
    Output('line_chart', 'figure'),
    Input('song_artist_dropdown', 'value'),
    Input('time_range_slider', 'value'),
    Input('view_dropdown', 'value')
)
def update_line_chart(selected_value, time_range, view):
    start_year, end_year = time_range
    filtered_df = df[(df['snapshot_date'].dt.year >= start_year) & 
                     (df['snapshot_date'].dt.year <= end_year)]
    
    if view == 'song':
        filtered_df = filtered_df[filtered_df['name'] == selected_value]
    else:
        filtered_df = filtered_df[filtered_df['artists'] == selected_value]
    
    fig = px.line(filtered_df, x='snapshot_date', y='popularity', 
                  title=f'Popularity of {selected_value} Over Time')
    
    return fig

#-------defining call back tab 2---------#
@app.callback(
    Output('scatter_plot', 'figure'),
    [Input('scatter_plot_feature', 'value')]
)
def update_scatter_plot(selected_feature):
    correlation = df['popularity'].corr(df[selected_feature])

    fig = px.scatter(
        df,
        x='popularity',
        y=selected_feature,
        color='artists',  # Color by artist for differentiation
        title=f"Scatter Plot: Popularity vs. {selected_feature} (Corr: {correlation:.2f})",
        labels={'popularity': 'Popularity', selected_feature: selected_feature},
        hover_data=['name', 'artists', 'album_name'],
    )

    fig.update_layout(
        xaxis_title="Popularity",
        yaxis_title=selected_feature,
        legend_title="Artist",
        plot_bgcolor='#374149', 
        paper_bgcolor='#374149', 
        font_color='white'
    )

    return fig

#-------defining call back tab 3---------#

@app.callback(
    [Output('pie_chart', 'figure'),
     Output('bar_chart', 'figure')],
    [Input('tabs', 'value'),
     Input('year_dropdown', 'value')]  # Add year selection input here
)
def update_pie_and_bar_chart(_, selected_year):
    # Filter the dataframe by the selected year
    filtered_df = df[df['snapshot_date'].dt.year == selected_year]
    explicit_counts = filtered_df.groupby('is_explicit_label')['popularity'].sum().reset_index()

    pie_fig = px.pie(
        explicit_counts,
        names='is_explicit_label',
        values='popularity',
        title=f"Popularity Distribution: Explicit vs Non-Explicit Songs ({selected_year})",
        color='is_explicit_label',
        color_discrete_map={'Explicit': '#ff6361', 'Non-Explicit': '#58508d'}
    )
    pie_fig.update_layout(
        plot_bgcolor='#374149', 
        paper_bgcolor='#374149', 
        font_color='white'
    )
    
    bar_fig = px.bar(
        explicit_counts,
        x='is_explicit_label',
        y='popularity',
        title=f"Popularity Comparison: Explicit vs Non-Explicit Songs ({selected_year})",
        color='is_explicit_label',
        color_discrete_map={'Explicit': '#ff6361', 'Non-Explicit': '#58508d'}
    )
    bar_fig.update_layout(
        plot_bgcolor='#374149', 
        paper_bgcolor='#374149', 
        font_color='white'
    )

    return pie_fig, bar_fig



#-------defining call back tab 4---------#
@app.callback(
    Output('country_top_songs_chart', 'figure'),
    Input('country_dropdown', 'value')
)
def update_country_chart(selected_country):
    filtered_df = df[df['country'] == selected_country]
    
    top_songs = filtered_df.groupby('name')['popularity'].sum().reset_index()
    top_songs = top_songs.sort_values(by='popularity', ascending=False).head(10)  

    fig = px.bar(
        top_songs, 
        x='popularity', 
        y='name', 
        orientation='h',  
        title=f"Top Songs in {selected_country}",
        labels={'popularity': 'Popularity', 'name': 'Song Name'},
        color='popularity', 
        color_continuous_scale='viridis'
    )

    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        plot_bgcolor='#374149', 
        paper_bgcolor='#374149', 
        font_color='white'
    )

    return fig

#--------------RUN THE APP--------------#
if __name__ == '__main__':
    app.run_server(debug=True)