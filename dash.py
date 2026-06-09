import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import plotly.express as px

st.write("Hello")
# path = "C:\\Users\\Raj Gandhi\\Downloads\\output\\data.xlsx"
upload_file = st.file_uploader("Choose an excel file to be uploaded: ", type=["xlsx", "xls"])

if upload_file:
    try:
        df = pd.read_excel(upload_file, sheet_name=None)
        
        s_names = list(df.keys())

        st.success("File uploaded successfully")

        st.subheader("Data Preview")

        if "selected_sheet" not in st.session_state:
            st.session_state.selected_sheet = s_names[0]

        current_df = df[st.session_state.selected_sheet]

        st.dataframe(current_df, width='stretch', height=500)

        # st.dataframe(df)
        # st.markdown("---")
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

        

        # st.subheader("Data Preview from: {}".format(selected_sheet))

        # current_df = df[selected_sheet]

        # st.dataframe(current_df, use_container_width=True, height=500)

        top_from_each_batch = [] #bar chart
        all_student_percentage = [] #pie chart for all student

        cols = st.columns(2)

        for x in range(len(s_names)):
            dfx = df[s_names[x]]
            # print(dfx)
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
                        use_container_width=True,
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

        if top_from_each_batch or all_student_percentage:
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

            st.subheader("Overall Performance Categories")
            if all_student_percentage:
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

    except Exception as e:
        st.error("Error processing the excel - {}".format(e))
else:
    st.info("Please upload an excel file to display the data")


