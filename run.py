import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('electric_car_survey')


def run_survey():
    """
    Runs the survey part of the application.
    Asks each of the questions contained in the questions worksheet in
    turn by calling the get question function and printing the returned
    question to screen.
    Returns the users responses to all questions as a list.
    """
    questions_worksheet = SHEET.worksheet('questions')
    number_of_questions = len(questions_worksheet.row_values(1))
    ind = 1
    responses = []
    while ind <= number_of_questions:
        question = get_question(ind)
        print(f'Question {ind}: {question[1]}\n')
        ind += 1
        final_answer_index = len(question) - 1
        answer_index = 2

        while answer_index <= final_answer_index:
            answer_number = answer_index - 1
            print(f'Answer {answer_number}: {question[answer_index]}\n')
            answer_index += 1
        
        response = input('Please enter the number for your answer:')
        responses.append(response)

    return responses


def get_question(ind):
    """
    Imports the required survey question from the questions worksheet
    """
    questions_worksheet = SHEET.worksheet('questions')
    question = questions_worksheet.col_values(ind)

    return question


def save_responses(responses):
    """
    Takes the responses from a particular survey, when passed to it,
    and saves them to the responses worksheet.
    """
    responses_worksheet = SHEET.worksheet('responses')
    responses_worksheet.append_row(responses)


responses = run_survey()
save_responses(responses)

