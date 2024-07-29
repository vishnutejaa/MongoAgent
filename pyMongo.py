from pymongo import MongoClient
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os


# Replace the placeholder with your EC2 instance's public IP address or domain name
ec2_instance_ip = ''

port = 27017  # Default MongoDB port
mongo_url = f"mongodb://{ec2_instance_ip}:{port}/"
client = MongoClient(mongo_url)

# Connect to MongoDB
try:
    client.admin.command('ismaster')
    print("MongoDB connection successful")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    exit()

prompt_template = ChatPromptTemplate.from_template(
    """
    This JSON object holds detailed information about movies. Each field serves a specific purpose:
    
    - 'Title': Name of the movie.
    - 'Year': Year of release.
    - 'Rated': Movie's rating.
    - 'Released': Official release date.
    - 'Runtime': Duration of the movie.
    - 'Genre': Categorization of the movie.
    - 'Director': Name of the movie's director.
    - 'Writer': Screenplay and original graphic novel authors.
    - 'Actors': Main cast members.
    - 'Plot': Brief summary of the storyline.
    - 'Language': Language of the movie.
    - 'Country': Country where it was produced.
    - 'Awards': Number of awards won or nominated.
    - 'Poster': URL link to the movie poster.
    - 'Metascore': Metacritic score.
    - 'imdbRating': IMDb rating.
    - 'imdbVotes': Total IMDb votes.
    - 'imdbID': IMDb unique identifier.
    - 'Type': Type of media.
    - 'Response': API response status.
    - 'Images': URLs to related images.
    
    We're here to assist you in crafting MongoDB queries as an expert. Our collection name is 'film'.
    
    Example: "Which year was the movie Avatar released?" Answer: film.find({{'Title': 'Avatar'}}, {{'Year': 1, '_id': 0}})
    
    Now, your turn! Respond with a query in the same format, without any extra information: {user_query}
    """
)

# Set up the OpenAI client
# openai_api_key = ''

# Initialize OpenAI with the GPT-4 model
llm = ChatOpenAI(
    api_key=openai_api_key,
    model_name="gpt-4",
    temperature=0.5,
    max_tokens=1024
)

# Define the user query
user_query = "give me a list of all movies names"

# Format the prompt
formatted_prompt = prompt_template.format(user_query=user_query)

# Generate the query
response = llm(formatted_prompt)

print("llm response: ")
print(response)

# Extract the query string from the response content
query_string = response.content.strip()
print("query_string: ")
print(query_string)


# # film.find({}, {'Title': 1, '_id': 0})

# ######################################################

import ast

def parse_query(query_string):
    # Remove the prefix and suffix
    query_core = query_string.replace("db.", "").replace("find(", "").rstrip(")")
    collection_name, query_params = query_core.split(".", 1)
    query, projection = query_params.split("}, {", 1)
    query = query + "}"
    projection = "{" + projection
    return collection_name, ast.literal_eval(query), ast.literal_eval(projection)

print(parse_query(query_string))


# Parse the query string
collection_name, query, projection = parse_query(query_string)
print(collection_name)
print(query)
print(projection)

db = client['film_det']  # Replace with your database name

# Access the collection
collection = db[collection_name]
# # Execute the query
results = collection.find(query, projection)
# # Print the results
for result in results:
    print(result)
