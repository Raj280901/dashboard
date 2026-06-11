import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import plotly.express as px

def upload_file():
    upload_file = st.file_uploader("Choose an excel file to be uploaded: ", type=["xlsx", "xls"])
    if upload_file:
        try:
            df = pd.read_excel(upload_file, sheet_name=None)
            st.success("File uploaded successfully")    

            return df

        except Exception as e:
            st.error("Error processing the excel - {}".format(e))
    else:
        st.info("Please upload an excel file to display the data")

        
def data_preview(df):
    try:
        s_names = list(df.keys())
        st.subheader("Data Preview")

        if "selected_sheet" not in st.session_state:
            st.session_state.selected_sheet = s_names[0]

        current_df = df[st.session_state.selected_sheet]

        st.dataframe(current_df, width='stretch', height=500)
        selected_sheet = option_menu(
            menu_title=None,
            options=s_names,
            icons=["file-earmark-spreadsheet"] * len(s_names),
            menu_icon="cast",
            default_index=s_names.index(st.session_state.selected_sheet),
            orientation="horizontal",
        )
        if selected_sheet != st.session_state.selected_sheet:
            st.session_state.selected_sheet = selected_sheet
            st.rerun()

        return s_names

    except Exception as e:
        st.error("Error processing the excel - {}".format(e))

def topFive_from_each_batch(df, s_names):
    try:
        top_from_each_batch = []  #for bar chart
        all_student_percentage = [] #pie chart for all student

        cols = st.columns(2)
        # print(len(s_names))
        for x in range(len(s_names)):
            # print(x)
            dfx = df[s_names[x]]
            if "Student Name" in dfx.columns and "TotalMarks" in dfx.columns:

                dfx["Percentage"] = (dfx["TotalMarks"]/300)*100
                dfx["Percentage"] = dfx["Percentage"].round(2)
                all_student_percentage.extend(dfx["Percentage"].tolist())

                top_5 = dfx.sort_values(by="TotalMarks", ascending=False).head(5)[["Student Name", "TotalMarks"]].reset_index(drop=True)

                with cols[x%(len(cols))]:
                    st.subheader("Top 5 from {}".format(s_names[x]))
                    # st.table(top_5.reset_index(drop=True))
                    st.dataframe(
                        top_5,
                        width='stretch',
                        hide_index=True
                    )
                top_student = top_5.iloc[0]
                top_from_each_batch.append({
                    "Batch": s_names[x],
                    "Student": top_student["Student Name"],
                    "Marks": top_student["TotalMarks"]
                })

            else:
                st.warning("Sheet {} must contain 'Name' and 'Marks' columns".format(df.keys()[x]))
        return top_from_each_batch, all_student_percentage

    except Exception as e:
        st.error("Error processing the excel - {}".format(e))

def topper_comparison_from_each_batch(top_from_each_batch):

    st.subheader("Comparison of top students accross Batches")

    chart_df = pd.DataFrame(top_from_each_batch)

    fig = px.bar(
        chart_df,
        x="Student",
        y="Marks",
        text="Marks"
        # width='stretch'
    )

    fig.update_traces(
        width=0.4,
        textposition="outside",
        marker_color="#3a1fb4"
    )

    fig.update_layout(
        xaxis=dict(
            tickangle=0,
        ),
        yaxis=dict(title="Marks"),
        margin=dict(l=20, r=20, t=20, b=40),
        height=450
    )

    st.plotly_chart(fig, width='stretch')

def performance_cateories(all_student_percentage):
    categories = []
                
    for p in all_student_percentage:
        if p >= 80:
            categories.append("Excellent (≥ 80%)")
        elif 60 < p <= 79:
            categories.append("Good (61% - 79%)")
        elif 40 < p <= 59:
            categories.append("Average (41% - 59%)")
        else:
            categories.append("Weak (≤ 40%)")

    pie_df = pd.DataFrame({"Category": categories})
    category_counts = pie_df["Category"].value_counts().reset_index()
    category_counts.columns = ["Category", "Student Count"]

    color_map = {
        "Excellent (≥ 80%)": "#3a1fb4",  # Green
        "Good (61% - 79%)": "#11be1d",   # Blue
        "Average (41% - 59%)": "#ff7f0e",# Orange
        "Weak (≤ 40%)": "#d62728"        # Red
    }

    fig_pie = px.pie(
        category_counts,
        names="Category",
        values="Student Count",
        color="Category",
        color_discrete_map=color_map,
        hole=0.3
    )

    fig_pie.update_traces(
        textinfo="percent+value",
        insidetextorientation="radial"
    )
    fig_pie.update_layout(
        margin=dict(l=20,r=20,t=20,b=40),
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
    )

    st.plotly_chart(fig_pie, width='stretch')

