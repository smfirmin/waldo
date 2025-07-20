# AI Engineer Take-Home Assessment: News Article Geocoding & Summarization
Objective: The goal of this exercise is to assess your ability to build a lightweight, AI-powered application from end to end. You will leverage a Large Language Model (LLM) to parse unstructured text, extract geographic information, and visualize it on a map.

Time Allotment: 4 hours.

# The Challenge
News articles are rich with unstructured data. An important piece of that data is location. An event happens somewhere. Your task is to build an application that can take a news article, identify the locations mentioned, and plot them on an interactive map.

# Your application should:

1. Accept a news article as input (either via a URL or by pasting the full text).
2. Process the article to extract all relevant real-world locations (cities, states, countries, landmarks, etc.).
3. Convert these location names into structured geospatial data (latitude/longitude coordinates).
4. Display these coordinates as markers on an interactive map.

## Core Requirements
- Input: The application must provide a simple user interface to input either a URL to a news article or the full text of an article.
- LLM Integration: You must use a Large Language Model for at least one of the core steps (e.g., location extraction, text summarization, data structuring). We recommend using the Gemini API.
- Location Extraction: The application must identify and extract geopolitical entities and location names from the article text.
Geocoding: The extracted location names must be converted into latitude and longitude coordinates. You can use a traditional geocoding service or explore using an LLM for this.
- Map Visualization: The coordinates must be plotted as pins or markers on an interactive map (e.g., using libraries like Leaflet, Folium, or Plotly).

## Bonus Requirements
- Event Summarization: When a user hovers over or clicks on a map marker, display a brief, AI-generated summary (1-2 sentences) of the events that took place at that specific location, based on the article's content.
- Deployment: (not required but nice to have) a live url for your app/notebook 

# Technical Guidelines & Constraints
- Framework: You can build this as a simple web app using a framework like Streamlit, Flask, or FastAPI or as a self-contained notebook to run in Jupyter or Google Colab. The choice is yours.
- AI Assistants: You are allowed and encouraged to use AI coding assistants (e.g., Gemini, GitHub Copilot, ec.) to help you build faster. We are most interested in your ability to direct these tools to produce a high-quality, functional result.
- Documentation: Your code must be well-documented. Include a README.md file with clear, step-by-step instructions on how to set up the environment (e.g., requirements.txt, pip install ...), configure the necessary API keys, and run the application. Our team should be able to read your docs and follow your guidelines to run your app.

## LLM Recommendation & API Key Instructions
You can use Anthropic, OpenAI, local models, Google AI Studio, or Google Cloud Platform models. If you don’t already have accounts/keys, we recommend Google AI Studio Gemini for ease of free tier API setup and search grounding capabilities.


# Evaluation Criteria
You will be evaluated on the following:

- Functionality: Does the application meet all the core requirements? Does it handle reasonable edge cases (e.g., articles with no locations, ambiguous locations)?
Code Quality & Design: Is the code clean, well-organized, and commented? Did you make logical design choices?
- AI-Forward Approach: How effectively did you leverage the LLM? Did you use it in an innovative way (e.g., for data structuring, disambiguation, or the bonus summary)?
- Documentation & Reproducibility: Can another engineer easily set up and run your project using your instructions?

Submission Format
Please submit your work as a github link or single .zip file containing all your code, a requirements.txt file, and your README.md documentation.

Good luck! We look forward to seeing what you build.