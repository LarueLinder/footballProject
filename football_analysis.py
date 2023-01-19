import streamlit as st
from PIL import Image
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

#main title
st.title('NFL Receiving Leaders')

image = Image.open('pic.jpeg')
st.image(image, width = 500)

st.markdown("""
This app scrapes pro-football-reference to get the league leaders in receiving yards. You can
filter by year and position. 
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn
* **Data source:** [pro-football-reference.com](https://www.pro-football-reference.com/).
""")

st.sidebar.header('Filter by Year, Team and Position')
selected_year = st.sidebar.selectbox('Year', list(reversed(range(1990,2023))))

# Web scraping of NFL player stats
# https://www.pro-football-reference.com/years/2022/receiving.htm
@st.cache
def load_data(year):
    url = "https://www.pro-football-reference.com/years/" + str(year) + "/receiving.htm"
    html = pd.read_html(url, header = 0)
    df = html[0]
    #print("columns........")
    #print(df.columns)
    raw = df.drop(df[df.Age == 'Age'].index) # Deletes repeating headers in content
    raw = raw.fillna(0)
    playerstats = raw.drop(['Rk'], axis=1)
    return playerstats
playerstats = load_data(selected_year)

# Sidebar - user can select team
sorted_unique_team = sorted(playerstats.Tm.unique())
selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

# Sidebar - user can select position
unique_pos = ['RB','WR','FB','TE']
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

# Filtering data
df_selected_team = playerstats[(playerstats.Tm.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]

st.header('Display Player Stats of Selected Team(s)')
st.write('Data Dimension: ' + str(df_selected_team.shape[0]) + ' rows and ' + str(df_selected_team.shape[1]) + ' columns.')
st.dataframe(df_selected_team)

# Download the receiving stats data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(dataFile):
    csv = dataFile.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

# Heatmap
if st.button('Intercorrelation Heatmap'):
    st.header('Intercorrelation Matrix Heatmap')
    df_selected_team.to_csv('output.csv',index=False)
    df = pd.read_csv('output.csv')

    corr = df.corr()
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True
    with sns.axes_style("white"):
        fig, ax = plt.subplots(figsize=(7, 5))
        ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
    st.pyplot(fig)

    #fig, ax = plt.subplots()
    #ax.scatter([1, 2, 3], [1, 2, 3])
    #other stuff
    #st.pyplot(fig)

    #more info on heat map 
expander_bar = st.expander("**click for more info on the heatmap**")
expander_bar.markdown("""https://vitalflux.com/correlation-heatmap-with-seaborn-pandas/""")