def phy_subject_difficulty(df, s_names):
    all_batches_phy_data = []
    for x in range(len(s_names)):
        dfx = df[s_names[x]]
        # print("Outside if-------------------------------------------------xxxxxxxxxxxxxxxxxxxxxx")
        # print(dfx.columns)
        # print(s_names[x])
        if 'MarksInPhysics' in dfx.columns:
            # print("Inside if---------------------------------------------------------")
            avg_physics = dfx['MarksInPhysics'].mean()
            all_batches_phy_data.append({
                "Batch": s_names[x],
                "Average Physics Score": round(avg_physics, 2)
            })

    summary_df = pd.DataFrame(all_batches_phy_data)
    print(summary_df)
    summary_df = summary_df.sort_values(by="Average Physics Score")

    # col1, col2 = st.columns([1,2])

    # with col1:
    st.subheader("Summary Table for Physics")
    st.dataframe(summary_df, width='stretch')

    lowest_batch = summary_df.iloc[0]['Batch']
    lowest_score = summary_df.iloc[0]['Average Physics Score']
    st.warning("**'{}'** struggles the most with Physics, averaging **{}** marks.".format(lowest_batch, lowest_score))

    # with col2:
    st.subheader("Visual Comparison for Physics")

    fig_b = px.bar(
        summary_df,
        x="Batch",
        y="Average Physics Score",
        title="Average Physics Score by Batch",
        labels={"Average Physics Score": "Avg Physics Marks"},
        color="Average Physics Score",
        color_continuous_scale="Reds_r"
    )

    st.plotly_chart(fig_b, width='stretch')

def chem_subject_difficulty(df, s_names):
    all_batches_chem_data = []
    for x in range(len(s_names)):
        dfx = df[s_names[x]]
        # print("Outside if-------------------------------------------------xxxxxxxxxxxxxxxxxxxxxx")
        # print(dfx.columns)
        # print(s_names[x])
        if 'MarksInChemistry' in dfx.columns:
            # print("Inside if---------------------------------------------------------")
            avg_chemistry = dfx['MarksInChemistry'].mean()
            all_batches_chem_data.append({
                "Batch": s_names[x],
                "Average Chemistry Score": round(avg_chemistry, 2)
            })

    summary_df = pd.DataFrame(all_batches_chem_data)
    print(summary_df)
    summary_df = summary_df.sort_values(by="Average Chemistry Score")

    # col1, col2 = st.columns([1,2])

    # with col1:
    st.subheader("Summary Table for Chemistry")
    st.dataframe(summary_df, width='stretch')

    lowest_batch = summary_df.iloc[0]['Batch']
    lowest_score = summary_df.iloc[0]['Average Chemistry Score']
    st.warning("**'{}'** struggles the most with Chemistry, averaging **{}** marks.".format(lowest_batch, lowest_score))

    # with col2:
    st.subheader("Visual Comparison for Chemistry")

    fig_b = px.bar(
        summary_df,
        x="Batch",
        y="Average Chemistry Score",
        title="Average Chemistry Score by Batch",
        labels={"Average Chemistry Score": "Avg Chemistry Marks"},
        color="Average Chemistry Score",
        color_continuous_scale="Reds_r"
    )

    st.plotly_chart(fig_b, width='stretch')

def math_subject_difficulty(df, s_names):
    all_batches_math_data = []
    for x in range(len(s_names)):
        dfx = df[s_names[x]]
        # print("Outside if-------------------------------------------------xxxxxxxxxxxxxxxxxxxxxx")
        # print(dfx.columns)
        # print(s_names[x])
        if 'MarksInMaths' in dfx.columns:
            # print("Inside if---------------------------------------------------------")
            avg_math = dfx['MarksInMaths'].mean()
            all_batches_math_data.append({
                "Batch": s_names[x],
                "Average Maths Score": round(avg_math, 2)
            })

    summary_df = pd.DataFrame(all_batches_math_data)
    print(summary_df)
    summary_df = summary_df.sort_values(by="Average Maths Score")

    # col1, col2 = st.columns([1,2])

    # with col1:
    st.subheader("Summary Table for Maths")
    st.dataframe(summary_df, width='stretch')

    lowest_batch = summary_df.iloc[0]['Batch']
    lowest_score = summary_df.iloc[0]['Average Maths Score']
    st.warning("**'{}'** struggles the most with Maths, averaging **{}** marks.".format(lowest_batch, lowest_score))

    # with col2:
    st.subheader("Visual Comparison for Maths")

    fig_b = px.bar(
        summary_df,
        x="Batch",
        y="Average Maths Score",
        title="Average Maths Score by Batch",
        labels={"Average Maths Score": "Avg Maths Marks"},
        color="Average Maths Score",
        color_continuous_scale="Reds_r"
    )

    st.plotly_chart(fig_b, width='stretch')

def download_file():
    url1 = "https://github.com/Raj280901/dashboard/raw/refs/heads/main/StudentData_File1.xlsx"
    response = requests.get(url1)
    if response.status_code == 200:
        return response.content
    else:
        st.error("Failed to fetch demo file")
        return None

st.write("Hello")
# path = "C:\\Users\\Raj Gandhi\\Downloads\\output\\data.xlsx"

file_data = download_file()
if file_data:
    st.download_button(
        label="Download Demo file",
        data=file_data,
        file_name="Student_data_demo.xlsx",
        mime="text/xlsx"
    )

df = upload_file()
if df:
    s_names = data_preview(df)
    top_from_each_batch, all_student_percentage = topFive_from_each_batch(df, s_names)
    topper_comparison_from_each_batch(top_from_each_batch)
    performance_cateories(all_student_percentage)
    phy_subject_difficulty(df, s_names)
    chem_subject_difficulty(df, s_names)
    math_subject_difficulty(df, s_names)
