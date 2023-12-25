![y_page_header](https://github.com/Bhskr25/YTDataHarvestWarehouse/assets/95600191/3a39d6f6-f303-4dc6-bab6-080d9dee42b9)
#####
# YOUTUBE DATA HARVESTING AND WARE HOUSING 
> USING MONGO_DB, MySQL AND STREAMLIT
---
## Project Intro/Objective

The purpose of this project is to collect, store, and analyze data from YouTube channels using the YouTube Data API. The project involves data harvesting from YouTube, warehousing the collected data in both MongoDB and MySQL databases, and presenting the information through an interactive Streamlit web application.
> The goal is to enable users to explore and analyze the channel details, videos, and comments, providing insights into YouTube content and engagement metrics.

---
### Methods Used
* API-Integration (YouTube Data API)
* Data Harvesting
* Data Warehousing
* UserInteractions (Streamlit)
* Query (SQL)
---
### Technologies
* Python
* MongoDB
* MySql
* Pandas
* Streamlit
---
## Project Description
This project leverages the YouTube Data API to harvest data from channels, videos, and comments. The collected information is stored in MongoDB and PostgreSQL databases, facilitating efficient data management. An interactive Streamlit web application enables users to explore and analyze YouTube content easily. The project is structured with modular functions for data harvesting, warehousing, and user interaction, providing a seamless experience.

### Project Wrokflow
<p align='center'><img src='https://github.com/Bhskr25/YTDataHarvestWarehouse/assets/95600191/3f15a9b4-cf73-482b-8f64-840fb1c53305' width='auto'></p>

#### Users can input channel IDs
  <p><img src='https://github.com/Bhskr25/YTDataHarvestWarehouse/assets/95600191/25522977-62ef-484f-b6fa-87e94d01f940' width='auto'></p>
  
#### Visualize tables
  <p><img src='https://github.com/Bhskr25/YTDataHarvestWarehouse/assets/95600191/5c64398d-103f-49a1-9124-383d73fdecc1' width='auto'></p>
  
#### Perform SQL queries for analysis
  <p><img src='https://github.com/Bhskr25/YTDataHarvestWarehouse/assets/95600191/e20ec374-8d95-42a7-b0e3-aa08251df619' width='auto'></p>
  
####
---

## Prerequests and Needs
The needs of this project can be categorized into several key aspects. Here is a list of the essential needs

1. **YouTube API Key:**
   - A valid YouTube Data API key is required to access YouTube data programmatically.
     >  Keep your API key private 

2. **Database Connectivity:**
   - MongoDB: A connection to a MongoDB database to store channel, playlist, video, and comment information.
   - MySQL: A connection to a MySQL database to store structured data in tables.

3. **Python Libraries:**
   - The project requires various Python libraries, including:
     - `pymongo`: For interacting with MongoDB.
     - `pymysql`: For connecting to and interacting with MySQL.
     - `pandas`: For data manipulation and analysis.
     - `streamlit`: For creating the interactive web application.
     - `googleapiclient`: For interacting with the YouTube Data API.

4. **User Input (Streamlit):**
   - User needs to provide YouTube channel IDs for data harvesting.

5. **Streamlit Web Application:**
   - Streamlit should be installed to run the web application for user interaction and data presentation.

6. **Database Services:**
   - MongoDB and MySQL databases should be available or set up for data warehousing.

7. **Data Warehousing Process:**
   - There is a need for a functioning process to store YouTube data in MongoDB and PostgreSQL databases.

8. **Data Analysis and Visualization:**
   - Users might require basic understanding and knowledge of SQL queries for data analysis.

9. **Environment Setup:**
    - Proper Python environment setup with necessary dependencies installed.

10. **Internet Connection:**
    - An active internet connection is needed to fetch data from the YouTube API.
---
## Getting Started
- Ensure you have the required API key for the YouTube Data API.
- Set up MongoDB and PostgreSQL databases.
- Install necessary Python libraries using requirements.txt.
- Run the script to harvest data, create tables, and launch the Streamlit application.

1. Create a virtual environment:
    ```python
    python -m venv venv
    ```
2. Activate the virtual environment:
    - On Windows:
        ```python
        .\venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```python
        source venv/bin/activate
        ```
3. Install required packages:
    ```python
    pip install -r requirements.txt
    ```
4. Running the Set-up in (venv)
    ```python
    streamlit run <python_file>.py
    ```
---

## Conclusion

Thank you for exploring our YouTube Data Harvesting and Warehousing project! Hope this tool proves valuable for data analysis needs.

### Contributing

If you'd like to contribute to this project, please follow the [Contribution Guidelines](CONTRIBUTING.md).

### Acknowledgments

A big thank you to all contributors who helped improve and refine this project.

### Contact

For any questions or suggestions, feel free to reach me out at [pranaybhskr@gmail.com].

Happy analyzing!

---

Feel free to customize this template based on your project's specific details and requirements.
