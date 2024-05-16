# -*- coding: utf-8 -*-
"""RFM Metrics

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1kxZTijIQCzyZUWcWu4ar2CZri8DuygKn
"""

# @title Setup
from google.colab import auth
from google.cloud import bigquery
from google.colab import data_table

project = 'precise-crowbar-414008' # Project ID inserted based on the query results selected to explore
location = 'EU' # Location inserted based on the query results selected to explore
client = bigquery.Client(project=project, location=location)
data_table.enable_dataframe_formatter()
auth.authenticate_user()

"""## Reference SQL syntax from the original job
Use the ```jobs.query```
[method](https://cloud.google.com/bigquery/docs/reference/rest/v2/jobs/query) to
return the SQL syntax from the job. This can be copied from the output cell
below to edit the query now or in the future. Alternatively, you can use
[this link](https://console.cloud.google.com/bigquery?j=precise-crowbar-414008:EU:bquxjob_39ae56e3_18ef0003633)
back to BigQuery to edit the query within the BigQuery user interface.
"""

# Running this code will display the query used to generate your previous job

job = client.get_job('bquxjob_39ae56e3_18ef0003633') # Job ID inserted based on the query results selected to explore
print(job.query)

"""# Result set loaded from BigQuery job as a DataFrame
Query results are referenced from the Job ID ran from BigQuery and the query
does not need to be re-run to explore results. The ```to_dataframe```
[method](https://googleapis.dev/python/bigquery/latest/generated/google.cloud.bigquery.job.QueryJob.html#google.cloud.bigquery.job.QueryJob.to_dataframe)
downloads the results to a Pandas DataFrame by using the BigQuery Storage API.

To edit query syntax, you can do so from the BigQuery SQL editor or in the
```Optional:``` sections below.
"""

# Running this code will read results from your previous job

job = client.get_job('bquxjob_39ae56e3_18ef0003633') # Job ID inserted based on the query results selected to explore
results = job.to_dataframe()
results

"""## Show descriptive statistics using describe()
Use the ```pandas DataFrame.describe()```
[method](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.describe.html)
to generate descriptive statistics. Descriptive statistics include those that
summarize the central tendency, dispersion and shape of a dataset’s
distribution, excluding ```NaN``` values. You may also use other Python methods
to interact with your data.
"""

results.describe()

"""# Editing by me"""

results.info()

results.isnull().sum()

import pandas as pd
merged_df = results.dropna(subset=['attributes_notifications_marketing_push'])
merged_df.isnull().sum()

columns_to_remove = ['ea_cardholderpresence', 'ea_merchant_mcc', 'ea_merchant_city', 'ea_merchant_country']

# Drop specified columns
df_cleaned=merged_df.drop(columns=columns_to_remove)

df_cleaned.isnull().sum()

"""# Eending to clean and marge"""

# Calculate RFM metrics
df_cleaned['recency'] = (df_cleaned['transaction_created_date'] - merged_df['user_created_date']).dt.days
df_cleaned['frequency'] = df_cleaned.groupby('user_id')['transaction_id'].transform('count')
df_cleaned['monetary'] = df_cleaned.groupby('user_id')['amount_usd'].transform('count')

# Segment customers
df_cleaned['customer_segment'] = pd.cut(df_cleaned['monetary'],
                                        bins=[-1, 100, 500, 1000, float('inf')],
                                        labels=['Very Low Value Customer', 'Low Value Customer', 'Medium Value Customer', 'High Value Customer'])

import plotly.express as px

# Create the scatter plot
fig = px.scatter(df_cleaned, x='num_contacts', y='frequency', color='customer_segment', color_discrete_sequence=['red', 'orange', 'green', 'blue'])

# Update y-axis range
fig.update_xaxes(range=[0, 500])

fig.update_layout(
    title='RFM Analysis',
    xaxis_title='Number of Contacts',
    yaxis_title='Total Transactions Amount (USD)',
    width=1200,
    height=800,
    font=dict(
        family="Courier New, monospace",
        size=14,
        color="black"
    )
)

fig.show()

fig = px.histogram(df_cleaned, x='recency', title='Recency Distribution', marginal='box', color_discrete_sequence=['skyblue'])
fig.update_layout(bargap=0.1)

fig.show()

fig2 = px.histogram(df_cleaned, x='frequency', title='Frequency Distribution', marginal='box', color_discrete_sequence=['salmon'])
fig2.update_layout(bargap=0.1)

fig2.show()

fig3 = px.histogram(df_cleaned, x='monetary', title='Monetary Distribution', marginal='box', color_discrete_sequence=['green'])
fig3.update_layout(bargap=0.1)

fig3.show()

"""# Spred + shape"""

# Creating subplots
from plotly.subplots import make_subplots

# Create figure with subplots
fig4 = make_subplots(rows=1, cols=3, subplot_titles=('Recency Distribution', 'Frequency Distribution', 'Monetary Distribution'))

# Add histograms to subplots
fig4.add_trace(fig['data'][0], row=1, col=1)
fig4.add_trace(fig2['data'][0], row=1, col=2)
fig4.add_trace(fig3['data'][0], row=1, col=3)

# Update layout
fig4.update_layout(
    showlegend=False,
    width=1200,
    height=600,
    title_text="Spread Shape of Recency, Frequency, and Monetary Distributions",
    bargap=0.1
)

# Show plot
fig4.show()