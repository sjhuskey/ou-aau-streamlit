import streamlit as st
import pandas as pd

st.title("OU v. Public AAU Foreign Language Enrollment Dashboard")
st.write("Welcome to my dashboard for comparing foreign language enrollments at OU with enrollments at public AAU institutions.")
st.write("To assist in the discussion about the foreign language requirement in the Dodge Family College of Arts and Sciences (DFCAS) at the University of Oklahoma, I'm providing this [Streamlit](https://streamlit.io/) app that shows an analysis of data from the [Modern Language Association's](https://www.mla.org/) [Language Enrollment Database, 1958–2021](https://apps.mla.org/flsurvey_search).")
st.write("**NOTE**: The numbers displayed here are from the MLA report's 'UG TOTAL' column, representing all enrollment in a given language at lower and upper levels.")
st.write("Use the dropdown to select a language. The reports will change to show the results.")

@st.cache_data
def load_data():
    return pd.read_csv("institutions.csv")

institutions = load_data()

# Language selection
selected_language = st.selectbox("Select a Language:", institutions['LANGUAGE'].unique())

# Institution Rankings by Language
st.subheader(f"Institution Rankings for {selected_language}")

# Filter data
lang_df = institutions[institutions['LANGUAGE'] == selected_language]
ranking_df = lang_df[lang_df['SRVY_YEAR'] == 2021].sort_values('UG TOTAL', ascending=False)
ranking_df['RANK'] = pd.RangeIndex(start=1, stop=len(ranking_df) + 1)

def highlight_ou_html(df):
    """
    Converts a dataframe to an HTML table, highlighting rows where 'U OF OKLAHOMA' is in the 'UNIV' column.
    """
    # Start the HTML table
    html = '<table style="width:100%; border-collapse: collapse;">'
    
    # Add table headers
    html += '<thead><tr>'
    for col in df.columns:
        html += f'<th style="border: 1px solid black; padding: 5px; text-align: left;">{col}</th>'
    html += '</tr></thead>'

    # Add table rows
    html += '<tbody>'
    for _, row in df.iterrows():
        if row['UNIV'] == 'U OF OKLAHOMA':  # Highlight this row
            html += '<tr style="background-color: #841617; color: white; font-weight: bold;">'
        else:
            html += '<tr>'
        for col in df.columns:
            html += f'<td style="border: 1px solid black; padding: 5px;">{row[col]}</td>'
        html += '</tr>'
    html += '</tbody></table>'

    return html

# Filter and create the ranking dataframe
filtered_df = ranking_df[['RANK','UNIV', 'UG TOTAL']]

# Convert to HTML with highlights
highlighted_table = highlight_ou_html(filtered_df)

# Display in Streamlit
st.write(f"Ranking for {selected_language} in 2021")
st.markdown(highlighted_table, unsafe_allow_html=True)


# OU vs. Other Institutions Comparison
st.subheader(f"OU vs. Average for All AAU Institutions for {selected_language}")

# Separate OU and others
ou_df = lang_df[lang_df['UNIV'] == 'U OF OKLAHOMA']
other_df = lang_df[lang_df['UNIV'] != 'U OF OKLAHOMA']

# Safely calculate metrics with error handling
avg_other = other_df['UG TOTAL'].mean()  # May result in NaN
avg_other = int(avg_other) if not pd.isna(avg_other) else None

ou_total = ou_df['UG TOTAL'].iloc[0] if not ou_df.empty else None
ou_total = int(ou_total) if ou_total is not None else None

# Display warnings for missing data at the top
if avg_other is None:
    avg_other = "none"
    st.warning(f"No enrollment data available for public AAU institutions in {selected_language}.")
if ou_total is None:
    st.warning(f"No enrollment data available for OU in {selected_language}.")

# Handle cases where no data is available for both
if avg_other is None and ou_total is None:
    st.warning(f"No enrollment data available for {selected_language}.")
else:
    # Create a comparison table
    comparison_table = pd.DataFrame({
        "Metric": ["Average at Public AAU's", "OU"],
        "UG TOTAL": [avg_other, ou_total]
    })

    # Convert to HTML table and hide the index
    html_table = comparison_table.to_html(index=False, border=0)

    # Render the table in Streamlit
    st.markdown(html_table, unsafe_allow_html=True)


# Enrollment Trend Graphs
import matplotlib.pyplot as plt

st.subheader(f"Enrollment Trends for {selected_language}")

def lang_compare_streamlit(lang):
    """
    Compare enrollment trends in a given language at OU to other public AAU institutions.

    Args:
        lang: The name of a language as it appears in the LANGUAGE column.

    Displays:
        Line graph of enrollment trends at OU vs. other public AAU institutions.
    """
    # Filter for OU and other institutions
    ou = institutions[institutions['UNIV'] == 'U OF OKLAHOMA']
    aau = institutions[~institutions['UNIV'].isin(['U OF OKLAHOMA'])]
    
    # Filter by the selected language
    ou_lang = ou[ou['LANGUAGE'] == lang]
    aau_lang = aau[aau['LANGUAGE'] == lang]
    
    # Check if there is data for the selected language
    if ou_lang.empty and aau_lang.empty:
        st.warning(f"No data available for {lang}. Please select another language.")
        return
    
    # Group by year and calculate mean enrollments
    ou_lang_grouped = ou_lang.groupby(['LANGUAGE', 'SRVY_YEAR'])['UG TOTAL'].mean().reset_index()
    aau_lang_mean = aau_lang.groupby(['LANGUAGE', 'SRVY_YEAR'])['UG TOTAL'].mean().reset_index()

    # Display warnings at the top
    if ou_lang_grouped.empty:
        st.warning(f"No enrollment data available for OU in {lang}.")
    if aau_lang_mean.empty:
        st.warning(f"No enrollment data available for public AAU institutions in {lang}.")
    
    # Plot data
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot OU data if available
    if not ou_lang_grouped.empty:
        ax.plot(
            ou_lang_grouped['SRVY_YEAR'],
            ou_lang_grouped['UG TOTAL'],
            label='University of Oklahoma',
            color='#841617',
            marker='o',
        )
    
    # Plot AAU data if available
    if not aau_lang_mean.empty:
        ax.plot(
            aau_lang_mean['SRVY_YEAR'],
            aau_lang_mean['UG TOTAL'],
            label='Public AAU Institutions',
            color='#0070b9',
            marker='s',
        )
    
    # Customize the plot
    ax.set_title(f'Total UG Enrollment for {lang}')
    ax.set_xlabel('Year')
    ax.set_ylabel('Enrollment')
    ax.legend()

    # Set x-axis ticks to the exact years in SRVY_YEAR
    years = ou_lang_grouped['SRVY_YEAR'].unique()
    plt.xticks(ticks=years, labels=years)

    ax.grid(True)

    # Display the plot
    st.pyplot(fig)

lang_compare_streamlit(selected_language)

# File Download
st.subheader(f"Download Data for {selected_language}")
st.write("Download a CSV file for the selected language.")

# Convert dataframe to CSV
csv = ranking_df.to_csv(index=False)

st.download_button(
    label="Download Rankings as CSV",
    data=csv,
    file_name=f"{selected_language}_rankings.csv",
    mime='text/csv',
)

st.subheader("Download the Entire Dataset")

st.write("Click below to download the entire set of data on foreign language enrollment at public AAU institutions and OU.")
st.download_button(
    label="Download All Data",
    data=csv,
    file_name=f"institutions.csv",
    mime='text/csv',
)