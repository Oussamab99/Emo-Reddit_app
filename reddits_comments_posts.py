import praw,csv,re,emoji
from flask import Flask, render_template, request
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Create a Reddit instance
reddit = praw.Reddit(client_id='_eKNz7Dy3GHTLstei3H6_w',
                     client_secret='iJnOAsLDiPEnHEsqYLph_lCCY42QzQ',
                     user_agent='VotingBoY 1.0 by /u/PlazeBox')

# Create a new Flask application
app = Flask(__name__)

# Define a route that displays the form to enter the Reddit username
@app.route('/')
def index():
    return render_template('index.html')

# Define a route that receives the form data and retrieves the user's posts and comments
@app.route('/posts', methods=['POST'])
def posts():
    # Get the Reddit username from the form data
    username = request.form['username']

    # Retrieve the specified number of posts for the given user
    user = reddit.redditor(username)
    if not username:
        return "Please enter a username"
    submissions = user.submissions.new(limit=None)  # Adjust the limit as needed

    # Create a list to store the posts and comments
    posts = []

    # Iterate over the posts and retrieve their text and comments
    for submission in submissions:
        post = {
            'title': submission.title,
            'text': submission.selftext,
            'post_id': submission.id,
            'comments': []  # Initialize the comments list
        }
        posts.append(post)

    # Render the HTML template with the posts and comments
    return render_template('posts.html', username=username, posts=posts)

# Define a route that displays the comments for a specific post
@app.route('/comments/<post_id>')
def comments(post_id):

    # Retrieve the post with the given ID
    submission = reddit.submission(id=post_id)

    # Retrieve the comments for the post
    submission.comments.replace_more(limit=None)  # Retrieve all comments

    # Create a list to store the comments
    comments = []

    # Iterate over the comments and retrieve their text
    for comment in submission.comments.list():
        comments.append({
            'author': comment.author,
            'body': comment.body
        })

     # Open the CSV file in write mode
    with open('comments.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write the comments to the CSV file
        writer.writerow(['Comments'])
        for comment in comments:
            writer.writerow([ comment['body']])

    # Render the HTML template with the comments
    return render_template('comments.html', post_title=submission.title, comments=comments)

#define a routr that create the cv file cleaned and tokenized
@app.route('/Analyse', methods=['POST'])
def Analyse():
        
    def remove_special_characters(text):
        # Remove special characters using regular expressions
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        return text

    def remove_urls(text):
        # Remove URLs using regular expressions
        text = re.sub(r'http\S+|www\S+|https\S+', '', text)
        return text

    def remove_emojis(text):
        # Remove emojis using the emoji library
        text = emoji.demojize(text)
        text = re.sub(r':[a-zA-Z_]+:', '', text)
        return text

    # Read the contents of the comments.csv file
    with open('comments.csv', 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        comments = [row[0] for row in reader]

    # Process the comments to remove special characters, URLs, and emojis
    processed_comments = []
    for comment in comments:
        processed_comment = remove_special_characters(comment)
        processed_comment = remove_urls(processed_comment)
        processed_comment = remove_emojis(processed_comment)
        processed_comments.append(processed_comment)

    # Write the processed comments back to the comments.csv file
    with open('process_comments.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for comment in processed_comments:
            writer.writerow([comment])

    
    stemmer = PorterStemmer()
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))

    # Function to process comments
    def process_comments(comments):
        processed_comments = []
        for comment in comments:
            # Tokenize comment
            tokens = word_tokenize(comment)

            # Remove stopwords and perform stemming and lemmatization 
            processed_tokens = []
            for token in tokens:
                if token.lower() not in stop_words:
                    stemmed_token = stemmer.stem(token)
                    lemmatized_token = lemmatizer.lemmatize(stemmed_token, pos='v')
                    processed_tokens.append(lemmatized_token)

            # Add processed tokens to the list of comments
            processed_comments.append(processed_tokens)

        return processed_comments

    # Read comments from CSV file
    comments = []
    with open('process_comments.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            comments.append(row[0])

    # Process comments
    processed_comments = process_comments(comments)

    # Write processed words to CSV file
    with open('SLT.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Final Data'])
        for comment in processed_comments:
            writer.writerow([comment])

    return render_template('Analyse.html')


if __name__ == '__main__':
    app.run(debug=True)
